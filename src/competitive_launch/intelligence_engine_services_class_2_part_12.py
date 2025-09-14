from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def _generate_threat_alerts(self, threats: List[CompetitiveThreat]) -> List[Dict[str, Any]]:
        """Generate alerts for competitive threats."""
        alerts = []
        for threat in threats:
            alert = {'threat_id': f'threat_{threat.competitor}_{threat.threat_type}', 'severity': threat.response_urgency.value, 'description': f'{threat.competitor} {threat.threat_type} detected', 'response_deadline': threat.response_deadline.isoformat(), 'recommended_action': 'generate_differentiation_strategy'}
            alerts.append(alert)
        return alerts

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

