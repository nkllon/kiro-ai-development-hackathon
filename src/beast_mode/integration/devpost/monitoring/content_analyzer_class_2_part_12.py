from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def _get_content_type(self, file_path: Path) -> Optional[str]:
        """Get MIME type of file."""
        return mimetypes.guess_type(str(file_path))[0]
