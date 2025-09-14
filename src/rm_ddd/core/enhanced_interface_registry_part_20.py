from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def __init__(self, registry_file: str = "enhanced_interface_registry.json"):
        super().__init__(registry_file)
        self.metrics: Dict[str, InterfaceMetrics] = {}
        self.cache: Dict[str, Any] = {}
        self.load_metrics()
    