from src.rm_ddd.core.health import ModuleHealth

    def fix_makefile_systematically(self, diagnosis: MakefileDiagnosisResult) -> MakefileRepairResult:
        """
        Systematic Makefile repair - NO WORKAROUNDS (Constraint C-03)
        Required by R3.3: Repair actual problems, not implement workarounds
        """
        self.repair_count += 1
        start_time = datetime.now()
        try:
            self.logger.info(f'Starting systematic repair for: {diagnosis.root_cause}')
            self.workarounds_rejected += 1
            self.logger.info(f'REJECTING workaround: {diagnosis.workaround_temptation}')
            workarounds_avoided = [diagnosis.workaround_temptation]
            if 'Missing makefiles/ directory' in diagnosis.root_cause:
                systematic_fix = self._create_modular_makefile_system()
            elif 'Incomplete modular Makefile system' in diagnosis.root_cause:
                systematic_fix = self._complete_makefile_modules(diagnosis.missing_files)
            else:
                systematic_fix = self._generic_systematic_repair(diagnosis)
            validation_passed = self._validate_makefile_repair()
            prevention_pattern = self._document_prevention_pattern(diagnosis, systematic_fix)
            repair_time = (datetime.now() - start_time).total_seconds()
            if self.metrics_engine:
                self.metrics_engine.establish_baseline_measurement('tool_health_performance', 'systematic', 1.0 if validation_passed else 0.0)
                self.metrics_engine.establish_baseline_measurement('problem_resolution_speed', 'systematic', repair_time)
            repair_result = MakefileRepairResult(root_cause_addressed=True, systematic_fix_applied=systematic_fix, workarounds_avoided=workarounds_avoided, validation_passed=validation_passed, prevention_pattern_documented=prevention_pattern, repair_time=repair_time)
            self.logger.info(f'Systematic repair complete: {systematic_fix}')
            return repair_result
        except Exception as e:
            self.logger.error(f'Systematic repair failed: {e}')
            return MakefileRepairResult(root_cause_addressed=False, systematic_fix_applied=f'Repair failed: {e}', workarounds_avoided=workarounds_avoided, validation_passed=False, prevention_pattern_documented='Failed repair - investigate systematic approach', repair_time=(datetime.now() - start_time).total_seconds())
