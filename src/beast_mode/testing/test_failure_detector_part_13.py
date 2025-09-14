
    def extract_failure_context(self, failure_info: dict) -> Dict[str, Any]:
        """
        Extract comprehensive context from failure information
        Requirements: 5.2, 5.3 - Comprehensive failure context extraction
        """
        try:
            context = {'timestamp': datetime.now().isoformat(), 'python_version': sys.version, 'working_directory': os.getcwd(), 'environment_variables': {}, 'pytest_version': self._get_pytest_version()}
            relevant_env_vars = ['PYTHONPATH', 'PATH', 'VIRTUAL_ENV', 'PYTEST_CURRENT_TEST', 'CI', 'GITHUB_ACTIONS', 'RCA_ON_FAILURE', 'RCA_TIMEOUT']
            for var in relevant_env_vars:
                if var in os.environ:
                    context['environment_variables'][var] = os.environ[var]
            if isinstance(failure_info, dict):
                context.update(failure_info)
            return context
        except Exception as e:
            self.logger.error(f'Context extraction failed: {e}')
            return {'extraction_error': str(e)}
