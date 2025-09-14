from src.rm_ddd.core.registry import register_module
class MessageType(str, Enum, ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
    """Get health indicators for this module."""
    return {
    "module_id": self.module_id,
    "status": self.health_status,
    "last_updated": self.last_updated,
    "capabilities_count": len(self.capabilities),
    "dependencies_count": len(self.dependencies)
    }

class GethealthindicatorsClass:
    """Auto-generated class for functions."""

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
    """Standard Beast Mode message types for agent collaboration."""
    AGENT_ANNOUNCEMENT = 'agent_announcement'
    CAPABILITY_BROADCAST = 'capability_broadcast'
    DISCOVERY_REQUEST = 'discovery_request'
    DISCOVERY_RESPONSE = 'discovery_response'
    HELP_REQUEST = 'help_request'
    HELP_RESPONSE = 'help_response'
    COLLABORATION_INVITE = 'collaboration_invite'
    COLLABORATION_ACCEPT = 'collaboration_accept'
    COLLABORATION_DECLINE = 'collaboration_decline'
    TASK_ASSIGNMENT = 'task_assignment'
    TASK_UPDATE = 'task_update'
    TASK_COMPLETION = 'task_completion'
    TASK_FAILURE = 'task_failure'
    SPORE_SHARE = 'spore_share'
    SPORE_REQUEST = 'spore_request'
    SPORE_VALIDATION = 'spore_validation'
    SPORE_APPLICATION = 'spore_application'
    HEARTBEAT = 'heartbeat'
    STATUS_UPDATE = 'status_update'
    ERROR_REPORT = 'error_report'
    SHUTDOWN_NOTICE = 'shutdown_notice'
    OFFICE_HOURS_ANNOUNCEMENT = 'office_hours_announcement'
    SCHEDULE_REQUEST = 'schedule_request'
    SCHEDULE_CONFIRMATION = 'schedule_confirmation'
    DIRECT_MESSAGE = 'direct_message'
    BROADCAST_MESSAGE = 'broadcast_message'

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

    register_module('MessageType', self)