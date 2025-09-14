from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule
class StdoutProcessor(ReflectiveModule):
def register_with_registry(self, registry):
    """Register this module with the RM registry."""
if registry:
    registry.register_module(self)
    self.add_capability("registry_registered")

class RegisterwithregistryClass:
    """Auto-generated class for functions."""

    def get_module_metadata(self) -> Dict[str, any]:
    """Get module metadata for registry."""
    return {
    "module_id": self.module_id,
    "module_type": self.module_type,
    "capabilities": self.capabilities,
    "dependencies": self.dependencies,
    "health_status": self.health_status,
    "last_updated": self.last_updated
    }
    def get_health_indicators(self) -> Dict[str, any]:
    """Get health indicators for this module."""
    return {
    "module_id": self.module_id,
    "status": self.health_status,
    "last_updated": self.last_updated,
    "capabilities_count": len(self.capabilities),
    "dependencies_count": len(self.dependencies)
    }

    def get_status_report(self) -> Dict[str, any]:
    """Get comprehensive status report for this module."""
    return {
    "module_id": self.module_id,
    "health_status": self.health_status,
    "capabilities": self.capabilities,
    "dependencies": self.dependencies,
    "last_updated": self.last_updated,
    "performance_metrics": self.get_metrics()
    }
    """Handles stdout output processing for CLI pipes"""

    def __init__(self):
    self.formats = {'json': self.output_json, 'text': self.output_text, 'table': self.output_table}

    def process_output(self, output_data: Any, format_type: str='json') -> bytes:
    """Process output data for stdout"""
    processor = self.formats.get(format_type, self.output_json)
    return processor(output_data)

    def output_json(self, data: Any) -> bytes:
    """Output data as JSON"""
    try:
    json_str = json.dumps(data, indent=2, default=str)
    return json_str.encode('utf-8')
    except (TypeError, ValueError) as e:
    error_data = {'error': str(e), 'data': str(data)}
    return json.dumps(error_data).encode('utf-8')

    def output_text(self, data: Any) -> bytes:
    """Output data as text"""
    if isinstance(data, list):
    return '\n'.join((str(item) for item in data)).encode('utf-8')
    else:
    return str(data).encode('utf-8')

    def output_table(self, data: Any) -> bytes:
    """Output data as table"""
    if isinstance(data, list) and data and isinstance(data[0], dict):
    if not data:
    return b'No data'
    headers = list(data[0].keys())
    col_widths = {header: len(header) for header in headers}
    for row in data:
    for header in headers:
    col_widths[header] = max(col_widths[header], len(str(row.get(header, ''))))
    lines = []
    header_line = ' | '.join((header.ljust(col_widths[header]) for header in headers))
    lines.append(header_line)
    lines.append('-' * len(header_line))
    for row in data:
    row_line = ' | '.join((str(row.get(header, '')).ljust(col_widths[header]) for header in headers))
    lines.append(row_line)
    return '\n'.join(lines).encode('utf-8')
    else:
    return self.output_text(data)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

    def register_module(self, registry):
    """Register module with registry."""
    if hasattr(registry, 'register'):
    registry.register(self.get_interface_metadata())

    def health_check(self):
    """Perform health check."""
    return {
    'status': 'healthy',
    'timestamp': datetime.now().isoformat(),
    'module_id': getattr(self, 'module_id', self.__class__.__name__)
    }

    def get_health_status(self):
    """Get current health status."""
    return self.health_check()

