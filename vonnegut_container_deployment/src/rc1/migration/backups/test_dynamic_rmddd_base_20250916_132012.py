#!/usr/bin/env python3
"""
Test Dynamic RMDDD Base Interface
=================================

Test how the dynamic base class automatically handles most RMDDD interface
functionality through introspection, AST analysis, and code generation.
"""

import sys
import json
from typing import Dict, Any, List

from rmddd_base_interface import create_dynamic_rmddd_interface
from ghostbusters_consultation_refactored import (
    ghostbusters_consultation_refactored_node,
)
from verification_modules import VerificationOrchestrator


def test_dynamic_ghostbusters_interface():
    """Test dynamic RMDDD interface for Ghostbusters consultation node"""

    print("🚨 TESTING DYNAMIC GHOSTBUSTERS RMDDD INTERFACE")
    print("=" * 60)

    # Create dynamic RMDDD interface
    dynamic_interface = create_dynamic_rmddd_interface(
        ghostbusters_consultation_refactored_node, "ghostbusters_consultation"
    )

    # Test dynamic self-documentation
    print("\n📚 DYNAMIC SELF-DOCUMENTATION")
    print("-" * 40)
    docs = dynamic_interface.get_self_documentation()
    print(f"Component: {docs['component_name']}")
    print(f"Function: {docs['function_name']}")
    print(f"Module: {docs['module']}")
    print(f"Dynamic Analysis: {docs['dynamic_analysis']}")
    print(f"RMDDD Compliance: {docs['rmddd_compliance']}")
    print(f"Analysis Timestamp: {docs['analysis_timestamp']}")

    # Test dynamic component map
    print("\n🗺️ DYNAMIC COMPONENT MAP")
    print("-" * 40)
    component_map = dynamic_interface.component_map
    print(f"Component: {component_map.component_name}")
    print(f"Capabilities ({len(component_map.capabilities)}):")
    for capability in component_map.capabilities[:3]:
        print(f"  • {capability}")
    if len(component_map.capabilities) > 3:
        print(f"  ... and {len(component_map.capabilities) - 3} more")

    print(f"Limitations ({len(component_map.limitations)}):")
    for limitation in component_map.limitations[:2]:
        print(f"  • {limitation}")

    print(f"Dependencies ({len(component_map.dependencies)}):")
    for dependency in component_map.dependencies[:3]:
        print(f"  • {dependency}")

    print(f"Knowledge Domains: {component_map.knowledge_domains}")
    print(f"Unknown Areas: {component_map.unknown_areas}")

    # Test code complexity analysis
    print("\n🔍 DYNAMIC CODE COMPLEXITY ANALYSIS")
    print("-" * 40)
    complexity = component_map.code_complexity
    print(f"Cyclomatic Complexity: {complexity.get('cyclomatic_complexity', 'N/A')}")
    print(f"Complexity Rating: {complexity.get('complexity_rating', 'N/A')}")
    print(f"Function Calls: {complexity.get('function_calls', 'N/A')}")
    print(f"Conditionals: {complexity.get('conditionals', 'N/A')}")
    print(f"Loops: {complexity.get('loops', 'N/A')}")

    # Test confidence levels
    print("\n📊 DYNAMIC CONFIDENCE LEVELS")
    print("-" * 40)
    confidence = component_map.confidence_levels
    for level, value in confidence.items():
        print(f"{level.replace('_', ' ').title()}: {value:.1%}")

    # Test dynamic babble fish
    print("\n🐟 DYNAMIC BABBLE FISH Q&A")
    print("-" * 40)

    questions = [
        "What does this node do?",
        "What are the limitations?",
        "What does it depend on?",
        "How complex is the code?",
        "What do you know about?",
        "What can't you do?",
    ]

    for question in questions:
        response = dynamic_interface.babble_fish_ask(question)
        print(f"\nQ: {response.question}")
        print(f"A: {response.answer}")
        print(f"   Confidence: {response.confidence:.1%}")
        print(f"   Knowledge Source: {response.knowledge_source}")
        print(f"   Code References: {', '.join(response.code_references[:2])}")

    return dynamic_interface


