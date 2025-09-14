from src.rm_ddd.core.health import ModuleHealth

    def get_module_status(self) -> ModuleStatus:
        """Get current module status with health indicators."""
        return ModuleStatus(module_name=self.name, version=self.version, status='active' if self.is_healthy() else 'error', uptime=self.get_uptime(), last_activity=self.last_activity, health_indicators=self.get_health_indicators(), performance_metrics={'execution_stats': self.execution_stats, 'command_history_size': len(self.command_history), 'registered_patterns': len(self.command_patterns), 'registered_handlers': len(self.action_handlers)})
