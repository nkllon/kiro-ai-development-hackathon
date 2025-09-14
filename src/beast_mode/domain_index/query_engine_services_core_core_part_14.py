from src.rm_ddd.core.health import ModuleHealth

def _pattern_suggests_capability(self, pattern: str, capability: str) -> bool:
    """Check if a file pattern suggests a particular capability"""
    pattern_lower = pattern.lower()
    capability_patterns = {'test': ['test_', '_test', 'tests/', '/test/', '*.test.*'], 'doc': ['docs/', '/doc/', '*.md', '*.rst', 'readme'], 'config': ['config', 'settings', '*.yaml', '*.yml', '*.json', '*.toml'], 'script': ['scripts/', '*.sh', '*.py', 'bin/'], 'web': ['*.html', '*.css', '*.js', 'templates/', 'static/'], 'data': ['*.sql', '*.db', 'data/', 'migrations/'], 'api': ['api/', 'endpoints/', 'routes/', 'handlers/'], 'cli': ['cli/', 'commands/', '*.py']}
    if capability in capability_patterns:
        return any((cap_pattern in pattern_lower for cap_pattern in capability_patterns[capability]))
    return False
