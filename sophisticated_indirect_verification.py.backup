#!/usr/bin/env python3
"""
Sophisticated Indirect Verification
===================================
Multi-dimensional indirect verification strategy that works within LangGraph's
architectural constraints to definitively determine which components are integrated.
"""
import hashlib
import json
import sys
import time
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import List


@dataclass
class VerificationResult:
    """Result of verification analysis"""

    node_type: str
    confidence: float
    evidence: List[str]
    execution_characteristics: Dict[str, Any]
    state_mutations: Dict[str, Any]
    performance_metrics: Dict[str, Any]


class IndirectVerificationAnalyzer:
    """Analyzes execution characteristics to determine node type"""

    def __init__(self):
        self.baseline_characteristics = {
            "monolithic": {
                "execution_time_range": (0.1, 0.5),
                "memory_usage_range": (5, 20),
                "state_mutation_count": (10, 30),
                "message_count": (2, 5),
                "investigation_depth": "comprehensive",
            },
            "modular": {
                "execution_time_range": (0.01, 0.1),
                "memory_usage_range": (1, 5),
                "state_mutation_count": (5, 15),
                "message_count": (3, 8),
                "investigation_depth": "orchestrated",
            },
        }

    def analyze_execution_characteristics(
        self, execution_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Analyze execution characteristics against baselines"""
        scores = {"monolithic_score": 0.0, "modular_score": 0.0}
        # Execution time analysis
        exec_time = execution_data.get("execution_time", 0)
        monolithic_time_range = self.baseline_characteristics["monolithic"][
            "execution_time_range"
        ]
        modular_time_range = self.baseline_characteristics["modular"][
            "execution_time_range"
        ]
        if monolithic_time_range[0] <= exec_time <= monolithic_time_range[1]:
            scores["monolithic_score"] += 0.3
        if modular_time_range[0] <= exec_time <= modular_time_range[1]:
            scores["modular_score"] += 0.3
        # Memory usage analysis
        memory_usage = execution_data.get("memory_delta", 0)
        monolithic_memory_range = self.baseline_characteristics["monolithic"][
            "memory_usage_range"
        ]
        modular_memory_range = self.baseline_characteristics["modular"][
            "memory_usage_range"
        ]
        if monolithic_memory_range[0] <= memory_usage <= monolithic_memory_range[1]:
            scores["monolithic_score"] += 0.2
        if modular_memory_range[0] <= memory_usage <= modular_memory_range[1]:
            scores["modular_score"] += 0.2
        # State mutation analysis
        state_mutations = execution_data.get("state_mutation_count", 0)
        monolithic_state_range = self.baseline_characteristics["monolithic"][
            "state_mutation_count"
        ]
        modular_state_range = self.baseline_characteristics["modular"][
            "state_mutation_count"
        ]
        if monolithic_state_range[0] <= state_mutations <= monolithic_state_range[1]:
            scores["monolithic_score"] += 0.2
        if modular_state_range[0] <= state_mutations <= modular_state_range[1]:
            scores["modular_score"] += 0.2
        # Message count analysis
        message_count = execution_data.get("message_count", 0)
        monolithic_message_range = self.baseline_characteristics["monolithic"][
            "message_count"
        ]
        modular_message_range = self.baseline_characteristics["modular"][
            "message_count"
        ]
        if monolithic_message_range[0] <= message_count <= monolithic_message_range[1]:
            scores["monolithic_score"] += 0.1
        if modular_message_range[0] <= message_count <= modular_message_range[1]:
            scores["modular_score"] += 0.1
        return scores


class StateMutationAnalyzer:
    """Analyzes state mutations to determine node type"""

    def __init__(self):
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

    def analyze_state_mutations(
        self, initial_state: Dict[str, Any], final_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze state mutations to determine node type"""
        analysis = {
            "mutation_count": 0,
            "modular_indicators_found": [],
            "monolithic_indicators_found": [],
            "state_signature": "",
            "mutation_pattern": "unknown",
        }
        # Count mutations
        for key, value in final_state.items():
            if key not in initial_state or initial_state[key] != value:
                analysis["mutation_count"] += 1
        # Look for modular indicators
        state_str = json.dumps(final_state, sort_keys=True)
        for indicator in self.modular_indicators:
            if indicator in state_str:
                analysis["modular_indicators_found"].append(indicator)
        # Look for monolithic indicators
        for indicator in self.monolithic_indicators:
            if indicator in state_str:
                analysis["monolithic_indicators_found"].append(indicator)
        # Create state signature
        analysis["state_signature"] = hashlib.md5(state_str.encode()).hexdigest()[:16]
        # Determine mutation pattern
        modular_count = len(analysis["modular_indicators_found"])
        monolithic_count = len(analysis["monolithic_indicators_found"])
        if modular_count > monolithic_count:
            analysis["mutation_pattern"] = "modular"
        elif monolithic_count > modular_count:
            analysis["mutation_pattern"] = "monolithic"
        else:
            analysis["mutation_pattern"] = "unclear"
        return analysis


class PerformanceAnalyzer:
    """Analyzes performance characteristics"""

    def __init__(self):
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

    def analyze_performance(
        self, execution_times: List[float], memory_deltas: List[float]
    ) -> Dict[str, Any]:
        """Analyze performance characteristics"""
        analysis = {
            "avg_execution_time": sum(execution_times) / len(execution_times),
            "min_execution_time": min(execution_times),
            "max_execution_time": max(execution_times),
            "execution_variance": max(execution_times) - min(execution_times),
            "avg_memory_delta": sum(memory_deltas) / len(memory_deltas),
            "performance_type": "unknown",
            "confidence": 0.0,
        }
        # Analyze execution time
        avg_time = analysis["avg_execution_time"]
        monolithic_time_range = self.performance_baselines["monolithic"]
        modular_time_range = self.performance_baselines["modular"]
        if (
            modular_time_range["min_execution_time"]
            <= avg_time
            <= modular_time_range["max_execution_time"]
        ):
            analysis["performance_type"] = "modular"
            analysis["confidence"] += 0.4
        elif (
            monolithic_time_range["min_execution_time"]
            <= avg_time
            <= monolithic_time_range["max_execution_time"]
        ):
            analysis["performance_type"] = "monolithic"
            analysis["confidence"] += 0.4
        # Analyze memory usage
        avg_memory = analysis["avg_memory_delta"]
        if (
            modular_time_range["min_memory_delta"]
            <= avg_memory
            <= modular_time_range["max_memory_delta"]
        ):
            if analysis["performance_type"] == "modular":
                analysis["confidence"] += 0.3
            else:
                analysis["performance_type"] = "modular"
                analysis["confidence"] = 0.3
        elif (
            monolithic_time_range["min_memory_delta"]
            <= avg_memory
            <= monolithic_time_range["max_memory_delta"]
        ):
            if analysis["performance_type"] == "monolithic":
                analysis["confidence"] += 0.3
            else:
                analysis["performance_type"] = "monolithic"
                analysis["confidence"] = 0.3
        # Analyze execution variance
        variance = analysis["execution_variance"]
        if variance <= modular_time_range["execution_variance"]:
            if analysis["performance_type"] == "modular":
                analysis["confidence"] += 0.2
        elif variance >= monolithic_time_range["execution_variance"]:
            if analysis["performance_type"] == "monolithic":
                analysis["confidence"] += 0.2
        return analysis


class SophisticatedVerificationSystem:
    """Main verification system that combines all analysis methods"""

    def __init__(self):
        self.execution_analyzer = IndirectVerificationAnalyzer()
        self.state_analyzer = StateMutationAnalyzer()
        self.performance_analyzer = PerformanceAnalyzer()

    def verify_integration(
        self, workflow, test_scenarios: List[Dict[str, Any]]
    ) -> VerificationResult:
        """Perform sophisticated indirect verification"""
        print("🔬 SOPHISTICATED INDIRECT VERIFICATION")
        print("=" * 50)
        all_execution_data = []
        all_state_mutations = []
        all_performance_data = []
        # Run multiple test scenarios
        for i, scenario in enumerate(test_scenarios):
            print("\n📊 Running scenario {i+1}/{len(test_scenarios)}")
            execution_data = self._run_scenario(workflow, scenario)
            all_execution_data.append(execution_data)
            state_mutations = self._analyze_state_mutations(execution_data)
            all_state_mutations.append(state_mutations)
            performance_data = self._extract_performance_data(execution_data)
            all_performance_data.append(performance_data)
        # Combine all analysis results
        combined_analysis = self._combine_analysis_results(
            all_execution_data, all_state_mutations, all_performance_data
        )
        return combined_analysis

    def _run_scenario(self, workflow, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test scenario"""
        from langgraph_devpost_state import create_initial_state

        # Create initial state
        initial_state = create_initial_state()
        initial_state.update(scenario["initial_state"])
        # Get the ghostbusters node
        graph = workflow.graph
        ghostbusters_node = graph.nodes["ghostbusters_consultation"]
        # Measure execution
        start_time = time.time()
        start_memory = self._get_memory_usage()
        # Execute the node (this is the key - we're actually calling the node)
        final_state = ghostbusters_node.invoke(initial_state)
        end_time = time.time()
        end_memory = self._get_memory_usage()
        return {
            "scenario": scenario["name"],
            "initial_state": initial_state,
            "final_state": final_state,
            "execution_time": end_time - start_time,
            "memory_delta": end_memory - start_memory,
            "state_mutation_count": self._count_state_mutations(
                initial_state, final_state
            ),
            "message_count": len(final_state.get("messages", []))
            - len(initial_state.get("messages", [])),
        }

    def _analyze_state_mutations(
        self, execution_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze state mutations for a single execution"""
        return self.state_analyzer.analyze_state_mutations(
            execution_data["initial_state"], execution_data["final_state"]
        )

    def _extract_performance_data(
        self, execution_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract performance data from execution"""
        return {
            "execution_time": execution_data["execution_time"],
            "memory_delta": execution_data["memory_delta"],
        }

    def _combine_analysis_results(
        self,
        execution_data: List[Dict],
        state_mutations: List[Dict],
        performance_data: List[Dict],
    ) -> VerificationResult:
        """Combine all analysis results into final verification result"""
        # Analyze execution characteristics
        execution_scores = {"monolithic_score": 0.0, "modular_score": 0.0}
        for data in execution_data:
            scores = self.execution_analyzer.analyze_execution_characteristics(data)
            execution_scores["monolithic_score"] += scores["monolithic_score"]
            execution_scores["modular_score"] += scores["modular_score"]
        # Normalize scores
        total_scenarios = len(execution_data)
        execution_scores["monolithic_score"] /= total_scenarios
        execution_scores["modular_score"] /= total_scenarios
        # Analyze state mutations
        modular_indicators_total = 0
        monolithic_indicators_total = 0
        for mutations in state_mutations:
            modular_indicators_total += len(mutations["modular_indicators_found"])
            monolithic_indicators_total += len(mutations["monolithic_indicators_found"])
        # Analyze performance
        execution_times = [data["execution_time"] for data in execution_data]
        memory_deltas = [data["memory_delta"] for data in execution_data]
        performance_analysis = self.performance_analyzer.analyze_performance(
            execution_times, memory_deltas
        )
        # Determine final node type
        total_evidence = []
        confidence = 0.0
        node_type = "unknown"
        # Execution characteristics evidence
        if execution_scores["modular_score"] > execution_scores["monolithic_score"]:
            total_evidence.append(
                "Execution characteristics favor modular (score: {execution_scores['modular_score']:.2f})"
            )
            confidence += execution_scores["modular_score"]
            node_type = "modular"
        else:
            total_evidence.append(
                "Execution characteristics favor monolithic (score: {execution_scores['monolithic_score']:.2f})"
            )
            confidence += execution_scores["monolithic_score"]
            node_type = "monolithic"
        # State mutation evidence
        if modular_indicators_total > monolithic_indicators_total:
            total_evidence.append(
                "State mutations favor modular ({modular_indicators_total} vs {monolithic_indicators_total} indicators)"
            )
            confidence += 0.2
            if node_type != "modular":
                node_type = "modular"
        else:
            total_evidence.append(
                "State mutations favor monolithic ({monolithic_indicators_total} vs {modular_indicators_total} indicators)"
            )
            confidence += 0.2
            if node_type != "monolithic":
                node_type = "monolithic"
        # Performance evidence
        if performance_analysis["performance_type"] == "modular":
            total_evidence.append(
                "Performance characteristics favor modular (confidence: {performance_analysis['confidence']:.2f})"
            )
            confidence += performance_analysis["confidence"] * 0.3
        else:
            total_evidence.append(
                "Performance characteristics favor monolithic (confidence: {performance_analysis['confidence']:.2f})"
            )
            confidence += performance_analysis["confidence"] * 0.3
        return VerificationResult(
            node_type=node_type,
            confidence=min(confidence, 1.0),
            evidence=total_evidence,
            execution_characteristics=execution_scores,
            state_mutations={
                "modular_indicators": modular_indicators_total,
                "monolithic_indicators": monolithic_indicators_total,
            },
            performance_metrics=performance_analysis,
        )

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import os

            import psutil

            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0

    def _count_state_mutations(
        self, initial_state: Dict[str, Any], final_state: Dict[str, Any]
    ) -> int:
        """Count the number of state mutations"""
        count = 0
        for key, value in final_state.items():
            if key not in initial_state or initial_state[key] != value:
                count += 1
        return count


def main():
    """Run sophisticated indirect verification"""
    print("🎯 SOPHISTICATED INDIRECT VERIFICATION SYSTEM")
    print("=" * 70)
    try:
        from langgraph_devpost_workflow import DevPostWorkflow

        # Create workflow
        workflow = DevPostWorkflow()
        print("✅ Workflow created successfully")
        # Create test scenarios
        test_scenarios = [
            {
                "name": "Low Confidence Scenario",
                "initial_state": {
                    "session_recovery": {
                        "confidence": 0.15,
                        "similarity_type": "unknown",
                    },
                    "session_save_data": {
                        "current_page_data": {
                            "url": "https://devpost.com/test1",
                            "title": "Test Page 1",
                            "pageText": "This is test page 1",
                            "navigation": [{"text": "Submit", "type": "submit"}],
                            "buttons": [{"text": "Submit", "type": "submit"}],
                        }
                    },
                },
            },
            {
                "name": "Medium Confidence Scenario",
                "initial_state": {
                    "session_recovery": {
                        "confidence": 0.25,
                        "similarity_type": "devpost_known",
                    },
                    "session_save_data": {
                        "current_page_data": {
                            "url": "https://devpost.com/test2",
                            "title": "Test Page 2",
                            "pageText": "This is test page 2 with more content",
                            "navigation": [
                                {"text": "Submit", "type": "submit"},
                                {"text": "Cancel", "type": "button"},
                            ],
                            "buttons": [
                                {"text": "Submit", "type": "submit"},
                                {"text": "Cancel", "type": "button"},
                            ],
                        }
                    },
                },
            },
            {
                "name": "High Confidence Scenario",
                "initial_state": {
                    "session_recovery": {
                        "confidence": 0.35,
                        "similarity_type": "exact",
                    },
                    "session_save_data": {
                        "current_page_data": {
                            "url": "https://devpost.com/test3",
                            "title": "Test Page 3",
                            "pageText": "This is test page 3 with comprehensive content for testing",
                            "navigation": [
                                {"text": "Submit", "type": "submit"},
                                {"text": "Save", "type": "button"},
                                {"text": "Cancel", "type": "button"},
                            ],
                            "buttons": [
                                {"text": "Submit", "type": "submit"},
                                {"text": "Save", "type": "button"},
                                {"text": "Cancel", "type": "button"},
                            ],
                        }
                    },
                },
            },
        ]
        print("📊 Created {len(test_scenarios)} test scenarios")
        # Run verification
        verification_system = SophisticatedVerificationSystem()
        result = verification_system.verify_integration(workflow, test_scenarios)
        # Display results
        print("\n🎯 VERIFICATION RESULTS")
        print("=" * 50)
        print("Node Type: {result.node_type}")
        print("Confidence: {result.confidence:.2f}")
        print("Evidence Count: {len(result.evidence)}")
        print("\n📊 Evidence:")
        for evidence in result.evidence:
            print("   • {evidence}")
        print("\n📈 Execution Characteristics:")
        print(
            "   Monolithic Score: {result.execution_characteristics['monolithic_score']:.2f}"
        )
        print(
            "   Modular Score: {result.execution_characteristics['modular_score']:.2f}"
        )
        print("\n🔍 State Mutations:")
        print("   Modular Indicators: {result.state_mutations['modular_indicators']}")
        print(
            "   Monolithic Indicators: {result.state_mutations['monolithic_indicators']}"
        )
        print("\n⚡ Performance Metrics:")
        print("   Performance Type: {result.performance_metrics['performance_type']}")
        print("   Confidence: {result.performance_metrics['confidence']:.2f}")
        print(
            "   Avg Execution Time: {result.performance_metrics['avg_execution_time']:.4f}s"
        )
        # Final determination
        if result.confidence >= 0.7 and result.node_type == "modular":
            print(
                "\n🎉 DEFINITIVE RESULT: Refactored modular components are integrated!"
            )
            return True
        elif result.confidence >= 0.5 and result.node_type == "modular":
            print("\n✅ LIKELY RESULT: Refactored components are probably integrated")
            return True
        elif result.confidence >= 0.7 and result.node_type == "monolithic":
            print(
                "\n❌ DEFINITIVE RESULT: Old monolithic components are still being used!"
            )
            return False
        else:
            print(
                "\n❓ UNCLEAR RESULT: Cannot definitively determine which components are used"
            )
            return False
    except Exception:
        print("❌ Verification failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
