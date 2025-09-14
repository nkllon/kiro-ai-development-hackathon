from src.rm_ddd.core.health import ModuleHealth

    def get_result_summary(self) -> Dict[str, Any]:
        """Get sync result summary."""
        return {'success': self.success, 'error_message': self.error_message, 'records_processed': self.records_processed, 'records_failed': self.records_failed, 'success_rate': (self.records_processed - self.records_failed) / max(1, self.records_processed), 'sync_time': self.sync_time.isoformat()}
