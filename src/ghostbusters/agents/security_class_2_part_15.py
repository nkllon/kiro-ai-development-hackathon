from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def _check_python_security(self, content: str, file_path: Path) -> List[Finding]:
        """Python-specific security checks"""
        findings = []
        lines = content.splitlines()
        python_patterns = [('pickle\\.loads?\\s*\\(', 'unsafe_deserialization', Severity.HIGH), ('yaml\\.load\\s*\\(', 'unsafe_yaml_load', Severity.HIGH), ('input\\s*\\(\\s*\\)', 'unsafe_input', Severity.MEDIUM), ('__import__\\s*\\(', 'dynamic_import', Severity.MEDIUM)]
        for line_num, line in enumerate(lines, 1):
            for pattern, issue_type, severity in python_patterns:
                if re.search(pattern, line):
                    findings.append(Finding(type=FindingType.SECURITY_VULNERABILITY, severity=severity, location=CodeLocation(str(file_path), line_num), description=f"Python security issue: {issue_type.replace('_', ' ')}", confidence=0.8, evidence={'vulnerability_type': issue_type, 'language': 'python', 'line_content': line.strip()}))
        return findings
