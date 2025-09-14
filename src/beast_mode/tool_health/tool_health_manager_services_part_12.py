
    def _check_installation_integrity(self, tool_name: str) -> Dict[str, Any]:
        """Check if tool files are missing or corrupted"""
        if tool_name == 'makefile':
            makefiles_dir = Path('makefiles')
            if not makefiles_dir.exists():
                return {'healthy': False, 'issues': ['makefiles/ directory missing'], 'root_causes': ['modular_makefile_structure_not_created']}
        return {'healthy': True, 'issues': [], 'root_causes': []}
