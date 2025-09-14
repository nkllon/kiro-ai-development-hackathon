
    def _calculate_health_score(self) -> float:
        """Calculate health score."""
        score = 1.0
        if self._errors > 0:
            score -= min(0.5, self._errors * 0.1)
        if not self.success:
            score -= 0.3
        if self.records_failed > 0:
            failure_rate = self.records_failed / max(1, self.records_processed)
            score -= failure_rate * 0.4
        return max(0.0, score)
