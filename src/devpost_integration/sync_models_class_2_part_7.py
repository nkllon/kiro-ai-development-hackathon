
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {'module_id': self.module_id, 'version': self.version, 'file_path': self.file_path, 'change_type': self.change_type.value if hasattr(self.change_type, 'value') else str(self.change_type), 'timestamp': self.timestamp.isoformat()}
