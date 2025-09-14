
    def _identify_health_issues(self) -> List[str]:
        """Identify health issues"""
        issues = []
        if self._metrics['success_rate'] < 0.8:
            issues.append('Low success rate detected')
        if self._metrics['error_count'] > 10:
            issues.append('High error count detected')
        if not self.preview_data.get('title'):
            issues.append('Preview title not set')
        if not self.preview_data.get('preview_url'):
            issues.append('Preview URL not set')
        return issues
