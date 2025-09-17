from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def merge_to_base(self) -> bool:
        """Merge session branch back to base branch."""
        if not self.branch_name:
            return False
        
        try:
            # Switch to base branch
            subprocess.run(
                ["git", "checkout", self.base_branch],
                check=True, capture_output=True
            )
            
            # Merge session branch
            subprocess.run(
                ["git", "merge", self.branch_name],
                check=True, capture_output=True
            )
            
            self.logger.info(f"Merged {self.branch_name} to {self.base_branch}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to merge branch: {e}")
            return False

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

    