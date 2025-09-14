from src.rm_ddd.core.health import ModuleHealth

    def is_healthy(self) -> bool:
        """Check if migration manager is healthy"""
        try:
            for state in self.migration_states.values():
                if state.migration_phase == 'failed':
                    return False
            if self.migration_states and (not self.rollback_snapshots):
                return False
            return True
        except Exception as e:
            self.logger.error(f'Migration manager health check failed: {e}')
            return False
