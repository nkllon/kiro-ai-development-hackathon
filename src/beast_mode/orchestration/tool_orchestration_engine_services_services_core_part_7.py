
def _route_decision_by_confidence(self, context: DecisionContext, confidence_level: DecisionConfidenceLevel, preferred_tools: Optional[List[str]]=None) -> Dict[str, Any]:
    """
        Route decision based on confidence level
        - High (80%+): Use Model Registry + Domain Tools
        - Medium (50-80%): Registry + Basic Multi-Perspective Check  
        - Low (<50%): Full Stakeholder-Driven Multi-Perspective Analysis
        """
    if confidence_level == DecisionConfidenceLevel.HIGH:
        return self._make_high_confidence_decision(context, preferred_tools)
    elif confidence_level == DecisionConfidenceLevel.MEDIUM:
        return self._make_medium_confidence_decision(context, preferred_tools)
    else:
        return self._make_low_confidence_decision(context, preferred_tools)
