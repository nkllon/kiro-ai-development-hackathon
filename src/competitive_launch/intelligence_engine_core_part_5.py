from src.rm_ddd.core.health import ModuleHealth

def calculate_competitive_advantage(self) -> Dict[str, Any]:
    """
        Calculate quantitative competitive advantage metrics.
        
        Returns:
            Dict containing competitive advantage metrics
        """
    logger.info('Calculating competitive advantage metrics')
    try:
        systematic_metrics = self._calculate_systematic_metrics()
        fmh_metrics = self._calculate_fmh_metrics()
        accountability_metrics = self._calculate_accountability_metrics()
        requirements_metrics = self._calculate_requirements_metrics()
        time_to_market = self._calculate_time_to_market_advantage()
        overall_advantage = self._calculate_overall_advantage(systematic_metrics, fmh_metrics, accountability_metrics, requirements_metrics, time_to_market)
        result = {'overall_advantage': overall_advantage, 'systematic_metrics': systematic_metrics, 'fmh_metrics': fmh_metrics, 'accountability_metrics': accountability_metrics, 'requirements_metrics': requirements_metrics, 'time_to_market': time_to_market, 'competitive_position': self._determine_competitive_position(overall_advantage)}
        logger.info(f'Competitive advantage calculated: {overall_advantage:.2%} overall advantage')
        return result
    except Exception as e:
        logger.error(f'Competitive advantage calculation failed: {e}')
        return {'overall_advantage': 0.0, 'error': str(e)}
