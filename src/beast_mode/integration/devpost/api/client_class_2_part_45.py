from src.rm_ddd.core.registry import register_module

def _get_content_type(self, file_path: Path) -> str:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Get content type for file upload."""
    suffix = file_path.suffix.lower()
    content_types = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.gif': 'image/gif', '.mp4': 'video/mp4', '.mov': 'video/quicktime', '.avi': 'video/x-msvideo', '.pdf': 'application/pdf', '.txt': 'text/plain', '.md': 'text/markdown'}
    return content_types.get(suffix, 'application/octet-stream')
