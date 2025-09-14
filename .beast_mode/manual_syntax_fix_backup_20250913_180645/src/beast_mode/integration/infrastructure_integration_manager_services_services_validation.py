"""
Infrastructure Integration Manager Services Services Validation

This module was extracted from infrastructure_integration_manager_services_services.py
as part of RM-DDD compliance refactoring.
"""

import json
import subprocess
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from ..core.reflective_module import ReflectiveModule, HealthStatus

def validate_complete_integration(self) -> Dict[str, Any]:
    """
        Validate complete Beast Mode integration with existing infrastructure
        Implements UC-25: Integration validation
        """
    self.logger.info('Starting complete infrastructure integration validation')
    validation_results = []
    makefile_result = self._validate_makefile_integration()
    validation_results.append(makefile_result)
    registry_result = self._validate_project_registry_integration()
    validation_results.append(registry_result)
    cursor_result = self._validate_cursor_rules_integration()
    validation_results.append(cursor_result)
    config_result = self._validate_beast_mode_configuration()
    validation_results.append(config_result)
    integration_health = self._calculate_integration_health(validation_results)
    self._update_integration_metrics(validation_results, integration_health)
    self.validation_history.append({'timestamp': datetime.now(), 'results': validation_results, 'health_score': integration_health, 'overall_status': 'healthy' if integration_health >= 0.7 else 'degraded'})
    self.validation_history = self.validation_history[-50:]
    return {'validation_id': f'INFRA-{int(datetime.now().timestamp())}', 'overall_health_score': integration_health, 'overall_status': 'healthy' if integration_health >= 0.7 else 'degraded', 'component_results': validation_results, 'recommendations': self._generate_integration_recommendations(validation_results), 'timestamp': datetime.now()}

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

def _validate_project_registry_integration(self) -> ValidationResult:
    """Validate project model registry integration"""
    issues = []
    recommendations = []
    if not self.config.project_registry_path.exists():
        return ValidationResult(component='project_registry', status=IntegrationStatus.MISSING, details='Project model registry not found', issues=['project_model_registry.json missing'], recommendations=['Create project model registry with domain architecture'])
    try:
        registry_content = json.loads(self.config.project_registry_path.read_text())
        required_keys = ['domain_architecture', 'project_purpose', 'description']
        for key in required_keys:
            if key not in registry_content:
                issues.append(f'Missing required key: {key}')
                recommendations.append(f'Add {key} section to project registry')
        if 'domain_architecture' in registry_content:
            domain_arch = registry_content['domain_architecture']
            for domain in self.config.required_registry_domains:
                if domain not in domain_arch:
                    issues.append(f'Missing required domain: {domain}')
                    recommendations.append(f'Add {domain} domain to registry')
            total_domains = domain_arch.get('overview', {}).get('total_domains', 0)
            if total_domains < 50:
                issues.append(f'Insufficient domains: {total_domains} (minimum 50)')
                recommendations.append('Expand domain architecture to meet requirements')
        compliance = registry_content.get('domain_architecture', {}).get('overview', {}).get('compliance_standard')
        if compliance != 'Reflective Module (RM)':
            issues.append('Compliance standard not set to Reflective Module (RM)')
            recommendations.append("Set compliance_standard to 'Reflective Module (RM)'")
        if not issues:
            status = IntegrationStatus.INTEGRATED
            details = 'Project registry fully integrated with Beast Mode requirements'
        elif len(issues) <= 3:
            status = IntegrationStatus.PARTIAL
            details = 'Project registry partially integrated, some issues detected'
        else:
            status = IntegrationStatus.FAILED
            details = 'Project registry integration failed, multiple issues detected'
        self.integration_status['project_registry'] = status.value
        return ValidationResult(component='project_registry', status=status, details=details, issues=issues, recommendations=recommendations)
    except json.JSONDecodeError as e:
        self.integration_status['project_registry'] = IntegrationStatus.FAILED.value
        return ValidationResult(component='project_registry', status=IntegrationStatus.FAILED, details=f'Invalid JSON in project registry: {str(e)}', issues=[f'JSON parsing error: {str(e)}'], recommendations=['Fix JSON syntax in project_model_registry.json'])
    except Exception as e:
        self.integration_status['project_registry'] = IntegrationStatus.FAILED.value
        return ValidationResult(component='project_registry', status=IntegrationStatus.FAILED, details=f'Registry validation failed: {str(e)}', issues=[f'Validation error: {str(e)}'], recommendations=['Debug project registry validation process'])

