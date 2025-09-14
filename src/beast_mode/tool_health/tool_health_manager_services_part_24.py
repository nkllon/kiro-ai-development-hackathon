
    def is_healthy(self) -> bool:
        """Check if tool health manager is healthy"""
        try:
            if not self.repair_history:
                return True
            successful_repairs = len([r for r in self.repair_history if r.repair_successful])
            success_rate = successful_repairs / len(self.repair_history)
            return success_rate >= 0.7
        except Exception as e:
            self.logger.error(f'Tool health manager health check failed: {e}')
            return False
