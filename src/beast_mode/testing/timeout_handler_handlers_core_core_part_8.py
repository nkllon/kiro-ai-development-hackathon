
def get_timeout_recommendations(self, operation_id: str, current_elapsed: float) -> Dict[str, Any]:
    """
        Get timeout recommendations based on current operation progress
        Requirements: 4.2 - Performance monitoring and optimization
        """
    try:
        recommendations = {'operation_id': operation_id, 'current_elapsed_seconds': current_elapsed, 'timeout_status': 'normal', 'recommendations': [], 'degradation_suggested': False, 'estimated_completion_time': None}
        if current_elapsed >= self.timeout_config.hard_timeout_seconds:
            recommendations['timeout_status'] = 'critical'
            recommendations['recommendations'].append('immediate_termination_required')
        elif current_elapsed >= self.timeout_config.primary_timeout_seconds:
            recommendations['timeout_status'] = 'exceeded'
            recommendations['recommendations'].append('hard_timeout_imminent')
            recommendations['degradation_suggested'] = True
        elif current_elapsed >= self.timeout_config.graceful_timeout_seconds:
            recommendations['timeout_status'] = 'warning'
            recommendations['recommendations'].append('consider_graceful_degradation')
            recommendations['degradation_suggested'] = True
        elif current_elapsed >= self.timeout_config.warning_timeout_seconds:
            recommendations['timeout_status'] = 'approaching'
            recommendations['recommendations'].append('monitor_closely')
        if current_elapsed > 15:
            recommendations['recommendations'].append('reduce_analysis_scope')
        if current_elapsed > 20:
            recommendations['recommendations'].append('enable_fast_pattern_matching_only')
        if current_elapsed > 25:
            recommendations['recommendations'].append('prepare_for_graceful_degradation')
        recommendations['estimated_completion_time'] = self._estimate_completion_time(operation_id, current_elapsed)
        return recommendations
    except Exception as e:
        self.logger.error(f'Failed to get timeout recommendations for operation {operation_id}: {e}')
        return {'operation_id': operation_id, 'error': str(e), 'timeout_status': 'unknown', 'recommendations': ['check_timeout_handler_health']}
