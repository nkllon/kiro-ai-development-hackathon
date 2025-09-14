
def get_configuration(self) -> Dict[str, Any]:
    """Get module configuration"""
    return {'version': self.version, 'auto_validation_enabled': True, 'metadata_schema_enforced': True, 'logging_level': 'INFO'}
