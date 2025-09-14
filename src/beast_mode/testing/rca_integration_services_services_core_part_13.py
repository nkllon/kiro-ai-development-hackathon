from src.rm_ddd.core.health import ModuleHealth

def _handle_degradation_callback(self, degradation_config: Dict[str, Any]) -> None:
    """
        Handle graceful degradation callback from timeout handler
        Requirements: 1.4 - Graceful degradation implementation
        """
    try:
        self.logger.info(f'Applying degradation configuration: {degradation_config}')
        self._current_degradation_config = degradation_config
        if degradation_config.get('analysis_scope') == 'reduced':
            self.max_failures_per_group = min(5, self.max_failures_per_group)
        elif degradation_config.get('analysis_scope') == 'pattern_matching_only':
            self._pattern_matching_only = True
        elif degradation_config.get('analysis_scope') == 'minimal':
            self._minimal_analysis_mode = True
        self.logger.info('Degradation configuration applied successfully')
    except Exception as e:
        self.logger.error(f'Failed to apply degradation configuration: {e}')
