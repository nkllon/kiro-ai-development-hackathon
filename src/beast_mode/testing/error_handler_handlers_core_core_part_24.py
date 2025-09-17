from src.rm_ddd.core.health import ModuleHealth


def _generate_basic_recommendations(self, test_failures: List[Any], error: Exception) -> List[str]:
    """Generate basic recommendations when RCA is unavailable"""
    recommendations = [f'RCA analysis failed due to: {str(error)[:100]}', f'Found {len(test_failures)} test failures requiring attention']
    failure_types = set((f.failure_type for f in test_failures))
    if 'import' in failure_types:
        recommendations.append('Check Python import paths and dependencies')
    if 'assertion' in failure_types:
        recommendations.append('Review test assertions and expected values')
    if 'timeout' in failure_types:
        recommendations.append('Check test execution timeouts and performance')
    recommendations.extend(['Review test logs for detailed error information', 'Check system resources and configuration', 'Retry RCA analysis when system is stable'])
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

