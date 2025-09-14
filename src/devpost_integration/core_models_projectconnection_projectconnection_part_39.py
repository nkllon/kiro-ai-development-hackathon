
def get_configuration(self) -> Dict[str, Any]:
    """Get module configuration."""
    return {'max_metadata_size': 1000, 'required_fields': ['title', 'description'], 'optional_fields': ['tags', 'category', 'difficulty']}
