
def _determine_intent(self, query: str) -> str:
    """Determine the intent of the natural language query"""
    if any((word in query for word in ['pattern', 'file', 'path', '*.py', 'src/'])):
        return 'pattern_search'
    elif any((word in query for word in ['contains', 'content', 'indicator', 'includes'])):
        return 'content_search'
    elif any((word in query for word in ['tool', 'capability', 'can', 'does', 'supports', 'run'])):
        return 'capability_search'
    else:
        return 'general_search'
