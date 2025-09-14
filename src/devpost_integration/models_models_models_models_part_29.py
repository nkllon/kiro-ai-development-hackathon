
    def _get_default_preview_data(self) -> Dict[str, Any]:
        """Get default preview data"""
        return {'preview_id': self._generate_preview_id(), 'content_type': 'text', 'title': '', 'description': '', 'thumbnail_url': '', 'preview_url': '', 'metadata': {}, 'generated_at': datetime.now().isoformat(), 'expires_at': None, 'access_count': 0, 'status': 'active'}
