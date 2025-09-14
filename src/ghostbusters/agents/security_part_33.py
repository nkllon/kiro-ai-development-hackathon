from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _get_checks_performed(self) -> List[str]:
        """Get list of security checks performed"""
        return ['sql_injection', 'xss_vulnerabilities', 'command_injection', 'hardcoded_secrets', 'crypto_issues', 'path_traversal', 'file_permissions', 'language_specific_checks']
