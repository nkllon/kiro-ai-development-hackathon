
def relationship_query(self, domain: str, relationship_type: str) -> List[Domain]:
    """Query domain relationships with advanced analysis"""
    with self._time_operation('relationship_query'):
        try:
            if not self.registry_manager:
                return []
            target_domain = self.registry_manager.get_domain(domain)
            all_domains = self.registry_manager.get_all_domains()
            related_domains = []
            if relationship_type == 'dependencies':
                for dep_name in target_domain.dependencies:
                    if dep_name in all_domains:
                        related_domains.append(all_domains[dep_name])
            elif relationship_type == 'dependents':
                for domain_name, domain_obj in all_domains.items():
                    if domain in domain_obj.dependencies:
                        related_domains.append(domain_obj)
            elif relationship_type == 'transitive_dependencies':
                related_domains = self._get_transitive_dependencies(domain, all_domains)
            elif relationship_type == 'transitive_dependents':
                related_domains = self._get_transitive_dependents(domain, all_domains)
            elif relationship_type == 'similar':
                related_domains = self._find_similar_domains(target_domain, all_domains)
            elif relationship_type == 'circular':
                circular_chains = self._detect_circular_dependencies(domain, all_domains)
                circular_domain_names = set()
                for chain in circular_chains:
                    circular_domain_names.update(chain)
                circular_domain_names.discard(domain)
                for domain_name in circular_domain_names:
                    if domain_name in all_domains:
                        related_domains.append(all_domains[domain_name])
            elif relationship_type == 'coupling_high':
                related_domains = self._find_high_coupling_domains(target_domain, all_domains)
            elif relationship_type == 'extraction_related':
                related_domains = self._find_extraction_related_domains(target_domain, all_domains)
            return related_domains
        except Exception as e:
            self._handle_error(e, 'relationship_query')
            return []
