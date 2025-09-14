from src.rm_ddd.core.health import ModuleHealth

class MapchangestotasksClass:
    """Auto-generated class for functions."""

    def map_changes_to_tasks(self, file_changes: FileChangeAnalysis, task_patterns: Optional[Dict[str, List[str]]]=None) -> Dict[str, List[str]]:
    """
    Map file changes to potential task completions based on patterns.

    Args:
    file_changes: The file change analysis results
    task_patterns: Optional mapping of task patterns to file patterns

    Returns:
    Dictionary mapping task identifiers to affected files
    """
    self.logger.info('Mapping file changes to potential task completions')
    if task_patterns is None:
    task_patterns = self._get_default_task_patterns()
    task_mapping = {}
    all_changed_files = file_changes.files_added + file_changes.files_modified + file_changes.files_deleted
    for task_id, patterns in task_patterns.items():
    matching_files = []
    for file_path in all_changed_files:
    for pattern in patterns:
    if self._file_matches_pattern(file_path, pattern):
    matching_files.append(file_path)
    break
    if matching_files:
    task_mapping[task_id] = sorted(list(set(matching_files)))
    self.logger.info(f'Mapped changes to {len(task_mapping)} potential tasks')
    return task_mapping

    def register_module(self, registry):
    """Register module with registry."""
    metadata = self.get_interface_metadata()
    if hasattr(registry, 'register'):
    registry.register(metadata)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

