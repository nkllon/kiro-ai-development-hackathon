#!/usr/bin/env python3
"""
Verification Modules
===================

RMDDD-compliant modules for sophisticated indirect verification.
Each module handles a specific aspect of the verification process.
"""

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
import time
import json
import hashlib


@dataclass
class VerificationResult:
    """Result of a verification module"""

    module_name: str
    success: bool
    data: Dict[str, Any]
    confidence: float
    evidence: List[str] = None
    errors: List[str] = None


class VerificationModule(ABC):
    """Base class for verification modules following RMDDD principles"""

    def __init__(self, name: str):
        self.name = name
        self.errors = []

    @abstractmethod
    def verify(
        self, execution_data: Dict[str, Any], context: Dict[str, Any] = None
    ) -> VerificationResult:
        """Perform verification and return results"""
        pass

    def _add_error(self, error: str):
        """Add error to module error list"""
        self.errors.append(f"{self.name}: {error}")

    def get_module_info(self) -> Dict[str, Any]:
        """Get module information for debugging"""
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "errors": self.errors,
        }


class ExecutionAnalyzer(VerificationModule):
    """Analyzes execution characteristics to determine node type"""

    def __init__(self):
        super().__init__("ExecutionAnalyzer")
        self.baseline_characteristics = {
            "monolithic": {
                "execution_time_range": (0.1, 0.5),
                "memory_usage_range": (5, 20),
                "state_mutation_count": (10, 30),
                "message_count": (2, 5),
            },
            "modular": {
                "execution_time_range": (0.01, 0.1),
                "memory_usage_range": (1, 5),
                "state_mutation_count": (5, 15),
                "message_count": (3, 8),
            },
        }

    def verify(
        self, execution_data: Dict[str, Any], context: Dict[str, Any] = None
    ) -> VerificationResult:
        """Analyze execution characteristics"""
        try:
            evidence = []
            confidence = 0.0

            # Execution time analysis
            exec_time = execution_data.get("execution_time", 0)
            monolithic_time_range = self.baseline_characteristics["monolithic"][
                "execution_time_range"
            ]
            modular_time_range = self.baseline_characteristics["modular"][
                "execution_time_range"
            ]

            if modular_time_range[0] <= exec_time <= modular_time_range[1]:
                evidence.append(
                    f"Fast execution time ({exec_time:.4f}s) suggests modular approach"
                )
                confidence += 0.3
            elif monolithic_time_range[0] <= exec_time <= monolithic_time_range[1]:
                evidence.append(
                    f"Slower execution time ({exec_time:.4f}s) suggests monolithic approach"
                )
                confidence += 0.2

            # Memory usage analysis
            memory_usage = execution_data.get("memory_delta", 0)
            monolithic_memory_range = self.baseline_characteristics["monolithic"][
                "memory_usage_range"
            ]
            modular_memory_range = self.baseline_characteristics["modular"][
                "memory_usage_range"
            ]

            if modular_memory_range[0] <= memory_usage <= modular_memory_range[1]:
                evidence.append(
                    f"Low memory usage ({memory_usage:.2f}MB) suggests modular approach"
                )
                confidence += 0.2
            elif (
                monolithic_memory_range[0] <= memory_usage <= monolithic_memory_range[1]
            ):
                evidence.append(
                    f"High memory usage ({memory_usage:.2f}MB) suggests monolithic approach"
                )
                confidence += 0.1

            # State mutation analysis
            state_mutations = execution_data.get("state_mutation_count", 0)
            monolithic_state_range = self.baseline_characteristics["monolithic"][
                "state_mutation_count"
            ]
            modular_state_range = self.baseline_characteristics["modular"][
                "state_mutation_count"
            ]

            if modular_state_range[0] <= state_mutations <= modular_state_range[1]:
                evidence.append(
                    f"Moderate state mutations ({state_mutations}) suggests modular approach"
                )
                confidence += 0.2
            elif (
                monolithic_state_range[0]
                <= state_mutations
                <= monolithic_state_range[1]
            ):
                evidence.append(
                    f"High state mutations ({state_mutations}) suggests monolithic approach"
                )
                confidence += 0.1

            # Message count analysis
            message_count = execution_data.get("message_count", 0)
            monolithic_message_range = self.baseline_characteristics["monolithic"][
                "message_count"
            ]
            modular_message_range = self.baseline_characteristics["modular"][
                "message_count"
            ]

            if modular_message_range[0] <= message_count <= modular_message_range[1]:
                evidence.append(
                    f"Moderate message count ({message_count}) suggests modular approach"
                )
                confidence += 0.1
            elif (
                monolithic_message_range[0]
                <= message_count
                <= monolithic_message_range[1]
            ):
                evidence.append(
                    f"Low message count ({message_count}) suggests monolithic approach"
                )
                confidence += 0.05

            return VerificationResult(
                module_name=self.name,
                success=True,
                data={
                    "execution_time": exec_time,
                    "memory_usage": memory_usage,
                    "state_mutations": state_mutations,
                    "message_count": message_count,
                    "confidence": confidence,
                },
                confidence=confidence,
                evidence=evidence,
            )

        except Exception as e:
            self._add_error(str(e))
            return VerificationResult(
                module_name=self.name,
                success=False,
                data={},
                confidence=0.0,
                errors=self.errors,
            )


