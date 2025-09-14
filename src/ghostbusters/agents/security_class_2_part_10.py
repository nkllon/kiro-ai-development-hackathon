from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


class CheckcommandinjectionClass:
    """Auto-generated class for functions."""

    def _check_command_injection(self, content: str, file_path: Path) -> List[Finding]:
    """Check for command injection vulnerabilities"""
    findings = []
    lines = content.splitlines()
    for line_num, line in enumerate(lines, 1):
    for pattern in self.command_injection_patterns:
    if re.search(pattern, line, re.IGNORECASE):
    findings.append(Finding(type=FindingType.SECURITY_VULNERABILITY, severity=Severity.CRITICAL, location=CodeLocation(str(file_path), line_num), description='Potential command injection vulnerability detected', confidence=0.8, evidence={'vulnerability_type': 'command_injection', 'pattern_matched': pattern, 'line_content': line.strip()}))
    return findings

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

