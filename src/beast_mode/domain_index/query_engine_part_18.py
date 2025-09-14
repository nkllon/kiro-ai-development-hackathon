from src.rm_ddd.core.health import ModuleHealth

def suggest_queries(self, partial_query: str) -> List[str]:
    """Suggest query completions with advanced NLP"""
    with self._time_operation('suggest_queries'):
        try:
            suggestions = []
            partial_lower = partial_query.lower().strip()
            if len(partial_lower) < 2:
                return self._get_popular_query_templates()
            partial_parsed = self._parse_partial_query(partial_lower)
            suggestions.extend(self._generate_contextual_suggestions(partial_lower, partial_parsed))
            suggestions.extend(self._generate_completion_suggestions(partial_lower))
            suggestions.extend(self._generate_template_suggestions(partial_lower, partial_parsed))
            seen = set()
            unique_suggestions = []
            for suggestion in suggestions:
                if suggestion not in seen:
                    seen.add(suggestion)
                    unique_suggestions.append(suggestion)
            return unique_suggestions[:self.suggestion_limit]
        except Exception as e:
            self._handle_error(e, 'suggest_queries')
            return []
