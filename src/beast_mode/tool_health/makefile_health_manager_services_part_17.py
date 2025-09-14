from src.rm_ddd.core.health import ModuleHealth

    def _document_prevention_pattern(self, diagnosis: MakefileDiagnosisResult, fix: str) -> str:
        """
        Document prevention pattern for future use
        Required by R3.5: Document patterns for future prevention
        """
        pattern = f"""\nPREVENTION PATTERN: Modular Makefile System Health\n\nROOT CAUSE: {diagnosis.root_cause}\nSYSTEMATIC FIX: {fix}\nWORKAROUND AVOIDED: {diagnosis.workaround_temptation}\n\nPREVENTION MEASURES:\n1. Always check makefiles/ directory exists before Makefile execution\n2. Validate all module files present: {', '.join(self.expected_makefile_modules)}\n3. Use 'make -n' for syntax validation before execution\n4. Implement systematic health monitoring for build system\n5. Never accept broken tools - always fix root causes\n\nDETECTION PATTERN:\n- Error: "No such file or directory" for makefiles/*.mk\n- Symptom: make help fails with missing includes\n- Root Cause: Missing modular Makefile system structure\n\nSYSTEMATIC REPAIR PATTERN:\n1. Diagnose missing components systematically\n2. Create complete modular system (not partial workarounds)\n3. Validate repair with actual make command execution\n4. Document pattern for future prevention\n"""
        pattern_file = Path('makefiles/prevention_patterns.md')
        with open(pattern_file, 'a') as f:
            f.write(f'\n## {datetime.now().isoformat()}\n{pattern}\n')
        return pattern.strip()
