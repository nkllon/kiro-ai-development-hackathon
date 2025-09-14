from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


class AnalyzecompetitivethreatsClass:
    """Auto-generated class for functions."""

    def _analyze_competitive_threats(self, moves: List[CompetitorMove]) -> List[CompetitiveThreat]:
    """Analyze competitor moves for threats."""
    threats = []
    for move in moves:
    if move.response_urgency.value in ['immediate', 'urgent']:
    threat = CompetitiveThreat(competitor=move.competitor, threat_type=move.move_type, impact_level=move.market_impact, response_urgency=move.response_urgency, market_impact={'description': move.description}, detection_time=datetime.now(), response_deadline=datetime.now() + timedelta(hours=24))
    threats.append(threat)
    return threats

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

