from datetime import datetime
from typing import Dict, List, Any

    def _prepare_demo_environment(self) -> DemoEnvironment:
        """Prepare reliable demo environment."""
        from .models import IsolationLevel
        return DemoEnvironment(environment_id=f"demo-{datetime.now().strftime('%Y%m%d-%H%M%S')}", isolation_level=IsolationLevel.CONTAINER, dependency_status={'python': True, 'requirements': True, 'database': True}, backup_strategies=['Local fallback', 'Recorded demo', 'Screenshot sequence'], failure_scenarios=['Network failure', 'Dependency conflict', 'Performance issues'], monitoring_config={'health_check': True, 'performance_monitoring': True}, reliability_score=0)

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

