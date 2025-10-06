"""
Status Persistence Layer

Provides Redis-based status persistence with brownfield safety.
Uses separate Redis namespace to avoid conflicts with Observatory.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import asdict
import os

from .models import DoctorStatus, BudgetStatus, CostAnalytics
from .doctor_status_manager import StatusChangeEvent
from .feature_flags import feature_flags, FeatureFlag
from .circuit_breaker import with_circuit_breaker
from .exceptions import ConsultationError
from .health_checker import ComponentHealth

logger = logging.getLogger(__name__)


class StatusPersistence:
    """
    Redis-based status persistence with brownfield safety
    
    Features:
    - Separate Redis namespace to avoid Observatory conflicts
    - Automatic key expiration and cleanup
    - Circuit breaker protection
    - Fallback to database when Redis unavailable
    - Connection pooling and health monitoring
    """
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        key_prefix: str = "ai_consultation",
        default_ttl: int = 3600,  # 1 hour
        max_connections: int = 10
    ):
        self.redis_url = redis_url or self._get_redis_url()
        self.key_prefix = key_prefix
        self.default_ttl = default_ttl
        self.max_connections = max_connections
        
        # Redis client
        self._redis_client = None
        self._connection_pool = None
        
        # Fallback mode
        self._fallback_mode = False
        self._fallback_storage: Dict[str, Any] = {}
        
        # Statistics
        self._stats = {
            'operations_total': 0,
            'operations_failed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'fallback_operations': 0
        }
    
    def _get_redis_url(self) -> str:
        """Get Redis URL from environment"""
        # Check for AI consultation specific Redis URL first
        redis_url = os.getenv('AI_CONSULTATION_REDIS_URL')
        if redis_url:
            return redis_url
        
        # Check for general Redis URL
        redis_url = os.getenv('REDIS_URL')
        if redis_url:
            # Modify to use different database to avoid Observatory conflicts
            if redis_url.endswith('/0'):
                redis_url = redis_url[:-1] + '1'  # Use database 1 instead of 0
            elif not redis_url.split('/')[-1].isdigit():
                redis_url += '/1'  # Add database 1
            return redis_url
        
        # Default to localhost with database 1
        return 'redis://localhost:6379/1'
    
    async def initialize(self) -> None:
        """Initialize Redis connection"""
        try:
            logger.info("Initializing Status Persistence")
            
            # Check if feature is enabled
            if not await feature_flags.is_enabled(FeatureFlag.REDIS_PERSISTENCE):
                logger.info("Redis persistence is disabled via feature flag")
                self._fallback_mode = True
                return
            
            # Try to initialize Redis
            await self._initialize_redis()
            
            logger.info(f"Status Persistence initialized - Fallback mode: {self._fallback_mode}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Status Persistence: {e}")
            self._fallback_mode = True
            # Don't raise - should degrade gracefully
    
    async def _initialize_redis(self) -> None:
        """Initialize Redis client and connection pool"""
        try:
            # Import Redis only if needed
            import redis.asyncio as redis
            
            # Create connection pool
            self._connection_pool = redis.ConnectionPool.from_url(
                self.redis_url,
                max_connections=self.max_connections,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Create Redis client
            self._redis_client = redis.Redis(
                connection_pool=self._connection_pool,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Test connection
            await self._redis_client.ping()
            
            # Set up key expiration monitoring
            await self._setup_key_monitoring()
            
            logger.info("Redis connection established")
            
        except ImportError:
            logger.warning("Redis not available - using fallback mode")
            self._fallback_mode = True
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e} - using fallback mode")
            self._fallback_mode = True
    
    async def _setup_key_monitoring(self) -> None:
        """Set up Redis key expiration monitoring"""
        try:
            # Enable keyspace notifications for expired keys
            await self._redis_client.config_set('notify-keyspace-events', 'Ex')
            
        except Exception as e:
            logger.warning(f"Failed to set up key monitoring: {e}")
    
    def _make_key(self, key_type: str, identifier: str = "") -> str:
        """Create Redis key with proper namespace"""
        if identifier:
            return f"{self.key_prefix}:{key_type}:{identifier}"
        return f"{self.key_prefix}:{key_type}"
    
    @with_circuit_breaker('redis_operations')
    async def store_doctor_status(self, status: DoctorStatus, ttl: Optional[int] = None) -> bool:
        """Store doctor status in Redis"""
        try:
            self._stats['operations_total'] += 1
            
            if self._fallback_mode:
                return await self._store_fallback('doctor_status', asdict(status))
            
            key = self._make_key('doctor_status', 'current')
            data = {
                'is_available': status.is_available,
                'reason': status.reason.value,
                'cost_budget_remaining': status.cost_budget_remaining,
                'daily_usage': status.daily_usage,
                'monthly_usage': status.monthly_usage,
                'last_updated': status.last_updated.isoformat(),
                'next_budget_reset': status.next_budget_reset.isoformat() if status.next_budget_reset else None,
                'active_sessions': status.active_sessions,
                'queue_length': status.queue_length
            }
            
            # Store with TTL
            ttl = ttl or self.default_ttl
            await self._redis_client.setex(key, ttl, json.dumps(data))
            
            # Also store in history
            history_key = self._make_key('doctor_status_history', str(int(datetime.utcnow().timestamp())))
            await self._redis_client.setex(history_key, ttl * 24, json.dumps(data))  # Keep history longer
            
            logger.debug(f"Stored doctor status in Redis: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store doctor status: {e}")
            self._stats['operations_failed'] += 1
            return await self._store_fallback('doctor_status', asdict(status))
    
    @with_circuit_breaker('redis_operations')
    async def get_doctor_status(self) -> Optional[DoctorStatus]:
        """Get current doctor status from Redis"""
        try:
            self._stats['operations_total'] += 1
            
            if self._fallback_mode:
                data = await self._get_fallback('doctor_status')
                if data:
                    self._stats['cache_hits'] += 1
                    return self._deserialize_doctor_status(data)
                self._stats['cache_misses'] += 1
                return None
            
            key = self._make_key('doctor_status', 'current')
            data = await self._redis_client.get(key)
            
            if data:
                self._stats['cache_hits'] += 1
                status_data = json.loads(data)
                return self._deserialize_doctor_status(status_data)
            
            self._stats['cache_misses'] += 1
            return None
            
        except Exception as e:
            logger.error(f"Failed to get doctor status: {e}")
            self._stats['operations_failed'] += 1
            return None
    
    def _deserialize_doctor_status(self, data: Dict[str, Any]) -> DoctorStatus:
        """Deserialize doctor status from stored data"""
        from .models import DoctorStatusReason
        
        return DoctorStatus(
            is_available=data['is_available'],
            reason=DoctorStatusReason(data['reason']),
            cost_budget_remaining=data['cost_budget_remaining'],
            daily_usage=data['daily_usage'],
            monthly_usage=data['monthly_usage'],
            last_updated=datetime.fromisoformat(data['last_updated']),
            next_budget_reset=datetime.fromisoformat(data['next_budget_reset']) if data['next_budget_reset'] else None,
            active_sessions=data['active_sessions'],
            queue_length=data['queue_length']
        )
    
    @with_circuit_breaker('redis_operations')
    async def store_budget_status(self, budget: BudgetStatus, ttl: Optional[int] = None) -> bool:
        """Store budget status in Redis"""
        try:
            self._stats['operations_total'] += 1
            
            if self._fallback_mode:
                return await self._store_fallback('budget_status', asdict(budget))
            
            key = self._make_key('budget_status', 'current')
            data = asdict(budget)
            # Convert datetime to ISO string
            data['last_updated'] = budget.last_updated.isoformat()
            
            ttl = ttl or self.default_ttl
            await self._redis_client.setex(key, ttl, json.dumps(data))
            
            logger.debug(f"Stored budget status in Redis: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store budget status: {e}")
            self._stats['operations_failed'] += 1
            return await self._store_fallback('budget_status', asdict(budget))
    
    @with_circuit_breaker('redis_operations')
    async def get_budget_status(self) -> Optional[BudgetStatus]:
        """Get current budget status from Redis"""
        try:
            self._stats['operations_total'] += 1
            
            if self._fallback_mode:
                data = await self._get_fallback('budget_status')
                if data:
                    self._stats['cache_hits'] += 1
                    data['last_updated'] = datetime.fromisoformat(data['last_updated'])
                    return BudgetStatus(**data)
                self._stats['cache_misses'] += 1
                return None
            
            key = self._make_key('budget_status', 'current')
            data = await self._redis_client.get(key)
            
            if data:
                self._stats['cache_hits'] += 1
                budget_data = json.loads(data)
                budget_data['last_updated'] = datetime.fromisoformat(budget_data['last_updated'])
                return BudgetStatus(**budget_data)
            
            self._stats['cache_misses'] += 1
            return None
            
        except Exception as e:
            logger.error(f"Failed to get budget status: {e}")
            self._stats['operations_failed'] += 1
            return None
    
    @with_circuit_breaker('redis_operations')
    async def store_status_event(self, event: StatusChangeEvent, ttl: Optional[int] = None) -> bool:
        """Store status change event in Redis"""
        try:
            self._stats['operations_total'] += 1
            
            event_data = {
                'timestamp': event.timestamp.isoformat(),
                'old_status': event.old_status,
                'new_status': event.new_status,
                'reason': event.reason.value,
                'transition_type': event.transition_type.value,
                'triggered_by': event.triggered_by,
                'cost_data': event.cost_data,
                'metadata': event.metadata
            }
            
            if self._fallback_mode:
                return await self._store_fallback(f'status_event_{event.timestamp.timestamp()}', event_data)
            
            # Store event with timestamp as part of key
            key = self._make_key('status_events', str(int(event.timestamp.timestamp())))
            
            ttl = ttl or (self.default_ttl * 24)  # Keep events longer
            await self._redis_client.setex(key, ttl, json.dumps(event_data))
            
            # Also add to recent events list
            recent_key = self._make_key('recent_events')
            await self._redis_client.lpush(recent_key, json.dumps(event_data))
            await self._redis_client.ltrim(recent_key, 0, 99)  # Keep last 100 events
            await self._redis_client.expire(recent_key, ttl)
            
            logger.debug(f"Stored status event in Redis: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store status event: {e}")
            self._stats['operations_failed'] += 1
            return False
    
    @with_circuit_breaker('redis_operations')
    async def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent status change events"""
        try:
            self._stats['operations_total'] += 1
            
            if self._fallback_mode:
                # Return events from fallback storage
                events = []
                for key, value in self._fallback_storage.items():
                    if key.startswith('status_event_'):
                        events.append(value)
                # Sort by timestamp and limit
                events.sort(key=lambda x: x['timestamp'], reverse=True)
                return events[:limit]
            
            key = self._make_key('recent_events')
            event_data = await self._redis_client.lrange(key, 0, limit - 1)
            
            events = []
            for data in event_data:
                try:
                    event = json.loads(data)
                    events.append(event)
                except json.JSONDecodeError:
                    continue
            
            self._stats['cache_hits'] += 1
            return events
            
        except Exception as e:
            logger.error(f"Failed to get recent events: {e}")
            self._stats['operations_failed'] += 1
            return []
    
    @with_circuit_breaker('redis_operations')
    async def store_session_data(self, session_id: str, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Store session-specific data"""
        try:
            self._stats['operations_total'] += 1
            
            if self._fallback_mode:
                return await self._store_fallback(f'session_{session_id}', data)
            
            key = self._make_key('sessions', session_id)
            ttl = ttl or 1800  # 30 minutes for session data
            
            await self._redis_client.setex(key, ttl, json.dumps(data))
            
            logger.debug(f"Stored session data in Redis: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store session data: {e}")
            self._stats['operations_failed'] += 1
            return False
    
    @with_circuit_breaker('redis_operations')
    async def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session-specific data"""
        try:
            self._stats['operations_total'] += 1
            
            if self._fallback_mode:
                data = await self._get_fallback(f'session_{session_id}')
                if data:
                    self._stats['cache_hits'] += 1
                    return data
                self._stats['cache_misses'] += 1
                return None
            
            key = self._make_key('sessions', session_id)
            data = await self._redis_client.get(key)
            
            if data:
                self._stats['cache_hits'] += 1
                return json.loads(data)
            
            self._stats['cache_misses'] += 1
            return None
            
        except Exception as e:
            logger.error(f"Failed to get session data: {e}")
            self._stats['operations_failed'] += 1
            return None
    
    @with_circuit_breaker('redis_operations')
    async def delete_session_data(self, session_id: str) -> bool:
        """Delete session-specific data"""
        try:
            self._stats['operations_total'] += 1
            
            if self._fallback_mode:
                key = f'session_{session_id}'
                if key in self._fallback_storage:
                    del self._fallback_storage[key]
                return True
            
            key = self._make_key('sessions', session_id)
            await self._redis_client.delete(key)
            
            logger.debug(f"Deleted session data from Redis: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete session data: {e}")
            self._stats['operations_failed'] += 1
            return False
    
    async def _store_fallback(self, key: str, data: Any) -> bool:
        """Store data in fallback memory storage"""
        try:
            self._fallback_storage[key] = data
            self._stats['fallback_operations'] += 1
            return True
        except Exception as e:
            logger.error(f"Fallback storage failed: {e}")
            return False
    
    async def _get_fallback(self, key: str) -> Optional[Any]:
        """Get data from fallback memory storage"""
        try:
            data = self._fallback_storage.get(key)
            if data:
                self._stats['fallback_operations'] += 1
            return data
        except Exception as e:
            logger.error(f"Fallback retrieval failed: {e}")
            return None
    
    async def cleanup_expired_keys(self) -> int:
        """Clean up expired keys (maintenance task)"""
        try:
            if self._fallback_mode:
                # Clean up old fallback data (simple time-based cleanup)
                current_time = datetime.utcnow().timestamp()
                expired_keys = []
                
                for key in self._fallback_storage:
                    if key.startswith('status_event_'):
                        # Extract timestamp from key
                        try:
                            timestamp = float(key.split('_')[-1])
                            if current_time - timestamp > self.default_ttl:
                                expired_keys.append(key)
                        except (ValueError, IndexError):
                            continue
                
                for key in expired_keys:
                    del self._fallback_storage[key]
                
                return len(expired_keys)
            
            # Redis cleanup - get keys that are about to expire
            pattern = f"{self.key_prefix}:*"
            keys = await self._redis_client.keys(pattern)
            
            expired_count = 0
            for key in keys:
                ttl = await self._redis_client.ttl(key)
                if ttl == -1:  # No expiration set
                    await self._redis_client.expire(key, self.default_ttl)
                elif ttl < 60:  # About to expire in less than 1 minute
                    expired_count += 1
            
            return expired_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired keys: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get persistence statistics"""
        stats = dict(self._stats)
        
        if not self._fallback_mode and self._redis_client:
            try:
                # Get Redis info
                info = await self._redis_client.info()
                stats.update({
                    'redis_connected_clients': info.get('connected_clients', 0),
                    'redis_used_memory': info.get('used_memory', 0),
                    'redis_keyspace_hits': info.get('keyspace_hits', 0),
                    'redis_keyspace_misses': info.get('keyspace_misses', 0)
                })
            except Exception:
                pass
        
        stats.update({
            'fallback_mode': self._fallback_mode,
            'fallback_storage_size': len(self._fallback_storage)
        })
        
        return stats
    
    async def health_check(self) -> ComponentHealth:
        """Perform health check"""
        try:
            if self._fallback_mode:
                return ComponentHealth(
                    component="status_persistence",
                    status="degraded",
                    response_time=0.0,
                    error_message="Running in fallback mode",
                    metadata={
                        "fallback_storage_size": len(self._fallback_storage),
                        "operations_total": self._stats['operations_total'],
                        "operations_failed": self._stats['operations_failed']
                    },
                    last_check=datetime.utcnow()
                )
            
            # Test Redis connection
            start_time = datetime.utcnow()
            await self._redis_client.ping()
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return ComponentHealth(
                component="status_persistence",
                status="healthy",
                response_time=response_time,
                error_message=None,
                metadata={
                    "operations_total": self._stats['operations_total'],
                    "operations_failed": self._stats['operations_failed'],
                    "cache_hit_rate": self._stats['cache_hits'] / max(1, self._stats['operations_total']),
                    "redis_url": self.redis_url.split('@')[-1] if '@' in self.redis_url else self.redis_url
                },
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            return ComponentHealth(
                component="status_persistence",
                status="unhealthy",
                response_time=0.0,
                error_message=str(e),
                metadata={},
                last_check=datetime.utcnow()
            )
    
    async def cleanup(self) -> None:
        """Cleanup persistence resources"""
        try:
            logger.info("Cleaning up Status Persistence")
            
            if self._redis_client:
                await self._redis_client.close()
            
            if self._connection_pool:
                await self._connection_pool.disconnect()
            
            self._fallback_storage.clear()
            
            logger.info("Status Persistence cleaned up")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


# Global persistence instance
status_persistence = StatusPersistence()


async def initialize_persistence() -> None:
    """Initialize the status persistence"""
    await status_persistence.initialize()


async def cleanup_persistence() -> None:
    """Cleanup the status persistence"""
    await status_persistence.cleanup()