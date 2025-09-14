from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def __init__(self, repo_path: str='.'):
    super().__init__(repo_path)
    self.git_executable = self._find_git_executable()
    self._validate_repository()
