from datetime import datetime
from typing import Dict, List, Any

def _is_media_file(self, file_path: Path) -> bool:
    """Check if file is a media file."""
    media_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.avi', '.pdf', '.webp', '.svg'}
    return file_path.suffix.lower() in media_extensions
