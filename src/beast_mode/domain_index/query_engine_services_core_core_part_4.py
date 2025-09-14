
def _build_search_indexes(self):
    """Build search indexes for efficient querying"""
    with self._time_operation('build_indexes'):
        try:
            domains = self.registry_manager.get_all_domains()
            self._pattern_index = {}
            self._content_index = {}
            self._capability_index = {}
            for domain_name, domain in domains.items():
                for pattern in domain.patterns:
                    pattern_key = pattern.lower()
                    if pattern_key not in self._pattern_index:
                        self._pattern_index[pattern_key] = set()
                    self._pattern_index[pattern_key].add(domain_name)
                for indicator in domain.content_indicators:
                    indicator_key = indicator.lower()
                    if indicator_key not in self._content_index:
                        self._content_index[indicator_key] = set()
                    self._content_index[indicator_key].add(domain_name)
                capabilities = domain.requirements + [domain.tools.linter, domain.tools.formatter]
                for capability in capabilities:
                    if capability:
                        cap_key = capability.lower()
                        if cap_key not in self._capability_index:
                            self._capability_index[cap_key] = set()
                        self._capability_index[cap_key].add(domain_name)
            self._index_built = True
            self.logger.info(f'Built search indexes for {len(domains)} domains')
        except Exception as e:
            self._handle_error(e, 'build_indexes')
