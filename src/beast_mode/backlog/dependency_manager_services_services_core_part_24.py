from src.rm_ddd.core.health import ModuleHealth

def _assess_path_risks(self, critical_path: List[str]) -> Dict[str, RiskLevel]:
    """Assess risk factors for nodes in the critical path"""
    risk_factors = {}
    for node in critical_path:
        max_risk = RiskLevel.LOW
        for dep_spec in self._dependencies.values():
            if dep_spec.target_item_id == node or ('_depends_on_' in dep_spec.dependency_id and dep_spec.dependency_id.split('_depends_on_')[0] == node):
                if dep_spec.risk_level.value > max_risk.value:
                    max_risk = dep_spec.risk_level
        risk_factors[node] = max_risk
    return risk_factors
