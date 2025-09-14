from src.rm_ddd.core.health import ModuleHealth

    def get_event_details(self) -> Dict[str, Any]:
        """Get detailed event information."""
        return {'file_path': self.file_path, 'change_type': self.change_type.value if hasattr(self.change_type, 'value') else str(self.change_type), 'timestamp': self.timestamp.isoformat(), 'file_size': self.file_size, 'checksum': self.checksum}
