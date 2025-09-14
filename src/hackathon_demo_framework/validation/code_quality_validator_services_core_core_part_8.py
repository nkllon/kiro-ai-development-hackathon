from src.rm_ddd.core.health import ModuleHealth

def _analyze_documentation(self, tree: ast.AST, file_path: Path) -> Dict[str, Any]:
    """Analyze documentation coverage and quality."""
    issues = []
    total_items = 0
    documented_items = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            total_items += 1
            has_docstring = node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str)
            if has_docstring:
                documented_items += 1
                docstring = node.body[0].value.value
                if len(docstring.strip()) < 10:
                    issues.append(CodeQualityIssue(file_path=str(file_path), line_number=node.lineno, issue_type=CodeQualityMetric.DOCUMENTATION, severity='minor', message=f"{type(node).__name__} '{node.name}' has minimal docstring", suggestion='Provide more detailed documentation'))
            else:
                severity = 'major' if isinstance(node, ast.ClassDef) else 'minor'
                issues.append(CodeQualityIssue(file_path=str(file_path), line_number=node.lineno, issue_type=CodeQualityMetric.DOCUMENTATION, severity=severity, message=f"{type(node).__name__} '{node.name}' missing docstring", suggestion='Add comprehensive docstring with description and parameters'))
    documentation_score = documented_items / total_items * 100 if total_items > 0 else 100
    return {'score': documentation_score, 'issues': issues}
