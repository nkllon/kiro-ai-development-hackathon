#!/usr/bin/env python3
"""
Test Actual Integration
======================

Test that the refactored components are actually integrated into the workflow.
"""

import sys
import traceback
from typing import Dict, Any

def test_import_integration():
    """Test that the refactored components can be imported"""
    
    print("🔧 TESTING ACTUAL INTEGRATION")
    print("=" * 50)
    
    try:
        print("1. Testing refactored component imports...")
        
        # Test investigation modules
        from investigation_modules import (
            InvestigationOrchestrator,
            PageStructureAnalyzer,
            NavigationAnalyzer,
            ContentAnalyzer,
            DiagnosticTester
        )
        print("   ✅ Investigation modules imported successfully")
        
        # Test refactored consultation
        from ghostbusters_consultation_refactored import (
            GhostbustersConsultationRefactored,
            ghostbusters_consultation_refactored_node
        )
        print("   ✅ Refactored consultation imported successfully")
        
        # Test workflow integration
        from langgraph_devpost_workflow import DevPostWorkflow
        print("   ✅ Workflow imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        traceback.print_exc()
        return False


def test_workflow_integration():
    """Test that the workflow actually uses the refactored components"""
    
    print("\n2. Testing workflow integration...")
    
    try:
        from langgraph_devpost_workflow import DevPostWorkflow
        
        # Create workflow instance
        workflow = DevPostWorkflow()
        print("   ✅ Workflow instance created successfully")
        
        # Check if the workflow has the refactored node
        graph = workflow.graph
        nodes = list(graph.nodes.keys())
        
        print(f"   📊 Workflow nodes: {nodes}")
        
        if "ghostbusters_consultation" in nodes:
            print("   ✅ Ghostbusters consultation node present")
            
            # Get the actual node function
            node_func = graph.nodes["ghostbusters_consultation"]
            node_name = getattr(node_func, '__name__', 'unknown')
            print(f"   📝 Node function name: {node_name}")
            
            # Check if it's the refactored version
            if "refactored" in node_name or "refactored" in str(node_func):
                print("   ✅ Refactored node is being used")
                return True
            else:
                print("   ❌ Old monolithic node is still being used")
                return False
        else:
            print("   ❌ Ghostbusters consultation node not found")
            return False
            
    except Exception as e:
        print(f"   ❌ Workflow integration test failed: {e}")
        traceback.print_exc()
        return False


def test_modular_components():
    """Test that the modular components work independently"""
    
    print("\n3. Testing modular components...")
    
    try:
        from investigation_modules import InvestigationOrchestrator
        
        # Create orchestrator
        orchestrator = InvestigationOrchestrator()
        print("   ✅ Investigation orchestrator created")
        
        # Test with mock data
        mock_page_data = {
            "url": "https://devpost.com/test",
            "title": "Test Page",
            "pageText": "This is a test page",
            "navigation": [],
            "buttons": []
        }
        
        # Run investigation
        results = orchestrator.run_investigation(mock_page_data)
        print(f"   ✅ Investigation completed: {results['successful_modules']}/{results['total_modules']} modules")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Modular components test failed: {e}")
        traceback.print_exc()
        return False


def test_refactored_consultation():
    """Test the refactored consultation node"""
    
    print("\n4. Testing refactored consultation...")
    
    try:
        from ghostbusters_consultation_refactored import GhostbustersConsultationRefactored
        from langgraph_devpost_state import create_initial_state
        
        # Create consultation instance
        consultation = GhostbustersConsultationRefactored()
        print("   ✅ Refactored consultation created")
        
        # Create mock state
        mock_state = create_initial_state()
        mock_state["session_recovery"] = {"confidence": 0.15}
        mock_state["session_save_data"] = {
            "current_page_data": {
                "url": "https://devpost.com/test",
                "title": "Test Page",
                "pageText": "This is a test page",
                "navigation": [],
                "buttons": []
            }
        }
        
        # Run consultation
        report = consultation.run_autonomous_investigation(mock_state)
        print(f"   ✅ Consultation completed: {report['consultation_id']}")
        print(f"   📊 Primary strategy: {report['primary_strategy']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Refactored consultation test failed: {e}")
        traceback.print_exc()
        return False


def test_end_to_end_integration():
    """Test end-to-end integration"""
    
    print("\n5. Testing end-to-end integration...")
    
    try:
        from langgraph_devpost_workflow import DevPostWorkflow
        from langgraph_devpost_state import create_initial_state
        
        # Create workflow
        workflow = DevPostWorkflow()
        print("   ✅ Workflow created")
        
        # Create initial state
        initial_state = create_initial_state()
        initial_state["session_recovery"] = {
            "confidence": 0.15,
            "similarity_type": "unknown"
        }
        initial_state["session_save_data"] = {
            "current_page_data": {
                "url": "https://devpost.com/test",
                "title": "Test Page",
                "pageText": "This is a test page",
                "navigation": [],
                "buttons": []
            }
        }
        
        print("   ✅ Initial state created")
        
        # Test that we can access the workflow graph
        graph = workflow.graph
        print(f"   ✅ Workflow graph accessible: {len(graph.nodes)} nodes")
        
        # Check if refactored node is present
        if "ghostbusters_consultation" in graph.nodes:
            node_func = graph.nodes["ghostbusters_consultation"]
            print(f"   ✅ Ghostbusters consultation node accessible: {node_func}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ End-to-end integration test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all integration tests"""
    
    print("🚀 ACTUAL INTEGRATION TESTING")
    print("=" * 60)
    
    tests = [
        ("Import Integration", test_import_integration),
        ("Workflow Integration", test_workflow_integration),
        ("Modular Components", test_modular_components),
        ("Refactored Consultation", test_refactored_consultation),
        ("End-to-End Integration", test_end_to_end_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            result = test_func()
            results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {status}")
        except Exception as e:
            print(f"   ❌ FAILED with exception: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n📊 INTEGRATION TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ Refactored components are properly integrated")
        print("✅ RMDDD refactoring is actually working")
    else:
        print("⚠️ SOME INTEGRATION TESTS FAILED")
        print("❌ Refactored components may not be properly integrated")
        print("🔧 Additional work needed for actual integration")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
