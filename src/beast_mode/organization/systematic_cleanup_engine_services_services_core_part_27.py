from src.rm_ddd.core.health import ModuleHealth

def _load_systematic_structure(self) -> Dict[str, Any]:
    """Load systematic organizational structure standards"""
    return {'core_directories': ['.kiro', 'src', 'tests', 'docs', 'logs'], 'archive_directories': ['archive/development-artifacts', 'archive/research', 'archive/media'], 'systematic_directories': ['docs/systematic', 'scripts', 'config']}
