#!/usr/bin/env python3
"""
Redis-based Execution Tracking System
=====================================
Centralized tracking of specification executions with Redis persistence.

Author: Beast Mode Framework
Date: 2025-10-01
Purpose: Track launched specifications, their status, and check-in history
"""

import json
import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from src.security.secure_credentials import get_secure_credentials


class ExecutionStatus(Enum):
    """Execution status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    STUCK = "stuck"
    UNKNOWN = "unknown"


@dataclass
class ExecutionRecord:
    """Execution record for a specification."""
    execution_id: str
    spec_name: str
    status: ExecutionStatus
    started_at: datetime
    last_checkin: datetime
    completed_at: Optional[datetime] = None
    pid: Optional[int] = None
    log_file: Optional[str] = None
    progress_file: Optional[str] = None
    lock_file: Optional[str] = None
    workflow_version: str = "v2.0"
    efficiency_gain: Optional[float] = None
    total_tasks: Optional[int] = None
    completed_tasks: Optional[int] = None
    estimated_hours: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class CheckinRecord:
    """Check-in record for execution monitoring."""
    execution_id: str
    timestamp: datetime
    status: ExecutionStatus
    phase: Optional[str] = None
    progress_percentage: Optional[float] = None
    message: Optional[str] = None
    resource_usage: Optional[Dict[str, float]] = None


class RedisExecutionTracker(ReflectiveModule):
    """Redis-based execution tracking system."""
    
    def __init__(self, redis_host: str = None, redis_port: int = None, redis_password: str = None):
        super().__init__()
        
        # ✅ SECURE: Use secure credentials helper for configuration
        creds = get_secure_credentials(strict_mode=False)
        redis_config = creds.get_redis_config()
        
        self.redis_host = redis_host or redis_config['host']
        self.redis_port = redis_port or redis_config['port']
        self.redis_password = redis_password or redis_config['password']
        self.redis_client: Optional[redis.Redis] = None
        self.tracker_id = f"execution_tracker_{uuid.uuid4().hex[:8]}"
        
        # Redis key prefixes
        self.EXECUTION_PREFIX = "execution:"
        self.CHECKIN_PREFIX = "checkin:"
        self.ACTIVE_EXECUTIONS_KEY = "active_executions"
        self.EXECUTION_HISTORY_KEY = "execution_history"
        
    def get_capabilities(self) -> Dict[str, Any]:
        """Return component capabilities."""
        return {
            'execution_tracking': True,
            'redis_persistence': REDIS_AVAILABLE,
            'status_monitoring': True,
            'checkin_tracking': True,
            'execution_history': True,
            'workflow_version': 'v2.0'
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Return component health status."""
        return {
            'status': 'healthy' if self.redis_client else 'degraded',
            'redis_connected': self.redis_client is not None,
            'tracker_id': self.tracker_id,
            'redis_host': self.redis_host,
            'redis_port': self.redis_port
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Return module information."""
        return {
            'name': 'RedisExecutionTracker',
            'version': '2.0.0',
            'description': 'Redis-based execution tracking for specifications',
            'dependencies': ['redis', 'ReflectiveModule'],
            'workflow_control': 'spec-creation-dag-compliance-v2'
        }
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation on errors."""
        return {
            'degraded_mode': True,
            'error': str(error),
            'available_functions': ['file_based_tracking'],
            'recommendation': 'Fall back to file-based execution tracking'
        }
    
    async def initialize(self) -> bool:
        """Initialize Redis connection."""
        if not REDIS_AVAILABLE:
            print("❌ Redis not available - install with: pip install redis")
            return False
        
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                password=self.redis_password,
                db=0,
                decode_responses=True,
                socket_timeout=5.0,
                socket_connect_timeout=5.0
            )
            
            # Test connection
            await self.redis_client.ping()
            print(f"✅ Redis connection established: {self.redis_host}:{self.redis_port}")
            return True
            
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            self.redis_client = None
            return False
    
    async def start_execution(self, spec_name: str, **kwargs) -> str:
        """Start tracking a new execution."""
        execution_id = f"{spec_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        execution_record = ExecutionRecord(
            execution_id=execution_id,
            spec_name=spec_name,
            status=ExecutionStatus.PENDING,
            started_at=datetime.now(),
            last_checkin=datetime.now(),
            **kwargs
        )
        
        if self.redis_client:
            try:
                # Store execution record
                await self.redis_client.hset(
                    f"{self.EXECUTION_PREFIX}{execution_id}",
                    mapping=self._serialize_execution_record(execution_record)
                )
                
                # Add to active executions
                await self.redis_client.sadd(self.ACTIVE_EXECUTIONS_KEY, execution_id)
                
                # Add to execution history
                await self.redis_client.zadd(
                    self.EXECUTION_HISTORY_KEY,
                    {execution_id: datetime.now().timestamp()}
                )
                
                print(f"✅ Execution started: {execution_id}")
                
            except Exception as e:
                print(f"❌ Failed to store execution record: {e}")
        
        return execution_id
    
    async def update_execution_status(self, execution_id: str, status: ExecutionStatus, **kwargs) -> bool:
        """Update execution status."""
        if not self.redis_client:
            return False
        
        try:
            # Get current record
            current_data = await self.redis_client.hgetall(f"{self.EXECUTION_PREFIX}{execution_id}")
            if not current_data:
                print(f"❌ Execution not found: {execution_id}")
                return False
            
            # Update fields
            updates = {
                'status': status.value,
                'last_checkin': datetime.now().isoformat(),
                **{k: json.dumps(v) if isinstance(v, (dict, list)) else str(v) 
                   for k, v in kwargs.items()}
            }
            
            if status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED, ExecutionStatus.CANCELLED]:
                updates['completed_at'] = datetime.now().isoformat()
                # Remove from active executions
                await self.redis_client.srem(self.ACTIVE_EXECUTIONS_KEY, execution_id)
            
            await self.redis_client.hset(f"{self.EXECUTION_PREFIX}{execution_id}", mapping=updates)
            
            print(f"✅ Execution updated: {execution_id} -> {status.value}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update execution: {e}")
            return False
    
    async def checkin_execution(self, execution_id: str, phase: Optional[str] = None, 
                               progress_percentage: Optional[float] = None, 
                               message: Optional[str] = None,
                               resource_usage: Optional[Dict[str, float]] = None) -> bool:
        """Record a check-in for an execution."""
        if not self.redis_client:
            return False
        
        try:
            checkin_record = CheckinRecord(
                execution_id=execution_id,
                timestamp=datetime.now(),
                status=ExecutionStatus.RUNNING,
                phase=phase,
                progress_percentage=progress_percentage,
                message=message,
                resource_usage=resource_usage
            )
            
            # Store check-in record
            checkin_key = f"{self.CHECKIN_PREFIX}{execution_id}:{datetime.now().timestamp()}"
            await self.redis_client.hset(
                checkin_key,
                mapping=self._serialize_checkin_record(checkin_record)
            )
            
            # Update last check-in time in execution record
            await self.redis_client.hset(
                f"{self.EXECUTION_PREFIX}{execution_id}",
                'last_checkin', datetime.now().isoformat()
            )
            
            # Set expiration for check-in records (30 days)
            await self.redis_client.expire(checkin_key, 30 * 24 * 3600)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to record check-in: {e}")
            return False
    
    async def get_active_executions(self) -> List[ExecutionRecord]:
        """Get all active executions."""
        if not self.redis_client:
            return []
        
        try:
            active_ids = await self.redis_client.smembers(self.ACTIVE_EXECUTIONS_KEY)
            executions = []
            
            for execution_id in active_ids:
                record = await self.get_execution_record(execution_id)
                if record:
                    executions.append(record)
            
            return executions
            
        except Exception as e:
            print(f"❌ Failed to get active executions: {e}")
            return []
    
    async def get_execution_record(self, execution_id: str) -> Optional[ExecutionRecord]:
        """Get execution record by ID."""
        if not self.redis_client:
            return None
        
        try:
            data = await self.redis_client.hgetall(f"{self.EXECUTION_PREFIX}{execution_id}")
            if not data:
                return None
            
            return self._deserialize_execution_record(data)
            
        except Exception as e:
            print(f"❌ Failed to get execution record: {e}")
            return None
    
    async def get_execution_history(self, spec_name: Optional[str] = None, 
                                   limit: int = 50) -> List[ExecutionRecord]:
        """Get execution history."""
        if not self.redis_client:
            return []
        
        try:
            # Get recent execution IDs
            execution_ids = await self.redis_client.zrevrange(
                self.EXECUTION_HISTORY_KEY, 0, limit - 1
            )
            
            executions = []
            for execution_id in execution_ids:
                record = await self.get_execution_record(execution_id)
                if record and (not spec_name or record.spec_name == spec_name):
                    executions.append(record)
            
            return executions
            
        except Exception as e:
            print(f"❌ Failed to get execution history: {e}")
            return []
    
    async def get_execution_checkins(self, execution_id: str) -> List[CheckinRecord]:
        """Get check-in history for an execution."""
        if not self.redis_client:
            return []
        
        try:
            # Find all check-in keys for this execution
            pattern = f"{self.CHECKIN_PREFIX}{execution_id}:*"
            keys = await self.redis_client.keys(pattern)
            
            checkins = []
            for key in sorted(keys):
                data = await self.redis_client.hgetall(key)
                if data:
                    checkin = self._deserialize_checkin_record(data)
                    checkins.append(checkin)
            
            return sorted(checkins, key=lambda x: x.timestamp)
            
        except Exception as e:
            print(f"❌ Failed to get check-ins: {e}")
            return []
    
    async def detect_stuck_executions(self, timeout_minutes: int = 60) -> List[ExecutionRecord]:
        """Detect executions that haven't checked in recently."""
        if not self.redis_client:
            return []
        
        try:
            active_executions = await self.get_active_executions()
            stuck_executions = []
            
            timeout_threshold = datetime.now() - timedelta(minutes=timeout_minutes)
            
            for execution in active_executions:
                if execution.last_checkin < timeout_threshold:
                    # Mark as stuck
                    await self.update_execution_status(
                        execution.execution_id, 
                        ExecutionStatus.STUCK,
                        error_message=f"No check-in for {timeout_minutes} minutes"
                    )
                    execution.status = ExecutionStatus.STUCK
                    stuck_executions.append(execution)
            
            return stuck_executions
            
        except Exception as e:
            print(f"❌ Failed to detect stuck executions: {e}")
            return []
    
    async def cleanup_old_records(self, days: int = 30) -> int:
        """Clean up old execution records."""
        if not self.redis_client:
            return 0
        
        try:
            cutoff_timestamp = (datetime.now() - timedelta(days=days)).timestamp()
            
            # Get old execution IDs
            old_ids = await self.redis_client.zrangebyscore(
                self.EXECUTION_HISTORY_KEY, 0, cutoff_timestamp
            )
            
            cleaned_count = 0
            for execution_id in old_ids:
                # Remove execution record
                await self.redis_client.delete(f"{self.EXECUTION_PREFIX}{execution_id}")
                
                # Remove check-in records
                checkin_keys = await self.redis_client.keys(f"{self.CHECKIN_PREFIX}{execution_id}:*")
                if checkin_keys:
                    await self.redis_client.delete(*checkin_keys)
                
                # Remove from history
                await self.redis_client.zrem(self.EXECUTION_HISTORY_KEY, execution_id)
                
                cleaned_count += 1
            
            print(f"✅ Cleaned up {cleaned_count} old execution records")
            return cleaned_count
            
        except Exception as e:
            print(f"❌ Failed to cleanup old records: {e}")
            return 0
    
    def _serialize_execution_record(self, record: ExecutionRecord) -> Dict[str, str]:
        """Serialize execution record for Redis storage."""
        data = asdict(record)
        
        # Convert datetime objects to ISO strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, ExecutionStatus):
                data[key] = value.value
            elif isinstance(value, (dict, list)):
                data[key] = json.dumps(value)
            elif value is None:
                data[key] = ""
            else:
                data[key] = str(value)
        
        return data
    
    def _deserialize_execution_record(self, data: Dict[str, str]) -> ExecutionRecord:
        """Deserialize execution record from Redis storage."""
        # Convert string values back to appropriate types
        parsed_data = {}
        
        for key, value in data.items():
            if key in ['started_at', 'last_checkin', 'completed_at'] and value:
                parsed_data[key] = datetime.fromisoformat(value)
            elif key == 'status':
                parsed_data[key] = ExecutionStatus(value)
            elif key in ['pid', 'total_tasks', 'completed_tasks'] and value:
                parsed_data[key] = int(value)
            elif key == 'efficiency_gain' and value:
                parsed_data[key] = float(value)
            elif key == 'metadata' and value:
                parsed_data[key] = json.loads(value)
            elif value == "":
                parsed_data[key] = None
            else:
                parsed_data[key] = value
        
        return ExecutionRecord(**parsed_data)
    
    def _serialize_checkin_record(self, record: CheckinRecord) -> Dict[str, str]:
        """Serialize check-in record for Redis storage."""
        data = asdict(record)
        
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, ExecutionStatus):
                data[key] = value.value
            elif isinstance(value, dict):
                data[key] = json.dumps(value)
            elif value is None:
                data[key] = ""
            else:
                data[key] = str(value)
        
        return data
    
    def _deserialize_checkin_record(self, data: Dict[str, str]) -> CheckinRecord:
        """Deserialize check-in record from Redis storage."""
        parsed_data = {}
        
        for key, value in data.items():
            if key == 'timestamp' and value:
                parsed_data[key] = datetime.fromisoformat(value)
            elif key == 'status':
                parsed_data[key] = ExecutionStatus(value)
            elif key == 'progress_percentage' and value:
                parsed_data[key] = float(value)
            elif key == 'resource_usage' and value:
                parsed_data[key] = json.loads(value)
            elif value == "":
                parsed_data[key] = None
            else:
                parsed_data[key] = value
        
        return CheckinRecord(**parsed_data)


# Global execution tracker instance
execution_tracker = RedisExecutionTracker()


async def initialize_execution_tracker() -> bool:
    """Initialize the global execution tracker."""
    return await execution_tracker.initialize()


async def start_tracking_execution(spec_name: str, **kwargs) -> str:
    """Start tracking a new execution."""
    return await execution_tracker.start_execution(spec_name, **kwargs)


async def update_execution_status(execution_id: str, status: ExecutionStatus, **kwargs) -> bool:
    """Update execution status."""
    return await execution_tracker.update_execution_status(execution_id, status, **kwargs)


async def checkin_execution(execution_id: str, **kwargs) -> bool:
    """Record a check-in for an execution."""
    return await execution_tracker.checkin_execution(execution_id, **kwargs)


async def get_active_executions() -> List[ExecutionRecord]:
    """Get all active executions."""
    return await execution_tracker.get_active_executions()


async def get_execution_history(spec_name: Optional[str] = None, limit: int = 50) -> List[ExecutionRecord]:
    """Get execution history."""
    return await execution_tracker.get_execution_history(spec_name, limit)