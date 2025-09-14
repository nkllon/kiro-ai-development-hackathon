from src.rm_ddd.core.health import ModuleHealth

def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
    """Analyze a single Python file for quality metrics."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content)
        lines_of_code = len([line for line in content.split('\n') if line.strip() and (not line.strip().startswith('#'))])
        complexity_analysis = self._analyze_complexity(tree, file_path)
        maintainability_analysis = self._analyze_maintainability(tree, content, file_path)
        documentation_analysis = self._analyze_documentation(tree, file_path)
        style_analysis = self._analyze_style(content, file_path)
        security_analysis = self._analyze_security(tree, content, file_path)
        performance_analysis = self._analyze_performance(tree, content, file_path)
        all_issues = []
        all_issues.extend(complexity_analysis['issues'])
        all_issues.extend(maintainability_analysis['issues'])
        all_issues.extend(documentation_analysis['issues'])
        all_issues.extend(style_analysis['issues'])
        all_issues.extend(security_analysis['issues'])
        all_issues.extend(performance_analysis['issues'])
        return {'lines_of_code': lines_of_code, 'complexity_score': complexity_analysis['score'], 'maintainability_score': maintainability_analysis['score'], 'documentation_score': documentation_analysis['score'], 'style_score': style_analysis['score'], 'security_score': security_analysis['score'], 'performance_score': performance_analysis['score'], 'issues': all_issues}
    except Exception as e:
        self.logger.error(f'Failed to analyze {file_path}: {e}')
        return {'lines_of_code': 0, 'complexity_score': 0, 'maintainability_score': 0, 'documentation_score': 0, 'style_score': 0, 'security_score': 0, 'performance_score': 0, 'issues': [CodeQualityIssue(file_path=str(file_path), line_number=1, issue_type=CodeQualityMetric.MAINTAINABILITY, severity='critical', message=f'File analysis failed: {e}', suggestion='Fix syntax errors or encoding issues')]}
