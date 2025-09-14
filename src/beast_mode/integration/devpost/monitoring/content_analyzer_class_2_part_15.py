from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def _get_media_category(self, file_path: Path) -> str:
        """Get media file category."""
        suffix = file_path.suffix.lower()
        if suffix in {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}:
            return 'image'
        elif suffix in {'.mp4', '.mov', '.avi', '.webm', '.mkv'}:
            return 'video'
        elif suffix in {'.pdf', '.doc', '.docx'}:
            return 'document'
        else:
            return 'other'
