from src.rm_ddd.core.health import ModuleHealth

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

