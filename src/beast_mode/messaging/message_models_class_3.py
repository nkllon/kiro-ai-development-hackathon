from src.rm_ddd.core.registry import register_module
class AgentCapability(str, Enum, ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
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

    def __init__(self):

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }
        
    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())
            
    def health_check(self):
        """Perform health check."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'module_id': getattr(self, 'module_id', self.__class__.__name__)
        }
        
    def get_health_status(self):
        """Get current health status."""
        return self.health_check()

        register_module('AgentCapability', self)