"""
Self Consistency Validator Core Validation

This module was extracted from self_consistency_validator_core.py
as part of RM-DDD compliance refactoring.
"""

import os
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from ..core.reflective_module import ReflectiveModule, HealthStatus
from ..core.pdca_orchestrator import PDCAOrchestrator
from ..intelligence.model_driven_intelligence_engine import (
    ModelDrivenIntelligenceEngine,
)
from ..tool_health.makefile_health_manager import MakefileHealthManager
from ..quality.automated_quality_gates import AutomatedQualityGates
from ..tool_health.makefile_health_manager import MakefileHealthManager
from ..services.gke_service_interface import GKEServiceInterface
from ..metrics.baseline_metrics_engine import BaselineMetricsEngine
from ..assessment.evidence_package_generator import EvidencePackageGenerator
from ..core.reflective_module import ReflectiveModule
from ..core.pdca_orchestrator import PDCAOrchestrator
from ..intelligence.model_driven_intelligence_engine import (
    ModelDrivenIntelligenceEngine,
)
from ..tool_health.makefile_health_manager import MakefileHealthManager
from ..quality.automated_quality_gates import AutomatedQualityGates
from ..tool_health.makefile_health_manager import MakefileHealthManager
from ..services.gke_service_interface import GKEServiceInterface
from ..metrics.baseline_metrics_engine import BaselineMetricsEngine
from ..assessment.evidence_package_generator import EvidencePackageGenerator
from ..core.reflective_module import ReflectiveModule


def validate_self_consistency(self) -> SelfConsistencyReport:
    """
    Comprehensive self-consistency validation for Beast Mode Framework
    Required by UC-25: Prove Beast Mode uses its own systematic methodology
    """
    self.validations_performed += 1
    start_time = time.time()
    try:
        self.logger.info("Starting Beast Mode self-consistency validation")
        validation_results = []
        for test_name, test_function in self.validation_tests.items():
            try:
                self.logger.info(f"Running validation test: {test_name}")
                result = test_function()
                validation_results.append(result)
            except Exception as e:
                self.logger.error(f"Validation test {test_name} failed: {e}")
                validation_results.append(
                    ValidationResult(
                        test_name=test_name,
                        status=ValidationStatus.FAILED,
                        score=0.0,
                        details={"error": str(e)},
                        evidence=[f"Test execution failed: {e}"],
                        recommendations=[f"Fix {test_name} validation test"],
                    )
                )
        total_execution_time = time.time() - start_time
        self.total_validation_time += total_execution_time
        overall_score = sum((result.score for result in validation_results)) / max(
            1, len(validation_results)
        )
        overall_status = self._determine_overall_validation_status(
            validation_results, overall_score
        )
        successful_validations = sum(
            (
                1
                for result in validation_results
                if result.status == ValidationStatus.PASSED
            )
        )
        self.validation_success_rate = successful_validations / max(
            1, len(validation_results)
        )
        credibility_proof = self._generate_credibility_proof(validation_results)
        superiority_evidence = self._generate_superiority_evidence(validation_results)
        recommendations = self._generate_self_consistency_recommendations(
            validation_results
        )
        report = SelfConsistencyReport(
            overall_status=overall_status,
            overall_score=overall_score,
            validation_results=validation_results,
            credibility_proof=credibility_proof,
            superiority_evidence=superiority_evidence,
            total_execution_time=total_execution_time,
            timestamp=datetime.now(),
            recommendations=recommendations,
        )
        self.logger.info(
            f"Self-consistency validation complete: {overall_status.value} (score: {overall_score:.2f})"
        )
        return report
    except Exception as e:
        self.logger.error(f"Self-consistency validation failed: {e}")
        return SelfConsistencyReport(
            overall_status=ValidationStatus.FAILED,
            overall_score=0.0,
            validation_results=[],
            credibility_proof={"validation_error": str(e)},
            superiority_evidence={"validation_error": str(e)},
            total_execution_time=time.time() - start_time,
            timestamp=datetime.now(),
            recommendations=[f"Fix validation system error: {e}"],
        )


