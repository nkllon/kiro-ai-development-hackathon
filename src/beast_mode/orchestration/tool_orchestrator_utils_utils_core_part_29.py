from src.rm_ddd.core.health import ModuleHealth

def _calculate_compliance_score(self) -> float:
    """Calculate overall compliance score for all tools"""
    if not self.registered_tools:
        return 0.0
    total_compliance = 0.0
    for tool_id, tool_def in self.registered_tools.items():
        constraints_met = 0
        total_constraints = len(tool_def.systematic_constraints) if hasattr(tool_def, 'systematic_constraints') else 1
        if hasattr(tool_def, 'systematic_constraints'):
            for constraint, required in tool_def.systematic_constraints.items():
                if required:
                    constraints_met += 1
        else:
            constraints_met = 1
        tool_compliance = constraints_met / total_constraints if total_constraints > 0 else 1.0
        total_compliance += tool_compliance
    return total_compliance / len(self.registered_tools)
