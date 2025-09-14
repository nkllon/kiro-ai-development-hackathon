from src.rm_ddd.core.registry import register_module

    def is_available(self) -> bool:
        """Check if this provider is available and functional"""
        try:
            self._run_git_command(['--version'])
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, RuntimeError):
            return False
