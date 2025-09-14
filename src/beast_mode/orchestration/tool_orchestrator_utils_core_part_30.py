
def _generate_compliance_improvements(self) -> List[str]:
    """Generate suggestions for improving tool compliance"""
    suggestions = []
    for tool_id, tool_def in self.registered_tools.items():
        if hasattr(tool_def, 'systematic_constraints'):
            for constraint, required in tool_def.systematic_constraints.items():
                if required and constraint not in ['no_ad_hoc_commands', 'systematic_error_handling']:
                    suggestions.append(f'Implement {constraint} for {tool_def.name}')
        else:
            suggestions.append(f'Add systematic constraints definition for {tool_def.name}')
    if len(suggestions) == 0:
        suggestions.extend(['All tools meet current compliance standards', 'Consider implementing advanced compliance monitoring', 'Review and update systematic constraints regularly'])
    return suggestions[:5]
