"""
Self Consistency Validator Validation Validation Validation

This module was extracted from self_consistency_validator_validation_validation.py
as part of RM-DDD compliance refactoring.
"""

import subprocess
import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from ..core.reflective_module import ReflectiveModule, HealthStatus

def validate_complete_self_consistency(self) -> SelfConsistencyReport:
    """
        Validate complete Beast Mode self-consistency (UC-25)
        Proves Beast Mode successfully uses its own systematic methodology
        """
    start_time = time.time()
    report_id = f'SC-{int(time.time())}'
    self.logger.info(f'Starting complete self-consistency validation: {report_id}')
    check_results = []
    model_driven_result = self._validate_model_driven_decisions()
    check_results.append(model_driven_result)
    tool_repair_result = self._validate_systematic_tool_repair()
    check_results.append(tool_repair_result)
    pdca_result = self._validate_pdca_methodology()
    check_results.append(pdca_result)
    rm_compliance_result = self._validate_rm_compliance()
    check_results.append(rm_compliance_result)
    quality_gates_result = self._validate_quality_gates()
    check_results.append(quality_gates_result)
    health_monitoring_result = self._validate_health_monitoring()
    check_results.append(health_monitoring_result)
    superiority_evidence_result = self._validate_superiority_evidence()
    check_results.append(superiority_evidence_result)
    overall_score = sum((result.score for result in check_results)) / len(check_results)
    credibility_established = overall_score >= self.consistency_thresholds['credibility_threshold']
    superiority_evidence = self._generate_superiority_evidence(check_results)
    self_application_proof = self._generate_self_application_proof(check_results)
    recommendations = self._generate_consistency_recommendations(check_results, overall_score)
    execution_time = int((time.time() - start_time) * 1000)
    report = SelfConsistencyReport(report_id=report_id, overall_consistency_score=overall_score, credibility_established=credibility_established, check_results=check_results, superiority_evidence=superiority_evidence, self_application_proof=self_application_proof, recommendations=recommendations, execution_time_ms=execution_time, timestamp=datetime.now())
    self._update_validation_metrics(report)
    self.validation_history.append({'report_id': report_id, 'timestamp': datetime.now(), 'overall_score': overall_score, 'credibility_established': credibility_established, 'check_results': len(check_results)})
    self.validation_history = self.validation_history[-50:]
    self.logger.info(f'Self-consistency validation completed: {report_id} (Score: {overall_score:.2f})')
    return report

def _validate_model_driven_decisions(self) -> ConsistencyResult:
    """Validate that Beast Mode uses model-driven decisions (not guesswork)"""
    start_time = time.time()
    evidence = []
    issues = []
    recommendations = []
    score = 0.0
    registry_path = self.project_root / 'project_model_registry.json'
    if registry_path.exists():
        evidence.append('Project model registry exists and is accessible')
        score += 0.3
        try:
            registry_content = json.loads(registry_path.read_text())
            if 'domain_architecture' in registry_content:
                evidence.append('Domain architecture defined in registry')
                score += 0.2
            total_domains = registry_content.get('domain_architecture', {}).get('overview', {}).get('total_domains', 0)
            if total_domains >= 50:
                evidence.append(f'Comprehensive domain coverage: {total_domains} domains')
                score += 0.2
            else:
                issues.append(f'Insufficient domain coverage: {total_domains} domains')
                recommendations.append('Expand domain architecture to meet requirements')
        except Exception as e:
            issues.append(f'Registry parsing error: {str(e)}')
            recommendations.append('Fix project registry JSON format')
    else:
        issues.append('Project model registry missing')
        recommendations.append('Create project_model_registry.json with domain architecture')
    intelligence_engine_path = self.project_root / 'src' / 'beast_mode' / 'intelligence'
    if intelligence_engine_path.exists():
        evidence.append('Model-driven intelligence engine implemented')
        score += 0.2
    else:
        issues.append('Model-driven intelligence engine missing')
        recommendations.append('Implement model-driven intelligence engine')
    if any((self.project_root / 'src' / 'beast_mode').rglob('*decision*')):
        evidence.append('Decision documentation system present')
        score += 0.1
    else:
        issues.append('Decision documentation system missing')
        recommendations.append('Implement decision documentation system')
    execution_time = int((time.time() - start_time) * 1000)
    return ConsistencyResult(check_type=ConsistencyCheck.MODEL_DRIVEN_DECISIONS, passed=score >= 0.7, score=min(score, 1.0), evidence=evidence, issues=issues, recommendations=recommendations, execution_time_ms=execution_time)

