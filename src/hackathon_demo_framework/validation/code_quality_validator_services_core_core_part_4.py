from src.rm_ddd.core.health import ModuleHealth

def _discover_source_files(self) -> List[Path]:
    """Discover Python source files to analyze."""
    source_files = []
    for pattern in self.source_patterns:
        files = list(self.project_path.rglob(pattern))
        source_files.extend(files)
    filtered_files = []
    for file_path in source_files:
        should_exclude = False
        for exclude_pattern in self.exclude_patterns:
            if file_path.match(exclude_pattern):
                should_exclude = True
                break
        if not should_exclude and file_path.is_file():
            filtered_files.append(file_path)
    return filtered_files
