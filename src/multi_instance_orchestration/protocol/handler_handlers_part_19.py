from src.rm_ddd.core.health import ModuleHealth

    def get_health_indicators(self) -> list[HealthIndicator]:
        """Get current health indicators."""
        success_rate = 0.0
        if self.execution_stats['total_commands'] > 0:
            success_rate = self.execution_stats['successful_commands'] / self.execution_stats['total_commands']
        performance_indicator = self.create_health_indicator('performance', 'healthy' if success_rate >= 0.9 else 'warning' if success_rate >= 0.7 else 'critical', f'Command success rate: {success_rate:.2%}', {'success_rate': success_rate, 'total_commands': self.execution_stats['total_commands'], 'average_execution_time': self.execution_stats['average_execution_time']})
        return self._health_indicators + [performance_indicator]

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

