from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """Criteria for Phase 3 readiness assessment."""
    RDI_COMPLIANCE = 'rdi_compliance'
    RM_COMPLIANCE = 'rm_compliance'
    TEST_COVERAGE = 'test_coverage'
    BLOCKING_ISSUES = 'blocking_issues'
    TASK_COMPLETION = 'task_completion'
    OVERALL_SCORE = 'overall_score'

@dataclass