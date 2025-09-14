from src.rm_ddd.core.health import ModuleHealth

def _analyze_security(self, tree: ast.AST, content: str, file_path: Path) -> Dict[str, Any]:
    """Analyze potential security issues."""
    issues = []
    security_score = 100
    security_patterns = [('eval\\s*\\(', 'Use of eval() can be dangerous'), ('exec\\s*\\(', 'Use of exec() can be dangerous'), ('subprocess\\.call\\s*\\(.*shell\\s*=\\s*True', 'Shell injection risk'), ('os\\.system\\s*\\(', 'Command injection risk'), ('pickle\\.loads?\\s*\\(', 'Pickle deserialization can be unsafe')]
    for pattern, message in security_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            issues.append(CodeQualityIssue(file_path=str(file_path), line_number=line_num, issue_type=CodeQualityMetric.SECURITY, severity='major', message=message, suggestion='Review for security implications and use safer alternatives'))
            security_score -= 10
    secret_patterns = ['password\\s*=\\s*["\\\'][^"\\\']+["\\\']', 'api_key\\s*=\\s*["\\\'][^"\\\']+["\\\']', 'secret\\s*=\\s*["\\\'][^"\\\']+["\\\']']
    for pattern in secret_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            issues.append(CodeQualityIssue(file_path=str(file_path), line_number=line_num, issue_type=CodeQualityMetric.SECURITY, severity='critical', message='Potential hardcoded secret found', suggestion='Use environment variables or secure configuration'))
            security_score -= 20
    return {'score': max(0, security_score), 'issues': issues}
