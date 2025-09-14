
    def _calculate_health_score(self) -> float:
        """Calculate health score based on various factors."""
        score = 1.0
        if self._errors > 0:
            score -= min(0.5, self._errors * 0.1)
        if self.status == 'failed':
            score -= 0.3
        if self.progress < 0 or self.progress > 1:
            score -= 0.2
        return max(0.0, score)
