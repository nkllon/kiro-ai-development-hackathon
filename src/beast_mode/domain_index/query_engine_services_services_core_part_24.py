
def explain_query_results(self, query: str, results: QueryResult) -> Dict[str, Any]:
    """Explain why certain results were returned for a query"""
    with self._time_operation('explain_query_results'):
        try:
            explanation = {'query_interpretation': {}, 'matching_strategy': '', 'result_ranking': {}, 'suggestions_for_improvement': []}
            parsed_query = self._parse_natural_language_query(query)
            explanation['query_interpretation'] = {'detected_intent': parsed_query.get('intent'), 'extracted_keywords': parsed_query.get('keywords'), 'identified_entities': parsed_query.get('entities'), 'query_type': parsed_query.get('query_type')}
            intent = parsed_query.get('intent', 'general_search')
            if intent == 'pattern_search':
                explanation['matching_strategy'] = 'Searched for domains with matching file patterns'
            elif intent == 'capability_search':
                explanation['matching_strategy'] = 'Searched for domains with matching capabilities or tools'
            elif intent == 'content_search':
                explanation['matching_strategy'] = 'Searched for domains with matching content indicators'
            else:
                explanation['matching_strategy'] = 'Performed combined search across patterns, content, and capabilities'
            if results.domains:
                top_domain = results.domains[0]
                relevance_score = results.relevance_scores.get(top_domain.name, 0.0)
                explanation['result_ranking'] = {'top_result': top_domain.name, 'relevance_score': relevance_score, 'ranking_factors': self._explain_relevance_factors(top_domain, parsed_query)}
            if len(results.domains) == 0:
                explanation['suggestions_for_improvement'] = ['Try using broader search terms', 'Check spelling of domain names or capabilities', 'Use wildcard patterns like *.py or src/**', 'Try searching for related concepts or synonyms']
            elif len(results.domains) > 50:
                explanation['suggestions_for_improvement'] = ['Add more specific filters to narrow results', "Include category filters like 'in core category'", "Add status filters like 'healthy domains'", 'Use more specific keywords or patterns']
            return explanation
        except Exception as e:
            self._handle_error(e, 'explain_query_results')
            return {}
