from src.rm_ddd.core.health import ModuleHealth

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

