
def pattern_search(self, pattern: str) -> List[Domain]:
    """Search domains by file patterns"""
    with self._time_operation('pattern_search'):
        self.pattern_searches += 1
        self._ensure_indexes_built()
        try:
            matching_domains = set()
            pattern_lower = pattern.lower()
            if pattern_lower in self._pattern_index:
                matching_domains.update(self._pattern_index[pattern_lower])
            for indexed_pattern, domain_names in self._pattern_index.items():
                if self._pattern_matches(pattern_lower, indexed_pattern):
                    matching_domains.update(domain_names)
            domains = []
            if self.registry_manager:
                all_domains = self.registry_manager.get_all_domains()
                for domain_name in matching_domains:
                    if domain_name in all_domains:
                        domains.append(all_domains[domain_name])
            return domains
        except Exception as e:
            self._handle_error(e, 'pattern_search')
            return []
