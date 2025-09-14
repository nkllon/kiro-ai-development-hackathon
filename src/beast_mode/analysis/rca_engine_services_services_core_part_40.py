
def _analyze_make_targets(self, failure: Failure) -> Dict[str, Any]:
    """Analyze make target structure"""
    target_analysis = {}
    try:
        result = subprocess.run(['make', 'help'], capture_output=True, text=True, timeout=5)
        target_analysis['make_help_available'] = result.returncode == 0
        if result.returncode == 0:
            target_analysis['available_targets'] = len(result.stdout.split('\n'))
        else:
            target_analysis['make_help_error'] = result.stderr
    except Exception as e:
        target_analysis['analysis_error'] = str(e)
    return target_analysis
