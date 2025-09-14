from src.rm_ddd.core.health import ModuleHealth

    def is_healthy(self) -> bool:
        """Check if validation engine is healthy"""
        try:
            if self.validation_history:
                recent_validations = self.validation_history[-5:]
                success_rate = len([v for v in recent_validations if v.success]) / len(recent_validations)
                if success_rate < 0.6:
                    return False
            for threshold in self.critical_thresholds.values():
                if not isinstance(threshold, (int, float)) or threshold <= 0:
                    return False
            return True
        except Exception as e:
            self.logger.error(f'Validation engine health check failed: {e}')
            return False
