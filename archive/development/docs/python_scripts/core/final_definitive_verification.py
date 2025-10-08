#!/usr/bin/env python3
"""
Final Definitive Verification
=============================

Simple, definitive verification that proves the refactored components are integrated.
"""

import sys
import time
from typing import Dict, Any


def test_definitive_integration():
    """Test that definitively proves which node is integrated"""

    print("🎯 FINAL DEFINITIVE VERIFICATION")
    print("=" * 50)

    try:
        from langgraph_devpost_workflow import DevPostWorkflow
        from langgraph_devpost_state import create_initial_state

        # Create workflow
        workflow = DevPostWorkflow()
        print("✅ Workflow created successfully")

        # Create test state that will trigger ghostbusters consultation
        mock_state = create_initial_state()
        mock_state["session_recovery"] = {
            "confidence": 0.15,  # Very low confidence - triggers ghostbusters autonomous
            "similarity_type": "unknown",
        }
        mock_state["session_save_data"] = {
            "current_page_data": {
                "url": "https://devpost.com/definitive-test",
                "title": "Definitive Test Page",
                "pageText": "This is the definitive test page for verification",
                "navigation": [
                    {"text": "Submit", "type": "submit", "href": None},
                    {"text": "Cancel", "type": "button", "href": None},
                ],
                "buttons": [
                    {"text": "Submit", "type": "submit"},
                    {"text": "Cancel", "type": "button"},
                ],
            }
        }

        print("✅ Test state created")

        # Get the ghostbusters node
        graph = workflow.graph
        ghostbusters_node = graph.nodes["ghostbusters_consultation"]

        print("🚀 Executing ghostbusters consultation node...")

        # Execute the node and capture output
        start_time = time.time()
        result_state = ghostbusters_node.invoke(mock_state)
        execution_time = time.time() - start_time

        print(f"✅ Node executed successfully in {execution_time:.4f}s")

        # Analyze the results to determine which node was used
        analysis = analyze_execution_results(result_state, execution_time)

        return analysis

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return {"success": False, "error": str(e)}


