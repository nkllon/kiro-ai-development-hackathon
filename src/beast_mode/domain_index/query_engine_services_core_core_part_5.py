
def natural_language_query(self, query: str) -> QueryResult:
    """Process natural language queries about domains with advanced NLP"""
    with self._time_operation('natural_language_query'):
        start_time = time.time()
        self.nl_queries += 1
        try:
            parsed_query = self._parse_natural_language_query(query)
            domains = self._execute_parsed_query(parsed_query)
            if parsed_query.get('filters'):
                domains = self._apply_parsed_filters(domains, parsed_query['filters'])
            suggestions = self._generate_intelligent_suggestions(query, parsed_query, domains)
            relevance_scores = self._calculate_enhanced_relevance_scores(domains, parsed_query)
            domains.sort(key=lambda d: (relevance_scores.get(d.name, 0.0), d.name), reverse=True)
            domains = self._rank_and_filter_results(domains, parsed_query)
            domains = domains[:self.max_results]
            query_time = (time.time() - start_time) * 1000
            return QueryResult(domains=domains, total_count=len(domains), query_time_ms=query_time, suggestions=suggestions, filters_applied={'intent': parsed_query.get('intent', 'unknown'), 'keywords': parsed_query.get('keywords', []), 'entities': parsed_query.get('entities', {}), 'filters': parsed_query.get('filters', {}), 'query_type': parsed_query.get('query_type', 'general')}, relevance_scores=relevance_scores)
        except Exception as e:
            self._handle_error(e, 'natural_language_query')
            raise QueryEngineError(f'Natural language query failed: {str(e)}')
