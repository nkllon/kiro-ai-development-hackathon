from datetime import datetime
from typing import Dict, List, Any

def get_compliance_monitor() -> EnhancedComplianceMonitor:
    """Get global compliance monitor instance"""
    project_root = Path(__file__).parent.parent.parent
    return EnhancedComplianceMonitor(project_root)
