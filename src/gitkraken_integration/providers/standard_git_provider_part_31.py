from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def delete_branch(self, name: str, force: bool=False) -> GitOperationResult:
        """Delete a branch"""
        start_time = time.time()
        try:
            args = ['branch']
            args.append('-D' if force else '-d')
            args.append(name)
            self._run_git_command(args)
            execution_time = int((time.time() - start_time) * 1000)
            return self._create_result(success=True, message=f"Deleted branch '{name}'", data={'branch_name': name, 'forced': force}, execution_time_ms=execution_time)
        except subprocess.CalledProcessError as e:
            execution_time = int((time.time() - start_time) * 1000)
            suggestions = []
            if 'not fully merged' in e.stderr:
                suggestions.extend([f"Branch '{name}' is not fully merged", 'Use force=True to delete anyway', 'Merge the branch first if you want to keep changes'])
            return self._create_result(success=False, message=f"Failed to delete branch '{name}': {e.stderr}", error_code='GIT_DELETE_BRANCH_FAILED', suggestions=suggestions, execution_time_ms=execution_time)
