from src.rm_ddd.core.health import ModuleHealth

def _validate_makefile_integration(self) -> ValidationResult:
    """Validate Makefile integration with Beast Mode operations"""
    issues = []
    recommendations = []
    if not self.config.makefile_path.exists():
        return ValidationResult(component='makefile', status=IntegrationStatus.MISSING, details='Makefile not found', issues=['Makefile missing from project root'], recommendations=['Create Makefile with Beast Mode integration'])
    try:
        makefile_content = self.config.makefile_path.read_text()
        if 'beast-mode.mk' not in makefile_content:
            issues.append('Beast Mode Makefile not included')
            recommendations.append("Add 'include makefiles/beast-mode.mk' to Makefile")
        missing_targets = []
        for target in self.config.required_makefile_targets:
            if target not in makefile_content:
                missing_targets.append(target)
        if missing_targets:
            issues.append(f"Missing Beast Mode targets: {', '.join(missing_targets)}")
            recommendations.append('Ensure all Beast Mode targets are available')
        try:
            result = subprocess.run(['make', 'help'], capture_output=True, text=True, timeout=30, cwd=self.project_root)
            if result.returncode != 0:
                issues.append('Makefile execution failed')
                recommendations.append('Fix Makefile syntax and dependency issues')
        except subprocess.TimeoutExpired:
            issues.append('Makefile execution timed out')
            recommendations.append('Optimize Makefile performance')
        except Exception as e:
            issues.append(f'Makefile execution error: {str(e)}')
            recommendations.append('Debug Makefile execution environment')
        if not issues:
            status = IntegrationStatus.INTEGRATED
            details = 'Makefile fully integrated with Beast Mode operations'
        elif len(issues) <= 2:
            status = IntegrationStatus.PARTIAL
            details = 'Makefile partially integrated, minor issues detected'
        else:
            status = IntegrationStatus.FAILED
            details = 'Makefile integration failed, multiple issues detected'
        self.integration_status['makefile'] = status.value
        return ValidationResult(component='makefile', status=status, details=details, issues=issues, recommendations=recommendations)
    except Exception as e:
        self.integration_status['makefile'] = IntegrationStatus.FAILED.value
        return ValidationResult(component='makefile', status=IntegrationStatus.FAILED, details=f'Makefile validation failed: {str(e)}', issues=[f'Validation error: {str(e)}'], recommendations=['Debug Makefile validation process'])
