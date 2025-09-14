
def content_search(self, content_indicator: str) -> List[Domain]:
    """Search domains by content indicators"""
    with self._time_operation('content_search'):
        self.content_searches += 1
        self._ensure_indexes_built()
        try:
            matching_domains = set()
            indicator_lower = content_indicator.lower()
            if indicator_lower in self._content_index:
                matching_domains.update(self._content_index[indicator_lower])
            for indexed_indicator, domain_names in self._content_index.items():
                if indicator_lower in indexed_indicator or indexed_indicator in indicator_lower:
                    matching_domains.update(domain_names)
            domains = []
            if self.registry_manager:
                all_domains = self.registry_manager.get_all_domains()
                for domain_name in matching_domains:
                    if domain_name in all_domains:
                        domains.append(all_domains[domain_name])
            return domains
        except Exception as e:
            self._handle_error(e, 'content_search')
            return []
