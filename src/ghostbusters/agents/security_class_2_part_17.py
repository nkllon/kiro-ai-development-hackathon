from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


class CheckjavasecurityClass:
    """Auto-generated class for functions."""

    def _check_java_security(self, content: str, file_path: Path) -> List[Finding]:
    """Java-specific security checks"""
    findings = []
    lines = content.splitlines()
    java_patterns = [('Runtime\\.getRuntime\\(\\)\\.exec', 'runtime_exec', Severity.HIGH), ('ObjectInputStream\\s*\\(', 'unsafe_deserialization', Severity.HIGH), ('Random\\s*\\(\\s*\\)', 'weak_random', Severity.MEDIUM), ('MessageDigest\\.getInstance\\s*\\(\\s*["\\\']MD5', 'weak_hash', Severity.MEDIUM)]
    for line_num, line in enumerate(lines, 1):
    for pattern, issue_type, severity in java_patterns:
    if re.search(pattern, line):
    findings.append(Finding(type=FindingType.SECURITY_VULNERABILITY, severity=severity, location=CodeLocation(str(file_path), line_num), description=f"Java security issue: {issue_type.replace('_', ' ')}", confidence=0.8, evidence={'vulnerability_type': issue_type, 'language': 'java', 'line_content': line.strip()}))
    return findings

    async def _generate_security_recommendations(self, findings: List[Finding]) -> List[Recommendation]:
    """Generate security-specific recommendations"""
    recommendations = []
    vuln_types = {}
    for finding in findings:
    vuln_type = finding.evidence.get('vulnerability_type', 'unknown')
    if vuln_type not in vuln_types:
    vuln_types[vuln_type] = []
    vuln_types[vuln_type].append(finding)
    for vuln_type, vuln_findings in vuln_types.items():
    if vuln_type == 'sql_injection':
    recommendations.append(Recommendation(title='Fix SQL Injection Vulnerabilities', description=f'Use parameterized queries or prepared statements for {len(vuln_findings)} SQL injection issue(s)', priority=Severity.HIGH, effort_estimate='30-60 minutes per issue', automated_fix_available=False))
    elif vuln_type == 'xss':
    recommendations.append(Recommendation(title='Fix XSS Vulnerabilities', description=f'Implement proper input sanitization and output encoding for {len(vuln_findings)} XSS issue(s)', priority=Severity.HIGH, effort_estimate='20-40 minutes per issue', automated_fix_available=False))
    elif vuln_type == 'hardcoded_secret':
    recommendations.append(Recommendation(title='Remove Hardcoded Secrets', description=f'Move {len(vuln_findings)} hardcoded secret(s) to environment variables or secure configuration', priority=Severity.HIGH, effort_estimate='15-30 minutes per secret', automated_fix_available=True, fix_command='externalize_secrets'))
    elif vuln_type == 'command_injection':
    recommendations.append(Recommendation(title='Fix Command Injection Vulnerabilities', description=f'Use safe command execution methods for {len(vuln_findings)} command injection issue(s)', priority=Severity.CRITICAL, effort_estimate='45-90 minutes per issue', automated_fix_available=False))
    return recommendations

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

