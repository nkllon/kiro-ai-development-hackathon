
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {'module_id': self.module_id, 'version': self.version, 'settings_count': len(self.settings_data), 'operation_count': self._operation_count}
