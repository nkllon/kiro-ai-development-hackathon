
def _generate_template_suggestions(self, partial_query: str, partial_info: Dict[str, Any]) -> List[str]:
    """Generate template-based suggestions"""
    suggestions = []
    templates = ['find domains with {capability}', 'domains that depend on {domain}', 'domains similar to {domain}', 'domains in {category} category', 'domains with pattern {pattern}', 'analyze {domain} relationships', 'show {domain} dependencies', 'domains with high coupling', 'domains suitable for extraction', 'healthy domains in {category}', 'domains containing {content}', 'domains that can run {tool}']
    for template in templates:
        if any((word in partial_query for word in template.split() if word not in ['{capability}', '{domain}', '{category}', '{pattern}', '{content}', '{tool}'])):
            filled_template = template
            if '{domain}' in template and self.registry_manager:
                domains = list(self.registry_manager.get_all_domains().keys())[:3]
                for domain in domains:
                    suggestions.append(filled_template.replace('{domain}', domain))
            elif '{capability}' in template:
                capabilities = ['testing', 'linting', 'formatting', 'deployment']
                for cap in capabilities:
                    suggestions.append(filled_template.replace('{capability}', cap))
            elif '{category}' in template:
                categories = ['core', 'tools', 'infrastructure', 'demo']
                for cat in categories:
                    suggestions.append(filled_template.replace('{category}', cat))
            else:
                suggestions.append(filled_template)
    return suggestions
