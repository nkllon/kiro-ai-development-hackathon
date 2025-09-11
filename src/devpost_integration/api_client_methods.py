from .reflective_module import ReflectiveModule, register_module, ModuleCapability, ModuleHealth, ModuleStatus, ModuleConfiguration
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DevPostAPIError(Exception):
    """Base exception for DevPost API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data

class DevPostAPIClient(ReflectiveModule):
    """DevPost API client with ReflectiveModule interface"""
    
    def __init__(self, api_key: str, base_url: str = "https://devpost.com"):
        super().__init__(module_id="api_client", version="1.0.0")
        self._start_time = datetime.now()
        register_module(self)
        
        self.api_key = api_key
        self.base_url = base_url
        self._error_count = 0
        self._command_count = 0
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information"""
        return {
            "name": self.__class__.__name__,
            "version": self.version,
            "module_id": self.module_id,
            "description": "DevPost API client for project management"
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities"""
        return [ModuleCapability.CORE_FUNCTIONALITY, ModuleCapability.API_CLIENT]
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies"""
        return ["reflective_module", "requests", "json"]
    
    def check_health(self) -> ModuleHealth:
        """Check module health"""
        try:
            if not hasattr(self, '_start_time'):
                return ModuleHealth.UNHEALTHY
            uptime = (datetime.now() - self._start_time).total_seconds()
            if uptime < 0:
                return ModuleHealth.UNHEALTHY
            error_count = getattr(self, '_error_count', 0)
            total_operations = getattr(self, '_command_count', 1)
            error_rate = error_count / total_operations if total_operations > 0 else 0
            if error_rate > 0.5:
                return ModuleHealth.UNHEALTHY
            elif error_rate > 0.1:
                return ModuleHealth.DEGRADED
            else:
                return ModuleHealth.HEALTHY
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return ModuleHealth.UNHEALTHY
    
    def get_configuration(self) -> ModuleConfiguration:
        """Get module configuration"""
        return ModuleConfiguration(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def update_configuration(self, config: ModuleConfiguration) -> bool:
        """Update module configuration"""
        try:
            if hasattr(config, 'api_key'):
                self.api_key = config.api_key
            if hasattr(config, 'base_url'):
                self.base_url = config.base_url
            return True
        except Exception as e:
            logger.error(f"Configuration update failed: {e}")
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics"""
        try:
            uptime = (datetime.now() - self._start_time).total_seconds() if hasattr(self, '_start_time') else 0
            error_count = getattr(self, '_error_count', 0)
            total_operations = getattr(self, '_command_count', 0)
            success_count = total_operations - error_count
            success_rate = (success_count / total_operations) if total_operations > 0 else 1.0
            error_rate = (error_count / total_operations) if total_operations > 0 else 0.0
            health_status = self.check_health()
            
            return {
                'uptime_seconds': uptime,
                'total_operations': total_operations,
                'success_count': success_count,
                'error_count': error_count,
                'success_rate': success_rate,
                'error_rate': error_rate,
                'health_status': health_status.value,
                'module_id': getattr(self, 'module_id', 'unknown'),
                'version': getattr(self, 'version', 'unknown'),
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
            return {
                'error': str(e),
                'health_status': 'UNHEALTHY',
                'last_updated': datetime.now().isoformat()
            }
    
    def reset_metrics(self) -> None:
        """Reset module metrics"""
        self._error_count = 0
        self._command_count = 0
        self._start_time = datetime.now()
