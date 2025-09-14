from src.rm_ddd.core.health import ModuleHealth

        def domain_loader(domain_name: str) -> Optional[Domain]:
            return self._domains.get(domain_name)
        priority_domains = domain_names[:20]
        warmed_count = self._domain_cache.warm_domains(domain_loader, priority_domains)
        self.logger.debug(f'Warmed cache with {warmed_count} domains')
    except Exception as e:
        self.logger.warning(f'Failed to warm cache: {e}')

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