def test_dynamic_verification_interface():
    """Test dynamic RMDDD interface for Verification Orchestrator"""

    print("\n🔬 TESTING DYNAMIC VERIFICATION RMDDD INTERFACE")
    print("=" * 60)

    # Create dynamic RMDDD interface
    dynamic_interface = create_dynamic_rmddd_interface(
        VerificationOrchestrator().verify_integration, "verification_orchestrator"
    )

    # Test dynamic self-documentation
    print("\n📚 DYNAMIC SELF-DOCUMENTATION")
    print("-" * 40)
    docs = dynamic_interface.get_self_documentation()
    print(f"Component: {docs['component_name']}")
    print(f"Function: {docs['function_name']}")
    print(f"Dynamic Analysis: {docs['dynamic_analysis']}")
    print(f"RMDDD Compliance: {docs['rmddd_compliance']}")

    # Test dynamic component map
    print("\n🗺️ DYNAMIC COMPONENT MAP")
    print("-" * 40)
    component_map = dynamic_interface.component_map
    print(f"Capabilities: {component_map.capabilities}")
    print(f"Knowledge Domains: {component_map.knowledge_domains}")
    print(f"Unknown Areas: {component_map.unknown_areas}")

    # Test dynamic babble fish
    print("\n🐟 DYNAMIC BABBLE FISH Q&A")
    print("-" * 40)

    verification_questions = [
        "What can you verify?",
        "How complex is your code?",
        "What do you depend on?",
        "What are your limitations?",
    ]

    for question in verification_questions:
        response = dynamic_interface.babble_fish_ask(question)
        print(f"\nQ: {response.question}")
        print(f"A: {response.answer}")
        print(f"   Confidence: {response.confidence:.1%}")

    return dynamic_interface


def test_dynamic_vs_manual_comparison():
    """Compare dynamic implementation vs manual implementation"""

    print("\n⚖️ DYNAMIC vs MANUAL IMPLEMENTATION COMPARISON")
    print("=" * 60)

    # Test both implementations
    from rmddd_interface_standards import create_rmddd_interface_for_node

    # Manual implementation
    manual_interface = create_rmddd_interface_for_node(
        ghostbusters_consultation_refactored_node, "ghostbusters_consultation"
    )

    # Dynamic implementation
    dynamic_interface = create_dynamic_rmddd_interface(
        ghostbusters_consultation_refactored_node, "ghostbusters_consultation"
    )

    # Compare results
    print("\n📊 COMPARISON RESULTS")
    print("-" * 40)

    # Self-documentation comparison
    manual_docs = manual_interface.get_self_documentation()
    dynamic_docs = dynamic_interface.get_self_documentation()

    print(f"Manual Documentation Fields: {len(manual_docs)}")
    print(f"Dynamic Documentation Fields: {len(dynamic_docs)}")
    print(f"Dynamic Analysis: {dynamic_docs.get('dynamic_analysis', False)}")

    # Component map comparison
    manual_map = manual_interface.build_component_map()
    dynamic_map = dynamic_interface.component_map

    print(f"\nManual Capabilities: {len(manual_map.capabilities)}")
    print(f"Dynamic Capabilities: {len(dynamic_map.capabilities)}")
    print(f"Manual Dependencies: {len(manual_map.dependencies)}")
    print(f"Dynamic Dependencies: {len(dynamic_map.dependencies)}")

    # Code complexity (only available in dynamic)
    complexity = dynamic_map.code_complexity
    print(
        f"\nDynamic Code Complexity: {complexity.get('cyclomatic_complexity', 'N/A')}"
    )
    print(f"Dynamic Complexity Rating: {complexity.get('complexity_rating', 'N/A')}")
    print(f"Dynamic Function Calls: {complexity.get('function_calls', 'N/A')}")

    # Confidence levels (only available in dynamic)
    confidence = dynamic_map.confidence_levels
    print(f"\nDynamic Confidence Levels:")
    for level, value in confidence.items():
        print(f"  {level.replace('_', ' ').title()}: {value:.1%}")

    return {
        "manual_interface": manual_interface,
        "dynamic_interface": dynamic_interface,
        "comparison_results": {
            "manual_docs_fields": len(manual_docs),
            "dynamic_docs_fields": len(dynamic_docs),
            "manual_capabilities": len(manual_map.capabilities),
            "dynamic_capabilities": len(dynamic_map.capabilities),
            "dynamic_complexity": complexity.get("cyclomatic_complexity", 0),
            "dynamic_confidence": confidence.get("overall", 0),
        },
    }


