from src.rm_ddd.core.health import ModuleHealth

def _execute_recovery_plan(self, plan: RecoveryPlan) -> bool:
    """Execute recovery plan (simplified implementation)."""
    logger.info(f'Executing recovery plan: {plan.recovery_strategy} for {plan.failed_instance}')
    return True

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

