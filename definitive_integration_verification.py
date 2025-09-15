#!/usr/bin/env python3
"""
Definitive Integration Verification
===================================

Multi-dimensional test to definitively prove whether refactored components
are actually integrated into the workflow.
"""

import sys
import time
import traceback
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock

def test_definitive_node_execution():
    """Test that definitively shows which node is actually executing"""
    
    print("🔍 DEFINITIVE NODE EXECUTION TEST")
    print("=" * 60)
    
    try:
        from langgraph_devpost_workflow import DevPostWorkflow
        from langgraph_devpost_state import create_initial_state
        
        # Create workflow
        workflow = DevPostWorkflow()
        print("✅ Workflow created successfully")
        
        # Create mock state that will trigger ghostbusters consultation
        mock_state = create_initial_state()
        mock_state["session_recovery"] = {
            "confidence": 0.15,  # Very low confidence - should trigger ghostbusters autonomous
            "similarity_type": "unknown"
        }
        mock_state["session_save_data"] = {
            "current_page_data": {
                "url": "https://devpost.com/test",
                "title": "Test Page",
                "pageText": "This is a test page for definitive verification",
                "navigation": [
                    {"text": "Submit", "type": "submit", "href": None}
                ],
                "buttons": [
                    {"text": "Submit", "type": "submit"}
                ]
            }
        }
        
        print("✅ Mock state created")
        
        # Get the actual node function
        graph = workflow.graph
        ghostbusters_node = graph.nodes["ghostbusters_consultation"]
        
        # Create a wrapper to capture execution details
        execution_details = {
            "node_executed": False,
            "execution_time": 0,
            "state_changes": {},
            "messages_added": 0
        }
        
        def capture_execution(state):
            start_time = time.time()
            execution_details["node_executed"] = True
            
            # Call the actual node
            result = ghostbusters_node.func(state)
            
            execution_details["execution_time"] = time.time() - start_time
            execution_details["state_changes"] = {
                key: value for key, value in result.items() 
                if key not in state or result[key] != state[key]
            }
            execution_details["messages_added"] = len(result.get("messages", [])) - len(state.get("messages", []))
            
            return result
        
        # Execute the node
        print("🚀 Executing ghostbusters consultation node...")
        result_state = capture_execution(mock_state)
        
        print(f"✅ Node executed successfully")
        print(f"   Execution time: {execution_details['execution_time']:.4f}s")
        print(f"   State changes: {len(execution_details['state_changes'])}")
        print(f"   Messages added: {execution_details['messages_added']}")
        
        # Analyze the results to determine which node was used
        analysis = analyze_node_execution(result_state, execution_details)
        
        return analysis
        
    except Exception as e:
        print(f"❌ Definitive test failed: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def analyze_node_execution(result_state: Dict[str, Any], execution_details: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze the execution results to determine which node was used"""
    
    print("\n🔬 ANALYZING NODE EXECUTION")
    print("=" * 40)
    
    analysis = {
        "success": True,
        "node_type": "unknown",
        "evidence": [],
        "confidence": 0.0
    }
    
    # Evidence 1: Check for modular investigation indicators
    if "ghostbusters_report" in result_state:
        report = result_state["ghostbusters_report"]
        
        if "investigation_results" in report:
            investigation = report["investigation_results"]
            
            if "successful_modules" in investigation and "total_modules" in investigation:
                analysis["evidence"].append("Modular investigation detected")
                analysis["confidence"] += 0.3
                
                # Check for specific module results
                if "results" in investigation:
                    module_results = investigation["results"]
                    if "PageStructureAnalyzer" in module_results:
                        analysis["evidence"].append("PageStructureAnalyzer module used")
                        analysis["confidence"] += 0.2
                    if "NavigationAnalyzer" in module_results:
                        analysis["evidence"].append("NavigationAnalyzer module used")
                        analysis["confidence"] += 0.2
                    if "ContentAnalyzer" in module_results:
                        analysis["evidence"].append("ContentAnalyzer module used")
                        analysis["confidence"] += 0.2
                    if "DiagnosticTester" in module_results:
                        analysis["evidence"].append("DiagnosticTester module used")
                        analysis["confidence"] += 0.2
    
    # Evidence 2: Check for refactored consultation indicators
    if "ghostbusters_report" in result_state:
        report = result_state["ghostbusters_report"]
        
        if "consultation_id" in report and "gb_consult_" in str(report["consultation_id"]):
            analysis["evidence"].append("Refactored consultation ID format detected")
            analysis["confidence"] += 0.1
        
        if "investigation_results" in report and "overall_confidence" in report["investigation_results"]:
            analysis["evidence"].append("Investigation orchestrator confidence calculation")
            analysis["confidence"] += 0.1
    
    # Evidence 3: Check execution characteristics
    if execution_details["execution_time"] < 0.1:  # Very fast execution suggests modular approach
        analysis["evidence"].append("Fast execution time suggests modular components")
        analysis["confidence"] += 0.1
    
    # Evidence 4: Check for old monolithic indicators (negative evidence)
    old_monolithic_indicators = [
        "comprehensive_investigation",
        "run_diagnostic_tests", 
        "analyze_page_structure",
        "analyze_navigation_elements"
    ]
    
    # If we find these in the state, it suggests old monolithic node
    for indicator in old_monolithic_indicators:
        if indicator in str(result_state):
            analysis["evidence"].append(f"Old monolithic indicator found: {indicator}")
            analysis["confidence"] -= 0.2
    
    # Determine node type based on confidence
    if analysis["confidence"] >= 0.7:
        analysis["node_type"] = "refactored_modular"
    elif analysis["confidence"] >= 0.4:
        analysis["node_type"] = "likely_refactored"
    elif analysis["confidence"] >= 0.0:
        analysis["node_type"] = "unclear"
    else:
        analysis["node_type"] = "likely_monolithic"
    
    print(f"📊 Analysis Results:")
    print(f"   Node Type: {analysis['node_type']}")
    print(f"   Confidence: {analysis['confidence']:.2f}")
    print(f"   Evidence Count: {len(analysis['evidence'])}")
    
    for evidence in analysis["evidence"]:
        print(f"   • {evidence}")
    
    return analysis


def test_performance_comparison():
    """Test performance characteristics to distinguish node types"""
    
    print("\n⚡ PERFORMANCE COMPARISON TEST")
    print("=" * 40)
    
    try:
        from langgraph_devpost_workflow import DevPostWorkflow
        from langgraph_devpost_state import create_initial_state
        
        # Create workflow
        workflow = DevPostWorkflow()
        
        # Create test state
        mock_state = create_initial_state()
        mock_state["session_recovery"] = {"confidence": 0.15}
        mock_state["session_save_data"] = {
            "current_page_data": {
                "url": "https://devpost.com/test",
                "title": "Performance Test Page",
                "pageText": "This is a performance test page with some content",
                "navigation": [
                    {"text": "Submit", "type": "submit", "href": None},
                    {"text": "Cancel", "type": "button", "href": None}
                ],
                "buttons": [
                    {"text": "Submit", "type": "submit"},
                    {"text": "Cancel", "type": "button"}
                ]
            }
        }
        
        # Get the node
        graph = workflow.graph
        ghostbusters_node = graph.nodes["ghostbusters_consultation"]
        
        # Run multiple times to get average performance
        execution_times = []
        for i in range(5):
            start_time = time.time()
            result_state = ghostbusters_node.func(mock_state.copy())
            execution_time = time.time() - start_time
            execution_times.append(execution_time)
        
        avg_time = sum(execution_times) / len(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        
        print(f"📊 Performance Results:")
        print(f"   Average execution time: {avg_time:.4f}s")
        print(f"   Min execution time: {min_time:.4f}s")
        print(f"   Max execution time: {max_time:.4f}s")
        print(f"   Execution count: {len(execution_times)}")
        
        # Analyze performance characteristics
        if avg_time < 0.05:  # Very fast - suggests modular approach
            print("   ✅ Fast execution suggests modular components")
            return {"performance_type": "modular", "confidence": 0.8}
        elif avg_time < 0.1:  # Fast - likely modular
            print("   ✅ Moderate execution time suggests modular components")
            return {"performance_type": "likely_modular", "confidence": 0.6}
        else:  # Slower - might be monolithic
            print("   ⚠️ Slower execution time might indicate monolithic approach")
            return {"performance_type": "possibly_monolithic", "confidence": 0.3}
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return {"performance_type": "error", "confidence": 0.0, "error": str(e)}


def test_memory_usage_analysis():
    """Test memory usage patterns to distinguish node types"""
    
    print("\n🧠 MEMORY USAGE ANALYSIS TEST")
    print("=" * 40)
    
    try:
        import psutil
        import os
        
        # Get current process
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        from langgraph_devpost_workflow import DevPostWorkflow
        from langgraph_devpost_state import create_initial_state
        
        # Create workflow
        workflow = DevPostWorkflow()
        
        # Create test state
        mock_state = create_initial_state()
        mock_state["session_recovery"] = {"confidence": 0.15}
        mock_state["session_save_data"] = {
            "current_page_data": {
                "url": "https://devpost.com/test",
                "title": "Memory Test Page",
                "pageText": "This is a memory test page",
                "navigation": [],
                "buttons": []
            }
        }
        
        # Get the node
        graph = workflow.graph
        ghostbusters_node = graph.nodes["ghostbusters_consultation"]
        
        # Execute node and measure memory
        before_memory = process.memory_info().rss / 1024 / 1024  # MB
        result_state = ghostbusters_node.func(mock_state)
        after_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        memory_delta = after_memory - before_memory
        
        print(f"📊 Memory Usage Results:")
        print(f"   Initial memory: {initial_memory:.2f} MB")
        print(f"   Before execution: {before_memory:.2f} MB")
        print(f"   After execution: {after_memory:.2f} MB")
        print(f"   Memory delta: {memory_delta:.2f} MB")
        
        # Analyze memory characteristics
        if memory_delta < 1.0:  # Low memory usage - suggests modular approach
            print("   ✅ Low memory usage suggests modular components")
            return {"memory_type": "modular", "confidence": 0.7}
        elif memory_delta < 5.0:  # Moderate memory usage
            print("   ✅ Moderate memory usage suggests modular components")
            return {"memory_type": "likely_modular", "confidence": 0.5}
        else:  # High memory usage - might be monolithic
            print("   ⚠️ High memory usage might indicate monolithic approach")
            return {"memory_type": "possibly_monolithic", "confidence": 0.3}
        
    except ImportError:
        print("   ⚠️ psutil not available, skipping memory analysis")
        return {"memory_type": "unavailable", "confidence": 0.0}
    except Exception as e:
        print(f"❌ Memory analysis failed: {e}")
        return {"memory_type": "error", "confidence": 0.0, "error": str(e)}


def main():
    """Run all definitive verification tests"""
    
    print("🎯 DEFINITIVE INTEGRATION VERIFICATION")
    print("=" * 70)
    
    tests = [
        ("Node Execution Analysis", test_definitive_node_execution),
        ("Performance Comparison", test_performance_comparison),
        ("Memory Usage Analysis", test_memory_usage_analysis)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            result = test_func()
            results[test_name] = result
            if result.get("success", True):
                print(f"   ✅ {test_name} completed")
            else:
                print(f"   ❌ {test_name} failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"   ❌ {test_name} failed with exception: {e}")
            results[test_name] = {"success": False, "error": str(e)}
    
    # Final analysis
    print(f"\n🎯 DEFINITIVE VERIFICATION SUMMARY")
    print("=" * 50)
    
    # Analyze node execution results
    if "Node Execution Analysis" in results:
        execution_result = results["Node Execution Analysis"]
        if execution_result.get("success"):
            node_type = execution_result.get("node_type", "unknown")
            confidence = execution_result.get("confidence", 0.0)
            
            print(f"📊 Node Type: {node_type}")
            print(f"📊 Confidence: {confidence:.2f}")
            
            if node_type == "refactored_modular" and confidence >= 0.7:
                print("🎉 DEFINITIVE RESULT: Refactored modular components are integrated!")
                return True
            elif node_type == "likely_refactored" and confidence >= 0.4:
                print("✅ LIKELY RESULT: Refactored components are probably integrated")
                return True
            elif node_type == "likely_monolithic" or confidence < 0.0:
                print("❌ DEFINITIVE RESULT: Old monolithic components are still being used!")
                return False
            else:
                print("❓ UNCLEAR RESULT: Cannot definitively determine which components are used")
                return False
        else:
            print("❌ Node execution analysis failed")
            return False
    else:
        print("❌ Node execution analysis not completed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
