from src.rm_ddd.core.health import ModuleHealth

    def is_healthy(self) -> bool:
        """
        Self-monitoring - accurate health assessment
        Required by R6.2 - components report health status accurately
        """
        try:
            # Check basic operational health
            if self._degradation_mode:
                return False
                
            # Check performance constraints (C-05: <500ms response)
            if not self._health_monitor.is_performance_healthy():
                return False
                
            # Check data consistency
            if not self._health_monitor.validate_data_consistency(self._backlog_items):
                return False
                
            # Check memory usage (basic check)
            if len(self._backlog_items) > 10000:  # Arbitrary large number
                self.logger.warning("Large number of backlog items may impact performance")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False
            