from src.rm_ddd.core.health import ModuleHealth

def complex_query(self, query_spec: Dict[str, Any]) -> QueryResult:
    """Execute complex structured queries"""
    with self._time_operation('complex_query'):
        start_time = time.time()
        try:
            patterns = query_spec.get('patterns', [])
            content_indicators = query_spec.get('content_indicators', [])
            capabilities = query_spec.get('capabilities', [])
            filters = query_spec.get('filters', {})
            all_results = set()
            for pattern in patterns:
                domains = self.pattern_search(pattern)
                all_results.update((d.name for d in domains))
            for indicator in content_indicators:
                domains = self.content_search(indicator)
                all_results.update((d.name for d in domains))
            for capability in capabilities:
                domains = self.capability_search(capability)
                all_results.update((d.name for d in domains))
            final_domains = []
            if self.registry_manager:
                all_domains = self.registry_manager.get_all_domains()
                for domain_name in all_results:
                    if domain_name in all_domains:
                        domain = all_domains[domain_name]
                        if self._apply_query_filters(domain, filters):
                            final_domains.append(domain)
            query_time = (time.time() - start_time) * 1000
            return QueryResult(domains=final_domains[:self.max_results], total_count=len(final_domains), query_time_ms=query_time, filters_applied=filters)
        except Exception as e:
            self._handle_error(e, 'complex_query')
            raise QueryEngineError(f'Complex query failed: {str(e)}')
