#!/usr/bin/env python3
"""
Core Verification System - Main verification logic
=================================================

Extracted from sophisticated_indirect_verification.py for RDI compliance.
Main verification system that combines all analysis methods.
"""

import time
from typing import Any, Dict, List

from .execution_analyzer import IndirectVerificationAnalyzer
from .performance_analyzer import PerformanceAnalyzer
from .state_analyzer import StateMutationAnalyzer
from .verification_result import VerificationResult


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
            print(f"\n📊 Running scenario {i+1}/{len(test_scenarios)}")
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
                f"Execution characteristics favor modular (score: {execution_scores['modular_score']:.2f})"
            )
            confidence += execution_scores["modular_score"]
            node_type = "modular"
        else:
            total_evidence.append(
                f"Execution characteristics favor monolithic (score: {execution_scores['monolithic_score']:.2f})"
            )
            confidence += execution_scores["monolithic_score"]
            node_type = "monolithic"
        
        # State mutation evidence
        if modular_indicators_total > monolithic_indicators_total:
            total_evidence.append(
                f"State mutations favor modular ({modular_indicators_total} vs {monolithic_indicators_total} indicators)"
            )
            confidence += 0.2
            if node_type != "modular":
                node_type = "modular"
        else:
            total_evidence.append(
                f"State mutations favor monolithic ({monolithic_indicators_total} vs {modular_indicators_total} indicators)"
            )
            confidence += 0.2
            if node_type != "monolithic":
                node_type = "monolithic"
        
        # Performance evidence
        if performance_analysis["performance_type"] == "modular":
            total_evidence.append(
                f"Performance characteristics favor modular (confidence: {performance_analysis['confidence']:.2f})"
            )
            confidence += performance_analysis["confidence"] * 0.3
        else:
            total_evidence.append(
                f"Performance characteristics favor monolithic (confidence: {performance_analysis['confidence']:.2f})"
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
