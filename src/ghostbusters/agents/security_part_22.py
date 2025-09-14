from datetime import datetime
from typing import Dict, List, Any

    def _check_xss_vulnerabilities(self, content: str, file_path: Path) -> List[Finding]:
        """Check for XSS vulnerabilities"""
        findings = []
        lines = content.splitlines()
        for line_num, line in enumerate(lines, 1):
            for pattern in self.xss_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(Finding(type=FindingType.SECURITY_VULNERABILITY, severity=Severity.HIGH, location=CodeLocation(str(file_path), line_num), description='Potential XSS vulnerability detected', confidence=0.7, evidence={'vulnerability_type': 'xss', 'pattern_matched': pattern, 'line_content': line.strip()}))
        return findings
