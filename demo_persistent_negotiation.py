#!/usr/bin/env python3
"""
Demo Persistent Negotiation
==========================

Demonstration of the persistent negotiation protocol that stays in
negotiation until the human counterparty provides a clear, executable
direction or disconnects (terminal failure mode).
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from negotiation_protocol import create_impasse_context
from interactive_negotiation_cli import InteractiveNegotiationCLI


def demonstrate_persistent_negotiation():
    """Demonstrate persistent negotiation behavior"""
    
    print("🎭 DEMONSTRATING PERSISTENT NEGOTIATION BEHAVIOR")
    print("=" * 60)
    print("This demo shows how the AI stays in negotiation until:")
    print("1. Human provides clear, executable direction")
    print("2. Human disconnects (Ctrl+D, Ctrl+C, EOF)")
    print("3. Terminal failure mode - AI cannot proceed")
    print("=" * 60)
    
    # Create a realistic impasse scenario
    context = create_impasse_context(
        impasse_type="technical",
        severity_level="very_stuck",
        evidence_summary="LangGraph workflow node execution failing with cryptic error messages. The ghostbusters_consultation_node is throwing PregelNode errors that cannot be resolved through normal debugging.",
        attempted_resolutions=[
            "Restart the specific failing node",
            "Clear node state and retry execution", 
            "Switch to alternative node implementation",
            "Enable debug mode and trace execution step by step",
            "Check node dependencies and imports"
        ],
        failure_reasons=[
            "Node state corruption detected in PregelNode wrapper",
            "Alternative implementation not available in current codebase",
            "Debug mode reveals no obvious issues in node logic",
            "Error messages are non-descriptive and generic",
            "Dependencies appear to be correctly installed"
        ],
        current_state={
            "current_node": "ghostbusters_consultation_node",
            "workflow_state": "executing",
            "error_count": 5,
            "last_error": "PregelNode execution failed with AttributeError",
            "session_data": {
                "important_context": "preserve_this",
                "user_preferences": "session_must_not_be_lost",
                "workflow_progress": "75%_complete"
            },
            "active_components": ["langgraph", "playwright", "browser_session", "telemetry_graph"]
        }
    )
    
    print(f"\n🚀 Starting persistent negotiation session...")
    print(f"   Impasse Type: {context.impasse_type}")
    print(f"   Severity Level: {context.severity_level}")
    print(f"   Session Preservation Priority: {context.session_preservation_priority}")
    
    # Start the interactive negotiation
    cli = InteractiveNegotiationCLI()
    
    print(f"\n💡 NEGOTIATION BEHAVIOR DEMONSTRATION:")
    print(f"   - AI will stay in negotiation loop until clear direction received")
    print(f"   - Human can ask questions, request info, suggest alternatives")
    print(f"   - AI will not proceed without executable direction")
    print(f"   - Session preservation is the top priority")
    print(f"   - Terminal failure modes are handled gracefully")
    
    try:
        result = cli.start_negotiation_session(context)
        
        print(f"\n📊 NEGOTIATION SESSION COMPLETED:")
        if result:
            print(f"   Success: {'✅' if result.success else '❌'}")
            print(f"   Impasse Resolved: {'✅' if result.impasse_resolved else '❌'}")
            print(f"   Session Preserved: {'✅' if result.session_preserved else '❌'}")
            print(f"   Human Approved: {'✅' if result.human_approved else '❌'}")
            print(f"   Breadcrumbs Left: {len(result.breadcrumbs_left)}")
            
            if result.chosen_option:
                print(f"   Executed Solution: {result.chosen_option.title}")
                print(f"   Solution Risk Level: {result.chosen_option.risk_level}")
        else:
            print(f"   Negotiation was abandoned or failed")
        
        return result
        
    except KeyboardInterrupt:
        print(f"\n\n🛑 DEMONSTRATION INTERRUPTED")
        print(f"   This simulates human counterparty disconnecting (Ctrl+C)")
        print(f"   AI would handle this as a terminal failure mode")
        return None
    
    except EOFError:
        print(f"\n\n🛑 DEMONSTRATION TERMINATED")
        print(f"   This simulates human counterparty disconnecting (Ctrl+D)")
        print(f"   AI would handle this as a terminal failure mode")
        return None


def demonstrate_negotiation_scenarios():
    """Demonstrate different negotiation scenarios"""
    
    print("\n🎭 DEMONSTRATING NEGOTIATION SCENARIOS")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "Clear Direction Scenario",
            "description": "Human provides clear, executable direction immediately",
            "simulation": "Human selects option 1 (Run Diagnostic Tests)"
        },
        {
            "name": "Information Gathering Scenario", 
            "description": "Human asks for more information before deciding",
            "simulation": "Human requests info about options, then selects"
        },
        {
            "name": "Custom Solution Scenario",
            "description": "Human suggests a custom solution approach",
            "simulation": "Human proposes custom fix, AI analyzes and executes"
        },
        {
            "name": "Disconnection Scenario",
            "description": "Human counterparty disconnects during negotiation",
            "simulation": "Human disconnects (Ctrl+D/Ctrl+C), AI handles gracefully"
        },
        {
            "name": "Terminal Failure Scenario",
            "description": "AI reaches terminal failure mode without direction",
            "simulation": "AI cannot proceed, preserves session with breadcrumbs"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 Scenario {i}: {scenario['name']}")
        print(f"   Description: {scenario['description']}")
        print(f"   Simulation: {scenario['simulation']}")
        
        # Show how AI would handle each scenario
        if "Clear Direction" in scenario['name']:
            print(f"   🤖 AI Response: 'Clear direction received! Executing your choice...'")
            print(f"   ✅ Outcome: Solution executed, session preserved")
        
        elif "Information" in scenario['name']:
            print(f"   🤖 AI Response: 'Let me provide detailed information...'")
            print(f"   🤖 AI Response: 'What would you like to do next?'")
            print(f"   ✅ Outcome: Continues negotiation until clear direction")
        
        elif "Custom" in scenario['name']:
            print(f"   🤖 AI Response: 'Interesting approach! Let me analyze this...'")
            print(f"   🤖 AI Response: 'Clear custom direction received! Executing...'")
            print(f"   ✅ Outcome: Custom solution executed if feasible")
        
        elif "Disconnection" in scenario['name']:
            print(f"   🤖 AI Response: 'Human counterparty disconnected. Terminal failure mode.'")
            print(f"   🤖 AI Response: 'I cannot proceed. Preserving session with breadcrumbs.'")
            print(f"   ✅ Outcome: Graceful handling, session preserved")
        
        elif "Terminal Failure" in scenario['name']:
            print(f"   🤖 AI Response: 'Maximum negotiation rounds reached.'")
            print(f"   🤖 AI Response: 'Terminal failure mode - cannot proceed without direction.'")
            print(f"   ✅ Outcome: Session preserved, clear failure state")
    
    return True


def main():
    """Main demonstration function"""
    
    print("🚀 PERSISTENT NEGOTIATION DEMONSTRATION")
    print("=" * 60)
    print("This demonstration shows the persistent negotiation protocol")
    print("that stays in negotiation until clear direction is received.")
    print("=" * 60)
    
    # Demonstrate negotiation scenarios
    demonstrate_negotiation_scenarios()
    
    print(f"\n💡 KEY PRINCIPLES DEMONSTRATED:")
    print(f"   ✅ AI stays in negotiation until clear direction received")
    print(f"   ✅ Human can gather information and explore options")
    print(f"   ✅ AI handles disconnections gracefully (terminal failure mode)")
    print(f"   ✅ Session preservation is always the top priority")
    print(f"   ✅ Breadcrumbs are left for recovery in all scenarios")
    print(f"   ✅ AI never proceeds without executable direction")
    
    print(f"\n🤝 NEGOTIATION TERMINATION CONDITIONS:")
    print(f"   1. Human provides clear, executable direction → Execute solution")
    print(f"   2. Human disconnects (Ctrl+D/Ctrl+C) → Terminal failure mode")
    print(f"   3. Maximum negotiation rounds reached → Terminal failure mode")
    print(f"   4. Human explicitly exits negotiation → Terminal failure mode")
    
    print(f"\n⚠️  TERMINAL FAILURE MODE BEHAVIOR:")
    print(f"   - AI recognizes it cannot proceed")
    print(f"   - Session is preserved with comprehensive breadcrumbs")
    print(f"   - Clear error state is established")
    print(f"   - Human can resume later with full context")
    
    # Note: We don't run the actual interactive session in demo mode
    # as it would require real human input
    print(f"\n📝 NOTE: To test actual interactive negotiation, run:")
    print(f"   python3 interactive_negotiation_cli.py")
    print(f"   This will start a real negotiation session requiring human input.")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
