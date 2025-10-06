#!/usr/bin/env python3
"""
Redis Data Collector for Runtime State Registry

Collects and parses data from Redis sources including ReflectiveModule
auto-registration, DAG execution, and Celery tasks.
"""

import os
import sys
import json
import redis
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule, ModuleCapability, ModuleHealth, ModuleStatus, 
    GracefulDegradationResult
)
from ..core.models import (
    RedisServiceData, ServiceStatus, ServiceEvent, EventType,
    HistoricalStateEvent
)


class RedisDataCollector(ReflectiveModule):
    """
    Collects and parses data from Redis sources for Runtime State Registry.
    
    Handles:
    - ReflectiveModule auto-registration data (health:*, service:registry:*, beast_mode:active_modules)
    - DAG execution tracking data
    - Celery task queue data
    - Real-time pub/sub updates
    """
    
    def __init__(self, redis_host: str = None, redis_port: int = 6379):
        super().__init__()
        
        # Redis connection configuration
        self.redis_host = redis_host or self._resolve_redis_host()
        self.redis_port = redis_port
        self.redis_client = None
        self.pubsub_client = None
        
        # Data storage
        self._service_data: Dict[str, RedisServiceData] = {}
        self._last_collection: Optional[datetime] = None
        
        # Pub/sub monitoring
        self._pubsub_active = False
        self._pubsub_task: Optional[asyncio.Task] = None
        
        # Key patterns for different data sources
        self.key_patterns = {
            'health': 'health:*',
            'service_registry': 'service:registry:*',
            'active_modules': 'beast_mode:active_modules',
            'dag_execution': 'dag:execution:*',
            'celery_tasks': 'celery-task-meta-*'
        }
        
        # Initialize connections
        self._initialize_redis()
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            'module_id': 'redis_data_collector',
            'version': '1.0.0',
            'description': 'Redis data collection for Runtime State Registry',
            'redis_host': self.redis_host,
            'redis_port': self.redis_port,
            'key_patterns': self.key_patterns
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status."""
        issues = []
        health_score = 1.0
        
        # Check Redis connectivity
        if not self._test_redis_connection():
            issues.append("Redis connection failed")
            health_score -= 0.6
        
        # Check pub/sub status
        if not self._pubsub_active:
            issues.append("Pub/sub monitoring not active")
            health_score -= 0.2
        
        # Check data freshness
        if self._last_collection and (datetime.now() - self._last_collection).seconds > 300:
            issues.append("Data collection stale (>5 minutes)")
            health_score -= 0.2
        
        # Determine overall status
        if health_score >= 0.8:
            status = ModuleStatus.HEALTHY
        elif health_score >= 0.5:
            status = ModuleStatus.WARNING
        else:
            status = ModuleStatus.ERROR
        
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        return ModuleHealth(
            module_id='redis_data_collector',
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=uptime,
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation."""
        try:
            # Stop pub/sub monitoring
            if self._pubsub_active:
                self._stop_pubsub_monitoring()
            
            # Close Redis connections
            if self.pubsub_client:
                self.pubsub_client.close()
            if self.redis_client:
                self.redis_client.close()
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=[ModuleCapability.MONITORING],
                remaining_capabilities=[ModuleCapability.DATA_PROCESSING]
            )
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=self.get_capabilities(),
                remaining_capabilities=[],
                error_message=str(e)
            )
    
    def _resolve_redis_host(self) -> str:
        """Smart Redis host resolution with container detection."""
        # Check for explicit Redis host
        explicit_host = os.getenv('REDIS_HOST')
        if explicit_host:
            return explicit_host
        
        # Detect container environment
        if os.path.exists('/.dockerenv'):
            return "host.docker.internal"
        elif os.getenv('KUBERNETES_SERVICE_HOST'):
            return "redis-service"
        else:
            return "localhost"
    
    def _initialize_redis(self):
        """Initialize Redis connections."""
        try:
            # Main Redis client
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                password=os.getenv('REDIS_PASSWORD', ''),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Pub/sub client (separate connection)
            self.pubsub_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                password=os.getenv('REDIS_PASSWORD', ''),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connections
            if self._test_redis_connection():
                self._logger.info(f"Redis connected: {self.redis_host}:{self.redis_port}")
            else:
                self._logger.warning("Redis connection failed")
                
        except Exception as e:
            self._logger.error(f"Failed to initialize Redis: {e}")
            self.redis_client = None
            self.pubsub_client = None
    
    def _test_redis_connection(self) -> bool:
        """Test Redis connection."""
        try:
            if self.redis_client:
                self.redis_client.ping()
                return True
        except Exception:
            pass
        return False
    
    async def collect_all_data(self) -> Dict[str, RedisServiceData]:
        """Collect all Redis data and return structured service data."""
        if not self.redis_client:
            self._logger.error("Redis client not available")
            return {}
        
        try:
            self._service_data.clear()
            
            # Collect ReflectiveModule data
            await self._collect_reflective_module_data()
            
            # Collect health key data
            await self._collect_health_data()
            
            # Collect service registry data
            await self._collect_service_registry_data()
            
            # Collect DAG execution data
            await self._collect_dag_execution_data()
            
            # Collect Celery task data
            await self._collect_celery_task_data()
            
            self._last_collection = datetime.now()
            self._logger.info(f"Collected data for {len(self._service_data)} services")
            
            return self._service_data.copy()
            
        except Exception as e:
            self._logger.error(f"Data collection failed: {e}")
            self._increment_error_count()
            return {}
    
    async def _collect_reflective_module_data(self):
        """Collect ReflectiveModule auto-registration data."""
        try:
            # Get active modules
            active_modules = self.redis_client.hgetall("beast_mode:active_modules")
            
            for module_id, module_data_str in active_modules.items():
                try:
                    module_data = json.loads(module_data_str)
                    
                    # Create or update service data
                    if module_id not in self._service_data:
                        self._service_data[module_id] = RedisServiceData()
                    
                    service_data = self._service_data[module_id]
                    service_data.registry_key = "beast_mode:active_modules"
                    service_data.registry_data = module_data
                    service_data.module_type = module_data.get('module_type')
                    service_data.capabilities = module_data.get('capabilities', [])
                    
                    # Parse timestamp
                    if 'registered_at' in module_data:
                        try:
                            service_data.heartbeat_timestamp = datetime.fromisoformat(
                                module_data['registered_at'].replace('Z', '+00:00')
                            )
                        except (ValueError, AttributeError):
                            pass
                    
                except json.JSONDecodeError as e:
                    self._logger.warning(f"Failed to parse module data for {module_id}: {e}")
                    continue
                    
        except Exception as e:
            self._logger.error(f"Failed to collect ReflectiveModule data: {e}")
    
    async def _collect_health_data(self):
        """Collect health key data."""
        try:
            health_keys = self.redis_client.keys("health:*")
            
            for health_key in health_keys:
                service_name = health_key.replace("health:", "")
                health_data = self.redis_client.hgetall(health_key)
                
                # Create or update service data
                if service_name not in self._service_data:
                    self._service_data[service_name] = RedisServiceData()
                
                service_data = self._service_data[service_name]
                service_data.health_key = health_key
                service_data.health_data = health_data
                
                # Parse last check timestamp
                if 'last_check' in health_data:
                    try:
                        service_data.heartbeat_timestamp = datetime.fromisoformat(
                            health_data['last_check'].replace('Z', '+00:00')
                        )
                    except (ValueError, AttributeError):
                        pass
                        
        except Exception as e:
            self._logger.error(f"Failed to collect health data: {e}")
    
    async def _collect_service_registry_data(self):
        """Collect service registry data."""
        try:
            registry_keys = self.redis_client.keys("service:registry:*")
            
            for registry_key in registry_keys:
                service_name = registry_key.replace("service:registry:", "")
                registry_data = self.redis_client.hgetall(registry_key)
                
                # Create or update service data
                if service_name not in self._service_data:
                    self._service_data[service_name] = RedisServiceData()
                
                service_data = self._service_data[service_name]
                service_data.registry_key = registry_key
                service_data.registry_data = registry_data
                
                # Parse capabilities if stored as JSON
                if 'capabilities' in registry_data:
                    try:
                        service_data.capabilities = json.loads(registry_data['capabilities'])
                    except json.JSONDecodeError:
                        service_data.capabilities = [registry_data['capabilities']]
                        
        except Exception as e:
            self._logger.error(f"Failed to collect service registry data: {e}")
    
    async def _collect_dag_execution_data(self):
        """Collect DAG execution tracking data."""
        try:
            dag_keys = self.redis_client.keys("dag:execution:*")
            
            for dag_key in dag_keys:
                dag_data = self.redis_client.hgetall(dag_key)
                
                # Extract service information from DAG data
                if 'services' in dag_data:
                    try:
                        services = json.loads(dag_data['services'])
                        for service_name in services:
                            if service_name not in self._service_data:
                                self._service_data[service_name] = RedisServiceData()
                            
                            # Add DAG context to registry data
                            if not self._service_data[service_name].registry_data:
                                self._service_data[service_name].registry_data = {}
                            
                            self._service_data[service_name].registry_data['dag_context'] = {
                                'dag_key': dag_key,
                                'execution_data': dag_data
                            }
                    except json.JSONDecodeError:
                        pass
                        
        except Exception as e:
            self._logger.error(f"Failed to collect DAG execution data: {e}")
    
    async def _collect_celery_task_data(self):
        """Collect Celery task metadata."""
        try:
            celery_keys = self.redis_client.keys("celery-task-meta-*")
            
            # Group tasks by service/worker
            task_summary = {}
            
            for task_key in celery_keys:
                task_data = self.redis_client.get(task_key)
                if task_data:
                    try:
                        task_info = json.loads(task_data)
                        
                        # Extract worker/service information
                        worker = task_info.get('worker', 'unknown')
                        task_name = task_info.get('task', 'unknown')
                        
                        if worker not in task_summary:
                            task_summary[worker] = {
                                'tasks': [],
                                'last_activity': None
                            }
                        
                        task_summary[worker]['tasks'].append({
                            'task_name': task_name,
                            'status': task_info.get('status'),
                            'timestamp': task_info.get('date_done')
                        })
                        
                    except json.JSONDecodeError:
                        continue
            
            # Add Celery data to service data
            for worker, worker_data in task_summary.items():
                if worker not in self._service_data:
                    self._service_data[worker] = RedisServiceData()
                
                if not self._service_data[worker].registry_data:
                    self._service_data[worker].registry_data = {}
                
                self._service_data[worker].registry_data['celery_tasks'] = worker_data
                
        except Exception as e:
            self._logger.error(f"Failed to collect Celery task data: {e}")
    
    async def start_pubsub_monitoring(self):
        """Start Redis pub/sub monitoring for real-time updates."""
        if self._pubsub_active or not self.pubsub_client:
            return
        
        self._pubsub_active = True
        self._pubsub_task = asyncio.create_task(self._pubsub_monitoring_loop())
        self._logger.info("Started Redis pub/sub monitoring")
    
    async def stop_pubsub_monitoring(self):
        """Stop Redis pub/sub monitoring."""
        self._pubsub_active = False
        if self._pubsub_task:
            self._pubsub_task.cancel()
            try:
                await self._pubsub_task
            except asyncio.CancelledError:
                pass
        self._logger.info("Stopped Redis pub/sub monitoring")
    
    async def _pubsub_monitoring_loop(self):
        """Main pub/sub monitoring loop."""
        try:
            pubsub = self.pubsub_client.pubsub()
            
            # Subscribe to key patterns for real-time updates
            await pubsub.psubscribe('__keyspace@0__:health:*')
            await pubsub.psubscribe('__keyspace@0__:service:registry:*')
            await pubsub.psubscribe('__keyspace@0__:beast_mode:active_modules')
            
            while self._pubsub_active:
                try:
                    message = await pubsub.get_message(timeout=1.0)
                    if message and message['type'] == 'pmessage':
                        await self._handle_pubsub_message(message)
                        
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    self._logger.error(f"Pub/sub message handling error: {e}")
                    
        except Exception as e:
            self._logger.error(f"Pub/sub monitoring failed: {e}")
        finally:
            try:
                await pubsub.unsubscribe()
                await pubsub.close()
            except:
                pass
    
    async def _handle_pubsub_message(self, message):
        """Handle incoming pub/sub messages."""
        try:
            channel = message['channel']
            key = message['data']
            
            # Extract service name from key
            if ':health:' in channel:
                service_name = key.replace('health:', '')
            elif ':service:registry:' in channel:
                service_name = key.replace('service:registry:', '')
            elif ':beast_mode:active_modules' in channel:
                service_name = 'active_modules_update'
            else:
                return
            
            # Trigger incremental data collection for this service
            await self._collect_service_data(service_name, key)
            
        except Exception as e:
            self._logger.error(f"Failed to handle pub/sub message: {e}")
    
    async def _collect_service_data(self, service_name: str, key: str):
        """Collect data for a specific service."""
        try:
            if key.startswith('health:'):
                health_data = self.redis_client.hgetall(key)
                if service_name not in self._service_data:
                    self._service_data[service_name] = RedisServiceData()
                
                self._service_data[service_name].health_key = key
                self._service_data[service_name].health_data = health_data
                
            elif key.startswith('service:registry:'):
                registry_data = self.redis_client.hgetall(key)
                if service_name not in self._service_data:
                    self._service_data[service_name] = RedisServiceData()
                
                self._service_data[service_name].registry_key = key
                self._service_data[service_name].registry_data = registry_data
                
        except Exception as e:
            self._logger.error(f"Failed to collect data for service {service_name}: {e}")
    
    def _stop_pubsub_monitoring(self):
        """Stop pub/sub monitoring (synchronous version)."""
        self._pubsub_active = False
        if self._pubsub_task:
            self._pubsub_task.cancel()
    
    def get_service_data(self, service_name: str) -> Optional[RedisServiceData]:
        """Get data for a specific service."""
        return self._service_data.get(service_name)
    
    def get_all_service_data(self) -> Dict[str, RedisServiceData]:
        """Get all collected service data."""
        return self._service_data.copy()
    
    def detect_stale_data(self, max_age_minutes: int = 10) -> List[str]:
        """Detect services with stale data."""
        stale_services = []
        cutoff_time = datetime.now() - timedelta(minutes=max_age_minutes)
        
        for service_name, service_data in self._service_data.items():
            if (service_data.heartbeat_timestamp and 
                service_data.heartbeat_timestamp < cutoff_time):
                stale_services.append(service_name)
        
        return stale_services
    
    async def cleanup_stale_data(self, max_age_minutes: int = 60):
        """Clean up stale service data."""
        stale_services = self.detect_stale_data(max_age_minutes)
        
        for service_name in stale_services:
            self._logger.info(f"Removing stale data for service: {service_name}")
            del self._service_data[service_name]
        
        return len(stale_services)


# CLI interface for testing
async def main():
    """Main CLI interface for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Redis Data Collector")
    parser.add_argument('action', choices=['collect', 'monitor', 'health'],
                       help='Action to perform')
    parser.add_argument('--redis-host', help='Redis host override')
    
    args = parser.parse_args()
    
    collector = RedisDataCollector(redis_host=args.redis_host)
    
    try:
        if args.action == 'collect':
            data = await collector.collect_all_data()
            print(f"Collected data for {len(data)} services:")
            for service_name, service_data in data.items():
                print(f"  - {service_name}: {service_data.module_type or 'unknown'}")
        
        elif args.action == 'monitor':
            print("Starting pub/sub monitoring... Press Ctrl+C to stop")
            await collector.start_pubsub_monitoring()
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                await collector.stop_pubsub_monitoring()
                print("Monitoring stopped")
        
        elif args.action == 'health':
            health = collector.get_health_status()
            print(f"Status: {health.status.value}")
            print(f"Health Score: {health.health_score}")
            if health.issues:
                print("Issues:")
                for issue in health.issues:
                    print(f"  - {issue}")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())