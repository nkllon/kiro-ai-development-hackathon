from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


class InitClass:
    """Auto-generated class for functions."""

    def __init__(self, agent_id: str, transport_type: str='redis', transport_config: Optional[Dict[str, Any]]=None, shared_state_config: Optional[SharedStateConfig]=None, capabilities: Optional[List[str]]=None, specializations: Optional[List[str]]=None):
    """
    Initialize unified Beast Mode client.

    Args:
    agent_id: Unique agent identifier
    transport_type: Type of transport ('redis', 'nats', etc.)
    transport_config: Transport-specific configuration
    shared_state_config: Shared state configuration
    capabilities: Agent capabilities list
    specializations: Agent specializations list
    """
    self.agent_id = agent_id
    self.transport_type = transport_type
    self.capabilities = capabilities or []
    self.specializations = specializations or []
    self.transport = TransportFactory.create_transport(transport_type, agent_id=agent_id, **transport_config or {})
    self.shared_state = BeastModeSharedState(shared_state_config)
    self.message_handlers: Dict[MessageType, List[Callable]] = {}
    self.is_started = False
    self.stats = {'messages_sent': 0, 'messages_received': 0, 'start_time': None, 'last_activity': None}
    self.logger = logging.getLogger(__name__)

    def register_module(self, registry):
    """Register module with registry."""
    metadata = self.get_interface_metadata()
    if hasattr(registry, 'register'):
    registry.register(metadata)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

