
def get_service_usage_patterns(self) -> Dict[str, Any]:
    """
        Get service usage patterns and effectiveness metrics
        Documents service usage patterns and effectiveness for optimization
        """
    return {'service_usage_distribution': self.service_metrics['service_usage_patterns'], 'peak_usage_times': self._analyze_peak_usage_times(), 'team_expertise_correlation': self._analyze_expertise_service_correlation(), 'service_effectiveness': {'pdca_cycle': self._calculate_service_effectiveness(ServiceType.PDCA_CYCLE), 'model_driven_building': self._calculate_service_effectiveness(ServiceType.MODEL_DRIVEN_BUILDING), 'tool_health_management': self._calculate_service_effectiveness(ServiceType.TOOL_HEALTH_MANAGEMENT), 'quality_assurance': self._calculate_service_effectiveness(ServiceType.QUALITY_ASSURANCE)}, 'optimization_recommendations': self._generate_service_optimization_recommendations(), 'analysis_timestamp': datetime.now().isoformat()}
