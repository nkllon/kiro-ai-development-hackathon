from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.metrics_history: List[ComplianceMetrics] = []
        self.compliance_threshold = 95.0  # 95%+ target
    