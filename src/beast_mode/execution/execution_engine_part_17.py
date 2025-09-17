from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def __init__(self, auto_merge: bool = False, auto_revert_on_failure: bool = False):
        self.task_manager = TaskManager()
        self.agent_manager = AgentManager()
        self.git_session: Optional[GitSession] = None
        self.auto_merge = auto_merge
        self.auto_revert_on_failure = auto_revert_on_failure
        self.logger = logging.getLogger(__name__)

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

    