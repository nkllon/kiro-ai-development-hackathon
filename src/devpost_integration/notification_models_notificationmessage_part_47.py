from src.rm_ddd.core.health import ModuleHealth

def get_configuration(self) -> Dict[str, Any]:
    """Get module configuration."""
    return {'max_title_length': 200, 'max_content_length': 5000, 'max_recipients': 100, 'valid_priorities': ['low', 'normal', 'high', 'urgent'], 'valid_statuses': ['pending', 'sent', 'failed', 'cancelled']}
