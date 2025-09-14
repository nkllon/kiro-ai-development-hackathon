from src.rm_ddd.core.registry import register_module
class InterfaceType(Enum, ReflectiveModule):
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
    """Interface type enumeration"""
    REFLECTIVE_MODULE = "reflective_module"
    DOMAIN_SERVICE = "domain_service"
    API_INTERFACE = "api_interface"
    DATA_MODEL = "data_model"
    VALIDATION_RULE = "validation_rule"
    CONFIGURATION = "configuration"
    NOTIFICATION = "notification"
    STORAGE = "storage"
    TRANSPORT = "transport"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    MONITORING = "monitoring"
    LOGGING = "logging"
    METRICS = "metrics"
    HEALTH_CHECK = "health_check"
    CACHE = "cache"
    QUEUE = "queue"
    WORKFLOW = "workflow"
    ORCHESTRATION = "orchestration"

    def __init__(self):
        register_module('InterfaceType', self)