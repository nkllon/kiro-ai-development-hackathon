from src.rm_ddd.core.health import ModuleHealth

class OutputtableClass:
    """Auto-generated class for functions."""

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

