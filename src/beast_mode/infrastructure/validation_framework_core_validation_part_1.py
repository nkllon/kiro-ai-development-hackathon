from src.rm_ddd.core.health import ModuleHealth

def validate_complete_infrastructure(self) -> InfrastructureAssessment:
    """
        Perform complete systematic infrastructure validation
        
        Following Beast Mode priorities:
        1. Logging infrastructure (ALWAYS FIRST)
        2. Profiling infrastructure (ALWAYS SECOND)
        3. Monitoring infrastructure
        4. Testing infrastructure
        5. Documentation infrastructure
        """
    self.logger.info('🔍 Starting complete systematic infrastructure validation')
    assessment_id = f"infra_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    validation_results = []
    self.logger.info('📝 Validating logging infrastructure (PRIORITY 1)')
    logging_result = self._validate_logging_infrastructure()
    validation_results.append(logging_result)
    self.logger.info('📊 Validating profiling infrastructure (PRIORITY 2)')
    profiling_result = self._validate_profiling_infrastructure()
    validation_results.append(profiling_result)
    self.logger.info('📈 Validating monitoring infrastructure')
    monitoring_result = self._validate_monitoring_infrastructure()
    validation_results.append(monitoring_result)
    self.logger.info('🧪 Validating testing infrastructure')
    testing_result = self._validate_testing_infrastructure()
    validation_results.append(testing_result)
    self.logger.info('📚 Validating documentation infrastructure')
    documentation_result = self._validate_documentation_infrastructure()
    validation_results.append(documentation_result)
    assessment = self._calculate_infrastructure_assessment(assessment_id, validation_results)
    self.assessment_history.append(assessment)
    self.logger.info(f'✅ Infrastructure validation complete: {assessment.overall_compliance_score:.2f} compliance score')
    return assessment

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

