from src.rm_ddd.core.health import ModuleHealth

def _check_content_indicators(self, domain: Domain) -> List[HealthIssue]:
    """Check if content indicators are found in domain files"""
    issues = []
    try:
        domain_files = []
        for pattern in domain.patterns:
            matching_files = list(self.project_root.glob(pattern))
            domain_files.extend(matching_files)
        if not domain_files:
            return issues
        sample_files = domain_files[:5]
        indicators_found = set()
        for file_path in sample_files:
            if file_path.suffix in ['.py', '.js', '.ts', '.java', '.cpp', '.c']:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        for indicator in domain.content_indicators:
                            if indicator.lower() in content:
                                indicators_found.add(indicator)
                except Exception:
                    continue
        missing_indicators = set(domain.content_indicators) - indicators_found
        if missing_indicators and len(domain.content_indicators) > 0:
            issues.append(HealthIssue(severity=IssueSeverity.INFO, category=IssueCategory.VALIDATION, description=f"Content indicators not found in sample files: {', '.join(missing_indicators)}", suggested_fix='Verify content indicators are correct or update them'))
    except Exception as e:
        issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.VALIDATION, description=f'Failed to validate content indicators: {str(e)}', suggested_fix='Check file accessibility and content indicator configuration'))
    return issues
