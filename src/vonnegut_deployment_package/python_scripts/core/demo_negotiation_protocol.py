#!/usr/bin/env python3
"""
Demo Negotiation Protocol
========================

Simple demonstration of the general-purpose negotiation protocol
for when the AI encounters an impasse and needs to negotiate
a way forward with the human.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from negotiation_protocol import create_impasse_context, negotiate_impasse_resolution


def demonstrate_technical_impasse():
    """Demonstrate negotiation for a technical impasse"""

    print("🎭 DEMONSTRATING TECHNICAL IMPASSE NEGOTIATION")
    print("=" * 60)
    print("Scenario: LangGraph workflow node execution failing")
    print("=" * 60)

    context = create_impasse_context(
        impasse_type="technical",
        severity_level="very_stuck",
        evidence_summary="LangGraph workflow node execution failing with cryptic error messages. The ghostbusters_consultation_node is throwing PregelNode errors that cannot be resolved through normal debugging.",
        attempted_resolutions=[
            "Restart the specific failing node",
            "Clear node state and retry execution",
            "Switch to alternative node implementation",
            "Enable debug mode and trace execution step by step",
            "Check node dependencies and imports",
        ],
        failure_reasons=[
            "Node state corruption detected in PregelNode wrapper",
            "Alternative implementation not available in current codebase",
            "Debug mode reveals no obvious issues in node logic",
            "Error messages are non-descriptive and generic",
            "Dependencies appear to be correctly installed",
        ],
        current_state={
            "current_node": "ghostbusters_consultation_node",
            "workflow_state": "executing",
            "error_count": 5,
            "last_error": "PregelNode execution failed with AttributeError",
            "session_data": {
                "important_context": "preserve_this",
                "user_preferences": "session_must_not_be_lost",
                "workflow_progress": "75%_complete",
            },
            "active_components": [
                "langgraph",
                "playwright",
                "browser_session",
                "telemetry_graph",
            ],
        },
    )

    print("\n🚀 Initiating negotiation protocol...")
    result = negotiate_impasse_resolution(context)

    print(f"\n📊 NEGOTIATION RESULT:")
    print(f"   Success: {'✅' if result.success else '❌'}")
    print(f"   Impasse Resolved: {'✅' if result.impasse_resolved else '❌'}")
    print(f"   Session Preserved: {'✅' if result.session_preserved else '❌'}")
    print(f"   Human Approved: {'✅' if result.human_approved else '❌'}")
    print(f"   Breadcrumbs Left: {len(result.breadcrumbs_left)}")

    if result.chosen_option:
        print(f"   Chosen Solution: {result.chosen_option.title}")
        print(f"   Risk Level: {result.chosen_option.risk_level}")
        print(f"   Session Impact: {result.chosen_option.session_impact}")

    return result.success


def demonstrate_logical_impasse():
    """Demonstrate negotiation for a logical impasse"""

    print("\n🎭 DEMONSTRATING LOGICAL IMPASSE NEGOTIATION")
    print("=" * 60)
    print("Scenario: Cannot determine correct navigation strategy for DevPost")
    print("=" * 60)

    context = create_impasse_context(
        impasse_type="logical",
        severity_level="stuck",
        evidence_summary="Cannot determine the correct navigation strategy for DevPost form submission. All confidence scores are below threshold, and the system cannot decide between multiple viable approaches.",
        attempted_resolutions=[
            "Try exact match navigation based on telemetry",
            "Attempt visual similarity matching with screenshots",
            "Use semantic navigation approach with form analysis",
            "Fall back to adaptive navigation with learning",
            "Combine multiple strategies with weighted scoring",
        ],
        failure_reasons=[
            "No exact matches found in telemetry graph",
            "Visual similarity scores too low (< 0.3 threshold)",
            "Semantic analysis inconclusive for form fields",
            "Adaptive navigation lacks sufficient historical data",
            "Weighted scoring results in ties between strategies",
        ],
        current_state={
            "current_page": "DevPost submission form - step 3 of 5",
            "available_strategies": [
                "exact",
                "visual",
                "semantic",
                "adaptive",
                "hybrid",
            ],
            "confidence_scores": {
                "exact": 0.1,
                "visual": 0.25,
                "semantic": 0.15,
                "adaptive": 0.2,
                "hybrid": 0.22,
            },
            "threshold": 0.3,
            "session_data": {
                "form_fields": "preserve_these_mappings",
                "user_input": "beast_mode_framework_details",
                "progress": "step_3_of_5",
            },
        },
    )

    print("\n🚀 Initiating negotiation protocol...")
    result = negotiate_impasse_resolution(context)

    print(f"\n📊 NEGOTIATION RESULT:")
    print(f"   Success: {'✅' if result.success else '❌'}")
    print(f"   Impasse Resolved: {'✅' if result.impasse_resolved else '❌'}")
    print(f"   Session Preserved: {'✅' if result.session_preserved else '❌'}")
    print(f"   Human Approved: {'✅' if result.human_approved else '❌'}")
    print(f"   Breadcrumbs Left: {len(result.breadcrumbs_left)}")

    if result.chosen_option:
        print(f"   Chosen Solution: {result.chosen_option.title}")
        print(f"   Risk Level: {result.chosen_option.risk_level}")
        print(
            f"   Success Probability: {result.chosen_option.estimated_success_probability:.0%}"
        )

    return result.success


def demonstrate_resource_impasse():
    """Demonstrate negotiation for a resource impasse"""

    print("\n🎭 DEMONSTRATING RESOURCE IMPASSE NEGOTIATION")
    print("=" * 60)
    print("Scenario: Memory usage at 95%, cannot load additional components")
    print("=" * 60)

    context = create_impasse_context(
        impasse_type="resource",
        severity_level="extremely_stuck",
        evidence_summary="Memory usage at 95%, system cannot load additional components required for DevPost automation. Browser automation is consuming excessive memory and cannot continue.",
        attempted_resolutions=[
            "Clear temporary cache and browser data",
            "Unload unused components and services",
            "Optimize memory usage in active components",
            "Request additional memory allocation from system",
            "Reduce browser automation scope and complexity",
        ],
        failure_reasons=[
            "Cache clearing freed only 50MB, insufficient for needs",
            "No unused components available to unload",
            "Optimization attempts failed to reduce memory footprint",
            "Memory allocation request denied by system",
            "Reducing scope would break DevPost automation requirements",
        ],
        current_state={
            "memory_usage": 0.95,
            "available_memory": "50MB",
            "required_memory": "200MB",
            "memory_threshold": 0.9,
            "active_components": [
                "browser_session",
                "playwright",
                "langgraph",
                "telemetry_graph",
                "devpost_state_model",
            ],
            "session_data": {
                "critical_state": "must_preserve",
                "form_progress": "step_2_of_5",
                "user_data": "beast_mode_details",
            },
        },
    )

    print("\n🚀 Initiating negotiation protocol...")
    result = negotiate_impasse_resolution(context)

    print(f"\n📊 NEGOTIATION RESULT:")
    print(f"   Success: {'✅' if result.success else '❌'}")
    print(f"   Impasse Resolved: {'✅' if result.impasse_resolved else '❌'}")
    print(f"   Session Preserved: {'✅' if result.session_preserved else '❌'}")
    print(f"   Human Approved: {'✅' if result.human_approved else '❌'}")
    print(f"   Breadcrumbs Left: {len(result.breadcrumbs_left)}")

    if result.chosen_option:
        print(f"   Chosen Solution: {result.chosen_option.title}")
        print(f"   Risk Level: {result.chosen_option.risk_level}")
        print(f"   Session Impact: {result.chosen_option.session_impact}")
        print(
            f"   Requires Human Approval: {'Yes' if result.chosen_option.requires_human_approval else 'No'}"
        )

    return result.success


def demonstrate_unknown_impasse():
    """Demonstrate negotiation for an unknown/mysterious impasse"""

    print("\n🎭 DEMONSTRATING UNKNOWN IMPASSE NEGOTIATION")
    print("=" * 60)
    print("Scenario: Mysterious error with no clear cause or solution")
    print("=" * 60)

    context = create_impasse_context(
        impasse_type="unknown",
        severity_level="extremely_stuck",
        evidence_summary="Mysterious error occurring during DevPost form submission. System reports success but form data is not being saved. No error messages, no logs, no clear indication of what's wrong.",
        attempted_resolutions=[
            "Check browser console for JavaScript errors",
            "Verify network connectivity and API responses",
            "Inspect form field values and submission data",
            "Test form submission with manual browser interaction",
            "Review DevPost API documentation for changes",
        ],
        failure_reasons=[
            "No JavaScript errors found in console",
            "Network connectivity appears normal",
            "Form field values look correct",
            "Manual submission works fine",
            "API documentation shows no recent changes",
        ],
        current_state={
            "mystery_level": "high",
            "error_type": "silent_failure",
            "affected_component": "form_submission",
            "session_data": {
                "form_data": "appears_valid",
                "submission_attempts": 3,
                "last_success": "never",
                "critical_user_data": "must_not_be_lost",
            },
        },
    )

    print("\n🚀 Initiating negotiation protocol...")
    result = negotiate_impasse_resolution(context)

    print(f"\n📊 NEGOTIATION RESULT:")
    print(f"   Success: {'✅' if result.success else '❌'}")
    print(f"   Impasse Resolved: {'✅' if result.impasse_resolved else '❌'}")
    print(f"   Session Preserved: {'✅' if result.session_preserved else '❌'}")
    print(f"   Human Approved: {'✅' if result.human_approved else '❌'}")
    print(f"   Breadcrumbs Left: {len(result.breadcrumbs_left)}")

    if result.chosen_option:
        print(f"   Chosen Solution: {result.chosen_option.title}")
        print(f"   Risk Level: {result.chosen_option.risk_level}")
        print(
            f"   Success Probability: {result.chosen_option.estimated_success_probability:.0%}"
        )

    return result.success


def main():
    """Run the negotiation protocol demonstration"""

    print("🚀 NEGOTIATION PROTOCOL DEMONSTRATION")
    print("=" * 60)
    print("This demonstration shows how the AI negotiates with the human")
    print("when encountering impasses it cannot resolve autonomously.")
    print("=" * 60)

    demonstrations = [
        ("Technical Impasse", demonstrate_technical_impasse),
        ("Logical Impasse", demonstrate_logical_impasse),
        ("Resource Impasse", demonstrate_resource_impasse),
        ("Unknown Impasse", demonstrate_unknown_impasse),
    ]

    results = []

    for demo_name, demo_func in demonstrations:
        try:
            result = demo_func()
            results.append((demo_name, result))

            if result:
                print(f"\n✅ {demo_name}: NEGOTIATION SUCCESSFUL")
            else:
                print(f"\n❌ {demo_name}: NEGOTIATION FAILED")

        except Exception as e:
            print(f"\n❌ {demo_name}: ERROR - {e}")
            results.append((demo_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("📊 NEGOTIATION PROTOCOL DEMONSTRATION SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"Demonstrations Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total:.1%}")

    if passed == total:
        print("\n🎉 ALL NEGOTIATION SCENARIOS SUCCESSFUL!")
        print("\n💡 Key Features Demonstrated:")
        print("   ✅ General-purpose impasse detection and negotiation")
        print("   ✅ Context-aware solution generation")
        print("   ✅ Session preservation priority enforcement")
        print("   ✅ Breadcrumb trail creation for recovery")
        print("   ✅ Multiple impasse types handled appropriately")
        print("   ✅ Risk assessment and human approval workflows")
        print("   ✅ Graceful handling of mysterious/unknown issues")

        print("\n🤝 Negotiation Process Summary:")
        print("   1. AI detects impasse and cannot resolve autonomously")
        print("   2. AI initiates negotiation protocol with human")
        print("   3. AI presents evidence and attempted resolutions")
        print("   4. AI generates context-specific negotiation options")
        print("   5. Human and AI negotiate the best resolution approach")
        print("   6. AI executes negotiated solution while preserving session")
        print("   7. AI creates breadcrumb trail for future recovery")

        print("\n⚠️  Critical Principle:")
        print("   NEVER flush the session and start over without negotiation!")
        print("   Always attempt to leave a trail of breadcrumbs for recovery.")

    else:
        print(f"\n⚠️  {total - passed} demonstrations failed - review implementation")

    return passed == total


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
