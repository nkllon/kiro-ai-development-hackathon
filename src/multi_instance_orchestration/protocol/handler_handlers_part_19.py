
    def get_health_indicators(self) -> list[HealthIndicator]:
        """Get current health indicators."""
        success_rate = 0.0
        if self.execution_stats['total_commands'] > 0:
            success_rate = self.execution_stats['successful_commands'] / self.execution_stats['total_commands']
        performance_indicator = self.create_health_indicator('performance', 'healthy' if success_rate >= 0.9 else 'warning' if success_rate >= 0.7 else 'critical', f'Command success rate: {success_rate:.2%}', {'success_rate': success_rate, 'total_commands': self.execution_stats['total_commands'], 'average_execution_time': self.execution_stats['average_execution_time']})
        return self._health_indicators + [performance_indicator]
