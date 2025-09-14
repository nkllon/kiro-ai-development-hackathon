
def get_configuration(self) -> Dict[str, Any]:
    """Get module configuration."""
    return {'max_file_size': 100 * 1024 * 1024, 'supported_extensions': ['.py', '.md', '.json', '.yaml'], 'checksum_algorithm': 'sha256'}
