from src.rm_ddd.core.registry import register_module

def _is_release_tag(self, tag_name: str) -> bool:
    """Check if tag name indicates a release."""
    release_patterns = ['^v?\\d+\\.\\d+\\.\\d+', '^release', '^r\\d+']
    return any((re.match(pattern, tag_name.lower()) for pattern in release_patterns))
