
def _get_popular_query_templates(self) -> List[str]:
    """Get popular query templates for empty queries"""
    templates = ['find domains with testing capabilities', 'show all core domains', 'domains that depend on core_domain', 'domains with *.py patterns', 'analyze domain relationships', 'healthy domains', 'domains suitable for extraction', 'domains with high complexity', 'similar domains to test_domain', 'domains in infrastructure category']
    return templates[:self.suggestion_limit]
