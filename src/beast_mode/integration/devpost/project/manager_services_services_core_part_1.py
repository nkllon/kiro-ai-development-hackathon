
def __init__(self, project_root: Optional[Path]=None):
    """Initialize project manager.
        
        Args:
            project_root: Root directory of the project. If None, uses current directory.
        """
    self.project_root = project_root or Path.cwd()
    self.config_manager = DevpostConfigManager(self.project_root)
    self._current_connection: Optional[ProjectConnection] = None
    self._active_project_id: Optional[str] = None
    self._load_current_connection()
