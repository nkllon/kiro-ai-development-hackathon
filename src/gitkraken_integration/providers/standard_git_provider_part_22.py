from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def get_status(self) -> GitOperationResult:
        """Get comprehensive repository status"""
        start_time = time.time()
        try:
            result = self._run_git_command(['status', '--porcelain=v1'])
            files = self._parse_status_output(result.stdout)
            branch_result = self._run_git_command(['branch', '--show-current'])
            current_branch = branch_result.stdout.strip()
            ahead_behind = self._get_ahead_behind_counts(current_branch)
            is_clean = len(files) == 0
            execution_time = int((time.time() - start_time) * 1000)
            return self._create_result(success=True, message=f"Repository status retrieved successfully. {('Clean' if is_clean else 'Has changes')}", data={'clean': is_clean, 'files': [file.__dict__ for file in files], 'branch': current_branch, 'ahead_behind': ahead_behind, 'total_files': len(files), 'staged_files': len([f for f in files if f.staged]), 'modified_files': len([f for f in files if f.working_tree_status == 'M' or (f.status == 'M' and (not f.staged))]), 'untracked_files': len([f for f in files if f.status == '??'])}, execution_time_ms=execution_time)
        except subprocess.CalledProcessError as e:
            execution_time = int((time.time() - start_time) * 1000)
            return self._create_result(success=False, message=f'Failed to get repository status: {e.stderr}', error_code='GIT_STATUS_FAILED', suggestions=["Ensure you're in a valid git repository", 'Check git installation and permissions'], execution_time_ms=execution_time)

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

