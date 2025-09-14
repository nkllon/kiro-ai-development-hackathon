from src.rm_ddd.core.registry import register_module

def _is_valid_media_file(self, file_path: Path) -> bool:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """
        Check if file is a valid media file type.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file type is supported
        """
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.pdf', '.doc', '.docx', '.txt', '.md', '.rtf', '.zip', '.tar', '.gz', '.rar'}
    return file_path.suffix.lower() in valid_extensions
