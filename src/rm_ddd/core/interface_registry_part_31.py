from datetime import datetime
from typing import Dict, List, Any

    def __init__(self, registry_file: str = "interface_registry.json"):
        self.registry_file = registry_file
        self.interfaces: Dict[str, InterfaceMetadata] = {}
        self.domain_index: Dict[str, set] = {}
        self.load_registry()
    