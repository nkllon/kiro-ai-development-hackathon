from src.rm_ddd.core.health import ModuleHealth

def get_module_info(self) -> Dict[str, Any]:
    """Get module information."""
    return {'module_id': self.module_id, 'version': self.version, 'connected': self.connected, 'connection_time': self.connection_time}
