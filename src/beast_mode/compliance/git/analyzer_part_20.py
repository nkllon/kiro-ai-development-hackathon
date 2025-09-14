from src.rm_ddd.core.health import ModuleHealth

    def _get_default_task_patterns(self) -> Dict[str, List[str]]:
        """Get default patterns for mapping files to tasks."""
        return {'compliance_infrastructure': ['src/beast_mode/compliance/*', 'tests/*compliance*'], 'git_analysis': ['src/beast_mode/compliance/git/*', 'tests/*git*'], 'rdi_validation': ['src/beast_mode/compliance/rdi/*', 'tests/*rdi*'], 'rm_validation': ['src/beast_mode/compliance/rm/*', 'tests/*rm*'], 'reporting': ['src/beast_mode/compliance/reporting/*', 'tests/*report*'], 'documentation': ['docs/*', '*.md', 'README*'], 'tests': ['tests/*', '*test*.py']}
