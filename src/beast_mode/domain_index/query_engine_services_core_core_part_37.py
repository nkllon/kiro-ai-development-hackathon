
def _extract_relationship_info(self, query: str, entities: Dict[str, List[str]]) -> Dict[str, Any]:
    """Extract relationship information from query"""
    relationship_info = {'relationship_type': None, 'target_domain': None}
    if 'depend' in query:
        if 'circular' in query or 'cycle' in query:
            relationship_info['relationship_type'] = 'circular'
        elif 'transitive' in query:
            relationship_info['relationship_type'] = 'transitive_dependencies'
        else:
            relationship_info['relationship_type'] = 'dependencies'
    elif 'similar' in query or 'like' in query:
        relationship_info['relationship_type'] = 'similar'
    elif 'coupling' in query or 'coupled' in query:
        relationship_info['relationship_type'] = 'coupling_high'
    elif 'extract' in query:
        relationship_info['relationship_type'] = 'extraction_related'
    if entities['domain_names']:
        relationship_info['target_domain'] = entities['domain_names'][0]
    else:
        domain_matches = re.findall('\\b(\\w+(?:_domain)?)\\b', query)
        for match in domain_matches:
            if match.endswith('_domain') or match in ['core', 'test', 'api', 'data']:
                relationship_info['target_domain'] = match
                break
    return relationship_info