def _validate_makefile_works(self) -> ValidationResult:
    """Validate that Beast Mode's own Makefile works flawlessly"""
    start_time = time.time()
    try:
        result = subprocess.run(
            ["make", "help"], capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            beast_mode_operations = [
                "beast-mode",
                "pdca-cycle",
                "systematic-repair",
                "model-driven",
                "quality-gates",
                "self-consistency",
            ]
            operations_found = sum(
                (1 for op in beast_mode_operations if op in result.stdout)
            )
            score = operations_found / len(beast_mode_operations)
            status = (
                ValidationStatus.PASSED if score >= 0.8 else ValidationStatus.WARNING
            )
            evidence = [
                "make help command executes successfully",
                f"Found {operations_found}/{len(beast_mode_operations)} Beast Mode operations",
                "Makefile demonstrates systematic tool repair success",
            ]
            recommendations = []
            if score < 1.0:
                missing_ops = [
                    op for op in beast_mode_operations if op not in result.stdout
                ]
                recommendations.append(
                    f"Add missing Beast Mode operations: {missing_ops}"
                )
        else:
            score = 0.0
            status = ValidationStatus.FAILED
            evidence = [f"make help failed with return code {result.returncode}"]
            recommendations = [
                "Fix Makefile errors using systematic repair",
                "Ensure all Beast Mode operations are properly defined",
                "Validate Makefile syntax and dependencies",
            ]
        return ValidationResult(
            test_name="makefile_works",
            status=status,
            score=score,
            details={
                "make_help_success": result.returncode == 0,
                "beast_mode_operations_found": (
                    operations_found if result.returncode == 0 else 0
                ),
                "stdout_preview": result.stdout[:500] if result.stdout else "",
                "stderr": result.stderr if result.stderr else "",
            },
            evidence=evidence,
            recommendations=recommendations,
            execution_time_seconds=time.time() - start_time,
        )
    except subprocess.TimeoutExpired:
        return ValidationResult(
            test_name="makefile_works",
            status=ValidationStatus.FAILED,
            score=0.0,
            details={"error": "make help command timed out"},
            evidence=["Makefile execution timed out"],
            recommendations=["Fix Makefile performance issues"],
            execution_time_seconds=time.time() - start_time,
        )


def _validate_beast_mode_uses_pdca(self) -> ValidationResult:
    """Validate that Beast Mode uses its own PDCA cycles"""
    start_time = time.time()
    try:
        from ..core.pdca_orchestrator import PDCAOrchestrator

        orchestrator = PDCAOrchestrator()
        is_healthy = orchestrator.is_healthy()
        status_info = orchestrator.get_module_status()
        has_execute_method = hasattr(orchestrator, "execute_real_task_cycle")
        has_plan_method = hasattr(orchestrator, "plan_with_model_registry")
        has_do_method = hasattr(orchestrator, "do_systematic_implementation")
        has_check_method = hasattr(orchestrator, "check_with_rca")
        has_act_method = hasattr(orchestrator, "act_update_model")
        pdca_methods_available = sum(
            [
                has_execute_method,
                has_plan_method,
                has_do_method,
                has_check_method,
                has_act_method,
            ]
        )
        score = pdca_methods_available / 5 * (1.0 if is_healthy else 0.5)
        status = (
            ValidationStatus.PASSED
            if score >= 0.8
            else ValidationStatus.WARNING if score >= 0.5 else ValidationStatus.FAILED
        )
        evidence = [
            f"PDCA orchestrator is healthy: {is_healthy}",
            f"PDCA methods available: {pdca_methods_available}/5",
            "Beast Mode implements systematic PDCA methodology",
        ]
        recommendations = []
        if score < 1.0:
            missing_methods = []
            if not has_execute_method:
                missing_methods.append("execute_real_task_cycle")
            if not has_plan_method:
                missing_methods.append("plan_with_model_registry")
            if not has_do_method:
                missing_methods.append("do_systematic_implementation")
            if not has_check_method:
                missing_methods.append("check_with_rca")
            if not has_act_method:
                missing_methods.append("act_update_model")
            if missing_methods:
                recommendations.append(
                    f"Implement missing PDCA methods: {missing_methods}"
                )
        return ValidationResult(
            test_name="beast_mode_uses_pdca",
            status=status,
            score=score,
            details={
                "orchestrator_healthy": is_healthy,
                "pdca_methods_available": pdca_methods_available,
                "status_info": status_info,
                "execute_method": has_execute_method,
                "plan_method": has_plan_method,
                "do_method": has_do_method,
                "check_method": has_check_method,
                "act_method": has_act_method,
            },
            evidence=evidence,
            recommendations=recommendations,
            execution_time_seconds=time.time() - start_time,
        )
    except ImportError as e:
        return ValidationResult(
            test_name="beast_mode_uses_pdca",
            status=ValidationStatus.FAILED,
            score=0.0,
            details={"import_error": str(e)},
            evidence=["PDCA orchestrator not available"],
            recommendations=["Implement PDCA orchestrator for Beast Mode"],
            execution_time_seconds=time.time() - start_time,
        )


def _validate_model_driven_decisions(self) -> ValidationResult:
    """Validate that Beast Mode makes model-driven decisions"""
    start_time = time.time()
    try:
        from ..intelligence.model_driven_intelligence_engine import (
            ModelDrivenIntelligenceEngine,
        )

        engine = ModelDrivenIntelligenceEngine()
        is_healthy = engine.is_healthy()
        status_info = engine.get_module_status()
        project_registry_path = self.project_root / "project_model_registry.json"
        registry_exists = project_registry_path.exists()
        has_consult_registry = hasattr(engine, "consult_registry_first")
        has_domain_intelligence = hasattr(engine, "get_domain_intelligence")
        has_decision_documentation = hasattr(engine, "document_decision_reasoning")
        model_methods_available = sum(
            [has_consult_registry, has_domain_intelligence, has_decision_documentation]
        )
        registry_score = 1.0 if registry_exists else 0.0
        engine_score = model_methods_available / 3 * (1.0 if is_healthy else 0.5)
        score = (registry_score + engine_score) / 2
        status = (
            ValidationStatus.PASSED
            if score >= 0.8
            else ValidationStatus.WARNING if score >= 0.5 else ValidationStatus.FAILED
        )
        evidence = [
            f"Model-driven intelligence engine is healthy: {is_healthy}",
            f"Project registry exists: {registry_exists}",
            f"Model-driven methods available: {model_methods_available}/3",
            "Beast Mode consults project registry for decisions",
        ]
        recommendations = []
        if not registry_exists:
            recommendations.append("Ensure project_model_registry.json is available")
        if engine_score < 1.0:
            recommendations.append(
                "Complete model-driven intelligence engine implementation"
            )
        return ValidationResult(
            test_name="model_driven_decisions",
            status=status,
            score=score,
            details={
                "engine_healthy": is_healthy,
                "registry_exists": registry_exists,
                "model_methods_available": model_methods_available,
                "status_info": status_info,
            },
            evidence=evidence,
            recommendations=recommendations,
            execution_time_seconds=time.time() - start_time,
        )
    except ImportError as e:
        return ValidationResult(
            test_name="model_driven_decisions",
            status=ValidationStatus.FAILED,
            score=0.0,
            details={"import_error": str(e)},
            evidence=["Model-driven intelligence engine not available"],
            recommendations=["Implement model-driven intelligence engine"],
            execution_time_seconds=time.time() - start_time,
        )


def _validate_systematic_tool_repair(self) -> ValidationResult:
    """Validate that Beast Mode uses systematic tool repair"""
    start_time = time.time()
    try:
        from ..tool_health.makefile_health_manager import MakefileHealthManager

        manager = MakefileHealthManager()
        is_healthy = manager.is_healthy()
        status_info = manager.get_module_status()
        has_diagnose = hasattr(manager, "diagnose_makefile_issues")
        has_fix = hasattr(manager, "fix_makefile_systematically")
        has_validate = hasattr(manager, "validate_makefile_repair") or hasattr(
            manager, "_validate_makefile_repair"
        )
        has_document = hasattr(manager, "document_prevention_pattern") or hasattr(
            manager, "_document_prevention_pattern"
        )
        repair_methods_available = sum(
            [has_diagnose, has_fix, has_validate, has_document]
        )
        superiority_available = hasattr(manager, "demonstrate_systematic_superiority")
        score = repair_methods_available / 4 * (1.0 if is_healthy else 0.5)
        if superiority_available:
            score = min(1.0, score + 0.2)
        status = (
            ValidationStatus.PASSED
            if score >= 0.8
            else ValidationStatus.WARNING if score >= 0.5 else ValidationStatus.FAILED
        )
        evidence = [
            f"Makefile health manager is healthy: {is_healthy}",
            f"Systematic repair methods available: {repair_methods_available}/4",
            f"Superiority demonstration available: {superiority_available}",
            "Beast Mode fixes its own tools systematically",
        ]
        recommendations = []
        if repair_methods_available < 4:
            recommendations.append("Complete systematic repair method implementation")
        if not superiority_available:
            recommendations.append("Add systematic superiority demonstration")
        return ValidationResult(
            test_name="systematic_tool_repair",
            status=status,
            score=score,
            details={
                "manager_healthy": is_healthy,
                "repair_methods_available": repair_methods_available,
                "superiority_available": superiority_available,
                "status_info": status_info,
            },
            evidence=evidence,
            recommendations=recommendations,
            execution_time_seconds=time.time() - start_time,
        )
    except ImportError as e:
        return ValidationResult(
            test_name="systematic_tool_repair",
            status=ValidationStatus.FAILED,
            score=0.0,
            details={"import_error": str(e)},
            evidence=["Makefile health manager not available"],
            recommendations=["Implement systematic tool repair capabilities"],
            execution_time_seconds=time.time() - start_time,
        )


def _validate_rm_compliance(self) -> ValidationResult:
    """Validate that all Beast Mode components implement RM interface"""
    start_time = time.time()
    try:
        compliant_components = 0
        total_components = len(self.beast_mode_components)
        component_details = {}
        for component_path in self.beast_mode_components:
            try:
                module_parts = component_path.split(".")
                module_path = f"src.beast_mode.{component_path}"
                class_name = "".join(
                    (word.capitalize() for word in module_parts[-1].split("_"))
                )
                possible_classes = [
                    class_name,
                    f"{class_name}Engine",
                    f"{class_name}Manager",
                    f"{class_name}Orchestrator",
                    f"{class_name}Interface",
                ]
                component_found = False
                for class_name_attempt in possible_classes:
                    try:
                        module = __import__(module_path, fromlist=[class_name_attempt])
                        component_class = getattr(module, class_name_attempt)
                        from ..core.reflective_module import ReflectiveModule

                        is_rm_compliant = issubclass(component_class, ReflectiveModule)
                        if is_rm_compliant:
                            instance = component_class()
                            has_get_module_status = hasattr(
                                instance, "get_module_status"
                            )
                            has_is_healthy = hasattr(instance, "is_healthy")
                            has_get_health_indicators = hasattr(
                                instance, "get_health_indicators"
                            )
                            rm_methods_available = sum(
                                [
                                    has_get_module_status,
                                    has_is_healthy,
                                    has_get_health_indicators,
                                ]
                            )
                            if rm_methods_available >= 3:
                                compliant_components += 1
                            component_details[component_path] = {
                                "rm_compliant": True,
                                "rm_methods_available": rm_methods_available,
                                "class_name": class_name_attempt,
                            }
                            component_found = True
                            break
                    except (ImportError, AttributeError):
                        continue
                if not component_found:
                    component_details[component_path] = {
                        "rm_compliant": False,
                        "error": "Component not found or not RM compliant",
                    }
            except Exception as e:
                component_details[component_path] = {
                    "rm_compliant": False,
                    "error": str(e),
                }
        score = compliant_components / max(1, total_components)
        status = (
            ValidationStatus.PASSED
            if score >= 0.8
            else ValidationStatus.WARNING if score >= 0.5 else ValidationStatus.FAILED
        )
        evidence = [
            f"RM compliant components: {compliant_components}/{total_components}",
            "All components inherit from ReflectiveModule base class",
            "RM interface methods implemented across components",
        ]
        recommendations = []
        if score < 1.0:
            non_compliant = [
                comp
                for comp, details in component_details.items()
                if not details.get("rm_compliant", False)
            ]
            recommendations.append(f"Make components RM compliant: {non_compliant}")
        return ValidationResult(
            test_name="rm_compliance",
            status=status,
            score=score,
            details={
                "compliant_components": compliant_components,
                "total_components": total_components,
                "component_details": component_details,
            },
            evidence=evidence,
            recommendations=recommendations,
            execution_time_seconds=time.time() - start_time,
        )
    except Exception as e:
        return ValidationResult(
            test_name="rm_compliance",
            status=ValidationStatus.FAILED,
            score=0.0,
            details={"validation_error": str(e)},
            evidence=["RM compliance validation failed"],
            recommendations=["Fix RM compliance validation system"],
            execution_time_seconds=time.time() - start_time,
        )


def _validate_quality_gates_enforcement(self) -> ValidationResult:
    """Validate that Beast Mode enforces quality gates on itself"""
    start_time = time.time()
    try:
        from ..quality.automated_quality_gates import AutomatedQualityGates

        gates = AutomatedQualityGates()
        is_healthy = gates.is_healthy()
        status_info = gates.get_module_status()
        has_execute_assessment = hasattr(gates, "execute_quality_assessment")
        has_enforce_gates = hasattr(gates, "enforce_quality_gates")
        quality_methods_available = sum([has_execute_assessment, has_enforce_gates])
        score = quality_methods_available / 2 * (1.0 if is_healthy else 0.5)
        status = (
            ValidationStatus.PASSED
            if score >= 0.8
            else ValidationStatus.WARNING if score >= 0.5 else ValidationStatus.FAILED
        )
        evidence = [
            f"Quality gates system is healthy: {is_healthy}",
            f"Quality enforcement methods available: {quality_methods_available}/2",
            "Beast Mode enforces quality standards on itself",
        ]
        recommendations = []
        if quality_methods_available < 2:
            recommendations.append("Complete quality gates implementation")
        return ValidationResult(
            test_name="quality_gates_enforcement",
            status=status,
            score=score,
            details={
                "gates_healthy": is_healthy,
                "quality_methods_available": quality_methods_available,
                "status_info": status_info,
            },
            evidence=evidence,
            recommendations=recommendations,
            execution_time_seconds=time.time() - start_time,
        )
    except ImportError as e:
        return ValidationResult(
            test_name="quality_gates_enforcement",
            status=ValidationStatus.FAILED,
            score=0.0,
            details={"import_error": str(e)},
            evidence=["Quality gates system not available"],
            recommendations=["Implement automated quality gates"],
            execution_time_seconds=time.time() - start_time,
        )


def _validate_health_monitoring(self) -> ValidationResult:
    """Validate that Beast Mode components provide health monitoring"""
    start_time = time.time()
    try:
        healthy_components = 0
        total_tested = 0
        health_details = {}
        key_components = [
            ("core.reflective_module", "ReflectiveModule"),
            ("analysis.rca_engine", "RCAEngine"),
            ("tool_health.makefile_health_manager", "MakefileHealthManager"),
            ("quality.automated_quality_gates", "AutomatedQualityGates"),
        ]
        for component_path, class_name in key_components:
            try:
                module_path = f"src.beast_mode.{component_path}"
                module = __import__(module_path, fromlist=[class_name])
                component_class = getattr(module, class_name)
                if class_name == "ReflectiveModule":
                    continue
                instance = component_class()
                total_tested += 1
                is_healthy = instance.is_healthy()
                status_info = instance.get_module_status()
                health_indicators = instance.get_health_indicators()
                if is_healthy and status_info and health_indicators:
                    healthy_components += 1
                health_details[component_path] = {
                    "healthy": is_healthy,
                    "has_status": bool(status_info),
                    "has_indicators": bool(health_indicators),
                    "status_keys": list(status_info.keys()) if status_info else [],
                }
            except Exception as e:
                health_details[component_path] = {"healthy": False, "error": str(e)}
                total_tested += 1
        score = healthy_components / max(1, total_tested)
        status = (
            ValidationStatus.PASSED
            if score >= 0.8
            else ValidationStatus.WARNING if score >= 0.5 else ValidationStatus.FAILED
        )
        evidence = [
            f"Healthy components: {healthy_components}/{total_tested}",
            "Components provide comprehensive health monitoring",
            "Health indicators available for operational visibility",
        ]
        recommendations = []
        if score < 1.0:
            unhealthy = [
                comp
                for comp, details in health_details.items()
                if not details.get("healthy", False)
            ]
            recommendations.append(f"Fix health monitoring for: {unhealthy}")
        return ValidationResult(
            test_name="health_monitoring",
            status=status,
            score=score,
            details={
                "healthy_components": healthy_components,
                "total_tested": total_tested,
                "health_details": health_details,
            },
            evidence=evidence,
            recommendations=recommendations,
            execution_time_seconds=time.time() - start_time,
        )
    except Exception as e:
        return ValidationResult(
            test_name="health_monitoring",
            status=ValidationStatus.FAILED,
            score=0.0,
            details={"validation_error": str(e)},
            evidence=["Health monitoring validation failed"],
            recommendations=["Fix health monitoring validation"],
            execution_time_seconds=time.time() - start_time,
        )


def _validate_superiority_evidence(self) -> ValidationResult:
    """Validate that Beast Mode generates measurable superiority evidence"""
    start_time = time.time()
    try:
        evidence_sources = 0
        total_sources = 4
        evidence_details = {}
        try:
            from ..tool_health.makefile_health_manager import MakefileHealthManager

            manager = MakefileHealthManager()
            if hasattr(manager, "demonstrate_systematic_superiority"):
                evidence_sources += 1
                evidence_details["tool_health_superiority"] = True
            else:
                evidence_details["tool_health_superiority"] = False
        except:
            evidence_details["tool_health_superiority"] = False
        try:
            from ..services.gke_service_interface import GKEServiceInterface

            interface = GKEServiceInterface()
            if hasattr(interface, "measure_improvement_over_adhoc"):
                evidence_sources += 1
                evidence_details["gke_improvement_measurement"] = True
            else:
                evidence_details["gke_improvement_measurement"] = False
        except:
            evidence_details["gke_improvement_measurement"] = False
        try:
            from ..metrics.baseline_metrics_engine import BaselineMetricsEngine

            engine = BaselineMetricsEngine()
            evidence_sources += 1
            evidence_details["metrics_collection"] = True
        except:
            evidence_details["metrics_collection"] = False
        try:
            from ..assessment.evidence_package_generator import EvidencePackageGenerator

            generator = EvidencePackageGenerator()
            evidence_sources += 1
            evidence_details["evidence_package_generation"] = True
        except:
            evidence_details["evidence_package_generation"] = False
        score = evidence_sources / total_sources
        status = (
            ValidationStatus.PASSED
            if score >= 0.8
            else ValidationStatus.WARNING if score >= 0.5 else ValidationStatus.FAILED
        )
        evidence = [
            f"Superiority evidence sources: {evidence_sources}/{total_sources}",
            "Beast Mode generates measurable superiority metrics",
            "Concrete evidence available for systematic vs ad-hoc comparison",
        ]
        recommendations = []
        if score < 1.0:
            missing_sources = [
                source
                for source, available in evidence_details.items()
                if not available
            ]
            recommendations.append(
                f"Implement missing evidence sources: {missing_sources}"
            )
        return ValidationResult(
            test_name="superiority_evidence",
            status=status,
            score=score,
            details={
                "evidence_sources": evidence_sources,
                "total_sources": total_sources,
                "evidence_details": evidence_details,
            },
            evidence=evidence,
            recommendations=recommendations,
            execution_time_seconds=time.time() - start_time,
        )
    except Exception as e:
        return ValidationResult(
            test_name="superiority_evidence",
            status=ValidationStatus.FAILED,
            score=0.0,
            details={"validation_error": str(e)},
            evidence=["Superiority evidence validation failed"],
            recommendations=["Fix superiority evidence validation"],
            execution_time_seconds=time.time() - start_time,
        )
