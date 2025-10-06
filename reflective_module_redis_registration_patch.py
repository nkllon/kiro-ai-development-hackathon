#!/usr/bin/env python3
"""
ReflectiveModule Redis Auto-Registration Patch
==============================================

Simple patch to add Redis auto-registration to the ReflectiveModule base class.
This fixes the fundamental architecture gap where ReflectiveModules weren't 
auto-registering in Redis as expected by the Runtime State Registry.

Usage:
1. Add this code to unified_reflective_module.py __init__ method
2. All existing ReflectiveModule implementations will automatically start registering
3. Runtime State Registry will immediately see all active services
"""

import redis
import json
from datetime import datetime
from typing import Optional

class ReflectiveModuleRedisPatch:
    """Patch to add Redis auto-registration to ReflectiveModule"""
    
    def _initialize_redis_registration(self):
        """Initialize Redis auto-registration for this module."""
        try:
            # Connect to Redis
            self._redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', '6379')),
                password=os.getenv('REDIS_PASSWORD', ''),
                decode_responses=True
            )
            
            # Test connection
            self._redis_client.ping()
            
            # Register this module
            self._register_in_redis()
            
            # Start heartbeat
            self._start_redis_heartbeat()
            
            self._logger.info(f"Redis auto-registration enabled for {self.__class__.__name__}")
            
        except Exception as e:
            self._logger.warning(f"Redis auto-registration failed: {e}")
            self._redis_client = None
    
    def _register_in_redis(self):
        """Register this module in Redis."""
        if not self._redis_client:
            return
            
        try:
            module_info = self.get_module_info()
            health_status = self.get_health_status()
            capabilities = self.get_capabilities()
            
            # Create registration data
            registration_data = {
                "module_id": module_info.get("module_id", self.__class__.__name__),
                "module_type": self.__class__.__name__,
                "capabilities": [cap.value for cap in capabilities],
                "registered_at": datetime.now().isoformat(),
                "status": health_status.status.value,
                "health_score": health_status.health_score,
                "host": os.getenv('HOSTNAME', 'localhost'),
                "pid": os.getpid(),
                "version": module_info.get("version", "1.0.0")
            }
            
            # Register in multiple Redis patterns for discoverability
            module_id = registration_data["module_id"]
            
            # 1. Health key pattern (for health monitoring)
            health_key = f"health:{module_id}"
            self._redis_client.hset(health_key, mapping={
                "status": health_status.status.value,
                "health_score": health_status.health_score,
                "last_check": datetime.now().isoformat(),
                "uptime_seconds": health_status.uptime_seconds
            })
            self._redis_client.expire(health_key, 300)  # 5 minute TTL
            
            # 2. Service registry pattern (for service discovery)
            service_key = f"service:registry:{module_id}"
            self._redis_client.hset(service_key, mapping=registration_data)
            self._redis_client.expire(service_key, 300)  # 5 minute TTL
            
            # 3. Active modules pattern (for Runtime State Registry)
            active_key = "beast_mode:active_modules"
            self._redis_client.hset(active_key, module_id, json.dumps(registration_data))
            
            self._logger.debug(f"Registered {module_id} in Redis")
            
        except Exception as e:
            self._logger.error(f"Failed to register in Redis: {e}")
    
    def _start_redis_heartbeat(self):
        """Start Redis heartbeat to maintain registration."""
        if not self._redis_client:
            return
            
        def heartbeat():
            while True:
                try:
                    time.sleep(60)  # Heartbeat every minute
                    self._register_in_redis()  # Refresh registration
                except Exception as e:
                    self._logger.error(f"Redis heartbeat failed: {e}")
                    break
        
        # Start heartbeat in background thread
        import threading
        heartbeat_thread = threading.Thread(target=heartbeat, daemon=True)
        heartbeat_thread.start()
    
    def _cleanup_redis_registration(self):
        """Cleanup Redis registration on shutdown."""
        if not self._redis_client:
            return
            
        try:
            module_id = getattr(self, "module_id", self.__class__.__name__)
            
            # Remove from all Redis patterns
            self._redis_client.delete(f"health:{module_id}")
            self._redis_client.delete(f"service:registry:{module_id}")
            self._redis_client.hdel("beast_mode:active_modules", module_id)
            
            self._logger.info(f"Cleaned up Redis registration for {module_id}")
            
        except Exception as e:
            self._logger.error(f"Failed to cleanup Redis registration: {e}")


# PATCH INSTRUCTIONS:
# ====================
# 
# 1. Add to ReflectiveModule.__init__() after Prometheus initialization:
#
#    # Initialize Redis auto-registration if enabled
#    self._enable_redis = self._should_enable_redis()
#    if self._enable_redis:
#        self._initialize_redis_registration()
#
# 2. Add helper method:
#
#    def _should_enable_redis(self) -> bool:
#        """Check if Redis auto-registration should be enabled."""
#        return os.getenv("BEAST_MODE_REDIS_ENABLED", "true").lower() == "true"
#
# 3. Add cleanup to __del__ or shutdown method:
#
#    def __del__(self):
#        if hasattr(self, '_cleanup_redis_registration'):
#            self._cleanup_redis_registration()

# IMMEDIATE IMPACT:
# =================
# - All 40+ ReflectiveModule implementations will start auto-registering
# - Runtime State Registry will immediately see all active services  
# - Redis will be populated with health, service, and module data
# - Operational blindness problem solved for ReflectiveModule services