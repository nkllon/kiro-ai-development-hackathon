from src.rm_ddd.core.registry import register_module

class SavehealthchecksClass:
    """Auto-generated class for functions."""

    def save_health_checks(self):
    """Save interface health checks to storage"""
    health_file = self.registry_file.replace('.json', '_health.json')
    try:
    data = {
    interface_id: {
    'interface_id': health.interface_id,
    'status': health.status,
    'last_checked': health.last_checked.isoformat(),
    'issues': health.issues,
    'recommendations': health.recommendations,
    'health_score': health.health_score
    }
    for interface_id, health in self.health_checks.items()
    }
    with open(health_file, 'w') as f:
    json.dump(data, f, indent=2)
    except Exception as e:
    print(f"Error saving health checks: {e}")

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

