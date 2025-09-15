#!/usr/bin/env python3
"""
Test RMDDD Interfaces
====================

Test the self-documenting interfaces, safe command lines, component maps,
and babble fish for RMDDD-conforming LangGraph nodes.
"""

import sys
import json
from typing import Dict, Any

from rmddd_interface_standards import create_rmddd_interface_for_node
from ghostbusters_consultation_refactored import ghostbusters_consultation_refactored_node
from verification_modules import VerificationOrchestrator


def test_ghostbusters_rmddd_interface():
    """Test RMDDD interface for Ghostbusters consultation node"""
    
    print("🚨 TESTING GHOSTBUSTERS RMDDD INTERFACE")
    print("=" * 50)
    
    # Create RMDDD interface for Ghostbusters node
    ghostbusters_interface = create_rmddd_interface_for_node(
        ghostbusters_consultation_refactored_node,
        "ghostbusters_consultation"
    )
    
    # Test self-documentation
    print("\n📚 SELF-DOCUMENTATION")
    print("-" * 30)
    docs = ghostbusters_interface.get_self_documentation()
    print(f"Node Name: {docs['node_name']}")
    print(f"Purpose: {docs['purpose']}")
    print(f"Function: {docs['function_name']}")
    print(f"Module: {docs['module']}")
    print(f"RMDDD Compliance: {docs['rmddd_compliance']}")
    
    # Test component map
    print("\n🗺️ COMPONENT MAP")
    print("-" * 30)
    component_map = ghostbusters_interface.build_component_map()
    print(f"Component: {component_map.component_name}")
    print(f"Capabilities: {len(component_map.capabilities)}")
    for capability in component_map.capabilities[:3]:
        print(f"  • {capability}")
    if len(component_map.capabilities) > 3:
        print(f"  ... and {len(component_map.capabilities) - 3} more")
    
    print(f"Limitations: {len(component_map.limitations)}")
    for limitation in component_map.limitations:
        print(f"  • {limitation}")
    
    print(f"Dependencies: {len(component_map.dependencies)}")
    for dependency in component_map.dependencies:
        print(f"  • {dependency}")
    
    # Test babble fish
    print("\n🐟 BABBLE FISH Q&A")
    print("-" * 30)
    
    questions = [
        "What does this node do?",
        "What are the limitations?",
        "What inputs does it accept?",
        "What outputs does it produce?",
        "What does it depend on?",
        "What doesn't it know about?",
        "How confident is it in its capabilities?"
    ]
    
    for question in questions:
        response = ghostbusters_interface.babble_fish_ask(question)
        print(f"\nQ: {response.question}")
        print(f"A: {response.answer}")
        print(f"   Confidence: {response.confidence:.1%}")
        print(f"   Knowledge Source: {response.knowledge_source}")
        if response.follow_up_suggestions:
            print(f"   Follow-ups: {', '.join(response.follow_up_suggestions[:2])}")
    
    # Test safe command line
    print("\n💻 SAFE COMMAND LINE")
    print("-" * 30)
    parser = ghostbusters_interface.create_safe_command_line()
    help_text = parser.format_help()
    print("Command line help preview:")
    print(help_text[:500] + "..." if len(help_text) > 500 else help_text)
    
    # Test interface summary
    print("\n📋 INTERFACE SUMMARY")
    print("-" * 30)
    summary = ghostbusters_interface.get_interface_summary()
    print(f"Interface Name: {summary['name']}")
    print(f"Documentation Available: {'✅' if summary['documentation'] else '❌'}")
    print(f"Component Map Available: {'✅' if summary['component_map'] else '❌'}")
    print(f"Command Line Available: {'✅' if summary['command_line_help'] else '❌'}")
    print(f"Babble Fish Questions: {len(summary['babble_fish_questions'])}")
    
    return ghostbusters_interface


def test_verification_rmddd_interface():
    """Test RMDDD interface for Verification Orchestrator"""
    
    print("\n🔬 TESTING VERIFICATION RMDDD INTERFACE")
    print("=" * 50)
    
    # Create RMDDD interface for Verification Orchestrator
    verification_interface = create_rmddd_interface_for_node(
        VerificationOrchestrator().verify_integration,
        "verification_orchestrator"
    )
    
    # Test self-documentation
    print("\n📚 SELF-DOCUMENTATION")
    print("-" * 30)
    docs = verification_interface.get_self_documentation()
    print(f"Node Name: {docs['node_name']}")
    print(f"Purpose: {docs['purpose']}")
    print(f"Function: {docs['function_name']}")
    print(f"RMDDD Compliance: {docs['rmddd_compliance']}")
    
    # Test component map
    print("\n🗺️ COMPONENT MAP")
    print("-" * 30)
    component_map = verification_interface.build_component_map()
    print(f"Component: {component_map.component_name}")
    print(f"Capabilities: {len(component_map.capabilities)}")
    for capability in component_map.capabilities:
        print(f"  • {capability}")
    
    print(f"Knowledge Domains: {component_map.knowledge_domains}")
    print(f"Unknown Areas: {component_map.unknown_areas}")
    
    # Test babble fish with verification-specific questions
    print("\n🐟 BABBLE FISH Q&A")
    print("-" * 30)
    
    verification_questions = [
        "What can you verify?",
        "How do you analyze execution characteristics?",
        "What are your confidence levels?",
        "What can't you verify?",
        "What dependencies do you have?"
    ]
    
    for question in verification_questions:
        response = verification_interface.babble_fish_ask(question)
        print(f"\nQ: {response.question}")
        print(f"A: {response.answer}")
        print(f"   Confidence: {response.confidence:.1%}")
    
    return verification_interface


