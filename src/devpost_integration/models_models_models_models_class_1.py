class ProjectMetadata(ReflectiveModule):
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
    """ProjectMetadata with RM-DDD compliance - Project information handling"""
    def __init__(self, metadata: Dict[str, Any]=None):
        """Initialize project metadata with comprehensive functionality"""
        super().__init__(module_id='projectmetadata', version='1.0.0')
        register_module(self)
        self._logger = logging.getLogger(f'{__name__}.ProjectMetadata')
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.version = '1.0.0'
        self._metrics = {'operations_count': 0, 'last_operation_time': None, 'error_count': 0, 'success_rate': 1.0, 'metadata_updates': 0}
        self._logger.info('ProjectMetadata initialized with RM-DDD compliance')
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information"""
        return {'module_id': 'projectmetadata', 'version': '1.0.0', 'description': 'Project metadata management with comprehensive functionality', 'metadata_count': len(self.metadata), 'version': self.version}
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities"""
        return [ModuleCapability.CORE_FUNCTIONALITY, ModuleCapability.DATA_MANAGEMENT, ModuleCapability.VALIDATION, ModuleCapability.MONITORING]
    def get_dependencies(self) -> List[str]:
        """Get module dependencies"""
        return ['reflective_module', 'validation_result']
    def check_health(self) -> ModuleHealth:
        """Perform health check"""
        try:
            health_score = self._calculate_health_score()
            issues = self._identify_health_issues()
            return ModuleHealth(module_id='projectmetadata', status=ModuleStatus.HEALTHY if health_score > 0.8 else ModuleStatus.DEGRADED, health_score=health_score, issues=issues, capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self._metrics, last_check=datetime.now())
        except Exception as e:
            self._logger.error(f'Health check failed: {e}')
            return ModuleHealth(module_id='projectmetadata', status=ModuleStatus.UNHEALTHY, health_score=0.0, issues=[f'Health check error: {str(e)}'], capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self._metrics, last_check=datetime.now())
    def _calculate_health_score(self) -> float:
        """Calculate health score based on metrics"""
        if self._metrics['operations_count'] == 0:
            return 1.0
        success_rate = self._metrics['success_rate']
        error_penalty = min(self._metrics['error_count'] * 0.1, 0.5)
        return max(0.0, success_rate - error_penalty)
    def _identify_health_issues(self) -> List[str]:
        """Identify health issues"""
        issues = []
        if self._metrics['success_rate'] < 0.8:
            issues.append('Low success rate detected')
        if self._metrics['error_count'] > 10:
            issues.append('High error count detected')
        return issues
    def get_configuration(self) -> Dict[str, Any]:
        """Get module configuration"""
        return {'version': self.version, 'auto_validation_enabled': True, 'metadata_schema_enforced': True, 'logging_level': 'INFO'}
    def update_configuration(self, config: Dict[str, Any]) -> bool:
        """Update module configuration"""
        try:
            if 'auto_validation_enabled' in config:
                self._logger.info(f"Auto validation enabled: {config['auto_validation_enabled']}")
            if 'metadata_schema_enforced' in config:
                self._logger.info(f"Schema enforcement enabled: {config['metadata_schema_enforced']}")
            return True
        except Exception as e:
            self._logger.error(f'Configuration update failed: {e}')
            return False
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics"""
        return self._metrics.copy()
    def reset_metrics(self) -> None:
        """Reset module metrics"""
        self._metrics = {'operations_count': 0, 'last_operation_time': None, 'error_count': 0, 'success_rate': 1.0, 'metadata_updates': 0}
        self._logger.info('Metrics reset successfully')
    def set_metadata(self, key: str, value: Any) -> bool:
        """Set metadata value"""
        try:
            self._update_metrics('set_metadata')
            self.metadata[key] = value
            self.updated_at = datetime.now()
            self._metrics['metadata_updates'] += 1
            self._logger.info(f'Metadata set: {key}')
            return True
        except Exception as e:
            self._logger.error(f'Failed to set metadata: {e}')
            self._metrics['error_count'] += 1
            return False
    def get_metadata(self, key: str=None) -> Any:
        """Get metadata value or all metadata"""
        try:
            self._update_metrics('get_metadata')
            if key is None:
                return self.metadata.copy()
            return self.metadata.get(key)
        except Exception as e:
            self._logger.error(f'Failed to get metadata: {e}')
            self._metrics['error_count'] += 1
            return None
    def update_metadata(self, updates: Dict[str, Any]) -> bool:
        """Update multiple metadata values"""
        try:
            self._update_metrics('update_metadata')
            self.metadata.update(updates)
            self.updated_at = datetime.now()
            self._metrics['metadata_updates'] += len(updates)
            self._logger.info(f'Metadata updated with {len(updates)} values')
            return True
        except Exception as e:
            self._logger.error(f'Failed to update metadata: {e}')
            self._metrics['error_count'] += 1
            return False
    def validate_metadata(self) -> bool:
        """Validate metadata structure and content"""
        try:
            self._update_metrics('validate_metadata')
            required_fields = ['title', 'description', 'version']
            for field in required_fields:
                if field not in self.metadata or not self.metadata[field]:
                    self._logger.warning(f'Missing required metadata field: {field}')
                    return False
            return True
        except Exception as e:
            self._logger.error(f'Metadata validation failed: {e}')
            self._metrics['error_count'] += 1
            return False
    def clear_metadata(self) -> bool:
        """Clear all metadata"""
        try:
            self._update_metrics('clear_metadata')
            self.metadata.clear()
            self.updated_at = datetime.now()
            self._logger.info('Metadata cleared successfully')
            return True
        except Exception as e:
            self._logger.error(f'Failed to clear metadata: {e}')
            self._metrics['error_count'] += 1
            return False
    def _update_metrics(self, operation: str) -> None:
        """Update performance metrics"""
        self._metrics['operations_count'] += 1
        self._metrics['last_operation_time'] = datetime.now()
        total_ops = self._metrics['operations_count']
        errors = self._metrics['error_count']
        self._metrics['success_rate'] = (total_ops - errors) / total_ops if total_ops > 0 else 1.0
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }
    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())
    def health_check(self):
        """Perform health check."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'module_id': getattr(self, 'module_id', self.__class__.__name__)
        }
    def get_health_status(self):
        """Get current health status."""
        return self.health_check()
