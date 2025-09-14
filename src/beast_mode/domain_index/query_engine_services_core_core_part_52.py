from src.rm_ddd.core.health import ModuleHealth

def get_query_stats(self) -> Dict[str, Any]:
    """Get query engine statistics"""
    return {'total_queries': self.query_count, 'pattern_searches': self.pattern_searches, 'content_searches': self.content_searches, 'natural_language_queries': self.nl_queries, 'average_query_time_ms': self.total_query_time / max(self.query_count, 1), 'indexes_built': self._index_built, 'pattern_index_size': len(self._pattern_index), 'content_index_size': len(self._content_index), 'capability_index_size': len(self._capability_index), 'cache_stats': self.get_cache_stats()}
