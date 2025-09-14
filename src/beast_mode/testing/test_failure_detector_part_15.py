from src.rm_ddd.core.health import ModuleHealth

class ParsejsonoutputClass:
    """Auto-generated class for functions."""

    def _parse_json_output(self, json_file: str) -> List[TestFailureData]:
    """Parse pytest JSON output for failure information"""
    try:
    with open(json_file, 'r') as f:
    data = json.load(f)
    failures = []
    if 'tests' in data:
    for test in data['tests']:
    if test.get('outcome') in ['failed', 'error']:
    failure_data = self._create_failure_from_json(test)
    if failure_data:
    failures.append(failure_data)
    return failures
    except Exception as e:
    self.logger.error(f'JSON output parsing failed: {e}')
    return []

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

