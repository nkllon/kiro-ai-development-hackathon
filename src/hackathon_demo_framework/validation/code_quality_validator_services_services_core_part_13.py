
def _get_node_length(self, node: ast.AST) -> int:
    """Get the length of an AST node in lines."""
    if hasattr(node, 'end_lineno') and node.end_lineno:
        return node.end_lineno - node.lineno + 1
    else:
        return len(list(ast.walk(node)))
