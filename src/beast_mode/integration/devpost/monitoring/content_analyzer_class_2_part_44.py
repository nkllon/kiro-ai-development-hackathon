from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def _is_binary_file(self, file_path: Path) -> bool:
    """Check if file is binary."""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            return b'\x00' in chunk
    except Exception:
        return True
