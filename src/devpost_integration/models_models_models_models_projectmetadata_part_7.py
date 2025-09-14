
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information"""
        return {'module_id': 'projectmetadata', 'version': '1.0.0', 'description': 'Project metadata management with comprehensive functionality', 'metadata_count': len(self.metadata), 'version': self.version}
