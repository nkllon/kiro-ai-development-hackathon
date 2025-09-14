from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def __init__(self):
        self.compliance_results: Dict[str, ComplianceResult] = {}
        self.compliance_file = ".beast_mode/compliance_results.json"
    