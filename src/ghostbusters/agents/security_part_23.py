from datetime import datetime
from typing import Dict, List, Any

    def _check_command_injection(self, content: str, file_path: Path) -> List[Finding]:
        """Check for command injection vulnerabilities"""
        findings = []
        lines = content.splitlines()
        for line_num, line in enumerate(lines, 1):
            for pattern in self.command_injection_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(Finding(type=FindingType.SECURITY_VULNERABILITY, severity=Severity.CRITICAL, location=CodeLocation(str(file_path), line_num), description='Potential command injection vulnerability detected', confidence=0.8, evidence={'vulnerability_type': 'command_injection', 'pattern_matched': pattern, 'line_content': line.strip()}))
        return findings
