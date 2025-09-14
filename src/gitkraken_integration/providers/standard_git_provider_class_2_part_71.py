from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def _run_git_command(self, args: List[str], input_data: str=None, timeout: int=30) -> subprocess.CompletedProcess:
    """
        Run a git command and return the result.
        
        Args:
            args: Git command arguments
            input_data: Optional input data for the command
            timeout: Command timeout in seconds
            
        Returns:
            CompletedProcess result
            
        Raises:
            subprocess.CalledProcessError: If command fails
            subprocess.TimeoutExpired: If command times out
        """
    cmd = [self.git_executable] + args
    return subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True, input=input_data, timeout=timeout, check=True)
