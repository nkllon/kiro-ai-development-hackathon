from src.rm_ddd.core.health import ModuleHealth

class GetinterfacegovernancereportClass:
    """Auto-generated class for functions."""

    def get_interface_governance_report(self) -> Dict[str, Any]:
    """Generate interface governance report"""
    total_interfaces = len(self.interfaces)
    active_interfaces = len([i for i in self.interfaces.values() if i.status == InterfaceStatus.ACTIVE])
    deprecated_interfaces = len([i for i in self.interfaces.values() if i.status == InterfaceStatus.DEPRECATED])

    # Count by type
    type_counts = {}
    for interface in self.interfaces.values():
    type_name = interface.interface_type.value
    type_counts[type_name] = type_counts.get(type_name, 0) + 1

    # Count by domain
    domain_counts = {}
    for interface in self.interfaces.values():
    for term in interface.domain_terms:
    domain_counts[term] = domain_counts.get(term, 0) + 1

    return {
    'total_interfaces': total_interfaces,
    'active_interfaces': active_interfaces,
    'deprecated_interfaces': deprecated_interfaces,
    'type_distribution': type_counts,
    'domain_distribution': domain_counts,
    'most_used_terms': sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    }

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

