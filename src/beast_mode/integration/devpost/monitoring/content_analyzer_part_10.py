from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return self.dependencies
    