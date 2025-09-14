from src.rm_ddd.core.health import ModuleHealth

def _capability_matches(self, search_capability: str, target_capability: str) -> bool:
    """Check if a search capability matches a target capability"""
    if search_capability == target_capability:
        return True
    if search_capability in target_capability or target_capability in search_capability:
        return True
    capability_synonyms = {'test': ['testing', 'pytest', 'unittest', 'test_', '_test'], 'lint': ['linting', 'pylint', 'flake8', 'ruff'], 'format': ['formatting', 'black', 'autopep8', 'yapf'], 'type': ['typing', 'mypy', 'type_check', 'annotations'], 'doc': ['documentation', 'docs', 'sphinx', 'readme'], 'build': ['building', 'setup', 'packaging', 'wheel'], 'deploy': ['deployment', 'docker', 'kubernetes', 'helm'], 'monitor': ['monitoring', 'logging', 'metrics', 'observability'], 'security': ['sec', 'auth', 'authentication', 'authorization'], 'api': ['rest', 'graphql', 'endpoint', 'service'], 'data': ['database', 'db', 'sql', 'nosql', 'storage'], 'ml': ['machine_learning', 'ai', 'model', 'training'], 'web': ['http', 'server', 'client', 'browser'], 'cli': ['command', 'terminal', 'console', 'script']}
    for base_capability, synonyms in capability_synonyms.items():
        if search_capability == base_capability or search_capability in synonyms:
            if target_capability == base_capability or any((syn in target_capability for syn in synonyms)):
                return True
        if target_capability == base_capability or target_capability in synonyms:
            if search_capability == base_capability or any((syn in search_capability for syn in synonyms)):
                return True
    return False
