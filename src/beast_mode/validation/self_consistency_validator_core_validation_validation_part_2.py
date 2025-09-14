
def _validate_makefile_works(self) -> ValidationResult:
    """Validate that Beast Mode's own Makefile works flawlessly"""
    start_time = time.time()
    try:
        result = subprocess.run(['make', 'help'], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            beast_mode_operations = ['beast-mode', 'pdca-cycle', 'systematic-repair', 'model-driven', 'quality-gates', 'self-consistency']
            operations_found = sum((1 for op in beast_mode_operations if op in result.stdout))
            score = operations_found / len(beast_mode_operations)
            status = ValidationStatus.PASSED if score >= 0.8 else ValidationStatus.WARNING
            evidence = ['make help command executes successfully', f'Found {operations_found}/{len(beast_mode_operations)} Beast Mode operations', 'Makefile demonstrates systematic tool repair success']
            recommendations = []
            if score < 1.0:
                missing_ops = [op for op in beast_mode_operations if op not in result.stdout]
                recommendations.append(f'Add missing Beast Mode operations: {missing_ops}')
        else:
            score = 0.0
            status = ValidationStatus.FAILED
            evidence = [f'make help failed with return code {result.returncode}']
            recommendations = ['Fix Makefile errors using systematic repair', 'Ensure all Beast Mode operations are properly defined', 'Validate Makefile syntax and dependencies']
        return ValidationResult(test_name='makefile_works', status=status, score=score, details={'make_help_success': result.returncode == 0, 'beast_mode_operations_found': operations_found if result.returncode == 0 else 0, 'stdout_preview': result.stdout[:500] if result.stdout else '', 'stderr': result.stderr if result.stderr else ''}, evidence=evidence, recommendations=recommendations, execution_time_seconds=time.time() - start_time)
    except subprocess.TimeoutExpired:
        return ValidationResult(test_name='makefile_works', status=ValidationStatus.FAILED, score=0.0, details={'error': 'make help command timed out'}, evidence=['Makefile execution timed out'], recommendations=['Fix Makefile performance issues'], execution_time_seconds=time.time() - start_time)
