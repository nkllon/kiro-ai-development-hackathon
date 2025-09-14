from src.rm_ddd.core.registry import register_module

    def _check_javascript_security(self, content: str, file_path: Path) -> List[Finding]:
        """JavaScript-specific security checks"""
        findings = []
        lines = content.splitlines()
        js_patterns = [('localStorage\\.setItem\\s*\\(\\s*["\\\'][^"\\\']*password', 'password_in_localstorage', Severity.HIGH), ('sessionStorage\\.setItem\\s*\\(\\s*["\\\'][^"\\\']*password', 'password_in_sessionstorage', Severity.HIGH), ('window\\.location\\.href\\s*=.*\\+', 'open_redirect', Severity.MEDIUM), ('postMessage\\s*\\(\\s*.*\\*', 'unsafe_postmessage', Severity.MEDIUM)]
        for line_num, line in enumerate(lines, 1):
            for pattern, issue_type, severity in js_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(Finding(type=FindingType.SECURITY_VULNERABILITY, severity=severity, location=CodeLocation(str(file_path), line_num), description=f"JavaScript security issue: {issue_type.replace('_', ' ')}", confidence=0.7, evidence={'vulnerability_type': issue_type, 'language': 'javascript', 'line_content': line.strip()}))
        return findings
