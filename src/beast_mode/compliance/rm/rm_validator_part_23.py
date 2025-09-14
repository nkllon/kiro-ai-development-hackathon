from datetime import datetime
from typing import Dict, List, Any

    def __init__(self):
        self.compliance_results: Dict[str, ComplianceResult] = {}
        self.compliance_file = ".beast_mode/compliance_results.json"
    