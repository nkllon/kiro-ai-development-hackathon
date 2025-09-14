from src.rm_ddd.core.health import ModuleHealth

    def is_healthy(self) -> bool:
        """Check if Systo's metrics engine is healthy"""
        try:
            if len(self.metric_data) == 0:
                return True
            systematic_count = len([dp for dp in self.metric_data if dp.approach_type == 'systematic'])
            total_count = len(self.metric_data)
            systematic_ratio = systematic_count / total_count if total_count > 0 else 0
            return systematic_ratio >= 0.3
        except Exception as e:
            self.logger.error(f"Systo's metrics engine health check failed: {e}")
            return False