class StateMutationAnalyzer(VerificationModule):
    """Analyzes state mutations to determine node type"""

    def __init__(self):
        super().__init__("StateMutationAnalyzer")
        self.modular_indicators = [
            "investigation_results",
            "successful_modules",
            "total_modules",
            "PageStructureAnalyzer",
            "NavigationAnalyzer",
            "ContentAnalyzer",
            "DiagnosticTester",
            "InvestigationOrchestrator",
        ]

        self.monolithic_indicators = [
            "comprehensive_investigation",
            "run_diagnostic_tests",
            "analyze_page_structure",
            "analyze_navigation_elements",
            "analyze_content_elements",
        ]

    def verify(
        self, execution_data: Dict[str, Any], context: Dict[str, Any] = None
    ) -> VerificationResult:
        """Analyze state mutations to determine node type"""
        try:
            evidence = []
            confidence = 0.0

            initial_state = execution_data.get("initial_state", {})
            final_state = execution_data.get("final_state", {})

            # Count mutations
            mutation_count = 0
            for key, value in final_state.items():
                if key not in initial_state or initial_state[key] != value:
                    mutation_count += 1

            evidence.append(f"State mutations: {mutation_count}")

            # Look for modular indicators
            state_str = self._safe_state_to_string(final_state)
            modular_found = []
            for indicator in self.modular_indicators:
                if indicator in state_str:
                    modular_found.append(indicator)

            if modular_found:
                evidence.append(f"Modular indicators found: {modular_found}")
                confidence += len(modular_found) * 0.1

            # Look for monolithic indicators
            monolithic_found = []
            for indicator in self.monolithic_indicators:
                if indicator in state_str:
                    monolithic_found.append(indicator)

            if monolithic_found:
                evidence.append(f"Monolithic indicators found: {monolithic_found}")
                confidence -= len(monolithic_found) * 0.1

            # Create state signature
            state_signature = hashlib.md5(state_str.encode()).hexdigest()[:16]

            # Determine mutation pattern
            if len(modular_found) > len(monolithic_found):
                evidence.append("State mutations favor modular approach")
                confidence += 0.2
            elif len(monolithic_found) > len(modular_found):
                evidence.append("State mutations favor monolithic approach")
                confidence -= 0.2

            return VerificationResult(
                module_name=self.name,
                success=True,
                data={
                    "mutation_count": mutation_count,
                    "modular_indicators": modular_found,
                    "monolithic_indicators": monolithic_found,
                    "state_signature": state_signature,
                    "confidence": confidence,
                },
                confidence=confidence,
                evidence=evidence,
            )

        except Exception as e:
            self._add_error(str(e))
            return VerificationResult(
                module_name=self.name,
                success=False,
                data={},
                confidence=0.0,
                errors=self.errors,
            )

    def _safe_state_to_string(self, state: Dict[str, Any]) -> str:
        """Safely convert state to string for analysis"""
        try:
            return json.dumps(state, sort_keys=True, default=str)
        except (TypeError, ValueError):
            # Fallback for non-serializable objects
            return str(state)


