
def _analyze_build_dependencies(self, failure: Failure) -> Dict[str, Any]:
    """Analyze build dependency issues"""
    build_deps = {}
    try:
        build_deps['make_available'] = subprocess.run(['which', 'make'], capture_output=True).returncode == 0
        build_deps['gcc_available'] = subprocess.run(['which', 'gcc'], capture_output=True).returncode == 0
        build_deps['python_available'] = subprocess.run(['which', 'python3'], capture_output=True).returncode == 0
    except Exception as e:
        build_deps['analysis_error'] = str(e)
    return build_deps
