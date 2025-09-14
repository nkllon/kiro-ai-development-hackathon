from src.rm_ddd.core.registry import register_module

def _activate_ai_agents(self, resources: KiroResources) -> Dict[str, Any]:
    """Activate AI agents for development acceleration."""
    self.ai_agents_active = True
    return {'active': True, 'agents_count': resources.ai_agents, 'capabilities': ['code_generation', 'spec_analysis', 'quality_validation']}
