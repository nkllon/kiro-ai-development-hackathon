
def _pattern_matches(self, search_pattern: str, indexed_pattern: str) -> bool:
    """Check if search pattern matches indexed pattern"""
    if '*' in search_pattern:
        regex_pattern = search_pattern.replace('*', '.*')
        return bool(re.search(regex_pattern, indexed_pattern))
    return search_pattern in indexed_pattern
