from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def make_serializable(obj) -> Any:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [make_serializable(item) for item in obj]
        elif isinstance(obj, Enum):
            return obj.value
        else:
            return obj
    caps_dict = make_serializable(caps_dict)
    return BeastModeMessage(message_type=MessageType.AGENT_ANNOUNCEMENT, sender_id=agent_id, subject=f'Agent {capabilities.agent_name} is online', content={'capabilities': caps_dict, 'announcement_time': datetime.now().isoformat()})

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

