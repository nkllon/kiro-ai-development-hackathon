from src.rm_ddd.core.health import ModuleHealth

def _analyze_competitor_moves(self, moves: List[CompetitorMove]) -> Dict[str, Any]:
    """Analyze competitor moves for patterns and threats."""
    return {'total_moves': len(moves), 'high_impact_moves': len([m for m in moves if m.market_impact > 0.7]), 'urgent_responses_needed': len([m for m in moves if m.response_urgency.value == 'urgent']), 'primary_competitor': max(set((m.competitor for m in moves)), key=lambda x: sum((1 for m in moves if m.competitor == x)))}

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

