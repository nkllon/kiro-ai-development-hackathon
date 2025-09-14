
def _analyze_style(self, content: str, file_path: Path) -> Dict[str, Any]:
    """Analyze code style and formatting."""
    issues = []
    style_score = 100
    lines = content.split('\n')
    for i, line in enumerate(lines):
        line_num = i + 1
        if len(line) > 120:
            issues.append(CodeQualityIssue(file_path=str(file_path), line_number=line_num, issue_type=CodeQualityMetric.STYLE, severity='minor', message=f'Line too long: {len(line)} characters', suggestion='Break long lines for better readability'))
            style_score -= 1
        if line.endswith(' ') or line.endswith('\t'):
            issues.append(CodeQualityIssue(file_path=str(file_path), line_number=line_num, issue_type=CodeQualityMetric.STYLE, severity='minor', message='Trailing whitespace found', suggestion='Remove trailing whitespace'))
            style_score -= 0.5
        if '\t' in line and '    ' in line:
            issues.append(CodeQualityIssue(file_path=str(file_path), line_number=line_num, issue_type=CodeQualityMetric.STYLE, severity='major', message='Mixed tabs and spaces for indentation', suggestion='Use consistent indentation (prefer spaces)'))
            style_score -= 5
    return {'score': max(0, style_score), 'issues': issues}
