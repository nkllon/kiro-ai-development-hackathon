
def load_registry(self) -> bool:
    """Load the domain registry from JSON file"""
    with self._time_operation('load_registry'):
        try:
            if not self.registry_path.exists():
                raise DomainRegistryError(f'Registry file not found: {self.registry_path}')
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                self._raw_registry_data = json.load(f)
            self._parse_domains()
            self._registry_loaded = True
            self._last_load_time = datetime.now()
            self.load_count += 1
            self._clear_cache()
            self._index.build_index(self._domains)
            self._warm_cache()
            self.logger.info(f'Successfully loaded {len(self._domains)} domains from registry')
            return True
        except json.JSONDecodeError as e:
            error_msg = f'Invalid JSON in registry file: {e}'
            self.logger.error(error_msg)
            raise RegistryCorruptionError(str(self.registry_path), error_msg)
        except Exception as e:
            self._handle_error(e, 'load_registry')
            return False
