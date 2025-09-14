from src.rm_ddd.core.health import ModuleHealth

def _check_file_patterns(self, domain: Domain) -> List[HealthIssue]:
    """Check if domain file patterns match actual files"""
    issues = []
    try:
        for pattern in domain.patterns:
            pattern_path = self.project_root / pattern.replace('**', '*')
            matching_files = list(self.project_root.glob(pattern))
            if not matching_files:
                issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.PATTERN, description=f"Pattern '{pattern}' matches no files", suggested_fix=f'Verify pattern is correct or remove if no longer needed', affected_files=[pattern]))
            else:
                inaccessible_files = []
                for file_path in matching_files[:10]:
                    if not file_path.exists() or not os.access(file_path, os.R_OK):
                        inaccessible_files.append(str(file_path))
                if inaccessible_files:
                    issues.append(HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.FILE, description=f"Files matching '{pattern}' are not accessible", suggested_fix='Check file permissions and existence', affected_files=inaccessible_files))
    except Exception as e:
        issues.append(HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.PATTERN, description=f'Failed to validate patterns: {str(e)}', suggested_fix='Check pattern syntax and file system access'))
    return issues
