
def _apply_level_1_degradation(self, operation_id: str) -> Dict[str, Any]:
    """Apply level 1 degradation: Reduce analysis scope"""
    try:
        self.logger.info(f'Applying level 1 degradation for operation {operation_id}: reduced analysis scope')
        degradation_config = {'analysis_scope': 'reduced', 'comprehensive_analysis': 'disabled', 'pattern_matching': 'fast_only', 'fix_generation': 'basic_only', 'validation': 'minimal'}
        if operation_id in self.operation_callbacks:
            callback = self.operation_callbacks[operation_id]
            callback(degradation_config)
        return {'success': True, 'degradation_level': 1, 'strategy': 'reduced_analysis_scope', 'config': degradation_config, 'estimated_time_savings': '40%'}
    except Exception as e:
        self.logger.error(f'Level 1 degradation failed for operation {operation_id}: {e}')
        return {'success': False, 'error': str(e)}
