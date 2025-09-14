from src.rm_ddd.core.health import ModuleHealth

def __init__(self, registry_path: Optional[str]=None, config: Optional[Dict[str, Any]]=None):
    super().__init__('domain_registry_manager', config)
    self.config_obj = get_config()
    self.registry_path = Path(registry_path or self.config_obj.get('registry_path'))
    self.backup_dir = Path(self.config_obj.get('registry_backup_dir'))
    self._raw_registry_data = {}
    self._domains = {}
    self._registry_loaded = False
    self._last_load_time = None
    self._registry_version = None
    cache_config = self.config.get('cache', {})
    index_config = self.config.get('index', {})
    validator_config = self.config.get('validator', {})
    self._cache = DomainCache(cache_config)
    self._domain_cache = DomainSpecificCache(self._cache)
    self._index = DomainIndex(index_config)
    self._validator = DomainValidator(validator_config)
    self.load_count = 0
    self.validation_count = 0
    self.logger.info(f'Initialized DomainRegistryManager with registry: {self.registry_path}')
    self.logger.info('Initialized caching, indexing, and validation systems')
