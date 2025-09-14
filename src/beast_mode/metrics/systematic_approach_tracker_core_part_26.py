from datetime import datetime
from typing import Dict, List, Any

    def __init__(self):
        self.interfaces: Dict[str, InterfaceMetadata] = {}
        self.registry_file = ".beast_mode/interface_registry.json"
    