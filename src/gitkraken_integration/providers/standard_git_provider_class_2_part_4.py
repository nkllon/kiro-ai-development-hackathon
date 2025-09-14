from src.rm_ddd.core.registry import register_module

    def __init__(self, repo_path: str='.'):
        super().__init__(repo_path)
        self.git_executable = self._find_git_executable()
        self._validate_repository()
