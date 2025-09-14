
def _analyze_maintainability(self, tree: ast.AST, content: str, file_path: Path) -> Dict[str, Any]:
    """Analyze code maintainability metrics."""
    issues = []
    maintainability_score = 100
    lines = content.split('\n')
    line_counts = {}
    for i, line in enumerate(lines):
        stripped = line.strip()
        if len(stripped) > 10 and (not stripped.startswith('#')):
            if stripped in line_counts:
                line_counts[stripped].append(i + 1)
            else:
                line_counts[stripped] = [i + 1]
    for line_content, line_numbers in line_counts.items():
        if len(line_numbers) > 2:
            issues.append(CodeQualityIssue(file_path=str(file_path), line_number=line_numbers[0], issue_type=CodeQualityMetric.MAINTAINABILITY, severity='minor', message=f'Duplicated code found ({len(line_numbers)} occurrences)', suggestion='Extract common code into reusable functions'))
            maintainability_score -= 5
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            param_count = len(node.args.args)
            if param_count > 5:
                issues.append(CodeQualityIssue(file_path=str(file_path), line_number=node.lineno, issue_type=CodeQualityMetric.MAINTAINABILITY, severity='minor', message=f"Function '{node.name}' has too many parameters: {param_count}", suggestion='Consider using a configuration object or breaking down the function'))
                maintainability_score -= 3
    return {'score': max(0, maintainability_score), 'issues': issues}
