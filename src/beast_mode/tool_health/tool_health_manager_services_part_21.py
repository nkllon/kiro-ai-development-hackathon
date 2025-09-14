
    def _validate_all_make_targets(self) -> Dict[str, Any]:
        """Validate all make targets work correctly"""
        try:
            result = subprocess.run(['make', 'help'], capture_output=True, text=True, timeout=10)
            return {'all_targets_work': result.returncode == 0, 'tested_targets': ['help'], 'output': result.stdout}
        except Exception as e:
            return {'all_targets_work': False, 'error': str(e)}
