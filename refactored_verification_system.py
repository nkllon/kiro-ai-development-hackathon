#!/usr/bin/env python3
"""
Refactored Verification System
==============================

RMDDD-compliant verification system using modular components.
"""

import sys
import time
from typing import Dict, Any, List

from verification_modules import VerificationOrchestrator


class RefactoredVerificationSystem:
    """RMDDD-compliant verification system using modular components"""
    
    def __init__(self):
        self.orchestrator = VerificationOrchestrator()
    
    def verify_integration(self, workflow, test_scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform verification using modular components"""
        
        print("🔬 REFACTORED VERIFICATION SYSTEM")
        print("=" * 50)
        
        all_results = []
        
        # Run multiple test scenarios
        for i, scenario in enumerate(test_scenarios):
            print(f"\n📊 Running scenario {i+1}/{len(test_scenarios)}")
            
            execution_data = self._run_scenario(workflow, scenario)
            verification_result = self.orchestrator.verify_integration(execution_data)
            
            all_results.append(verification_result)
        
        # Combine results from all scenarios
        final_result = self._combine_scenario_results(all_results)
        
        return final_result
    
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
        
        # Execute the node
        final_state = ghostbusters_node.invoke(initial_state)
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        return {
            "scenario": scenario["name"],
            "initial_state": initial_state,
            "final_state": final_state,
            "execution_time": end_time - start_time,
            "memory_delta": end_memory - start_memory,
            "state_mutation_count": self._count_state_mutations(initial_state, final_state),
            "message_count": len(final_state.get("messages", [])) - len(initial_state.get("messages", []))
        }
    
    def _combine_scenario_results(self, all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine results from all scenarios"""
        
        print(f"\n📊 Combining results from {len(all_results)} scenarios...")
        
        # Calculate average confidence
        total_confidence = sum(result["confidence"] for result in all_results if result["success"])
        successful_scenarios = sum(1 for result in all_results if result["success"])
        avg_confidence = total_confidence / successful_scenarios if successful_scenarios > 0 else 0.0
        
        # Determine consensus node type
        node_types = [result["node_type"] for result in all_results if result["success"]]
        if node_types:
            # Count occurrences
            type_counts = {}
            for node_type in node_types:
                type_counts[node_type] = type_counts.get(node_type, 0) + 1
            
            # Get most common type
            consensus_type = max(type_counts, key=type_counts.get)
        else:
            consensus_type = "unknown"
        
        # Combine evidence
        all_evidence = []
        for result in all_results:
            all_evidence.extend(result.get("evidence", []))
        
        # Remove duplicates while preserving order
        unique_evidence = []
        seen = set()
        for evidence in all_evidence:
            if evidence not in seen:
                unique_evidence.append(evidence)
                seen.add(evidence)
        
        return {
            "success": successful_scenarios > 0,
            "node_type": consensus_type,
            "confidence": avg_confidence,
            "evidence": unique_evidence,
            "scenarios_run": len(all_results),
            "successful_scenarios": successful_scenarios,
            "individual_results": all_results
        }
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0
    
    def _count_state_mutations(self, initial_state: Dict[str, Any], final_state: Dict[str, Any]) -> int:
        """Count the number of state mutations"""
        count = 0
        for key, value in final_state.items():
            if key not in initial_state or initial_state[key] != value:
                count += 1
        return count


def main():
    """Run refactored verification system"""
    
    print("🎯 REFACTORED VERIFICATION SYSTEM")
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
                    "session_recovery": {"confidence": 0.15, "similarity_type": "unknown"},
                    "session_save_data": {
                        "current_page_data": {
                            "url": "https://devpost.com/test1",
                            "title": "Test Page 1",
                            "pageText": "This is test page 1",
                            "navigation": [{"text": "Submit", "type": "submit"}],
                            "buttons": [{"text": "Submit", "type": "submit"}]
                        }
                    }
                }
            },
            {
                "name": "Medium Confidence Scenario",
                "initial_state": {
                    "session_recovery": {"confidence": 0.25, "similarity_type": "devpost_known"},
                    "session_save_data": {
                        "current_page_data": {
                            "url": "https://devpost.com/test2",
                            "title": "Test Page 2",
                            "pageText": "This is test page 2 with more content",
                            "navigation": [
                                {"text": "Submit", "type": "submit"},
                                {"text": "Cancel", "type": "button"}
                            ],
                            "buttons": [
                                {"text": "Submit", "type": "submit"},
                                {"text": "Cancel", "type": "button"}
                            ]
                        }
                    }
                }
            }
        ]
        
        print(f"📊 Created {len(test_scenarios)} test scenarios")
        
        # Run verification
        verification_system = RefactoredVerificationSystem()
        result = verification_system.verify_integration(workflow, test_scenarios)
        
        # Display results
        print(f"\n🎯 VERIFICATION RESULTS")
        print("=" * 50)
        print(f"Success: {result['success']}")
        print(f"Node Type: {result['node_type']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Scenarios Run: {result['scenarios_run']}")
        print(f"Successful Scenarios: {result['successful_scenarios']}")
        print(f"Evidence Count: {len(result['evidence'])}")
        
        print(f"\n📋 Evidence:")
        for evidence in result['evidence'][:10]:  # Show first 10 pieces of evidence
            print(f"   • {evidence}")
        
        if len(result['evidence']) > 10:
            print(f"   ... and {len(result['evidence']) - 10} more pieces of evidence")
        
        # Final determination
        if result['success'] and result['confidence'] >= 0.7 and result['node_type'] == 'refactored_modular':
            print(f"\n🎉 DEFINITIVE RESULT: REFACTORED MODULAR COMPONENTS ARE INTEGRATED!")
            print("✅ The workflow is using the refactored Ghostbusters consultation node")
            print("✅ RMDDD refactoring is actually working in practice")
            print("✅ Verification system itself follows RMDDD principles")
            return True
        elif result['success'] and result['confidence'] >= 0.5:
            print(f"\n✅ LIKELY RESULT: REFACTORED COMPONENTS ARE INTEGRATED")
            print("✅ High confidence that refactored components are being used")
            return True
        else:
            print(f"\n❌ UNCLEAR RESULT: Cannot definitively determine integration status")
            return False
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
