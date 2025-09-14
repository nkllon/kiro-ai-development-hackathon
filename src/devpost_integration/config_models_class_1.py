class DevpostConfig(ReflectiveModule):
def register_with_registry(self, registry):
        """Register this module with the RM registry."""
        if registry:
            registry.register_module(self)
            self.add_capability("registry_registered")
    
    def get_module_metadata(self) -> Dict[str, any]:
        """Get module metadata for registry."""
        return {
            "module_id": self.module_id,
            "module_type": self.module_type,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "health_status": self.health_status,
            "last_updated": self.last_updated
        }
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """
    Manages DevPost configuration settings.
    
    This class handles all configuration parameters for
    DevPost integration including API settings, preferences,
    and connection parameters.
    """

    def __init__(self, config_data: Dict[str, Any]=None):
        """Initialize DevPost configuration."""
        super().__init__()
        self.module_id = 'devpost_config'
        self.version = '1.0.0'
        self.config_data = config_data or self._get_default_config()
        self._operation_count = 0
        self._errors = 0
        register_module(self)

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {'api_base_url': 'https://devpost.com/api', 'api_version': 'v1', 'timeout_seconds': 30, 'retry_attempts': 3, 'debug_mode': False, 'auto_sync': True, 'sync_interval_minutes': 60}

    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {'module_id': self.module_id, 'version': self.version, 'config_keys': list(self.config_data.keys()), 'operation_count': self._operation_count}

    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [ModuleCapability.CONFIG_MANAGEMENT, ModuleCapability.VALIDATION, ModuleCapability.EXPORT_IMPORT]

    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return ['reflective_module', 'typing']

    def check_health(self) -> ModuleHealth:
        """Check module health."""
        issues = []
        health_score = self._calculate_health_score()
        if self._errors > 0:
            issues.append(f'{self._errors} errors occurred')
        if not self.config_data:
            issues.append('No configuration data available')
        status = ModuleStatus.HEALTHY if health_score >= 0.9 else ModuleStatus.WARNING
        return ModuleHealth(module_id=self.module_id, status=status, health_score=health_score, issues=issues, capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self.get_metrics(), last_check=datetime.now())

    def _calculate_health_score(self) -> float:
        """Calculate health score."""
        score = 1.0
        if self._errors > 0:
            score -= min(0.5, self._errors * 0.1)
        if not self.config_data:
            score -= 0.3
        return max(0.0, score)

    def _identify_health_issues(self) -> List[str]:
        """Identify health issues."""
        issues = []
        if self._errors > 0:
            issues.append(f'Configuration errors: {self._errors}')
        if not self.config_data:
            issues.append('Missing configuration data')
        return issues

    def get_configuration(self) -> Dict[str, Any]:
        """Get module configuration."""
        return self.config_data.copy()

    def update_configuration(self, config: Dict[str, Any]) -> bool:
        """Update module configuration."""
        try:
            self.config_data.update(config)
            self._operation_count += 1
            return True
        except Exception as e:
            logger.error(f'Failed to update configuration: {e}')
            self._errors += 1
            return False

    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        return {'operation_count': self._operation_count, 'error_count': self._errors, 'config_keys': len(self.config_data), 'uptime_seconds': 0}

    def reset_metrics(self) -> None:
        """Reset module metrics."""
        self._operation_count = 0
        self._errors = 0

    def get_config_value(self, key: str, default: Any=None) -> Any:
        """Get configuration value by key."""
        try:
            return self.config_data.get(key, default)
        except Exception as e:
            logger.error(f'Failed to get config value: {e}')
            self._errors += 1
            return default

    def set_config_value(self, key: str, value: Any) -> bool:
        """Set configuration value by key."""
        try:
            self.config_data[key] = value
            self._operation_count += 1
            return True
        except Exception as e:
            logger.error(f'Failed to set config value: {e}')
            self._errors += 1
            return False

    def validate_configuration(self) -> bool:
        """Validate configuration values."""
        try:
            required_keys = ['api_base_url', 'api_version', 'timeout_seconds']
            for key in required_keys:
                if key not in self.config_data:
                    return False
            timeout = self.config_data.get('timeout_seconds', 0)
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                return False
            return True
        except Exception as e:
            logger.error(f'Configuration validation failed: {e}')
            self._errors += 1
            return False

    def reset_to_defaults(self) -> bool:
        """Reset configuration to defaults."""
        try:
            self.config_data = self._get_default_config()
            self._operation_count += 1
            return True
        except Exception as e:
            logger.error(f'Failed to reset to defaults: {e}')
            self._errors += 1
            return False

    def export_configuration(self) -> Dict[str, Any]:
        """Export configuration for backup."""
        try:
            export_data = {'config_data': self.config_data.copy(), 'export_time': datetime.now().isoformat(), 'version': self.version}
            self._operation_count += 1
            return export_data
        except Exception as e:
            logger.error(f'Failed to export configuration: {e}')
            self._errors += 1
            return {}

    def import_configuration(self, config_export: Dict[str, Any]) -> bool:
        """Import configuration from backup."""
        try:
            if 'config_data' in config_export:
                self.config_data = config_export['config_data'].copy()
                self._operation_count += 1
                return True
            return False
        except Exception as e:
            logger.error(f'Failed to import configuration: {e}')
            self._errors += 1
            return False

    def _update_metrics(self, operation: str) -> None:
        """Update internal metrics."""
        self._operation_count += 1
        logger.debug(f'DevPost config: {operation}')
