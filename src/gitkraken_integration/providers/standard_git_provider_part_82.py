from datetime import datetime
from typing import Dict, List, Any

def __init__(self, repo_path: str='.'):
    super().__init__(repo_path)
    self.git_executable = self._find_git_executable()
    self._validate_repository()
