from src.rm_ddd.core.health import ModuleHealth

def _extract_package_json_metadata(self) -> Optional[Dict[str, Any]]:
    """Extract metadata from package.json."""
    package_json_path = self.project_root / 'package.json'
    if not package_json_path.exists():
        return None
    try:
        with open(package_json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None
