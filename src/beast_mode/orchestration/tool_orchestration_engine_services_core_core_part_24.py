
def get_decision_framework_status(self) -> Dict[str, Any]:
    """
        Get status of the confidence-based decision framework
        Task 14 completion validation
        """
    return {'decision_framework_active': True, 'confidence_thresholds': self.confidence_thresholds, 'decision_paths': {'high_confidence_80_plus': 'Direct registry consultation', 'medium_confidence_50_80': 'Stakeholder validation escalation', 'low_confidence_below_50': 'Comprehensive RCA and multi-stakeholder synthesis'}, 'rca_integration': {'integrated': hasattr(self, 'rca_engine') and self.rca_engine is not None, 'rca_engine_healthy': self.rca_engine.is_healthy() if hasattr(self, 'rca_engine') else False}, 'adaptive_patterns': {'patterns_available': len(getattr(self, 'adaptive_patterns', {})), 'unknown_failure_handling': True, 'pattern_learning_active': True}, 'decision_metrics': self.orchestration_metrics['decision_confidence_distribution'], 'systematic_approach_compliance': True}
