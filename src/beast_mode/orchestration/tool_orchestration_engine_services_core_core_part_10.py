
def _make_low_confidence_decision(self, context: DecisionContext, preferred_tools: Optional[List[str]]=None) -> Dict[str, Any]:
    """
        Low confidence (<50%): Full Analysis with comprehensive RCA and multi-stakeholder synthesis
        Task 14 Requirement: <50% Full Analysis → Comprehensive RCA and multi-stakeholder synthesis
        """
    self.orchestration_metrics['decision_confidence_distribution']['low'] += 1
    self.logger.info(f'Making low confidence decision (<50%): {context.confidence_score:.1%}')
    rca_analysis = None
    if hasattr(context, 'failure_context') and context.failure_context:
        try:
            from ..analysis.rca_engine import Failure, FailureCategory
            failure = Failure(failure_id=f'tool_orchestration_{int(time.time())}', timestamp=datetime.now(), component='tool_orchestration', error_message=context.failure_context.get('error', 'Low confidence decision'), stack_trace=context.failure_context.get('stack_trace'), context=context.failure_context, category=FailureCategory.TOOL_FAILURE)
            rca_analysis = self.rca_engine.perform_systematic_rca(failure)
            self.logger.info('Comprehensive RCA completed for low confidence decision')
        except Exception as e:
            self.logger.warning(f'RCA analysis failed: {e}')
    stakeholder_analysis = self.multi_perspective_engine.analyze_low_percentage_decision(context)
    all_recommendations = []
    if rca_analysis and rca_analysis.systematic_fixes:
        for fix in rca_analysis.systematic_fixes:
            if 'tools' in fix.fix_description.lower():
                all_recommendations.extend(['systematic_repair_tools', 'rca_recommended_tools'])
    for perspective in stakeholder_analysis.get('perspectives', []):
        perspective_tools = perspective.get('recommended_tools', [])
        all_recommendations.extend(perspective_tools)
    from collections import Counter
    tool_votes = Counter(all_recommendations)
    consensus_tools = [tool for tool, votes in tool_votes.most_common() if votes >= 2]
    if not consensus_tools:
        consensus_tools = stakeholder_analysis.get('synthesized_recommendation', {}).get('tools', [])
    available_consensus = [tool for tool in consensus_tools if tool in self.tools_registry]
    if not available_consensus and preferred_tools:
        available_consensus = [tool for tool in preferred_tools if tool in self.tools_registry]
    return {'selected_tools': available_consensus, 'rationale': f'Low confidence ({context.confidence_score:.1%}) - comprehensive RCA and multi-stakeholder synthesis', 'decision_method': 'comprehensive_rca_and_stakeholder_synthesis', 'confidence_factors': ['Comprehensive RCA performed' if rca_analysis else 'RCA not applicable', 'Multi-stakeholder perspectives analyzed', 'Consensus-based tool selection', 'Systematic approach to uncertainty'], 'decision_path': '<50% Full Analysis → Comprehensive RCA and multi-stakeholder synthesis', 'validation_required': True, 'rca_analysis': rca_analysis, 'multi_perspective_analysis': stakeholder_analysis, 'systematic_approach': 'comprehensive_analysis_with_rca', 'rationale': f'Low confidence decision using comprehensive multi-stakeholder analysis', 'decision_method': 'full_multi_stakeholder_analysis', 'confidence_factors': ['All stakeholder perspectives analyzed', 'Consensus-based tool selection', 'Risk-reduced decision process'], 'stakeholder_analysis': stakeholder_analysis}
