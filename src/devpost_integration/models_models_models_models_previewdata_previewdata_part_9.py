
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information"""
        return {'module_id': 'previewdata', 'version': '1.0.0', 'description': 'Preview data management and generation with comprehensive functionality', 'preview_id': self.preview_id, 'content_type': self.preview_data.get('content_type', 'text'), 'status': self.preview_data.get('status', 'active')}
