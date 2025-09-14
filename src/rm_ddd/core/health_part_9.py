
    def to_dict(self) -> Dict[str, Any]:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Convert health status to dictionary."""
        return {'status': self.status.value, 'message': self.message, 'is_healthy': self.is_healthy, 'is_degraded': self.is_degraded, 'is_unavailable': self.is_unavailable, 'capabilities': [cap.name for cap in self.capabilities], 'domain_health': self.domain_health.to_dict() if self.domain_health else None, 'health_indicators': self.health_indicators, 'performance_metrics': {'response_time_ms': self.performance_metrics.response_time_ms, 'throughput_per_second': self.performance_metrics.throughput_per_second, 'error_rate': self.performance_metrics.error_rate, 'cpu_usage_percent': self.performance_metrics.cpu_usage_percent, 'memory_usage_mb': self.performance_metrics.memory_usage_mb} if self.performance_metrics else None, 'timestamp': self.timestamp.isoformat()}

@dataclass