from src.rm_ddd.core.health import ModuleHealth

def check_size_constraints(self, module_path: str) -> SizeConstraintResult:
    """
        Check that module meets size constraints (≤200 lines) and single responsibility.
        
        Args:
            module_path: Path to the Python module to validate
            
        Returns:
            SizeConstraintResult with validation details
        """
    issues = []
    try:
        with open(module_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        code_lines = [line.strip() for line in lines if line.strip() and (not line.strip().startswith('#'))]
        line_count = len(code_lines)
        meets_size_constraint = line_count <= self.max_lines_per_module
        if not meets_size_constraint:
            issues.append(ComplianceIssue(issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION, severity=IssueSeverity.HIGH, description=f'Module exceeds size constraint: {line_count} lines (max: {self.max_lines_per_module})', affected_files=[module_path], remediation_steps=['Refactor module to reduce size', 'Split large classes into smaller, focused components', 'Extract utility functions to separate modules', 'Consider breaking module into multiple focused modules'], blocking_merge=True))
        complexity_indicators = self._analyze_complexity(module_path)
        single_responsibility_score = self._calculate_single_responsibility_score(complexity_indicators)
        if single_responsibility_score < 0.7:
            issues.append(ComplianceIssue(issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION, severity=IssueSeverity.MEDIUM, description=f'Low single responsibility score: {single_responsibility_score:.2f}', affected_files=[module_path], remediation_steps=['Reduce module complexity', 'Ensure module has a single, clear responsibility', 'Extract unrelated functionality to separate modules'], blocking_merge=False))
        self._check_architectural_patterns(module_path, complexity_indicators, issues)
        return SizeConstraintResult(module_path=module_path, line_count=line_count, meets_size_constraint=meets_size_constraint, single_responsibility_score=single_responsibility_score, complexity_indicators=complexity_indicators, issues=issues)
    except Exception as e:
        issues.append(ComplianceIssue(issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION, severity=IssueSeverity.HIGH, description=f'Failed to check size constraints: {str(e)}', affected_files=[module_path], remediation_steps=['Fix file access issues', 'Ensure module file is readable'], blocking_merge=True))
        return SizeConstraintResult(module_path=module_path, line_count=0, meets_size_constraint=False, single_responsibility_score=0.0, complexity_indicators={}, issues=issues)
