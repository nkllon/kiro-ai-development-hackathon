
def _generate_preview_id(self) -> str:
    """Generate unique preview ID"""
    import uuid
    return f'preview_{uuid.uuid4().hex[:8]}'
