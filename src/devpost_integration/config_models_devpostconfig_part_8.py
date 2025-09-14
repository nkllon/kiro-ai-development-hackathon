
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {'module_id': self.module_id, 'version': self.version, 'config_keys': list(self.config_data.keys()), 'operation_count': self._operation_count}
