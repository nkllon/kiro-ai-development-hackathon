
def _make_high_confidence_decision(self, context: DecisionContext, preferred_tools: Optional[List[str]]=None) -> Dict[str, Any]:
    """
        High confidence (80%+): Direct registry consultation
        Task 14 Requirement: 80%+ Model confidence → Direct registry consultation
        """
    self.orchestration_metrics['decision_confidence_distribution']['high'] += 1
    self.logger.info(f'Making high confidence decision (80%+): {context.confidence_score:.1%}')
    domain_tools = self.intelligence_engine.get_domain_tools(context.domain or 'general')
    available_tools = [tool_id for tool_id in domain_tools if tool_id in self.tools_registry]
    if preferred_tools:
        prioritized_tools = [tool for tool in preferred_tools if tool in available_tools] + [tool for tool in available_tools if tool not in (preferred_tools or [])]
        available_tools = prioritized_tools
    selected_tools = self._select_tools_by_health_and_priority(available_tools)
    return {'selected_tools': selected_tools, 'rationale': f"High confidence ({context.confidence_score:.1%}) - direct registry consultation for {context.domain or 'general'} domain", 'decision_method': 'direct_registry_consultation', 'confidence_factors': ['Domain tools available', 'Registry intelligence high', 'Model confidence >80%'], 'decision_path': '80%+ Model confidence → Direct registry consultation', 'validation_required': False, 'multi_perspective_analysis': None, 'systematic_approach': 'model_driven_direct'}
