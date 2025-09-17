from src.rm_ddd.core.health import ModuleHealth

def _get_bobby_verdict(orchestration_result: OrchestrationResult) -> str:
    """Get Bobby's systematic verdict on ecosystem consumption."""
    quality_score = orchestration_result.systematic_quality_score
    success_prob = orchestration_result.mvp_route.success_probability
    risk_count = len(orchestration_result.risk_assessment.risk_factors)
    if quality_score > 0.9 and success_prob > 0.8:
        return 'DELICIOUS - Bobby loves systematic ecosystems'
    elif quality_score > 0.8 and success_prob > 0.7:
        return 'TASTY - Bobby consumed it with systematic satisfaction'
    elif quality_score > 0.7 and success_prob > 0.6:
        return 'EDIBLE - Bobby digested it but recommends systematic improvements'
    elif quality_score > 0.6:
        return 'TOUGH - Bobby chewed through it with systematic determination'
    else:
        return 'INDIGESTIBLE - Bobby recommends systematic remediation'

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

