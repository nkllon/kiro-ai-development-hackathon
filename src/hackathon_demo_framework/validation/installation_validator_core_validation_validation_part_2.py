from src.rm_ddd.core.health import ModuleHealth

def validate_installation_reliability(self, num_tests: int=3) -> ValidationResult:
    """
        Test installation reliability across multiple attempts.
        
        Args:
            num_tests: Number of installation attempts to test
            
        Returns:
            Validation result with reliability assessment
        """
    self.logger.info(f'Testing installation reliability with {num_tests} attempts')
    successful_installs = 0
    issues = []
    recommendations = []
    for attempt in range(num_tests):
        try:
            self.logger.info(f'Installation attempt {attempt + 1}/{num_tests}')
            with tempfile.TemporaryDirectory() as temp_dir:
                test_result = self._test_single_installation(Path(temp_dir))
                if test_result['success']:
                    successful_installs += 1
                else:
                    issues.extend(test_result['issues'])
        except Exception as e:
            issues.append(f'Installation attempt {attempt + 1} failed: {e}')
    success_rate = successful_installs / num_tests * 100
    if success_rate < 80:
        issues.append(f'Installation reliability too low: {success_rate:.1f}%')
        recommendations.append('Improve installation process reliability')
    if success_rate < 50:
        recommendations.append('Critical: Fix installation process - more than half of attempts fail')
    return ValidationResult(is_valid=success_rate >= 80, score=success_rate, issues=issues, recommendations=recommendations)
