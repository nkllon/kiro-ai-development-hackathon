from src.rm_ddd.core.health import ModuleHealth

def _generate_next_actions(self, pdca_result: Dict[str, Any]) -> List[str]:
    """Generate recommended next actions from PDCA result"""
    actions = []
    if pdca_result.get('plan_phase_success', False):
        actions.append('Execute implementation plan systematically')
    if pdca_result.get('do_phase_success', False):
        actions.append('Validate implementation against requirements')
    if pdca_result.get('check_phase_success', False):
        actions.append('Apply learnings to improve process')
    if pdca_result.get('act_phase_success', False):
        actions.append('Document and share systematic approach')
    actions.extend(['Integrate with GKE deployment pipeline', 'Set up monitoring and alerting', 'Plan for systematic maintenance'])
    return actions

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

