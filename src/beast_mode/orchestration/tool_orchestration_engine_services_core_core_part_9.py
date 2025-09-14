from src.rm_ddd.core.health import ModuleHealth

class MakemediumconfidencedecisionClass:
    """Auto-generated class for functions."""

    def _make_medium_confidence_decision(self, context: DecisionContext, preferred_tools: Optional[List[str]]=None) -> Dict[str, Any]:
    """
    Medium confidence (50-80%): Multi-Perspective validation escalation
    Task 14 Requirement: 50-80% Multi-Perspective → Stakeholder validation escalation
    """
    self.orchestration_metrics['decision_confidence_distribution']['medium'] += 1
    self.logger.info(f'Making medium confidence decision (50-80%): {context.confidence_score:.1%}')
    model_recommendation = self._make_high_confidence_decision(context, preferred_tools)
    perspective_analysis = self.multi_perspective_engine.analyze_decision_with_stakeholder_perspectives(context, model_recommendation['selected_tools'])
    model_tools = set(model_recommendation['selected_tools'])
    stakeholder_tools = set(perspective_analysis.get('recommended_tools', []))
    if stakeholder_tools:
    selected_tools = list(stakeholder_tools)
    elif model_tools:
    selected_tools = list(model_tools)
    else:
    selected_tools = preferred_tools or []
    return {'selected_tools': selected_tools, 'rationale': f'Medium confidence ({context.confidence_score:.1%}) - escalated to stakeholder validation', 'decision_method': 'stakeholder_validation_escalation', 'confidence_factors': ['Model registry consulted', 'Multi-stakeholder perspectives analyzed', 'Stakeholder validation escalation applied'], 'decision_path': '50-80% Multi-Perspective → Stakeholder validation escalation', 'validation_required': True, 'multi_perspective_analysis': perspective_analysis, 'systematic_approach': 'registry_plus_stakeholder_validation'}

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

