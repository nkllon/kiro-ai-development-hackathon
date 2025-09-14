from src.rm_ddd.core.registry import register_module

    def _check_hardcoded_secrets(self, content: str, file_path: Path) -> List[Finding]:
        """Check for hardcoded secrets and credentials"""
        findings = []
        lines = content.splitlines()
        for line_num, line in enumerate(lines, 1):
            for pattern, secret_type in self.secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(Finding(type=FindingType.SECURITY_VULNERABILITY, severity=Severity.HIGH, location=CodeLocation(str(file_path), line_num), description=f"Hardcoded {secret_type.replace('_', ' ')} detected", confidence=0.9, evidence={'vulnerability_type': 'hardcoded_secret', 'secret_type': secret_type, 'line_content': line.strip()}))
        return findings