def _validate_systematic_tool_repair(self) -> ConsistencyResult:
    """Validate that Beast Mode fixes tools systematically (no workarounds)"""
    start_time = time.time()
    evidence = []
    issues = []
    recommendations = []
    score = 0.0
    try:
        result = subprocess.run(['make', 'help'], capture_output=True, text=True, timeout=30, cwd=self.project_root)
        if result.returncode == 0:
            evidence.append("Beast Mode's own Makefile works correctly")
            score += 0.4
        else:
            issues.append("Beast Mode's own Makefile is broken")
            recommendations.append('Fix Makefile systematically (no workarounds)')
    except Exception as e:
        issues.append(f'Makefile execution failed: {str(e)}')
        recommendations.append('Debug and repair Makefile execution')
    tool_orchestration_path = self.project_root / 'src' / 'beast_mode' / 'orchestration'
    if tool_orchestration_path.exists():
        evidence.append('Tool orchestration engine implemented')
        score += 0.3
    else:
        issues.append('Tool orchestration engine missing')
        recommendations.append('Implement tool orchestration engine')
    rca_engine_path = self.project_root / 'src' / 'beast_mode' / 'analysis'
    if rca_engine_path.exists():
        evidence.append('RCA engine for systematic repair available')
        score += 0.2
    else:
        issues.append('RCA engine missing')
        recommendations.append('Implement RCA engine for systematic tool repair')
    if any((self.project_root / 'src' / 'beast_mode').rglob('*repair*')):
        evidence.append('Repair procedures documented')
        score += 0.1
    else:
        issues.append('Repair procedures not documented')
        recommendations.append('Document systematic repair procedures')
    execution_time = int((time.time() - start_time) * 1000)
    return ConsistencyResult(check_type=ConsistencyCheck.SYSTEMATIC_TOOL_REPAIR, passed=score >= 0.7, score=min(score, 1.0), evidence=evidence, issues=issues, recommendations=recommendations, execution_time_ms=execution_time)

def _validate_pdca_methodology(self) -> ConsistencyResult:
    """Validate that Beast Mode uses PDCA cycles for development"""
    start_time = time.time()
    evidence = []
    issues = []
    recommendations = []
    score = 0.0
    makefile_path = self.project_root / 'Makefile'
    if makefile_path.exists():
        makefile_content = makefile_path.read_text()
        pdca_targets = ['pdca-cycle', 'pdca-plan', 'pdca-do', 'pdca-check', 'pdca-act']
        found_targets = [target for target in pdca_targets if target in makefile_content]
        if len(found_targets) >= 4:
            evidence.append(f"PDCA targets implemented in Makefile: {', '.join(found_targets)}")
            score += 0.4
        else:
            issues.append(f'Missing PDCA targets: {set(pdca_targets) - set(found_targets)}')
            recommendations.append('Implement complete PDCA cycle targets in Makefile')
    pdca_orchestrator_path = self.project_root / 'src' / 'beast_mode' / 'orchestration'
    if pdca_orchestrator_path.exists():
        evidence.append('PDCA orchestrator implemented')
        score += 0.3
    else:
        issues.append('PDCA orchestrator missing')
        recommendations.append('Implement PDCA orchestrator for systematic development')
    if any((self.project_root / '.kiro' / 'specs').rglob('*pdca*')):
        evidence.append('PDCA methodology documented')
        score += 0.2
    else:
        issues.append('PDCA methodology not documented')
        recommendations.append('Document PDCA methodology application')
    if any((self.project_root / 'src' / 'beast_mode').rglob('*learning*')):
        evidence.append('Learning and model update mechanisms present')
        score += 0.1
    else:
        issues.append('Learning mechanisms missing')
        recommendations.append('Implement learning and model update capabilities')
    execution_time = int((time.time() - start_time) * 1000)
    return ConsistencyResult(check_type=ConsistencyCheck.PDCA_METHODOLOGY, passed=score >= 0.7, score=min(score, 1.0), evidence=evidence, issues=issues, recommendations=recommendations, execution_time_ms=execution_time)

