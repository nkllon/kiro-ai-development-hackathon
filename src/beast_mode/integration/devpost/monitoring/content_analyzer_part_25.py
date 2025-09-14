from datetime import datetime
from typing import Dict, List, Any

    def _get_content_type(self, file_path: Path) -> Optional[str]:
        """Get MIME type of file."""
        return mimetypes.guess_type(str(file_path))[0]
