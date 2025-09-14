from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _update_priorities_for_acceleration(self):
        """Update task priorities for emergency acceleration."""
        for task in self.tasks:
            if task.status == TaskStatus.COMPLETED:
                continue
            if task.competitive_impact > 0.8:
                task.priority = TaskPriority.CRITICAL
            elif task.competitive_impact < 0.3:
                task.priority = TaskPriority.LOW

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

