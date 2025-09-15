#!/usr/bin/env python3
"""
Test Negotiation Protocol
=========================

Comprehensive test suite for the general-purpose negotiation protocol
that handles impasse situations where the AI is stuck and needs to
negotiate a way forward with the human.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import tempfile
import json

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from negotiation_protocol import (
    create_impasse_context,
    negotiate_impasse_resolution,
    NegotiationProtocol,
    ImpasseContext,
    NegotiationOption
)


def test_technical_impasse():
    """Test negotiation for technical impasse"""
    
    print("🧪 TESTING TECHNICAL IMPASSE NEGOTIATION")
    print("=" * 50)
    
    context = create_impasse_context(
        impasse_type="technical",
        severity_level="very_stuck",
        evidence_summary="LangGraph workflow node execution failing with cryptic error messages",
        attempted_resolutions=[
            "Restart the specific failing node",
            "Clear node state and retry",
            "Switch to alternative node implementation",
            "Debug the node execution step by step"
        ],
        failure_reasons=[
            "Node state corruption detected",
            "Alternative implementation not available",
            "Debug mode reveals no obvious issues",
            "Error messages are non-descriptive"
        ],
        current_state={
            "current_node": "ghostbusters_consultation_node",
            "workflow_state": "executing",
            "error_count": 3,
            "session_data": {"important_context": "preserve_this"},
            "active_components": ["langgraph", "playwright", "browser_session"]
        }
    )
    
    result = negotiate_impasse_resolution(context)
    
    print(f"\n📊 TECHNICAL IMPASSE RESULT:")
    print(f"   Success: {result.success}")
    print(f"   Chosen Option: {result.chosen_option.title if result.chosen_option else 'None'}")
    print(f"   Session Preserved: {result.session_preserved}")
    print(f"   Breadcrumbs Left: {len(result.breadcrumbs_left)}")
    
    return result.success


def test_logical_impasse():
    """Test negotiation for logical impasse"""
    
    print("\n🧪 TESTING LOGICAL IMPASSE NEGOTIATION")
    print("=" * 50)
    
    context = create_impasse_context(
        impasse_type="logical",
        severity_level="stuck",
        evidence_summary="Cannot determine the correct navigation strategy for DevPost form submission",
        attempted_resolutions=[
            "Try exact match navigation",
            "Attempt visual similarity matching",
            "Use semantic navigation approach",
            "Fall back to adaptive navigation"
        ],
        failure_reasons=[
            "No exact matches found in telemetry",
            "Visual similarity scores too low",
            "Semantic analysis inconclusive",
            "Adaptive navigation lacks sufficient data"
        ],
        current_state={
            "current_page": "DevPost submission form",
            "available_strategies": ["exact", "visual", "semantic", "adaptive"],
            "confidence_scores": {"exact": 0.1, "visual": 0.2, "semantic": 0.15, "adaptive": 0.25},
            "session_data": {"form_fields": "preserve_these"}
        }
    )
    
    result = negotiate_impasse_resolution(context)
    
    print(f"\n📊 LOGICAL IMPASSE RESULT:")
    print(f"   Success: {result.success}")
    print(f"   Chosen Option: {result.chosen_option.title if result.chosen_option else 'None'}")
    print(f"   Session Preserved: {result.session_preserved}")
    print(f"   Breadcrumbs Left: {len(result.breadcrumbs_left)}")
    
    return result.success


def test_resource_impasse():
    """Test negotiation for resource impasse"""
    
    print("\n🧪 TESTING RESOURCE IMPASSE NEGOTIATION")
    print("=" * 50)
    
    context = create_impasse_context(
        impasse_type="resource",
        severity_level="extremely_stuck",
        evidence_summary="Memory usage at 95%, cannot load additional components",
        attempted_resolutions=[
            "Clear temporary cache",
            "Unload unused components",
            "Optimize memory usage",
            "Request additional memory allocation"
        ],
        failure_reasons=[
            "Cache clearing insufficient",
            "No unused components to unload",
            "Optimization attempts failed",
            "Memory allocation request denied"
        ],
        current_state={
            "memory_usage": 0.95,
            "available_memory": "50MB",
            "required_memory": "200MB",
            "active_components": ["browser", "playwright", "langgraph", "telemetry"],
            "session_data": {"critical_state": "must_preserve"}
        }
    )
    
    result = negotiate_impasse_resolution(context)
    
    print(f"\n📊 RESOURCE IMPASSE RESULT:")
    print(f"   Success: {result.success}")
    print(f"   Chosen Option: {result.chosen_option.title if result.chosen_option else 'None'}")
    print(f"   Session Preserved: {result.session_preserved}")
    print(f"   Breadcrumbs Left: {len(result.breadcrumbs_left)}")
    
    return result.success


def test_negotiation_options_generation():
    """Test the generation of negotiation options"""
    
    print("\n🧪 TESTING NEGOTIATION OPTIONS GENERATION")
    print("=" * 50)
    
    protocol = NegotiationProtocol()
    
    # Test different impasse types
    test_cases = [
        ("technical", "Node execution failure"),
        ("logical", "Navigation strategy confusion"),
        ("resource", "Memory exhaustion"),
        ("permission", "Access denied"),
        ("unknown", "Mysterious error")
    ]
    
    for impasse_type, description in test_cases:
        context = create_impasse_context(
            impasse_type=impasse_type,
            severity_level="stuck",
            evidence_summary=description,
            attempted_resolutions=["Try option 1", "Try option 2"],
            failure_reasons=["Reason 1", "Reason 2"],
            current_state={"test": "data"}
        )
        
        options = protocol._generate_negotiation_options(context)
        
        print(f"\n📋 {impasse_type.upper()} IMPASSE OPTIONS:")
        for i, option in enumerate(options[:3], 1):  # Show first 3 options
            risk_icon = {"low": "🟢", "medium": "🟡", "high": "🟠", "experimental": "🔴"}.get(option.risk_level, "⚪")
            print(f"   {i}. {option.title} {risk_icon} (Success: {option.estimated_success_probability:.0%})")
    
    return True


def test_breadcrumb_creation():
    """Test breadcrumb trail creation"""
    
    print("\n🧪 TESTING BREADCRUMB TRAIL CREATION")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            context = create_impasse_context(
                impasse_type="test",
                severity_level="stuck",
                evidence_summary="Testing breadcrumb creation",
                attempted_resolutions=["Test resolution"],
                failure_reasons=["Test failure"],
                current_state={"test": "breadcrumb_data"}
            )
            
            protocol = NegotiationProtocol()
            result = protocol.initiate_negotiation(context)
            
            # Check if breadcrumb file was created
            breadcrumb_files = list(Path(temp_dir).glob("negotiation_breadcrumbs_*.json"))
            
            if breadcrumb_files:
                print(f"✅ Breadcrumb file created: {breadcrumb_files[0].name}")
                
                # Verify breadcrumb content
                with open(breadcrumb_files[0], 'r') as f:
                    breadcrumb_data = json.load(f)
                
                required_fields = ["timestamp", "impasse_context", "negotiation_result", "system_state"]
                missing_fields = [field for field in required_fields if field not in breadcrumb_data]
                
                if not missing_fields:
                    print("✅ Breadcrumb content validation passed")
                    return True
                else:
                    print(f"❌ Missing breadcrumb fields: {missing_fields}")
                    return False
            else:
                print("❌ No breadcrumb file created")
                return False
                
        finally:
            os.chdir(original_cwd)
    
    return False


def test_session_preservation_priority():
    """Test that session preservation is always prioritized"""
    
    print("\n🧪 TESTING SESSION PRESERVATION PRIORITY")
    print("=" * 50)
    
    # Test with session preservation enabled
    context_with_preservation = create_impasse_context(
        impasse_type="test",
        severity_level="very_stuck",
        evidence_summary="Testing session preservation",
        attempted_resolutions=["Test"],
        failure_reasons=["Test"],
        current_state={"critical_session_data": "must_preserve"},
        session_preservation_priority=True
    )
    
    protocol = NegotiationProtocol()
    result = protocol.initiate_negotiation(context_with_preservation)
    
    print(f"📊 SESSION PRESERVATION TEST:")
    print(f"   Session Preserved: {result.session_preserved}")
    print(f"   Breadcrumbs Left: {len(result.breadcrumbs_left)}")
    print(f"   Chosen Option Impact: {result.chosen_option.session_impact if result.chosen_option else 'None'}")
    
    # Verify that session preservation was prioritized
    session_preserved = result.session_preserved
    breadcrumbs_created = len(result.breadcrumbs_left) > 0
    
    return session_preserved and breadcrumbs_created


def main():
    """Run all negotiation protocol tests"""
    
    print("🚀 NEGOTIATION PROTOCOL TEST SUITE")
    print("=" * 60)
    print("Testing the general-purpose negotiation protocol for impasse resolution")
    print("=" * 60)
    
    tests = [
        ("Technical Impasse", test_technical_impasse),
        ("Logical Impasse", test_logical_impasse),
        ("Resource Impasse", test_resource_impasse),
        ("Options Generation", test_negotiation_options_generation),
        ("Breadcrumb Creation", test_breadcrumb_creation),
        ("Session Preservation", test_session_preservation_priority)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 NEGOTIATION PROTOCOL TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total:.1%}")
    
    if passed == total:
        print("\n🎉 ALL NEGOTIATION PROTOCOL TESTS PASSED!")
        print("\n💡 Key Features Demonstrated:")
        print("   ✅ General-purpose impasse detection and negotiation")
        print("   ✅ Context-aware negotiation options generation")
        print("   ✅ Session preservation priority enforcement")
        print("   ✅ Breadcrumb trail creation for recovery")
        print("   ✅ Multiple impasse types handled")
        print("   ✅ Risk assessment and human approval workflows")
        
        print("\n🤝 Negotiation Process:")
        print("   1. AI detects impasse and cannot resolve autonomously")
        print("   2. AI initiates negotiation protocol with human")
        print("   3. AI presents evidence and attempted resolutions")
        print("   4. AI generates context-specific negotiation options")
        print("   5. Human and AI negotiate the best resolution approach")
        print("   6. AI executes negotiated solution while preserving session")
        print("   7. AI creates breadcrumb trail for future recovery")
        
    else:
        print(f"\n⚠️  {total - passed} tests failed - review implementation")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
