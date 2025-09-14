from src.rm_ddd.core.health import ModuleHealth

def __init__(self, registry_manager=None, config: Optional[Dict[str, Any]]=None):
    super().__init__('domain_query_engine', config)
    self.config_obj = get_config()
    self.query_timeout = self.config_obj.get('query_timeout_seconds', 30)
    self.max_results = self.config_obj.get('max_query_results', 100)
    self.suggestion_limit = self.config_obj.get('query_suggestion_limit', 5)
    self.registry_manager = registry_manager
    self.query_count = 0
    self.total_query_time = 0.0
    self.pattern_searches = 0
    self.content_searches = 0
    self.nl_queries = 0
    self._pattern_index = {}
    self._content_index = {}
    self._capability_index = {}
    self._index_built = False
    self.logger.info('Initialized DomainQueryEngine')
