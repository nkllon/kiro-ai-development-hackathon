from src.rm_ddd.core.health import ModuleHealth

    def _get_pytest_version(self) -> str:
        """Get pytest version for context"""
        try:
            result = subprocess.run(['python3', '-m', 'pytest', '--version'], capture_output=True, text=True, timeout=10)
            return result.stdout.strip() if result.returncode == 0 else 'unknown'
        except:
            return 'unknown'
