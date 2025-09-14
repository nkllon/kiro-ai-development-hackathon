from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def _is_documentation_file(self, file_path: Path) -> bool:
    """Check if file is a documentation file."""
    doc_patterns = ['readme', 'changelog', 'license', 'contributing', 'docs']
    filename_lower = file_path.name.lower()
    return any((pattern in filename_lower for pattern in doc_patterns)) or file_path.suffix.lower() in {'.md', '.txt', '.rst', '.adoc'} or 'docs/' in str(file_path).lower()
