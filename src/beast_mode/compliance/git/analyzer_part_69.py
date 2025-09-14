
def _file_matches_pattern(self, file_path: str, pattern: str) -> bool:
    """Check if a file path matches a given pattern."""
    import fnmatch
from src.rm_ddd.core.health import ModuleHealth

    return fnmatch.fnmatch(file_path, pattern)