def analyze_execution_results(
    result_state: Dict[str, Any], execution_time: float
) -> Dict[str, Any]:
    """Analyze execution results to determine which node was used"""

    print("\n🔬 ANALYZING EXECUTION RESULTS")
    print("=" * 40)

    analysis = {
        "success": True,
        "node_type": "unknown",
        "confidence": 0.0,
        "evidence": [],
        "definitive_result": False,
    }

    # Evidence 1: Check for modular investigation indicators
    if "ghostbusters_report" in result_state:
        report = result_state["ghostbusters_report"]
        analysis["evidence"].append("✅ Ghostbusters report present")
        analysis["confidence"] += 0.2

        # Check for investigation results
        if "investigation_results" in report:
            investigation = report["investigation_results"]
            analysis["evidence"].append("✅ Investigation results present")
            analysis["confidence"] += 0.2

            # Check for modular components
            if (
                "successful_modules" in investigation
                and "total_modules" in investigation
            ):
                successful = investigation["successful_modules"]
                total = investigation["total_modules"]
                analysis["evidence"].append(
                    f"✅ Modular investigation: {successful}/{total} modules"
                )
                analysis["confidence"] += 0.3

                # This is DEFINITIVE evidence of modular components
                if successful == 4 and total == 4:
                    analysis["evidence"].append(
                        "🎯 DEFINITIVE: All 4 investigation modules used"
                    )
                    analysis["confidence"] += 0.4
                    analysis["node_type"] = "refactored_modular"
                    analysis["definitive_result"] = True

            # Check for specific module results
            if "results" in investigation:
                module_results = investigation["results"]
                module_names = list(module_results.keys())

                expected_modules = [
                    "PageStructureAnalyzer",
                    "NavigationAnalyzer",
                    "ContentAnalyzer",
                    "DiagnosticTester",
                ]

                found_modules = [
                    name for name in expected_modules if name in module_names
                ]
                analysis["evidence"].append(f"✅ Found modules: {found_modules}")

                if len(found_modules) == 4:
                    analysis["evidence"].append(
                        "🎯 DEFINITIVE: All expected modules present"
                    )
                    analysis["confidence"] += 0.3
                    analysis["node_type"] = "refactored_modular"
                    analysis["definitive_result"] = True

        # Check for consultation ID format
        if "consultation_id" in report:
            consultation_id = str(report["consultation_id"])
            if "gb_consult_" in consultation_id:
                analysis["evidence"].append(
                    f"✅ Refactored consultation ID: {consultation_id}"
                )
                analysis["confidence"] += 0.1

        # Check for orchestrated investigation
        if "overall_confidence" in investigation:
            analysis["evidence"].append(
                "✅ Investigation orchestrator confidence calculation"
            )
            analysis["confidence"] += 0.1

    # Evidence 2: Check execution characteristics
    if execution_time < 0.1:  # Very fast execution suggests modular approach
        analysis["evidence"].append(
            f"✅ Fast execution time: {execution_time:.4f}s (suggests modular)"
        )
        analysis["confidence"] += 0.1
    else:
        analysis["evidence"].append(f"⚠️ Slower execution time: {execution_time:.4f}s")

    # Evidence 3: Check for old monolithic indicators (negative evidence)
    state_str = str(result_state)
    old_monolithic_indicators = [
        "comprehensive_investigation",
        "run_diagnostic_tests",
        "analyze_page_structure",
        "analyze_navigation_elements",
    ]

    found_old_indicators = [
        indicator for indicator in old_monolithic_indicators if indicator in state_str
    ]
    if found_old_indicators:
        analysis["evidence"].append(
            f"❌ Old monolithic indicators found: {found_old_indicators}"
        )
        analysis["confidence"] -= 0.3
        analysis["node_type"] = "monolithic"
    else:
        analysis["evidence"].append("✅ No old monolithic indicators found")
        analysis["confidence"] += 0.1

    # Final determination
    if analysis["definitive_result"]:
        analysis["node_type"] = "refactored_modular"
    elif analysis["confidence"] >= 0.7:
        if analysis["node_type"] == "unknown":
            analysis["node_type"] = "likely_refactored"
    elif analysis["confidence"] < 0.0:
        analysis["node_type"] = "monolithic"

    return analysis


def main():
    """Run final definitive verification"""

    print("🎯 FINAL DEFINITIVE VERIFICATION")
    print("=" * 70)

    try:
        # Run the test
        result = test_definitive_integration()

        if not result.get("success", True):
            print(f"❌ Test failed: {result.get('error', 'Unknown error')}")
            return False

        # Display results
        print(f"\n📊 VERIFICATION RESULTS")
        print("=" * 50)
        print(f"Node Type: {result['node_type']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Definitive Result: {result['definitive_result']}")
        print(f"Evidence Count: {len(result['evidence'])}")

        print(f"\n📋 Evidence:")
        for evidence in result["evidence"]:
            print(f"   {evidence}")

        # Final determination
        if result["definitive_result"]:
            print(
                f"\n🎉 DEFINITIVE RESULT: REFACTORED MODULAR COMPONENTS ARE INTEGRATED!"
            )
            print(
                "✅ The workflow is using the refactored Ghostbusters consultation node"
            )
            print("✅ All 4 investigation modules are being used")
            print("✅ The RMDDD refactoring is actually working in practice")
            return True
        elif (
            result["node_type"] == "refactored_modular" and result["confidence"] >= 0.7
        ):
            print(f"\n✅ LIKELY RESULT: REFACTORED COMPONENTS ARE INTEGRATED")
            print("✅ High confidence that refactored components are being used")
            return True
        elif result["node_type"] == "monolithic":
            print(
                f"\n❌ DEFINITIVE RESULT: OLD MONOLITHIC COMPONENTS ARE STILL BEING USED"
            )
            print("❌ The workflow is not using the refactored components")
            return False
        else:
            print(
                f"\n❓ UNCLEAR RESULT: Cannot definitively determine which components are used"
            )
            print("🔧 Additional investigation needed")
            return False

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
