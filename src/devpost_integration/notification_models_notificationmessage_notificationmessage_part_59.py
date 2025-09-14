
def get_module_info(self) -> Dict[str, Any]:
    """Get module information."""
    return {'module_id': self.module_id, 'version': self.version, 'enabled': self.enabled, 'timing': self.timing.value if hasattr(self.timing, 'value') else str(self.timing), 'channel_count': len(self.channels)}
