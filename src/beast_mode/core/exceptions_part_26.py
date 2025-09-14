from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def __init__(self):
        self.interfaces: Dict[str, InterfaceMetadata] = {}
        self.registry_file = ".beast_mode/interface_registry.json"
    