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
    """Standard agent capabilities for Beast Mode collaboration."""
    CODE_ANALYSIS = 'code_analysis'
    SECURITY_ANALYSIS = 'security_analysis'
    PERFORMANCE_ANALYSIS = 'performance_analysis'
    ARCHITECTURE_ANALYSIS = 'architecture_analysis'
    CODE_GENERATION = 'code_generation'
    TEST_GENERATION = 'test_generation'
    DOCUMENTATION_GENERATION = 'documentation_generation'
    REFACTORING = 'refactoring'
    DEPLOYMENT_MANAGEMENT = 'deployment_management'
    MONITORING_SETUP = 'monitoring_setup'
    CI_CD_CONFIGURATION = 'ci_cd_configuration'
    INFRASTRUCTURE_MANAGEMENT = 'infrastructure_management'
    AUTOMATED_TESTING = 'automated_testing'
    CODE_REVIEW = 'code_review'
    COMPLIANCE_CHECKING = 'compliance_checking'
    VULNERABILITY_SCANNING = 'vulnerability_scanning'
    PROJECT_COORDINATION = 'project_coordination'
    KNOWLEDGE_SHARING = 'knowledge_sharing'
    MENTORING = 'mentoring'
    PROBLEM_SOLVING = 'problem_solving'
    COST_OPTIMIZATION = 'cost_optimization'
    PERFORMANCE_TUNING = 'performance_tuning'
    DISASTER_RECOVERY = 'disaster_recovery'
    DATA_ANALYSIS = 'data_analysis'
