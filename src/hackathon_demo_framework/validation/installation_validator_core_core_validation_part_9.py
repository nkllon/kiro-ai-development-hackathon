
def _validate_setup_instructions(self) -> Dict[str, Any]:
    """Validate setup instructions in documentation."""
    issues = []
    score = 100
    doc_files_found = []
    for doc_file in self.doc_files:
        if (self.project_path / doc_file).exists():
            doc_files_found.append(self.project_path / doc_file)
    if not doc_files_found:
        issues.append(InstallationIssue(issue_type=InstallationIssueType.DOCUMENTATION, severity='major', message='No installation documentation found', suggestion='Add README.md with installation instructions'))
        score = 30
    else:
        for doc_file in doc_files_found:
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                sections_found = 0
                for section in self.required_sections:
                    if section in content:
                        sections_found += 1
                if sections_found == 0:
                    issues.append(InstallationIssue(issue_type=InstallationIssueType.SETUP_INSTRUCTIONS, severity='major', message=f'No installation instructions in {doc_file.name}', file_path=str(doc_file), suggestion='Add installation/setup section to documentation'))
                    score -= 20
                elif sections_found < 2:
                    issues.append(InstallationIssue(issue_type=InstallationIssueType.SETUP_INSTRUCTIONS, severity='minor', message=f'Limited installation instructions in {doc_file.name}', file_path=str(doc_file), suggestion='Expand installation instructions with more detail'))
                    score -= 10
                if '```' not in content and '`' not in content:
                    issues.append(InstallationIssue(issue_type=InstallationIssueType.SETUP_INSTRUCTIONS, severity='minor', message=f'No code examples in {doc_file.name}', file_path=str(doc_file), suggestion='Add code examples for installation commands'))
                    score -= 5
            except Exception as e:
                issues.append(InstallationIssue(issue_type=InstallationIssueType.DOCUMENTATION, severity='minor', message=f'Cannot read {doc_file.name}: {e}', file_path=str(doc_file), suggestion='Fix file encoding or permissions'))
                score -= 5
    return {'score': max(0, score), 'issues': issues}
