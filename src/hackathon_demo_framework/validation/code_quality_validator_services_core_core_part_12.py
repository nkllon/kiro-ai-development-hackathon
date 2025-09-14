
def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
    """Calculate cyclomatic complexity for a function (simplified)."""
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
            complexity += 1
        elif isinstance(child, ast.ExceptHandler):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
    return complexity