class PerformanceAnalyzer(VerificationModule):
    """Analyzes performance characteristics"""

    def __init__(self):
        super().__init__("PerformanceAnalyzer")
        self.performance_baselines = {
            "monolithic": {
                "min_execution_time": 0.05,
                "max_execution_time": 0.5,
                "min_memory_delta": 2.0,
                "max_memory_delta": 20.0,
                "execution_variance": 0.1,
            },
            "modular": {
                "min_execution_time": 0.001,
                "max_execution_time": 0.1,
                "min_memory_delta": 0.5,
                "max_memory_delta": 5.0,
                "execution_variance": 0.05,
            },
        }

    def verify(
        self, execution_data: Dict[str, Any], context: Dict[str, Any] = None
    ) -> VerificationResult:
        """Analyze performance characteristics"""
        try:
            evidence = []
            confidence = 0.0

            execution_time = execution_data.get("execution_time", 0)
            memory_delta = execution_data.get("memory_delta", 0)

            # Analyze execution time
            monolithic_time_range = self.performance_baselines["monolithic"]
            modular_time_range = self.performance_baselines["modular"]

            if (
                modular_time_range["min_execution_time"]
                <= execution_time
                <= modular_time_range["max_execution_time"]
            ):
                evidence.append(
                    f"Execution time ({execution_time:.4f}s) suggests modular approach"
                )
                confidence += 0.4
            elif (
                monolithic_time_range["min_execution_time"]
                <= execution_time
                <= monolithic_time_range["max_execution_time"]
            ):
                evidence.append(
                    f"Execution time ({execution_time:.4f}s) suggests monolithic approach"
                )
                confidence += 0.3

            # Analyze memory usage
            if (
                modular_time_range["min_memory_delta"]
                <= memory_delta
                <= modular_time_range["max_memory_delta"]
            ):
                evidence.append(
                    f"Memory usage ({memory_delta:.2f}MB) suggests modular approach"
                )
                confidence += 0.3
            elif (
                monolithic_time_range["min_memory_delta"]
                <= memory_delta
                <= monolithic_time_range["max_memory_delta"]
            ):
                evidence.append(
                    f"Memory usage ({memory_delta:.2f}MB) suggests monolithic approach"
                )
                confidence += 0.2

            # Determine performance type
            if confidence >= 0.6:
                performance_type = "modular"
            elif confidence >= 0.3:
                performance_type = "monolithic"
            else:
                performance_type = "unclear"

            evidence.append(f"Performance type: {performance_type}")

            return VerificationResult(
                module_name=self.name,
                success=True,
                data={
                    "execution_time": execution_time,
                    "memory_delta": memory_delta,
                    "performance_type": performance_type,
                    "confidence": confidence,
                },
                confidence=confidence,
                evidence=evidence,
            )

        except Exception as e:
            self._add_error(str(e))
            return VerificationResult(
                module_name=self.name,
                success=False,
                data={},
                confidence=0.0,
                errors=self.errors,
            )


