from src.rm_ddd.core.health import ModuleHealth

def get_configuration(self) -> Dict[str, Any]:
    """Get module configuration."""
    return {'max_name_length': 100, 'required_fields': ['id', 'name', 'email'], 'valid_roles': ['admin', 'member', 'viewer'], 'max_permissions': 20}
