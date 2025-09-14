from src.rm_ddd.core.health import ModuleHealth

    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {'module_id': self.module_id, 'version': self.version, 'message_id': self.message_id, 'title': self.title, 'status': self.status, 'recipient_count': len(self.recipients)}
