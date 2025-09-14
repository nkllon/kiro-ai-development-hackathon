from src.rm_ddd.core.health import ModuleHealth

    def get_configuration(self) -> Dict[str, Any]:
        """Get module configuration."""
        return {'operation_id': self.operation_id, 'operation_type': self.operation_type, 'max_retries': 3, 'timeout_seconds': 300}
