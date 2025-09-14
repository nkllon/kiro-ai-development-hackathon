from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


class GetbranchdetailsClass:
    """Auto-generated class for functions."""

    def get_branch_details(self, branch_name: str) -> GitOperationResult:
    """Get detailed information about a specific branch"""
    start_time = time.time()
    try:
    try:
    self._run_git_command(['show-ref', '--verify', f'refs/heads/{branch_name}'])
    except subprocess.CalledProcessError:
    return self._create_result(success=False, message=f"Branch '{branch_name}' does not exist", error_code='GIT_BRANCH_NOT_FOUND', suggestions=[f'Check available branches with list_branches()', f"Create branch with create_branch('{branch_name}')"])
    result = self._run_git_command(['show', '--format=%H|%h|%s|%an|%ae|%ci', '--no-patch', branch_name])
    commit_info = result.stdout.strip().split('|')
    if len(commit_info) >= 6:
    commit_hash = commit_info[0]
    short_hash = commit_info[1]
    commit_message = commit_info[2]
    author_name = commit_info[3]
    author_email = commit_info[4]
    commit_date_str = commit_info[5]
    try:
    commit_date = datetime.fromisoformat(commit_date_str.replace(' ', 'T', 1))
    except ValueError:
    commit_date = datetime.now()
    else:
    return self._create_result(success=False, message=f"Failed to parse branch information for '{branch_name}'", error_code='GIT_BRANCH_INFO_PARSE_FAILED')
    tracking_branch = None
    try:
    tracking_result = self._run_git_command(['config', f'branch.{branch_name}.remote'])
    remote = tracking_result.stdout.strip()
    merge_result = self._run_git_command(['config', f'branch.{branch_name}.merge'])
    merge_ref = merge_result.stdout.strip()
    if remote and merge_ref:
    remote_branch = merge_ref.replace('refs/heads/', '')
    tracking_branch = f'{remote}/{remote_branch}'
    except subprocess.CalledProcessError:
    pass
    ahead_behind = {'ahead': 0, 'behind': 0}
    if tracking_branch:
    ahead_behind = self._get_ahead_behind_counts(branch_name)
    current_branch_result = self._run_git_command(['branch', '--show-current'])
    is_current = current_branch_result.stdout.strip() == branch_name
    execution_time = int((time.time() - start_time) * 1000)
    branch_details = BranchInfo(name=branch_name, is_current=is_current, ahead_count=ahead_behind['ahead'], behind_count=ahead_behind['behind'], last_commit_hash=commit_hash, last_commit_message=commit_message, last_commit_date=commit_date, last_commit_author=author_name, tracking_branch=tracking_branch)
    return self._create_result(success=True, message=f"Retrieved details for branch '{branch_name}'", data={'branch': branch_details.__dict__, 'commit_hash': commit_hash, 'short_hash': short_hash, 'author_email': author_email, 'tracking_branch': tracking_branch, 'ahead_count': ahead_behind['ahead'], 'behind_count': ahead_behind['behind']}, execution_time_ms=execution_time)
    except subprocess.CalledProcessError as e:
    execution_time = int((time.time() - start_time) * 1000)
    return self._create_result(success=False, message=f"Failed to get branch details for '{branch_name}': {e.stderr}", error_code='GIT_BRANCH_DETAILS_FAILED', execution_time_ms=execution_time)

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

