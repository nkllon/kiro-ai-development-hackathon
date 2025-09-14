
def _calculate_health_score(self) -> float:
    """Calculate health score."""
    score = 1.0
    if self._errors > 0:
        score -= min(0.5, self._errors * 0.1)
    if not self.settings_data:
        score -= 0.3
    return max(0.0, score)
