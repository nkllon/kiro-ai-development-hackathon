from src.rm_ddd.core.health import ModuleHealth

def generate_quality_improvement_plan(self, report: CodeQualityReport) -> List[str]:
    """
        Generate systematic improvement plan based on quality assessment.
        
        Args:
            report: Code quality assessment report
            
        Returns:
            Prioritized list of improvement actions
        """
    improvement_plan = []
    if report.critical_issues > 0:
        improvement_plan.append('CRITICAL: Fix all critical code quality issues')
        critical_files = set((issue.file_path for issue in report.issues if issue.severity == 'critical'))
        for file_path in critical_files:
            improvement_plan.append(f'  - Review and fix critical issues in {file_path}')
    if report.complexity_score < 70:
        improvement_plan.append('HIGH: Reduce code complexity')
        improvement_plan.append('  - Break down complex functions into smaller units')
        improvement_plan.append('  - Simplify conditional logic and nested structures')
        improvement_plan.append('  - Extract common functionality into helper functions')
    if report.documentation_score < 80:
        improvement_plan.append('HIGH: Improve documentation coverage')
        improvement_plan.append('  - Add docstrings to all public functions and classes')
        improvement_plan.append('  - Document complex algorithms and business logic')
        improvement_plan.append('  - Add type hints for better code clarity')
    if report.maintainability_score < 70:
        improvement_plan.append('MEDIUM: Improve code maintainability')
        improvement_plan.append('  - Refactor duplicate code into reusable functions')
        improvement_plan.append('  - Improve variable and function naming')
        improvement_plan.append('  - Reduce coupling between modules')
    if report.style_score < 80:
        improvement_plan.append('MEDIUM: Improve code style consistency')
        improvement_plan.append('  - Run automated code formatter (black, autopep8)')
        improvement_plan.append('  - Fix linting issues (flake8, pylint)')
        improvement_plan.append('  - Ensure consistent naming conventions')
    if report.security_score < 90:
        improvement_plan.append('MEDIUM: Address security concerns')
        improvement_plan.append('  - Review and fix potential security vulnerabilities')
        improvement_plan.append('  - Validate all user inputs and external data')
        improvement_plan.append('  - Use secure coding practices')
    if report.performance_score < 80:
        improvement_plan.append('LOW: Optimize performance')
        improvement_plan.append('  - Profile and optimize slow code paths')
        improvement_plan.append('  - Reduce unnecessary computations and memory usage')
        improvement_plan.append('  - Consider algorithmic improvements')
    return improvement_plan

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

