
    def _generate_repair_recommendations(self, tool_name: str, root_causes: List[str]) -> List[str]:
        """Generate systematic repair recommendations"""
        recommendations = []
        for cause in root_causes:
            if cause == 'modular_makefile_structure_not_created':
                recommendations.append('Create makefiles/ directory with modular structure')
            else:
                recommendations.append(f'Address root cause: {cause}')
        return recommendations
