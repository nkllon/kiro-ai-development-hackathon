
def validate_installation_setup(self) -> InstallationReport:
    """
        Perform comprehensive installation and setup validation.
        
        Returns:
            Detailed installation validation report
        """
    self.logger.info('Starting installation and setup validation')
    try:
        import time
from src.rm_ddd.core.health import ModuleHealth

        start_time = time.time()
        all_issues = []
        self.logger.info('Validating configuration files')
        config_analysis = self._validate_configuration_files()
        all_issues.extend(config_analysis['issues'])
        self.logger.info('Validating dependencies')
        dependency_analysis = self._validate_dependencies()
        all_issues.extend(dependency_analysis['issues'])
        self.logger.info('Validating setup instructions')
        setup_analysis = self._validate_setup_instructions()
        all_issues.extend(setup_analysis['issues'])
        self.logger.info('Validating installation documentation')
        doc_analysis = self._validate_documentation()
        all_issues.extend(doc_analysis['issues'])
        self.logger.info('Testing installation process')
        installation_analysis = self._test_installation_process()
        all_issues.extend(installation_analysis['issues'])
        end_time = time.time()
        installation_time = end_time - start_time
        requirements_score = config_analysis['score']
        dependency_score = dependency_analysis['score']
        setup_score = setup_analysis['score']
        documentation_score = doc_analysis['score']
        environment_score = installation_analysis['score']
        overall_score = requirements_score * 0.25 + dependency_score * 0.25 + setup_score * 0.2 + documentation_score * 0.15 + environment_score * 0.15
        critical_issues = [i for i in all_issues if i.severity == 'critical']
        major_issues = [i for i in all_issues if i.severity == 'major']
        minor_issues = [i for i in all_issues if i.severity == 'minor']
        success_rate = max(0, 100 - len(critical_issues) * 30 - len(major_issues) * 10 - len(minor_issues) * 2)
        recommendations = self._generate_recommendations(all_issues, {'requirements': requirements_score, 'dependency': dependency_score, 'setup': setup_score, 'documentation': documentation_score, 'environment': environment_score})
        report = InstallationReport(overall_score=overall_score, requirements_score=requirements_score, dependency_score=dependency_score, setup_score=setup_score, documentation_score=documentation_score, environment_score=environment_score, total_issues=len(all_issues), critical_issues=len(critical_issues), major_issues=len(major_issues), minor_issues=len(minor_issues), issues=all_issues, recommendations=recommendations, installation_time=installation_time, success_rate=success_rate)
        self.logger.info(f'Installation validation complete. Overall score: {overall_score:.1f}')
        return report
    except Exception as e:
        self.logger.error(f'Installation validation failed: {e}')
        return self._create_error_report(f'Validation failed: {e}')

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

