
def _apply_filters(self, domain: Domain, filters: Dict[str, Any]) -> bool:
    """Apply filters to a domain"""
    for filter_key, filter_value in filters.items():
        if filter_key == 'category':
            if domain.metadata.demo_role != filter_value:
                return False
        elif filter_key == 'status':
            if domain.metadata.status != filter_value:
                return False
        elif filter_key == 'has_pattern':
            if not any((filter_value in pattern for pattern in domain.patterns)):
                return False
    return True
