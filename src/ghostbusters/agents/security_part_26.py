from datetime import datetime
from typing import Dict, List, Any

    def _check_path_traversal(self, content: str, file_path: Path) -> List[Finding]:
        """Check for path traversal vulnerabilities"""
        findings = []
        lines = content.splitlines()
        for line_num, line in enumerate(lines, 1):
            for pattern in self.path_traversal_patterns:
                if re.search(pattern, line):
                    findings.append(Finding(type=FindingType.SECURITY_VULNERABILITY, severity=Severity.HIGH, location=CodeLocation(str(file_path), line_num), description='Potential path traversal vulnerability detected', confidence=0.7, evidence={'vulnerability_type': 'path_traversal', 'pattern_matched': pattern, 'line_content': line.strip()}))
        return findings
