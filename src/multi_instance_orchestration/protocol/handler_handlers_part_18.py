
    def is_healthy(self) -> bool:
        """Check if module is in healthy state."""
        recent_indicators = [indicator for indicator in self._health_indicators if (datetime.now() - indicator.timestamp).total_seconds() < 300]
        critical_count = sum((1 for indicator in recent_indicators if indicator.status == 'critical'))
        return critical_count == 0
