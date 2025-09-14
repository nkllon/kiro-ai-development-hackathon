
def analyze_comprehensive_factors(self, failure: Failure) -> ComprehensiveAnalysisResult:
    """
        Analyze symptoms, tool health, dependencies, config, installation (R7.2)
        Required by R7.2: Analyze symptoms, tools, dependencies, configuration, installation integrity
        """
    try:
        self.logger.info(f'Analyzing comprehensive factors for failure: {failure.failure_id}')
        analysis_results = {}
        for component_name, analyzer in self.analysis_components.items():
            try:
                analysis_results[component_name] = analyzer(failure)
            except Exception as e:
                self.logger.warning(f'Analysis component {component_name} failed: {e}')
                analysis_results[component_name] = {'error': str(e), 'status': 'failed'}
        symptoms = analysis_results.get('symptoms', {}).get('identified_symptoms', [])
        tool_health = analysis_results.get('tool_health', {})
        dependencies = analysis_results.get('dependencies', {})
        configuration = analysis_results.get('configuration', {})
        installation = analysis_results.get('installation', {})
        environment = analysis_results.get('environment', {})
        confidence = self._calculate_analysis_confidence(analysis_results)
        return ComprehensiveAnalysisResult(symptoms=symptoms, tool_health_status=tool_health, dependency_analysis=dependencies, configuration_analysis=configuration, installation_integrity=installation, environmental_factors=environment, analysis_confidence=confidence)
    except Exception as e:
        self.logger.error(f'Comprehensive analysis failed: {e}')
        return ComprehensiveAnalysisResult(symptoms=[f'Analysis failed: {e}'], tool_health_status={'error': str(e)}, dependency_analysis={'error': str(e)}, configuration_analysis={'error': str(e)}, installation_integrity={'error': str(e)}, environmental_factors={'error': str(e)}, analysis_confidence=0.0)
