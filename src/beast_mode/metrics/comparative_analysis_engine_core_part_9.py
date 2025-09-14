from datetime import datetime
from typing import Dict, List, Any

    def register_with_registry(self, registry):
        """Register module with the RM registry."""
        if registry:
            registry.register_module(self)
    