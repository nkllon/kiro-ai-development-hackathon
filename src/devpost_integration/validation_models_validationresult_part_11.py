
    def _calculate_health_score(self) -> float:
        """Calculate health score."""
        score = 1.0
        
        # Penalize internal errors
        if self._errors > 0:
            score -= min(0.5, self._errors * 0.1)
        
        # Penalize high validation error count
        if len(self.errors) > 10:
            score -= 0.2
        
        return max(0.0, score)
    