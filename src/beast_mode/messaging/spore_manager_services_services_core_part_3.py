from src.rm_ddd.core.health import ModuleHealth

def _get_spore_paths(self, spore_name: str) -> Tuple[Path, Path]:
    """Get metadata and content file paths for a spore"""
    metadata_path = self.metadata_dir / f'{spore_name}.json'
    content_path = self.content_dir / f'{spore_name}.py'
    return (metadata_path, content_path)
