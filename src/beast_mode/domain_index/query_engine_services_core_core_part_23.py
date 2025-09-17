from src.rm_ddd.core.health import ModuleHealth

def suggest_query_corrections(self, query: str) -> List[str]:
    """Suggest corrections for potentially misspelled or ambiguous queries"""
    with self._time_operation('suggest_query_corrections'):
        try:
            corrections = []
            query_lower = query.lower()
            corrections_map = {'dependancies': 'dependencies', 'dependant': 'dependent', 'similiar': 'similar', 'analize': 'analyze', 'analisis': 'analysis', 'capabilty': 'capability', 'capabilties': 'capabilities', 'patern': 'pattern', 'paterns': 'patterns', 'domian': 'domain', 'domians': 'domains'}
            corrected_query = query_lower
            for misspelling, correction in corrections_map.items():
                if misspelling in corrected_query:
                    corrected_query = corrected_query.replace(misspelling, correction)
                    corrections.append(corrected_query)
            alternative_phrasings = {'find': ['show', 'list', 'get', 'search for'], 'domains with': ['domains that have', 'domains containing'], 'depends on': ['requires', 'needs', 'uses'], 'similar to': ['like', 'resembling', 'comparable to']}
            for original, alternatives in alternative_phrasings.items():
                if original in query_lower:
                    for alt in alternatives:
                        alt_query = query_lower.replace(original, alt)
                        corrections.append(alt_query)
            unique_corrections = list(set(corrections))
            return unique_corrections[:self.suggestion_limit]
        except Exception as e:
            self._handle_error(e, 'suggest_query_corrections')
            return []

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

