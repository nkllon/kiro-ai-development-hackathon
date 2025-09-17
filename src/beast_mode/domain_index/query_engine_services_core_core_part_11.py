from src.rm_ddd.core.health import ModuleHealth

def capability_search(self, capability: str) -> List[Domain]:
    """Find domains by capability or functionality with advanced matching"""
    with self._time_operation('capability_search'):
        self._ensure_indexes_built()
        try:
            matching_domains = set()
            capability_lower = capability.lower()
            if capability_lower in self._capability_index:
                matching_domains.update(self._capability_index[capability_lower])
            for indexed_capability, domain_names in self._capability_index.items():
                if capability_lower in indexed_capability:
                    matching_domains.update(domain_names)
            if self.registry_manager:
                all_domains = self.registry_manager.get_all_domains()
                for domain_name, domain in all_domains.items():
                    for requirement in domain.requirements:
                        if self._capability_matches(capability_lower, requirement.lower()):
                            matching_domains.add(domain_name)
                    tool_capabilities = [domain.tools.linter, domain.tools.formatter, domain.tools.validator]
                    tool_capabilities.extend(domain.tools.custom_tools.values())
                    for tool in tool_capabilities:
                        if tool and self._capability_matches(capability_lower, tool.lower()):
                            matching_domains.add(domain_name)
                    for indicator in domain.content_indicators:
                        if self._capability_matches(capability_lower, indicator.lower()):
                            matching_domains.add(domain_name)
            domains = []
            if self.registry_manager:
                all_domains = self.registry_manager.get_all_domains()
                for domain_name in matching_domains:
                    if domain_name in all_domains:
                        domains.append(all_domains[domain_name])
            domains.sort(key=lambda d: self._calculate_capability_relevance(d, capability_lower), reverse=True)
            return domains
        except Exception as e:
            self._handle_error(e, 'capability_search')
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

