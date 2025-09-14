from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _check_path_traversal(self, content: str, file_path: Path) -> List[Finding]:
        """Check for path traversal vulnerabilities"""
        findings = []
        lines = content.splitlines()
        for line_num, line in enumerate(lines, 1):
            for pattern in self.path_traversal_patterns:
                if re.search(pattern, line):
                    findings.append(Finding(type=FindingType.SECURITY_VULNERABILITY, severity=Severity.HIGH, location=CodeLocation(str(file_path), line_num), description='Potential path traversal vulnerability detected', confidence=0.7, evidence={'vulnerability_type': 'path_traversal', 'pattern_matched': pattern, 'line_content': line.strip()}))
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