def test_rmddd_interface_standards():
    """Test RMDDD interface standards compliance"""
    
    print("\n✅ TESTING RMDDD INTERFACE STANDARDS")
    print("=" * 50)
    
    # Test Ghostbusters interface
    ghostbusters_interface = test_ghostbusters_rmddd_interface()
    
    # Test Verification interface
    verification_interface = test_verification_rmddd_interface()
    
    # Test standards compliance
    print("\n🎯 RMDDD STANDARDS COMPLIANCE")
    print("-" * 30)
    
    interfaces = [ghostbusters_interface, verification_interface]
    compliance_results = {}
    
    for interface in interfaces:
        name = interface.name
        compliance = {
            "self_documenting_interface": bool(interface.get_self_documentation()),
            "safe_command_line": bool(interface.create_safe_command_line()),
            "component_map": bool(interface.build_component_map()),
            "babble_fish": bool(interface.babble_fish_ask("test")),
            "interface_summary": bool(interface.get_interface_summary())
        }
        
        compliance_results[name] = compliance
        
        print(f"\n{name}:")
        for standard, compliant in compliance.items():
            status = "✅" if compliant else "❌"
            print(f"  {status} {standard}")
    
    # Overall compliance
    all_compliant = all(
        all(compliance.values()) 
        for compliance in compliance_results.values()
    )
    
    print(f"\n🎉 OVERALL RMDDD COMPLIANCE: {'✅ PASS' if all_compliant else '❌ FAIL'}")
    
    return compliance_results


def demonstrate_rmddd_benefits():
    """Demonstrate the benefits of RMDDD interfaces"""
    
    print("\n🌟 RMDDD INTERFACE BENEFITS")
    print("=" * 50)
    
    benefits = [
        {
            "benefit": "Self-Documenting Interfaces",
            "description": "Every component automatically documents itself",
            "example": "Component knows its purpose, parameters, usage examples"
        },
        {
            "benefit": "Safe Command Lines",
            "description": "Every component has a safe CLI for testing/debugging",
            "example": "python ghostbusters_consultation.py --test --interactive"
        },
        {
            "benefit": "Component Maps",
            "description": "Every component has a knowledge graph of what it knows/doesn't know",
            "example": "Capabilities, limitations, dependencies, confidence levels"
        },
        {
            "benefit": "Babble Fish Q&A",
            "description": "Every component can answer questions about itself",
            "example": "What do you do? What can't you do? What do you depend on?"
        },
        {
            "benefit": "RMDDD Compliance",
            "description": "Every component follows RMDDD principles",
            "example": "Modular, testable, documented, single responsibility"
        }
    ]
    
    for i, benefit in enumerate(benefits, 1):
        print(f"\n{i}. {benefit['benefit']}")
        print(f"   {benefit['description']}")
        print(f"   Example: {benefit['example']}")
    
    print(f"\n🎯 KEY INSIGHT: Every RMDDD-conforming LangGraph node comes with:")
    print("   📚 Self-documenting interface")
    print("   💻 Safe command line interface")
    print("   🗺️ Component map (knowledge graph)")
    print("   🐟 Babble fish (Q&A interface)")
    
    return benefits


def main():
    """Main test function"""
    
    print("🧠 TESTING RMDDD INTERFACE STANDARDS")
    print("=" * 70)
    print("Every RMDDD-conforming LangGraph node must have:")
    print("1. Self-documenting interface")
    print("2. Safe command line interface")
    print("3. Component map (knowledge graph)")
    print("4. Babble fish (Q&A interface)")
    print("=" * 70)
    
    try:
        # Test RMDDD interface standards
        compliance_results = test_rmddd_interface_standards()
        
        # Demonstrate benefits
        benefits = demonstrate_rmddd_benefits()
        
        # Summary
        print(f"\n🎉 RMDDD INTERFACE STANDARDS TEST COMPLETED")
        print("=" * 50)
        
        total_interfaces = len(compliance_results)
        compliant_interfaces = sum(
            1 for compliance in compliance_results.values()
            if all(compliance.values())
        )
        
        print(f"Interfaces Tested: {total_interfaces}")
        print(f"Fully Compliant: {compliant_interfaces}")
        print(f"Compliance Rate: {compliant_interfaces/total_interfaces:.1%}")
        
        if compliant_interfaces == total_interfaces:
            print(f"\n✅ ALL INTERFACES ARE RMDDD COMPLIANT!")
            print("Every component has its own map and babble fish! 🗺️🐟")
            return True
        else:
            print(f"\n❌ SOME INTERFACES NEED IMPROVEMENT")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
