from src.rm_ddd.core.health import ModuleHealth

class AnalyzecomplexityClass:
    """Auto-generated class for functions."""

    def _analyze_complexity(self, tree: ast.AST, file_path: Path) -> Dict[str, Any]:
    """Analyze code complexity metrics."""
    issues = []
    complexity_scores = []
    for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
    complexity = self._calculate_cyclomatic_complexity(node)
    complexity_scores.append(min(100, max(0, 100 - (complexity - 1) * 10)))
    if complexity > self.thresholds['complexity_max']:
    issues.append(CodeQualityIssue(file_path=str(file_path), line_number=node.lineno, issue_type=CodeQualityMetric.COMPLEXITY, severity='major' if complexity > 15 else 'minor', message=f"Function '{node.name}' has high complexity: {complexity}", suggestion='Break down into smaller functions or simplify logic'))
    function_length = self._get_node_length(node)
    if function_length > self.thresholds['function_length_max']:
    issues.append(CodeQualityIssue(file_path=str(file_path), line_number=node.lineno, issue_type=CodeQualityMetric.COMPLEXITY, severity='minor', message=f"Function '{node.name}' is too long: {function_length} lines", suggestion='Break down into smaller, more focused functions'))
    elif isinstance(node, ast.ClassDef):
    class_length = self._get_node_length(node)
    if class_length > self.thresholds['class_length_max']:
    issues.append(CodeQualityIssue(file_path=str(file_path), line_number=node.lineno, issue_type=CodeQualityMetric.COMPLEXITY, severity='minor', message=f"Class '{node.name}' is too long: {class_length} lines", suggestion='Consider breaking into smaller, more focused classes'))
    avg_score = sum(complexity_scores) / len(complexity_scores) if complexity_scores else 100
    return {'score': avg_score, 'issues': issues}

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

