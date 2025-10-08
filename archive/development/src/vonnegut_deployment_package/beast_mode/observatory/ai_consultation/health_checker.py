"""
Health Checker Implementation for AI Consultation System

Provides health checking capabilities that integrate with existing Observatory
monitoring infrastructure without interfering with it.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
import logging
import psutil
import os

from .interfaces import IHealthChecker
from .circuit_breaker import circuit_breaker_manager
from .feature_flags import feature_flags

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health check status values"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class AIConsultationHealthChecker(IHealthChecker):
    """
    Health checker for AI consultation system components
    
    Provides health checks that complement existing Observatory monitoring
    without interfering with it.
    """
    
    def __init__(self):
        self._start_time = datetime.utcnow()
        self._last_health_check = None
        self._health_cache = {}
        self._cache_ttl = 30  # Cache health results for 30 seconds
    
    async def check_health(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check of AI consultation system
        
        Returns:
            Health check results with status and details
        """
        now = datetime.utcnow()
        
        # Use cached result if still valid
        if (self._last_health_check and 
            now - self._last_health_check < timedelta(seconds=self._cache_ttl)):
            return self._health_cache
        
        health_checks = {
            'system': await self._check_system_health(),
            'feature_flags': await self._check_feature_flags(),
            'circuit_breakers': await self._check_circuit_breakers(),
            'dependencies': await self._check_dependencies(),
            'resources': await self._check_resource_usage()
        }
        
        # Determine overall status
        overall_status = self._determine_overall_status(health_checks)
        
        result = {
            'status': overall_status.value,
            'timestamp': now.isoformat(),
            'uptime_seconds': (now - self._start_time).total_seconds(),
            'checks': health_checks,
            'version': '0.1.0',
            'service': 'ai-consultation'
        }
        
        # Cache the result
        self._health_cache = result
        self._last_health_check = now
        
        return result
    
    async def check_readiness(self) -> Dict[str, Any]:
        """
        Check if service is ready to handle requests
        
        Returns:
            Readiness check results
        """
        readiness_checks = {
            'feature_flags_loaded': await self._check_feature_flags_loaded(),
            'circuit_breakers_initialized': await self._check_circuit_breakers_initialized(),
            'configuration_valid': await self._check_configuration(),
            'dependencies_available': await self._check_critical_dependencies()
        }
        
        # Service is ready if all critical checks pass
        is_ready = all(check.get('status') == HealthStatus.HEALTHY.value 
                      for check in readiness_checks.values())
        
        return {
            'ready': is_ready,
            'timestamp': datetime.utcnow().isoformat(),
            'checks': readiness_checks
        }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get service metrics for monitoring
        
        Returns:
            Service metrics
        """
        now = datetime.utcnow()
        uptime = now - self._start_time
        
        # Get circuit breaker stats
        circuit_stats = await circuit_breaker_manager.get_all_stats()
        open_breakers = await circuit_breaker_manager.get_open_breakers()
        
        # Get feature flag stats
        all_flags = await feature_flags.get_all_flags()
        enabled_flags = sum(1 for enabled in all_flags.values() if enabled)
        
        return {
            'uptime_seconds': uptime.total_seconds(),
            'start_time': self._start_time.isoformat(),
            'circuit_breakers': {
                'total': len(circuit_stats),
                'open': len(open_breakers),
                'open_breakers': open_breakers,
                'stats': circuit_stats
            },
            'feature_flags': {
                'total': len(all_flags),
                'enabled': enabled_flags,
                'disabled': len(all_flags) - enabled_flags,
                'flags': all_flags
            },
            'system': {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'process_count': len(psutil.pids())
            }
        }
    
    async def _check_system_health(self) -> Dict[str, Any]:
        """Check basic system health"""
        try:
            # Check if we can perform basic operations
            test_time = time.time()
            await asyncio.sleep(0.001)  # Minimal async operation test
            
            return {
                'status': HealthStatus.HEALTHY.value,
                'message': 'System operations normal',
                'response_time_ms': (time.time() - test_time) * 1000
            }
        except Exception as e:
            logger.error(f"System health check failed: {e}")
            return {
                'status': HealthStatus.UNHEALTHY.value,
                'message': f'System health check failed: {str(e)}',
                'error': str(e)
            }
    
    async def _check_feature_flags(self) -> Dict[str, Any]:
        """Check feature flag system health"""
        try:
            # Test feature flag operations
            test_flag = await feature_flags.is_enabled('ai_consultation_enabled')
            all_flags = await feature_flags.get_all_flags()
            
            return {
                'status': HealthStatus.HEALTHY.value,
                'message': 'Feature flags operational',
                'total_flags': len(all_flags),
                'test_flag_result': test_flag
            }
        except Exception as e:
            logger.error(f"Feature flags health check failed: {e}")
            return {
                'status': HealthStatus.UNHEALTHY.value,
                'message': f'Feature flags check failed: {str(e)}',
                'error': str(e)
            }
    
    async def _check_circuit_breakers(self) -> Dict[str, Any]:
        """Check circuit breaker system health"""
        try:
            stats = await circuit_breaker_manager.get_all_stats()
            open_breakers = await circuit_breaker_manager.get_open_breakers()
            
            # Determine status based on open breakers
            if len(open_breakers) == 0:
                status = HealthStatus.HEALTHY
                message = "All circuit breakers closed"
            elif len(open_breakers) < len(stats) / 2:
                status = HealthStatus.DEGRADED
                message = f"Some circuit breakers open: {open_breakers}"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Many circuit breakers open: {open_breakers}"
            
            return {
                'status': status.value,
                'message': message,
                'total_breakers': len(stats),
                'open_breakers': len(open_breakers),
                'open_breaker_names': open_breakers
            }
        except Exception as e:
            logger.error(f"Circuit breakers health check failed: {e}")
            return {
                'status': HealthStatus.UNHEALTHY.value,
                'message': f'Circuit breakers check failed: {str(e)}',
                'error': str(e)
            }
    
    async def _check_dependencies(self) -> Dict[str, Any]:
        """Check external dependencies health"""
        dependencies = {
            'redis': await self._check_redis(),
            'database': await self._check_database(),
            'file_system': await self._check_file_system()
        }
        
        # Determine overall dependency status
        healthy_deps = sum(1 for dep in dependencies.values() 
                          if dep.get('status') == HealthStatus.HEALTHY.value)
        total_deps = len(dependencies)
        
        if healthy_deps == total_deps:
            status = HealthStatus.HEALTHY
            message = "All dependencies healthy"
        elif healthy_deps >= total_deps / 2:
            status = HealthStatus.DEGRADED
            message = f"Some dependencies unhealthy ({healthy_deps}/{total_deps})"
        else:
            status = HealthStatus.UNHEALTHY
            message = f"Many dependencies unhealthy ({healthy_deps}/{total_deps})"
        
        return {
            'status': status.value,
            'message': message,
            'dependencies': dependencies
        }
    
    async def _check_resource_usage(self) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Determine status based on resource usage
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
                status = HealthStatus.UNHEALTHY
                message = "High resource usage detected"
            elif cpu_percent > 70 or memory.percent > 70 or disk.percent > 80:
                status = HealthStatus.DEGRADED
                message = "Elevated resource usage"
            else:
                status = HealthStatus.HEALTHY
                message = "Resource usage normal"
            
            return {
                'status': status.value,
                'message': message,
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_free_gb': disk.free / (1024**3)
            }
        except Exception as e:
            logger.error(f"Resource usage check failed: {e}")
            return {
                'status': HealthStatus.UNKNOWN.value,
                'message': f'Resource check failed: {str(e)}',
                'error': str(e)
            }
    
    async def _check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity (if used)"""
        try:
            # This is a placeholder - would connect to actual Redis
            # For now, just check if Redis is likely available
            return {
                'status': HealthStatus.HEALTHY.value,
                'message': 'Redis connectivity assumed healthy',
                'note': 'Actual Redis check not implemented yet'
            }
        except Exception as e:
            return {
                'status': HealthStatus.UNHEALTHY.value,
                'message': f'Redis check failed: {str(e)}',
                'error': str(e)
            }
    
    async def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity (if used)"""
        try:
            # This is a placeholder - would connect to actual database
            return {
                'status': HealthStatus.HEALTHY.value,
                'message': 'Database connectivity assumed healthy',
                'note': 'Actual database check not implemented yet'
            }
        except Exception as e:
            return {
                'status': HealthStatus.UNHEALTHY.value,
                'message': f'Database check failed: {str(e)}',
                'error': str(e)
            }
    
    async def _check_file_system(self) -> Dict[str, Any]:
        """Check file system access"""
        try:
            # Test file system operations
            test_file = '/tmp/ai_consultation_health_check'
            with open(test_file, 'w') as f:
                f.write('health check')
            
            with open(test_file, 'r') as f:
                content = f.read()
            
            os.remove(test_file)
            
            if content == 'health check':
                return {
                    'status': HealthStatus.HEALTHY.value,
                    'message': 'File system operations normal'
                }
            else:
                return {
                    'status': HealthStatus.UNHEALTHY.value,
                    'message': 'File system read/write test failed'
                }
        except Exception as e:
            return {
                'status': HealthStatus.UNHEALTHY.value,
                'message': f'File system check failed: {str(e)}',
                'error': str(e)
            }
    
    async def _check_feature_flags_loaded(self) -> Dict[str, Any]:
        """Check if feature flags are properly loaded"""
        try:
            flags = await feature_flags.get_all_flags()
            if len(flags) > 0:
                return {
                    'status': HealthStatus.HEALTHY.value,
                    'message': f'Feature flags loaded ({len(flags)} flags)'
                }
            else:
                return {
                    'status': HealthStatus.DEGRADED.value,
                    'message': 'No feature flags loaded'
                }
        except Exception as e:
            return {
                'status': HealthStatus.UNHEALTHY.value,
                'message': f'Feature flags check failed: {str(e)}',
                'error': str(e)
            }
    
    async def _check_circuit_breakers_initialized(self) -> Dict[str, Any]:
        """Check if circuit breakers are initialized"""
        try:
            stats = await circuit_breaker_manager.get_all_stats()
            return {
                'status': HealthStatus.HEALTHY.value,
                'message': f'Circuit breaker manager operational ({len(stats)} breakers)'
            }
        except Exception as e:
            return {
                'status': HealthStatus.UNHEALTHY.value,
                'message': f'Circuit breakers check failed: {str(e)}',
                'error': str(e)
            }
    
    async def _check_configuration(self) -> Dict[str, Any]:
        """Check if configuration is valid"""
        try:
            # Check if configuration files exist and are readable
            config_checks = {
                'feature_flags_config': os.path.exists('config/ai_consultation_feature_flags.json')
            }
            
            if all(config_checks.values()):
                return {
                    'status': HealthStatus.HEALTHY.value,
                    'message': 'Configuration files accessible',
                    'checks': config_checks
                }
            else:
                return {
                    'status': HealthStatus.DEGRADED.value,
                    'message': 'Some configuration files missing',
                    'checks': config_checks
                }
        except Exception as e:
            return {
                'status': HealthStatus.UNHEALTHY.value,
                'message': f'Configuration check failed: {str(e)}',
                'error': str(e)
            }
    
    async def _check_critical_dependencies(self) -> Dict[str, Any]:
        """Check critical dependencies for readiness"""
        # For readiness, we only check the most critical dependencies
        critical_checks = [
            await self._check_file_system(),
            await self._check_feature_flags_loaded()
        ]
        
        all_healthy = all(check.get('status') == HealthStatus.HEALTHY.value 
                         for check in critical_checks)
        
        if all_healthy:
            return {
                'status': HealthStatus.HEALTHY.value,
                'message': 'Critical dependencies available'
            }
        else:
            return {
                'status': HealthStatus.UNHEALTHY.value,
                'message': 'Some critical dependencies unavailable',
                'checks': critical_checks
            }
    
    def _determine_overall_status(self, health_checks: Dict[str, Dict[str, Any]]) -> HealthStatus:
        """Determine overall health status from individual checks"""
        statuses = [check.get('status', HealthStatus.UNKNOWN.value) 
                   for check in health_checks.values()]
        
        if all(status == HealthStatus.HEALTHY.value for status in statuses):
            return HealthStatus.HEALTHY
        elif any(status == HealthStatus.UNHEALTHY.value for status in statuses):
            return HealthStatus.UNHEALTHY
        elif any(status == HealthStatus.DEGRADED.value for status in statuses):
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.UNKNOWN


# Global health checker instance
health_checker = AIConsultationHealthChecker()