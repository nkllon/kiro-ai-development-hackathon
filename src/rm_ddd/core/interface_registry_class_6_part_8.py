from src.rm_ddd.core.health import ModuleHealth

    def save_registry(self):
        """Save registry to persistent storage"""
        try:
            data = {
                'interfaces': {
                    interface_id: {
                        'interface_id': interface.interface_id,
                        'interface_name': interface.interface_name,
                        'interface_type': interface.interface_type.value,
                        'version': interface.version,
                        'status': interface.status.value,
                        'description': interface.description,
                        'domain_terms': interface.domain_terms,
                        'capabilities': interface.capabilities,
                        'dependencies': interface.dependencies,
                        'file_path': interface.file_path,
                        'created_at': interface.created_at.isoformat(),
                        'last_modified': interface.last_modified.isoformat(),
                        'created_by': interface.created_by,
                        'usage_count': interface.usage_count,
                        'tags': interface.tags,
                        'examples': interface.examples,
                        'documentation_url': interface.documentation_url
                    }
                    for interface_id, interface in self.interfaces.items()
                },
                'domain_index': self.domain_index
            }
            with open(self.registry_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving registry: {e}")
    