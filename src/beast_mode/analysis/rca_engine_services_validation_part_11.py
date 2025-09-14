
def _analyze_test_environment(self, failure: Failure) -> Dict[str, Any]:
    """Analyze test environment factors"""
    env_analysis = {}
    try:
        env_analysis['python_available'] = subprocess.run(['python3', '--version'], capture_output=True).returncode == 0
        env_analysis['pytest_available'] = subprocess.run(['python3', '-m', 'pytest', '--version'], capture_output=True).returncode == 0
        env_analysis['venv_active'] = 'VIRTUAL_ENV' in os.environ
        env_analysis['tests_dir_exists'] = Path('tests').exists()
        env_analysis['conftest_exists'] = Path('tests/conftest.py').exists()
    except Exception as e:
        env_analysis['analysis_error'] = str(e)
    return env_analysis
