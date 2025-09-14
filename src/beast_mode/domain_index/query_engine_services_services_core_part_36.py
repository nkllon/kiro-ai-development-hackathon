
def _extract_query_modifiers(self, query: str) -> List[str]:
    """Extract query modifiers (sorting, limiting, etc.)"""
    modifiers = []
    if re.search('\\bsort\\w*\\s+by\\s+(\\w+)\\b', query):
        sort_field = re.findall('\\bsort\\w*\\s+by\\s+(\\w+)\\b', query)[0]
        modifiers.append(f'sort_by:{sort_field}')
    if 'ascending' in query or 'asc' in query:
        modifiers.append('order:asc')
    elif 'descending' in query or 'desc' in query:
        modifiers.append('order:desc')
    limit_matches = re.findall('\\b(?:top|first|limit)\\s+(\\d+)\\b', query)
    if limit_matches:
        modifiers.append(f'limit:{limit_matches[0]}')
    return modifiers
