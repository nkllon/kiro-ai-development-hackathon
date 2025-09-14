from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def __init__(self, repo_path: str='.'):
        super().__init__(repo_path)
        self.git_executable = self._find_git_executable()
        self._validate_repository()

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

