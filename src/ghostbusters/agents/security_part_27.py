from datetime import datetime
from typing import Dict, List, Any

    def _check_file_permissions(self, file_path: Path) -> List[Finding]:
        """Check file permissions for security issues"""
        findings = []
        try:
            import stat
            file_stat = file_path.stat()
            if file_stat.st_mode & stat.S_IWOTH:
                findings.append(Finding(type=FindingType.SECURITY_VULNERABILITY, severity=Severity.MEDIUM, location=CodeLocation(str(file_path), 1), description='File is world-writable (security risk)', confidence=0.9, evidence={'vulnerability_type': 'file_permissions', 'permissions': oct(file_stat.st_mode)[-3:]}))
            if file_path.suffix.lower() in ['.sh', '.bat', '.cmd', '.exe'] and file_stat.st_mode & stat.S_IXUSR:
                findings.append(Finding(type=FindingType.SECURITY_VULNERABILITY, severity=Severity.LOW, location=CodeLocation(str(file_path), 1), description='Executable file detected - verify necessity', confidence=0.6, evidence={'vulnerability_type': 'executable_file', 'file_extension': file_path.suffix}))
        except Exception as e:
            logger.debug(f'Could not check permissions for {file_path}: {str(e)}')
        return findings
