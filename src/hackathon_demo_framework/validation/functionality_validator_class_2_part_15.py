from src.rm_ddd.core.registry import register_module

    def _calculate_test_score(self, test_results: Dict[str, Any]) -> float:
        """Calculate test execution score."""
        if test_results['total_tests'] == 0:
            return 0.0
        if test_results['errors']:
            return max(0, 50 - len(test_results['errors']) * 10)
        pass_rate = test_results['passed_tests'] / test_results['total_tests']
        return pass_rate * 100
