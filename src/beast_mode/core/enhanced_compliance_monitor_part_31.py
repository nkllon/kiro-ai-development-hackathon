from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def get_compliance_monitor() -> EnhancedComplianceMonitor:
    """Get global compliance monitor instance"""
    project_root = Path(__file__).parent.parent.parent
    return EnhancedComplianceMonitor(project_root)