def _validate_rm_compliance(self) -> ConsistencyResult:
    """Validate that all Beast Mode components implement RM interface"""
    start_time = time.time()
    evidence = []
    issues = []
    recommendations = []
    score = 0.0
    rm_path = self.project_root / 'src' / 'beast_mode' / 'core' / 'reflective_module.py'
    if rm_path.exists():
        evidence.append('ReflectiveModule base class implemented')
        score += 0.3
    else:
        issues.append('ReflectiveModule base class missing')
        recommendations.append('Implement ReflectiveModule base class')
    beast_mode_src = self.project_root / 'src' / 'beast_mode'
    if beast_mode_src.exists():
        python_files = list(beast_mode_src.rglob('*.py'))
        rm_compliant_files = []
        for py_file in python_files:
            if py_file.name == '__init__.py':
                continue
            try:
                content = py_file.read_text()
                if 'ReflectiveModule' in content and 'get_module_status' in content:
                    rm_compliant_files.append(py_file.name)
            except Exception:
                continue
        if rm_compliant_files:
            evidence.append(f'RM compliant components: {len(rm_compliant_files)} files')
            score += 0.4
        else:
            issues.append('No RM compliant components found')
            recommendations.append('Implement RM interface in all Beast Mode components')
    if any((self.project_root / 'src' / 'beast_mode').rglob('*health*')):
        evidence.append('Health monitoring capabilities present')
        score += 0.2
    else:
        issues.append('Health monitoring missing')
        recommendations.append('Implement comprehensive health monitoring')
    if any((self.project_root / 'src' / 'beast_mode').rglob('*degradation*')):
        evidence.append('Graceful degradation capabilities present')
        score += 0.1
    else:
        issues.append('Graceful degradation missing')
        recommendations.append('Implement graceful degradation mechanisms')
    execution_time = int((time.time() - start_time) * 1000)
    return ConsistencyResult(check_type=ConsistencyCheck.RM_COMPLIANCE, passed=score >= 0.7, score=min(score, 1.0), evidence=evidence, issues=issues, recommendations=recommendations, execution_time_ms=execution_time)

def _validate_quality_gates(self) -> ConsistencyResult:
    """Validate that Beast Mode implements quality gates"""
    start_time = time.time()
    evidence = []
    issues = []
    recommendations = []
    score = 0.0
    quality_gates_path = self.project_root / 'src' / 'beast_mode' / 'quality'
    if quality_gates_path.exists():
        evidence.append('Quality gates module implemented')
        score += 0.4
    else:
        issues.append('Quality gates module missing')
        recommendations.append('Implement code quality gates')
    tests_path = self.project_root / 'tests'
    if tests_path.exists():
        test_files = list(tests_path.glob('test_*.py'))
        if test_files:
            evidence.append(f'Test suite present: {len(test_files)} test files')
            score += 0.3
        else:
            issues.append('No test files found')
            recommendations.append('Create comprehensive test suite')
    else:
        issues.append('Tests directory missing')
        recommendations.append('Create tests directory with test suite')
    quality_configs = ['.pre-commit-config.yaml', 'pyproject.toml']
    found_configs = [config for config in quality_configs if (self.project_root / config).exists()]
    if found_configs:
        evidence.append(f"Quality configuration files: {', '.join(found_configs)}")
        score += 0.2
    else:
        issues.append('Quality configuration missing')
        recommendations.append('Add quality configuration files')
    if any((self.project_root / 'src' / 'beast_mode').rglob('*lint*')):
        evidence.append('Linting capabilities present')
        score += 0.1
    else:
        issues.append('Linting capabilities missing')
        recommendations.append('Implement linting and formatting enforcement')
    execution_time = int((time.time() - start_time) * 1000)
    return ConsistencyResult(check_type=ConsistencyCheck.QUALITY_GATES, passed=score >= 0.7, score=min(score, 1.0), evidence=evidence, issues=issues, recommendations=recommendations, execution_time_ms=execution_time)