class ResultCombiner(VerificationModule):
    """Combines results from multiple verification modules"""

    def __init__(self):
        super().__init__("ResultCombiner")

    def verify(
        self, execution_data: Dict[str, Any], context: Dict[str, Any] = None
    ) -> VerificationResult:
        """Combine results from multiple verification modules"""
        try:
            evidence = []
            confidence = 0.0

            # Get results from other modules
            module_results = context.get("module_results", {})

            # Combine confidence scores
            total_confidence = 0.0
            successful_modules = 0

            for module_name, result in module_results.items():
                if result.success:
                    total_confidence += result.confidence
                    successful_modules += 1
                    evidence.extend(result.evidence or [])

            if successful_modules > 0:
                confidence = total_confidence / successful_modules

            # Determine final node type
            node_type = "unknown"
            if confidence >= 0.7:
                node_type = "refactored_modular"
            elif confidence >= 0.4:
                node_type = "likely_refactored"
            elif confidence < 0.0:
                node_type = "monolithic"

            evidence.append(f"Combined confidence: {confidence:.2f}")
            evidence.append(f"Node type: {node_type}")

            return VerificationResult(
                module_name=self.name,
                success=True,
                data={
                    "total_confidence": confidence,
                    "successful_modules": successful_modules,
                    "node_type": node_type,
                    "module_results": module_results,
                },
                confidence=confidence,
                evidence=evidence,
            )

        except Exception as e:
            self._add_error(str(e))
            return VerificationResult(
                module_name=self.name,
                success=False,
                data={},
                confidence=0.0,
                errors=self.errors,
            )


class VerificationReporter(VerificationModule):
    """Reports verification results"""

    def __init__(self):
        super().__init__("VerificationReporter")

    def verify(
        self, execution_data: Dict[str, Any], context: Dict[str, Any] = None
    ) -> VerificationResult:
        """Generate verification report"""
        try:
            evidence = []
            confidence = 0.0

            # Get combined results
            combined_result = context.get("combined_result")
            if combined_result and combined_result.success:
                confidence = combined_result.confidence
                evidence.extend(combined_result.evidence or [])

                # Generate report
                report = {
                    "verification_status": (
                        "success" if confidence >= 0.7 else "uncertain"
                    ),
                    "node_type": combined_result.data.get("node_type", "unknown"),
                    "confidence": confidence,
                    "evidence_count": len(evidence),
                    "timestamp": time.time(),
                }

                evidence.append(
                    f"Verification report generated: {report['verification_status']}"
                )

                return VerificationResult(
                    module_name=self.name,
                    success=True,
                    data=report,
                    confidence=confidence,
                    evidence=evidence,
                )
            else:
                evidence.append("No combined results available for reporting")
                return VerificationResult(
                    module_name=self.name,
                    success=False,
                    data={},
                    confidence=0.0,
                    evidence=evidence,
                )

        except Exception as e:
            self._add_error(str(e))
            return VerificationResult(
                module_name=self.name,
                success=False,
                data={},
                confidence=0.0,
                errors=self.errors,
            )


class VerificationOrchestrator:
    """Orchestrates multiple verification modules"""

    def __init__(self):
        self.modules = [
            ExecutionAnalyzer(),
            StateMutationAnalyzer(),
            PerformanceAnalyzer(),
            ResultCombiner(),
            VerificationReporter(),
        ]

    def verify_integration(self, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run all verification modules and return combined results"""

        print("🔬 Running modular verification...")

        results = {}
        context = {}

        # Run individual verification modules
        for module in self.modules:
            print(f"   🔍 Running {module.name}...")
            result = module.verify(execution_data, context)
            results[module.name] = result

            if result.success:
                print(f"   ✅ {module.name}: {result.confidence:.2f} confidence")
            else:
                print(f"   ❌ {module.name}: Failed")

        # Combine results
        context["module_results"] = results
        combiner = ResultCombiner()
        combined_result = combiner.verify(execution_data, context)
        results["CombinedResult"] = combined_result

        # Generate report
        context["combined_result"] = combined_result
        reporter = VerificationReporter()
        report_result = reporter.verify(execution_data, context)
        results["Report"] = report_result

        # Return summary
        return {
            "success": combined_result.success,
            "node_type": combined_result.data.get("node_type", "unknown"),
            "confidence": combined_result.confidence,
            "evidence": combined_result.evidence or [],
            "report": report_result.data if report_result.success else {},
            "module_results": results,
        }

    def get_module_status(self) -> Dict[str, Any]:
        """Get status of all modules for debugging"""
        return {
            "modules": [module.get_module_info() for module in self.modules],
            "total_modules": len(self.modules),
        }
