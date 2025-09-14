from src.rm_ddd.core.health import ModuleHealth

class GetnodelengthClass:
    """Auto-generated class for functions."""

    def _get_node_length(self, node: ast.AST) -> int:
    """Get the length of an AST node in lines."""
    if hasattr(node, 'end_lineno') and node.end_lineno:
    return node.end_lineno - node.lineno + 1
    else:
    return len(list(ast.walk(node)))

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