def _validate_cursor_rules_integration(self) -> ValidationResult:
    """Validate cursor rules integration"""
    issues = []
    recommendations = []
    if not self.config.cursor_rules_path.exists():
        return ValidationResult(component='cursor_rules', status=IntegrationStatus.MISSING, details='Cursor rules directory not found', issues=['.cursor/rules directory missing'], recommendations=['Create .cursor/rules directory with Beast Mode integration'])
    try:
        beast_mode_rules = ['beast-mode-integration.mdc', 'beast.mdc']
        missing_rules = []
        for rule_file in beast_mode_rules:
            rule_path = self.config.cursor_rules_path / rule_file
            if not rule_path.exists():
                missing_rules.append(rule_file)
        if missing_rules:
            issues.append(f"Missing Beast Mode rules: {', '.join(missing_rules)}")
            recommendations.append('Create Beast Mode cursor rules for systematic development')
        rule_files = list(self.config.cursor_rules_path.glob('*.mdc'))
        beast_mode_mentions = 0
        for rule_file in rule_files:
            try:
                content = rule_file.read_text()
                if 'beast' in content.lower() or 'systematic' in content.lower():
                    beast_mode_mentions += 1
            except Exception:
                continue
        if beast_mode_mentions == 0:
            issues.append('No Beast Mode integration found in existing rules')
            recommendations.append('Add Beast Mode methodology to cursor rules')
        if not issues:
            status = IntegrationStatus.INTEGRATED
            details = 'Cursor rules fully integrated with Beast Mode methodology'
        elif len(issues) <= 2:
            status = IntegrationStatus.PARTIAL
            details = 'Cursor rules partially integrated, some rules missing'
        else:
            status = IntegrationStatus.FAILED
            details = 'Cursor rules integration incomplete'
        self.integration_status['cursor_rules'] = status.value
        return ValidationResult(component='cursor_rules', status=status, details=details, issues=issues, recommendations=recommendations)
    except Exception as e:
        self.integration_status['cursor_rules'] = IntegrationStatus.FAILED.value
        return ValidationResult(component='cursor_rules', status=IntegrationStatus.FAILED, details=f'Cursor rules validation failed: {str(e)}', issues=[f'Validation error: {str(e)}'], recommendations=['Debug cursor rules validation process'])

def _validate_beast_mode_configuration(self) -> ValidationResult:
    """Validate Beast Mode configuration and specs"""
    issues = []
    recommendations = []
    if not self.config.beast_mode_config_path.exists():
        return ValidationResult(component='beast_mode_config', status=IntegrationStatus.MISSING, details='Beast Mode configuration directory not found', issues=['.kiro/specs/beast-mode-framework directory missing'], recommendations=['Create Beast Mode configuration directory with specs'])
    try:
        required_config_files = ['requirements.md', 'design.md', 'tasks.md']
        missing_configs = []
        for config_file in required_config_files:
            config_path = self.config.beast_mode_config_path / config_file
            if not config_path.exists():
                missing_configs.append(config_file)
        if missing_configs:
            issues.append(f"Missing configuration files: {', '.join(missing_configs)}")
            recommendations.append('Create complete Beast Mode specification files')
        beast_mode_src = self.project_root / 'src' / 'beast_mode'
        if not beast_mode_src.exists():
            issues.append('Beast Mode source code directory missing')
            recommendations.append('Create src/beast_mode directory with framework code')
        else:
            core_modules = ['core/reflective_module.py', 'orchestration/tool_orchestration_engine.py', 'integration/infrastructure_integration_manager.py']
            missing_modules = []
            for module in core_modules:
                module_path = beast_mode_src / module
                if not module_path.exists():
                    missing_modules.append(module)
            if missing_modules:
                issues.append(f"Missing core modules: {', '.join(missing_modules)}")
                recommendations.append('Implement missing Beast Mode core modules')
        if not issues:
            status = IntegrationStatus.INTEGRATED
            details = 'Beast Mode configuration fully integrated and complete'
        elif len(issues) <= 2:
            status = IntegrationStatus.PARTIAL
            details = 'Beast Mode configuration partially complete'
        else:
            status = IntegrationStatus.FAILED
            details = 'Beast Mode configuration incomplete or missing'
        self.integration_status['beast_mode_config'] = status.value
        return ValidationResult(component='beast_mode_config', status=status, details=details, issues=issues, recommendations=recommendations)
    except Exception as e:
        self.integration_status['beast_mode_config'] = IntegrationStatus.FAILED.value
        return ValidationResult(component='beast_mode_config', status=IntegrationStatus.FAILED, details=f'Beast Mode configuration validation failed: {str(e)}', issues=[f'Validation error: {str(e)}'], recommendations=['Debug Beast Mode configuration validation'])
