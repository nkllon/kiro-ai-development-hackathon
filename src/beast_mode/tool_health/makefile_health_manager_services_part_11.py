from src.rm_ddd.core.health import ModuleHealth

    def diagnose_makefile_issues(self) -> MakefileDiagnosisResult:
        """
        Systematic diagnosis of Makefile health issues
        Required by R3.1: Diagnose root cause of tool failures systematically
        """
        self.diagnosis_count += 1
        start_time = datetime.now()
        try:
            self.logger.info('Starting systematic Makefile diagnosis...')
            makefile_path = Path('Makefile')
            if not makefile_path.exists():
                return MakefileDiagnosisResult(missing_files=['Makefile'], broken_targets=[], dependency_issues=[], root_cause='Main Makefile missing - complete system failure', systematic_fix_required=True, workaround_temptation='Create minimal Makefile with basic targets')
            makefiles_dir = Path('makefiles')
            missing_modules = []
            if not makefiles_dir.exists():
                missing_modules = self.expected_makefile_modules
                root_cause = 'Missing makefiles/ directory - modular system not implemented'
            else:
                for module in self.expected_makefile_modules:
                    module_path = makefiles_dir / module
                    if not module_path.exists():
                        missing_modules.append(module)
                if missing_modules:
                    root_cause = f'Incomplete modular Makefile system - missing {len(missing_modules)} modules'
                else:
                    root_cause = 'Unknown Makefile issue - requires deeper analysis'
            broken_targets = []
            dependency_issues = []
            try:
                result = subprocess.run(['make', 'help'], capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    broken_targets.append('help')
                    if 'No such file or directory' in result.stderr:
                        dependency_issues.extend(missing_modules)
            except subprocess.TimeoutExpired:
                broken_targets.append('help (timeout)')
            except FileNotFoundError:
                dependency_issues.append('make command not found')
            if missing_modules:
                workaround_temptation = f'Create empty files for {missing_modules[:2]} and ignore the rest'
            else:
                workaround_temptation = 'Comment out broken includes and use basic Makefile'
            diagnosis_result = MakefileDiagnosisResult(missing_files=missing_modules, broken_targets=broken_targets, dependency_issues=dependency_issues, root_cause=root_cause, systematic_fix_required=len(missing_modules) > 0 or len(broken_targets) > 0, workaround_temptation=workaround_temptation)
            if self.metrics_engine:
                diagnosis_time = (datetime.now() - start_time).total_seconds()
                self.metrics_engine.establish_baseline_measurement('tool_health_performance', 'systematic', diagnosis_time)
            self.logger.info(f'Diagnosis complete: {len(missing_modules)} missing modules, root cause: {root_cause}')
            return diagnosis_result
        except Exception as e:
            self.logger.error(f'Diagnosis failed: {e}')
            return MakefileDiagnosisResult(missing_files=[], broken_targets=['diagnosis_failed'], dependency_issues=[str(e)], root_cause=f'Diagnosis system failure: {e}', systematic_fix_required=True, workaround_temptation='Skip diagnosis and guess the problem')

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

