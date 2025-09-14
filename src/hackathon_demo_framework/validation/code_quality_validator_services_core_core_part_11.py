
def _analyze_performance(self, tree: ast.AST, content: str, file_path: Path) -> Dict[str, Any]:
    """Analyze potential performance issues."""
    issues = []
    performance_score = 100
    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            for child in ast.walk(node):
                if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                    if isinstance(child.target, ast.Name):
                        issues.append(CodeQualityIssue(file_path=str(file_path), line_number=node.lineno, issue_type=CodeQualityMetric.PERFORMANCE, severity='minor', message='Potential inefficient list concatenation in loop', suggestion='Consider using list comprehension or join()'))
                        performance_score -= 5
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name) and node.func.value.id == 're' and (node.func.attr in ['search', 'match', 'findall']):
                    issues.append(CodeQualityIssue(file_path=str(file_path), line_number=node.lineno, issue_type=CodeQualityMetric.PERFORMANCE, severity='minor', message='Consider compiling regex patterns for repeated use', suggestion='Use re.compile() for patterns used multiple times'))
                    performance_score -= 2
    return {'score': max(0, performance_score), 'issues': issues}
