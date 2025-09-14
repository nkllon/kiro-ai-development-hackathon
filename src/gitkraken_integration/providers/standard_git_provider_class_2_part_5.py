from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def _find_git_executable(self) -> str:
        """Find the git executable on the system"""
        try:
            result = subprocess.run(['which', 'git'], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            common_paths = ['/usr/bin/git', '/usr/local/bin/git', 'git']
            for path in common_paths:
                try:
                    subprocess.run([path, '--version'], capture_output=True, check=True)
                    return path
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            raise RuntimeError('Git executable not found on system')
