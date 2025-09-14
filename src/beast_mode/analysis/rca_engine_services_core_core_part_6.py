
def perform_systematic_rca(self, failure: Failure) -> RCAResult:
    """
        Systematic RCA to identify actual root causes (R7.1)
        Required by R7.1: Perform systematic RCA to identify actual root causes
        """
    self.rca_count += 1
    start_time = time.time()
    try:
        self.logger.info(f'Starting systematic RCA for failure: {failure.failure_id}')
        analysis_result = self.analyze_comprehensive_factors(failure)
        root_causes = self._identify_root_causes(failure, analysis_result)
        systematic_fixes = self.implement_systematic_fixes(root_causes)
        validation_results = []
        for fix in systematic_fixes:
            validation = self.validate_root_cause_addressed(fix, failure)
            validation_results.append(validation)
            if validation.fix_successful:
                self.successful_fixes += 1
        prevention_patterns = self.document_prevention_patterns(failure, root_causes, systematic_fixes)
        analysis_time = time.time() - start_time
        self.total_analysis_time += analysis_time
        rca_confidence = self._calculate_rca_confidence(analysis_result, root_causes, validation_results)
        rca_result = RCAResult(failure=failure, analysis=analysis_result, root_causes=root_causes, systematic_fixes=systematic_fixes, validation_results=validation_results, prevention_patterns=prevention_patterns, total_analysis_time_seconds=analysis_time, rca_confidence_score=rca_confidence)
        self.logger.info(f'RCA complete: {len(root_causes)} root causes, {len(systematic_fixes)} fixes, confidence: {rca_confidence:.2f}')
        return rca_result
    except Exception as e:
        self.logger.error(f'RCA failed: {e}')
        return RCAResult(failure=failure, analysis=ComprehensiveAnalysisResult([], {}, {}, {}, {}, {}, 0.0), root_causes=[], systematic_fixes=[], validation_results=[], prevention_patterns=[], total_analysis_time_seconds=time.time() - start_time, rca_confidence_score=0.0)