def _validate_health_monitoring(self) -> ConsistencyResult:
    """Validate that Beast Mode implements comprehensive health monitoring"""
    start_time = time.time()
    evidence = []
    issues = []
    recommendations = []
    score = 0.0
    observability_path = self.project_root / 'src' / 'beast_mode' / 'observability'
    if observability_path.exists():
        evidence.append('Observability module implemented')
        score += 0.3
    else:
        issues.append('Observability module missing')
        recommendations.append('Implement observability and monitoring')
    makefile_path = self.project_root / 'Makefile'
    if makefile_path.exists():
        makefile_content = makefile_path.read_text()
        health_targets = ['beast-mode-health', 'beast-mode-status']
        found_health_targets = [target for target in health_targets if target in makefile_content]
        if found_health_targets:
            evidence.append(f"Health monitoring targets: {', '.join(found_health_targets)}")
            score += 0.3
        else:
            issues.append('Health monitoring targets missing')
            recommendations.append('Add health monitoring targets to Makefile')
    if any((self.project_root / 'src' / 'beast_mode').rglob('*metric*')):
        evidence.append('Metrics collection capabilities present')
        score += 0.2
    else:
        issues.append('Metrics collection missing')
        recommendations.append('Implement metrics collection and analysis')
    if any((self.project_root / 'src' / 'beast_mode').rglob('*alert*')):
        evidence.append('Alerting capabilities present')
        score += 0.2
    else:
        issues.append('Alerting capabilities missing')
        recommendations.append('Implement alerting and notification system')
    execution_time = int((time.time() - start_time) * 1000)
    return ConsistencyResult(check_type=ConsistencyCheck.HEALTH_MONITORING, passed=score >= 0.7, score=min(score, 1.0), evidence=evidence, issues=issues, recommendations=recommendations, execution_time_ms=execution_time)

def _validate_superiority_evidence(self) -> ConsistencyResult:
    """Validate that Beast Mode generates concrete superiority evidence"""
    start_time = time.time()
    evidence = []
    issues = []
    recommendations = []
    score = 0.0
    metrics_path = self.project_root / 'src' / 'beast_mode' / 'metrics'
    if metrics_path.exists():
        evidence.append('Metrics collection engine implemented')
        score += 0.3
    else:
        issues.append('Metrics collection engine missing')
        recommendations.append('Implement metrics collection for superiority evidence')
    if any((self.project_root / 'src' / 'beast_mode').rglob('*comparison*')):
        evidence.append('Comparison framework present')
        score += 0.2
    else:
        issues.append('Comparison framework missing')
        recommendations.append('Implement systematic vs ad-hoc comparison framework')
    makefile_path = self.project_root / 'Makefile'
    if makefile_path.exists():
        makefile_content = makefile_path.read_text()
        if 'superiority-metrics' in makefile_content:
            evidence.append('Superiority metrics generation target available')
            score += 0.2
        else:
            issues.append('Superiority metrics target missing')
            recommendations.append('Add superiority metrics generation to Makefile')
    if any((self.project_root / 'src' / 'beast_mode').rglob('*performance*')):
        evidence.append('Performance measurement capabilities present')
        score += 0.2
    else:
        issues.append('Performance measurement missing')
        recommendations.append('Implement performance measurement and tracking')
    docs_path = self.project_root / 'docs'
    if docs_path.exists() and any(docs_path.rglob('*superiority*')):
        evidence.append('Superiority documentation present')
        score += 0.1
    else:
        issues.append('Superiority documentation missing')
        recommendations.append('Document concrete superiority evidence')
    execution_time = int((time.time() - start_time) * 1000)
    return ConsistencyResult(check_type=ConsistencyCheck.SUPERIORITY_EVIDENCE, passed=score >= 0.7, score=min(score, 1.0), evidence=evidence, issues=issues, recommendations=recommendations, execution_time_ms=execution_time)
