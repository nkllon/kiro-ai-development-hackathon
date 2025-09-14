
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {'module_id': self.module_id, 'version': self.version, 'operation_id': self.operation_id, 'operation_type': self.operation_type, 'status': self.status, 'progress': self.progress}
