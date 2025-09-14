from src.rm_ddd.core.health import ModuleHealth

def _generate_recommendations(self, rca_results: List[RCAResult]) -> List[str]:
    """Generate actionable recommendations from RCA results"""
    recommendations = []
    all_fixes = []
    for result in rca_results:
        all_fixes.extend(result.systematic_fixes)
    fix_types = {}
    for fix in all_fixes:
        fix_type = fix.root_cause.cause_type
        if fix_type not in fix_types:
            fix_types[fix_type] = []
        fix_types[fix_type].append(fix)
    for fix_type, fixes in fix_types.items():
        if len(fixes) > 1:
            recommendations.append(f'Address {len(fixes)} {fix_type.value} issues systematically')
        else:
            recommendations.append(f'Fix {fix_type.value}: {fixes[0].fix_description}')
    if len(all_fixes) > 5:
        recommendations.append('Consider implementing automated prevention checks')
    if not recommendations:
        recommendations.append('No specific systematic fixes identified - review test failures manually')
    return recommendations

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

