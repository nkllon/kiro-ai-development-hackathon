from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _analyze_current_progress(self, progress: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current progress against deadline."""
        return {'completion_percentage': progress.get('completion_percentage', 0), 'tasks_completed': progress.get('tasks_completed', 0), 'tasks_remaining': progress.get('tasks_remaining', 0), 'behind_schedule': progress.get('behind_schedule', False), 'quality_issues': progress.get('quality_issues', [])}

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