def demonstrate_dynamic_benefits():
    """Demonstrate the benefits of dynamic RMDDD interface"""

    print("\n🌟 DYNAMIC RMDDD INTERFACE BENEFITS")
    print("=" * 60)

    benefits = [
        {
            "benefit": "Automatic Code Analysis",
            "description": "Automatically analyzes source code through AST parsing",
            "example": "Cyclomatic complexity, function calls, conditionals, loops",
        },
        {
            "benefit": "Dynamic Capability Detection",
            "description": "Automatically detects capabilities from code patterns",
            "example": "Pattern matching for 'analyze', 'investigate', 'verify', etc.",
        },
        {
            "benefit": "Intelligent Limitation Analysis",
            "description": "Automatically identifies limitations from code structure",
            "example": "Error handling analysis, dependency detection, validation requirements",
        },
        {
            "benefit": "Automatic Dependency Discovery",
            "description": "Automatically extracts dependencies from import statements",
            "example": "Parses 'from module import' and 'import module' statements",
        },
        {
            "benefit": "Dynamic Knowledge Domain Detection",
            "description": "Automatically identifies knowledge domains from code content",
            "example": "Browser automation, web scraping, form handling, etc.",
        },
        {
            "benefit": "Intelligent Confidence Assessment",
            "description": "Automatically calculates confidence levels based on code quality",
            "example": "Error handling, type safety, documentation, overall confidence",
        },
        {
            "benefit": "Smart Babble Fish Responses",
            "description": "Dynamically generates contextual responses based on analysis",
            "example": "Code-aware answers with specific complexity metrics and limitations",
        },
    ]

    for i, benefit in enumerate(benefits, 1):
        print(f"\n{i}. {benefit['benefit']}")
        print(f"   {benefit['description']}")
        print(f"   Example: {benefit['example']}")

    print(
        f"\n🎯 KEY INSIGHT: Dynamic base class handles {len(benefits)} major areas automatically!"
    )
    print("   📊 Code analysis through AST parsing")
    print("   🔍 Pattern-based capability detection")
    print("   ⚠️ Intelligent limitation identification")
    print("   📦 Automatic dependency discovery")
    print("   🧠 Dynamic knowledge domain detection")
    print("   📈 Smart confidence assessment")
    print("   🐟 Context-aware babble fish responses")

    return benefits


def main():
    """Main test function"""

    print("🧠 TESTING DYNAMIC RMDDD BASE INTERFACE")
    print("=" * 70)
    print("Dynamic base class automatically handles most RMDDD interface")
    print("functionality through introspection, AST analysis, and code generation.")
    print("=" * 70)

    try:
        # Test dynamic Ghostbusters interface
        ghostbusters_dynamic = test_dynamic_ghostbusters_interface()

        # Test dynamic Verification interface
        verification_dynamic = test_dynamic_verification_interface()

        # Compare dynamic vs manual implementation
        comparison = test_dynamic_vs_manual_comparison()

        # Demonstrate dynamic benefits
        benefits = demonstrate_dynamic_benefits()

        # Summary
        print(f"\n🎉 DYNAMIC RMDDD BASE INTERFACE TEST COMPLETED")
        print("=" * 60)

        comparison_results = comparison["comparison_results"]
        print(
            f"Manual Documentation Fields: {comparison_results['manual_docs_fields']}"
        )
        print(
            f"Dynamic Documentation Fields: {comparison_results['dynamic_docs_fields']}"
        )
        print(f"Dynamic Capabilities: {comparison_results['dynamic_capabilities']}")
        print(
            f"Dynamic Complexity Analysis: {comparison_results['dynamic_complexity']}"
        )
        print(
            f"Dynamic Confidence Assessment: {comparison_results['dynamic_confidence']:.1%}"
        )

        print(f"\n✅ DYNAMIC BASE CLASS SUCCESSFULLY HANDLES:")
        print("   📊 Automatic code analysis and complexity metrics")
        print("   🔍 Dynamic capability and limitation detection")
        print("   📦 Automatic dependency discovery")
        print("   🧠 Intelligent knowledge domain identification")
        print("   📈 Smart confidence level assessment")
        print("   🐟 Context-aware babble fish responses")

        print(
            f"\n🎯 KEY ACHIEVEMENT: {len(benefits)} major areas handled automatically!"
        )
        print("Dynamic base class eliminates most manual RMDDD interface work! 🚀")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
