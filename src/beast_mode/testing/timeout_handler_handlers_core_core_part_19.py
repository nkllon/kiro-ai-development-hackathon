from src.rm_ddd.core.health import ModuleHealth

def _apply_level_2_degradation(self, operation_id: str) -> Dict[str, Any]:
    """Apply level 2 degradation: Pattern matching only"""
    try:
        self.logger.info(f'Applying level 2 degradation for operation {operation_id}: pattern matching only')
        degradation_config = {'analysis_scope': 'pattern_matching_only', 'comprehensive_analysis': 'disabled', 'pattern_matching': 'existing_patterns_only', 'fix_generation': 'from_patterns_only', 'validation': 'disabled'}
        if operation_id in self.operation_callbacks:
            callback = self.operation_callbacks[operation_id]
            callback(degradation_config)
        return {'success': True, 'degradation_level': 2, 'strategy': 'pattern_matching_only', 'config': degradation_config, 'estimated_time_savings': '70%'}
    except Exception as e:
        self.logger.error(f'Level 2 degradation failed for operation {operation_id}: {e}')
        return {'success': False, 'error': str(e)}

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

