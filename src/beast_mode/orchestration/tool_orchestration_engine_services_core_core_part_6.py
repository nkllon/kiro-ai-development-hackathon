from src.rm_ddd.core.health import ModuleHealth

def _assess_decision_confidence(self, context: DecisionContext) -> Dict[str, Any]:
    """
        Assess decision confidence using model-driven intelligence
        Returns confidence level and routing decision
        """
    if context.confidence_score > 0.0:
        base_confidence = context.confidence_score
        confidence_factors = ['Pre-calculated confidence score used']
    else:
        registry_result = self.intelligence_engine.consult_registry_first(context)
        base_confidence = 0.0
        confidence_factors = []
        if registry_result.get('domain_match'):
            base_confidence += 0.4
            confidence_factors.append('Domain intelligence available')
        if registry_result.get('requirements_match'):
            base_confidence += 0.3
            confidence_factors.append('Requirements mapping found')
        if registry_result.get('tool_mappings'):
            base_confidence += 0.2
            confidence_factors.append('Tool mappings available')
        if registry_result.get('historical_patterns'):
            base_confidence += 0.1
            confidence_factors.append('Historical patterns available')
        if context.time_pressure == 'immediate':
            base_confidence -= 0.1
            confidence_factors.append('Time pressure reduces confidence')
        if context.risk_tolerance == 'low':
            base_confidence -= 0.1
            confidence_factors.append('Low risk tolerance requires higher confidence')
        if len(context.previous_decisions) > 0:
            base_confidence += 0.05
            confidence_factors.append('Previous decision context available')
        context.confidence_score = base_confidence
    if base_confidence >= self.confidence_thresholds['high_threshold']:
        confidence_level = DecisionConfidenceLevel.HIGH
    elif base_confidence >= self.confidence_thresholds['medium_threshold']:
        confidence_level = DecisionConfidenceLevel.MEDIUM
    else:
        confidence_level = DecisionConfidenceLevel.LOW
    return {'confidence_level': confidence_level, 'confidence_score': base_confidence, 'confidence_factors': confidence_factors, 'registry_result': registry_result if context.confidence_score == 0.0 else None}

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

