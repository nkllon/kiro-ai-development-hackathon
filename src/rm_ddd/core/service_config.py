"""
Service Configuration Manager
============================

Central service configuration management for Beast Mode Framework.
Loads service endpoints from config/services.yml and provides
environment-aware service discovery.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ServiceEndpoint:
    """Service endpoint configuration."""
    host: str
    port: int
    url: str
    health_endpoint: Optional[str] = None
    api_endpoint: Optional[str] = None


class ServiceConfigManager:
    """Central service configuration manager."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config_file()
        self.config = self._load_config()
        self.environment = os.getenv('BEAST_MODE_ENVIRONMENT', 'development')
    
    def _find_config_file(self) -> str:
        """Find the services configuration file."""
        # Try multiple possible locations
        possible_paths = [
            'config/services.yml',
            '../config/services.yml',
            '../../config/services.yml',
            os.path.expanduser('~/.beast_mode/services.yml'),
            '/etc/beast_mode/services.yml'
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        
        raise FileNotFoundError("Could not find config/services.yml")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file with environment variable substitution."""
        try:
            with open(self.config_path, 'r') as f:
                content = f.read()
            
            # Substitute environment variables in the format ${VAR_NAME:-default}
            import re
            def env_substitute(match):
                var_expr = match.group(1)
                if ':-' in var_expr:
                    var_name, default_value = var_expr.split(':-', 1)
                    return os.getenv(var_name, default_value)
                else:
                    return os.getenv(var_expr, '')
            
            # Replace ${VAR_NAME:-default} patterns
            content = re.sub(r'\$\{([^}]+)\}', env_substitute, content)
            
            return yaml.safe_load(content)
        except Exception as e:
            raise RuntimeError(f"Failed to load service config: {e}")
    
    def get_service_config(self, service_name: str) -> ServiceEndpoint:
        """Get service configuration with environment overrides."""
        # Get base service config
        base_config = self.config.get('services', {}).get(service_name)
        if not base_config:
            raise ValueError(f"Service '{service_name}' not found in configuration")
        
        # Apply environment-specific overrides
        env_config = self.config.get('environments', {}).get(self.environment, {}).get(service_name, {})
        
        # Merge configurations (environment overrides base)
        merged_config = {**base_config, **env_config}
        
        return ServiceEndpoint(
            host=merged_config['host'],
            port=merged_config['port'],
            url=merged_config['url'],
            health_endpoint=merged_config.get('health_endpoint'),
            api_endpoint=merged_config.get('api_endpoint')
        )
    
    def get_directus_config(self) -> ServiceEndpoint:
        """Get Directus CMS configuration."""
        return self.get_service_config('directus')
    
    def get_jaeger_config(self) -> ServiceEndpoint:
        """Get Jaeger tracing configuration."""
        return self.get_service_config('jaeger')
    
    def get_grafana_config(self) -> ServiceEndpoint:
        """Get Grafana monitoring configuration."""
        return self.get_service_config('grafana')
    
    def get_prometheus_config(self) -> ServiceEndpoint:
        """Get Prometheus metrics configuration."""
        return self.get_service_config('prometheus')
    
    def get_redis_config(self) -> ServiceEndpoint:
        """Get Redis configuration."""
        return self.get_service_config('redis')
    
    def health_check_all_services(self) -> Dict[str, bool]:
        """Check health of all configured services."""
        import requests
        
        results = {}
        
        for service_name in self.config.get('services', {}):
            try:
                service_config = self.get_service_config(service_name)
                
                # Skip services without HTTP health endpoints
                if not service_config.health_endpoint:
                    results[service_name] = None  # Cannot check
                    continue
                
                health_url = f"{service_config.url}{service_config.health_endpoint}"
                response = requests.get(health_url, timeout=5)
                results[service_name] = response.status_code == 200
                
            except Exception:
                results[service_name] = False
        
        return results


# Global service config manager instance
_service_config = None


def get_service_config() -> ServiceConfigManager:
    """Get global service configuration manager."""
    global _service_config
    if _service_config is None:
        _service_config = ServiceConfigManager()
    return _service_config


def get_directus_url() -> str:
    """Get Directus URL from central configuration."""
    return get_service_config().get_directus_config().url


def get_jaeger_url() -> str:
    """Get Jaeger URL from central configuration."""
    return get_service_config().get_jaeger_config().url


def get_grafana_url() -> str:
    """Get Grafana URL from central configuration."""
    return get_service_config().get_grafana_config().url


def get_redis_host() -> str:
    """Get Redis host from central configuration."""
    return get_service_config().get_redis_config().host


def get_redis_port() -> int:
    """Get Redis port from central configuration."""
    return get_service_config().get_redis_config().port