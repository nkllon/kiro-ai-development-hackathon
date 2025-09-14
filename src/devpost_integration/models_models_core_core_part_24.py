
def get_configuration(self) -> Dict[str, Any]:
    """Get module configuration"""
    return {'preview_id': self.preview_id, 'content_type': self.preview_data.get('content_type', 'text'), 'status': self.preview_data.get('status', 'active'), 'access_count': self.preview_data.get('access_count', 0)}
