from src.rm_ddd.core.health import ModuleHealth

    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {'module_id': self.module_id, 'version': self.version, 'success': self.success, 'records_processed': self.records_processed, 'records_failed': self.records_failed}
