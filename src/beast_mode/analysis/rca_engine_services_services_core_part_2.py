
def get_module_status(self) -> Dict[str, Any]:
    """Operational visibility for external systems (GKE)"""
    return {'module_name': self.module_name, 'status': 'operational' if self.is_healthy() else 'degraded', 'rca_analyses_performed': self.rca_count, 'successful_fixes': self.successful_fixes, 'pattern_library_size': len(self.pattern_library), 'pattern_matches': self.pattern_matches, 'average_analysis_time': self.total_analysis_time / max(1, self.rca_count), 'degradation_active': self._degradation_active}
