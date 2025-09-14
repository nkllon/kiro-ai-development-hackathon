from src.rm_ddd.core.health import ModuleHealth

class SelectagentsfortaskClass:
    """Auto-generated class for functions."""

    def _select_agents_for_task(self, task: Task) -> List[Agent]:
    """Select appropriate agents for task based on requirements"""
    selected_agents = []
    for agent_type in task.required_agents:
    candidates = [agent for agent in self.agents if agent.agent_type == agent_type]
    if candidates:
    best_agent = max(candidates, key=lambda a: a.expertise_level + a.collaboration_score)
    selected_agents.append(best_agent)
    return selected_agents

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

