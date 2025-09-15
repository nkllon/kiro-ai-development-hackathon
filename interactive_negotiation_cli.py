#!/usr/bin/env python3
"""
Interactive Negotiation CLI
==========================

Real interactive negotiation interface that drops to a text prompt
for the AI to negotiate with the human counterparty when encountering
an impasse that cannot be resolved autonomously.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json
import tempfile
from typing import List, Optional

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from negotiation_protocol import (
    create_impasse_context,
    NegotiationProtocol,
    ImpasseContext,
    NegotiationOption
)


class InteractiveNegotiationCLI:
    """Interactive CLI for real-time negotiation with human counterparty"""
    
    def __init__(self):
        self.protocol = NegotiationProtocol()
        self.negotiation_history = []
    
    def start_negotiation_session(self, context: ImpasseContext):
        """Start an interactive negotiation session"""
        
        print("\n" + "="*80)
        print("🤝 INTERACTIVE NEGOTIATION SESSION STARTED")
        print("="*80)
        print(f"Session ID: {datetime.now().strftime('%Y%m%d_%H%M%S')}")
        print(f"Impasse Type: {context.impasse_type}")
        print(f"Severity: {context.severity_level}")
        
        # Generate negotiation options
        options = self.protocol._generate_negotiation_options(context)
        
        # Present the situation
        self._present_situation(context, options)
        
        # Conduct interactive negotiation
        result = self._conduct_interactive_negotiation(context, options)
        
        # Save negotiation history
        self.negotiation_history.append({
            "timestamp": datetime.now().isoformat(),
            "context": context.__dict__,
            "options": [opt.__dict__ for opt in options],
            "result": result.__dict__ if result else None
        })
        
        return result
    
    def _present_situation(self, context: ImpasseContext, options: List[NegotiationOption]):
        """Present the impasse situation to the human"""
        
        print(f"\n🚨 IMPASSE DETECTED - HUMAN COUNTERPARTY REQUIRED")
        print(f"   Type: {context.impasse_type.upper()}")
        print(f"   Severity: {context.severity_level.upper()}")
        print(f"   Evidence: {context.evidence_summary}")
        
        print(f"\n📋 ATTEMPTED RESOLUTIONS:")
        for i, resolution in enumerate(context.attempted_resolutions, 1):
            print(f"   {i}. {resolution}")
        
        print(f"\n❌ FAILURE REASONS:")
        for i, reason in enumerate(context.failure_reasons, 1):
            print(f"   {i}. {reason}")
        
        print(f"\n🎯 AVAILABLE NEGOTIATION OPTIONS:")
        for i, option in enumerate(options, 1):
            risk_icon = {"low": "🟢", "medium": "🟡", "high": "🟠", "experimental": "🔴"}.get(option.risk_level, "⚪")
            success_pct = option.estimated_success_probability * 100
            approval_req = "Yes" if option.requires_human_approval else "No"
            
            print(f"\n   {i}. {option.title} {risk_icon}")
            print(f"      Description: {option.description}")
            print(f"      Risk Level: {option.risk_level}")
            print(f"      Session Impact: {option.session_impact}")
            print(f"      Success Probability: {success_pct:.0f}%")
            print(f"      Human Approval Required: {approval_req}")
    
    def _conduct_interactive_negotiation(self, context: ImpasseContext, options: List[NegotiationOption]):
        """Conduct real interactive negotiation with human"""
        
        print(f"\n💬 INTERACTIVE NEGOTIATION PROMPT")
        print("="*60)
        print("🤖 AI: I'm stuck and need your help to resolve this impasse.")
        print("🤖 AI: I've analyzed the situation and generated several options.")
        print("🤖 AI: Please review the options above and let's negotiate a solution.")
        print("🤖 AI: I want to preserve our session data, so let's be careful.")
        print("🤖 AI: I will stay in this negotiation until you provide a clear direction.")
        print("="*60)
        
        negotiation_rounds = 0
        max_rounds = 50  # Prevent infinite loops, but allow extensive negotiation
        
        while negotiation_rounds < max_rounds:
            negotiation_rounds += 1
            try:
                print(f"\n🤔 HUMAN COUNTERPARTY, WHAT WOULD YOU LIKE TO DO?")
                print(f"   1. Select option number (1-{len(options)})")
                print(f"   2. Ask for more information about an option")
                print(f"   3. Request alternative options")
                print(f"   4. Suggest a custom solution")
                print(f"   5. Request additional diagnostics")
                print(f"   6. See current session state")
                print(f"   7. Exit negotiation (abandon impasse resolution)")
                
                choice = input(f"\n🤖 AI: Your choice (round {negotiation_rounds}): ").strip().lower()
                
                if choice in [str(i) for i in range(1, len(options) + 1)]:
                    # Human selected an option
                    option_index = int(choice) - 1
                    chosen_option = options[option_index]
                    
                    print(f"\n🤖 AI: You selected option {choice}: {chosen_option.title}")
                    print(f"🤖 AI: Let me confirm this choice...")
                    
                    # Ask for confirmation if it's a risky option
                    if chosen_option.risk_level in ["high", "experimental"]:
                        confirm = input(f"🤖 AI: This is a {chosen_option.risk_level} risk option. Are you sure? (yes/no): ").strip().lower()
                        if confirm not in ["yes", "y"]:
                            print(f"🤖 AI: Understood. Let's continue negotiating other options.")
                            continue
                    
                    # Execute the chosen option - THIS IS AN EXECUTABLE DIRECTION
                    print(f"🤖 AI: Clear direction received! Executing your choice...")
                    return self._execute_chosen_option(chosen_option, context)
                
                elif choice == "2":
                    # Ask for more information
                    self._handle_information_request(options)
                
                elif choice == "3":
                    # Request alternative options
                    self._handle_alternative_request(context, options)
                
                elif choice == "4":
                    # Suggest custom solution
                    custom_result = self._handle_custom_solution_request(context)
                    if custom_result:
                        # Custom solution was provided and executed
                        return custom_result
                    # Otherwise, continue negotiating
                
                elif choice == "5":
                    # Request additional diagnostics
                    self._handle_diagnostics_request(context)
                    print(f"🤖 AI: Diagnostics complete. Let's continue negotiating...")
                
                elif choice == "6":
                    # Show current session state
                    self._show_session_state(context)
                    print(f"🤖 AI: Session state displayed. What would you like to do next?")
                
                elif choice == "7":
                    # Exit negotiation - TERMINAL FAILURE MODE
                    print(f"\n🤖 AI: Understood. This is a terminal failure mode.")
                    print(f"🤖 AI: I cannot proceed without your direction.")
                    print(f"🤖 AI: Session will be preserved with breadcrumbs.")
                    return self._create_abandonment_result(context)
                
                else:
                    print(f"\n🤖 AI: I didn't understand that choice. Please try again.")
                    print(f"🤖 AI: I need a clear direction to proceed.")
                
            except KeyboardInterrupt:
                print(f"\n\n🤖 AI: Human counterparty disconnected (Ctrl+D/Ctrl+C).")
                print(f"🤖 AI: This is a terminal failure mode - I cannot proceed.")
                print(f"🤖 AI: Preserving session with breadcrumbs.")
                return self._create_abandonment_result(context)
            except EOFError:
                print(f"\n\n🤖 AI: Human counterparty disconnected (EOF).")
                print(f"🤖 AI: This is a terminal failure mode - I cannot proceed.")
                print(f"🤖 AI: Preserving session with breadcrumbs.")
                return self._create_abandonment_result(context)
            except Exception as e:
                print(f"\n🤖 AI: Error in negotiation: {e}")
                print(f"🤖 AI: Let's try a different approach. I'm still waiting for your direction.")
        
        # If we've exhausted negotiation rounds without clear direction
        print(f"\n🤖 AI: Maximum negotiation rounds reached ({max_rounds}).")
        print(f"🤖 AI: This is a terminal failure mode - I cannot proceed without clear direction.")
        print(f"🤖 AI: Preserving session with breadcrumbs.")
        return self._create_abandonment_result(context)
    
    def _handle_information_request(self, options: List[NegotiationOption]):
        """Handle request for more information about options"""
        
        print(f"\n🤖 AI: Which option would you like more information about?")
        for i, option in enumerate(options, 1):
            print(f"   {i}. {option.title}")
        
        try:
            choice = input(f"\n🤖 AI: Option number: ").strip()
            option_index = int(choice) - 1
            
            if 0 <= option_index < len(options):
                option = options[option_index]
                print(f"\n📋 DETAILED INFORMATION FOR: {option.title}")
                print(f"   ID: {option.option_id}")
                print(f"   Description: {option.description}")
                print(f"   Risk Level: {option.risk_level}")
                print(f"   Session Impact: {option.session_impact}")
                print(f"   Success Probability: {option.estimated_success_probability:.1%}")
                print(f"   Requires Human Approval: {'Yes' if option.requires_human_approval else 'No'}")
                print(f"   Fallback Available: {'Yes' if option.fallback_available else 'No'}")
                
                # Provide additional context
                if option.risk_level == "experimental":
                    print(f"\n⚠️  EXPERIMENTAL WARNING:")
                    print(f"   This option involves untested solutions.")
                    print(f"   Use only as a last resort.")
                    print(f"   Ensure you have good backups.")
                
                if option.session_impact == "significant":
                    print(f"\n⚠️  SESSION IMPACT WARNING:")
                    print(f"   This option will significantly affect the session.")
                    print(f"   Important data may be lost or modified.")
                    print(f"   Consider alternatives if session preservation is critical.")
            else:
                print(f"\n🤖 AI: Invalid option number. Please try again.")
        
        except ValueError:
            print(f"\n🤖 AI: Please enter a valid number.")
    
    def _handle_alternative_request(self, context: ImpasseContext, current_options: List[NegotiationOption]):
        """Handle request for alternative options"""
        
        print(f"\n🤖 AI: Let me generate some alternative options...")
        
        # Generate additional options based on context
        alternatives = []
        
        if context.impasse_type == "technical":
            alternatives.extend([
                NegotiationOption(
                    option_id="force_restart",
                    title="Force System Restart",
                    description="Force restart the entire system (high risk, will lose session)",
                    risk_level="experimental",
                    session_impact="significant",
                    requires_human_approval=True,
                    estimated_success_probability=0.4,
                    fallback_available=False
                ),
                NegotiationOption(
                    option_id="manual_code_fix",
                    title="Manual Code Fix",
                    description="Human manually fixes the code issue while AI provides guidance",
                    risk_level="medium",
                    session_impact="minimal",
                    requires_human_approval=True,
                    estimated_success_probability=0.8,
                    fallback_available=True
                )
            ])
        
        elif context.impasse_type == "resource":
            alternatives.extend([
                NegotiationOption(
                    option_id="emergency_cleanup",
                    title="Emergency Resource Cleanup",
                    description="Aggressively free up resources, may affect functionality",
                    risk_level="high",
                    session_impact="moderate",
                    requires_human_approval=True,
                    estimated_success_probability=0.6,
                    fallback_available=True
                )
            ])
        
        if alternatives:
            print(f"\n🆕 ALTERNATIVE OPTIONS GENERATED:")
            for i, option in enumerate(alternatives, 1):
                risk_icon = {"low": "🟢", "medium": "🟡", "high": "🟠", "experimental": "🔴"}.get(option.risk_level, "⚪")
                print(f"\n   A{i}. {option.title} {risk_icon}")
                print(f"      Description: {option.description}")
                print(f"      Risk Level: {option.risk_level}")
                print(f"      Success Probability: {option.estimated_success_probability:.0f}%")
            
            print(f"\n🤖 AI: These are additional options I can offer.")
            print(f"🤖 AI: Would you like to consider any of these alternatives?")
        else:
            print(f"\n🤖 AI: I couldn't generate additional alternatives at this time.")
            print(f"🤖 AI: The current options represent the best approaches I can think of.")
    
    def _handle_custom_solution_request(self, context: ImpasseContext):
        """Handle request for custom solution"""
        
        print(f"\n🤖 AI: I'm open to custom solutions!")
        print(f"🤖 AI: What approach would you like to try?")
        print(f"🤖 AI: Please describe your proposed solution.")
        
        custom_solution = input(f"\n🤖 AI: Your custom solution: ").strip()
        
        if custom_solution:
            print(f"\n🤖 AI: Interesting approach: {custom_solution}")
            print(f"🤖 AI: Let me analyze this solution...")
            
            # Analyze the custom solution
            analysis = self._analyze_custom_solution(custom_solution, context)
            
            print(f"\n📊 CUSTOM SOLUTION ANALYSIS:")
            print(f"   Feasibility: {analysis['feasibility']}")
            print(f"   Risk Level: {analysis['risk_level']}")
            print(f"   Session Impact: {analysis['session_impact']}")
            print(f"   Estimated Success: {analysis['success_probability']:.0f}%")
            
            if analysis['feasible']:
                print(f"\n🤖 AI: This solution looks feasible!")
                proceed = input(f"🤖 AI: Should we proceed with your custom solution? (yes/no): ").strip().lower()
                
                if proceed in ["yes", "y"]:
                    # Create custom option
                    custom_option = NegotiationOption(
                        option_id="custom_solution",
                        title="Custom Human Solution",
                        description=custom_solution,
                        risk_level=analysis['risk_level'],
                        session_impact=analysis['session_impact'],
                        requires_human_approval=True,
                        estimated_success_probability=analysis['success_probability'],
                        fallback_available=True
                    )
                    
                    print(f"🤖 AI: Clear custom direction received! Executing your solution...")
                    return self._execute_chosen_option(custom_option, context)
                else:
                    print(f"\n🤖 AI: Understood. Let's continue negotiating other options.")
                    return None  # Continue negotiation
            else:
                print(f"\n🤖 AI: I'm concerned about this approach due to: {analysis['concerns']}")
                print(f"🤖 AI: Let's continue negotiating safer alternatives.")
                return None  # Continue negotiation
        else:
            print(f"\n🤖 AI: No custom solution provided. Let's look at the standard options.")
            return None  # Continue negotiation
    
    def _handle_diagnostics_request(self, context: ImpasseContext):
        """Handle request for additional diagnostics"""
        
        print(f"\n🤖 AI: Running additional diagnostics...")
        print(f"🤖 AI: Gathering system state information...")
        
        diagnostics = {
            "timestamp": datetime.now().isoformat(),
            "impasse_context": context.__dict__,
            "system_info": {
                "python_version": sys.version,
                "working_directory": os.getcwd(),
                "available_memory": "Unknown",  # Would need psutil
                "active_processes": "Unknown"   # Would need psutil
            },
            "session_state": context.current_state
        }
        
        print(f"\n📊 DIAGNOSTIC RESULTS:")
        print(f"   Current Time: {diagnostics['timestamp']}")
        print(f"   Working Directory: {diagnostics['system_info']['working_directory']}")
        print(f"   Python Version: {diagnostics['system_info']['python_version']}")
        print(f"   Session State Keys: {list(diagnostics['session_state'].keys())}")
        
        # Save diagnostics to file
        diagnostic_file = f"negotiation_diagnostics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(diagnostic_file, 'w') as f:
                json.dump(diagnostics, f, indent=2, default=str)
            print(f"   Diagnostics saved to: {diagnostic_file}")
        except Exception as e:
            print(f"   Error saving diagnostics: {e}")
        
        print(f"\n🤖 AI: Diagnostics complete. This information may help us choose the best approach.")
    
    def _show_session_state(self, context: ImpasseContext):
        """Show current session state"""
        
        print(f"\n📊 CURRENT SESSION STATE:")
        print(f"   Impasse Type: {context.impasse_type}")
        print(f"   Severity Level: {context.severity_level}")
        print(f"   Session Preservation Priority: {context.session_preservation_priority}")
        
        print(f"\n📋 SESSION DATA:")
        for key, value in context.current_state.items():
            if isinstance(value, (dict, list)):
                print(f"   {key}: {type(value).__name__} with {len(value)} items")
            else:
                print(f"   {key}: {value}")
        
        print(f"\n🤖 AI: This is the current state of our session.")
        print(f"🤖 AI: We want to preserve this data while resolving the impasse.")
    
    def _analyze_custom_solution(self, solution: str, context: ImpasseContext) -> dict:
        """Analyze a custom solution proposed by the human"""
        
        # Simple heuristic analysis
        risk_indicators = ["restart", "kill", "delete", "remove", "force", "experimental"]
        safe_indicators = ["check", "verify", "test", "diagnose", "backup", "preserve"]
        
        solution_lower = solution.lower()
        
        risk_score = sum(1 for indicator in risk_indicators if indicator in solution_lower)
        safety_score = sum(1 for indicator in safe_indicators if indicator in solution_lower)
        
        if risk_score > safety_score:
            risk_level = "high"
            feasibility = "risky"
            session_impact = "significant"
            success_probability = 0.3
        elif risk_score == safety_score:
            risk_level = "medium"
            feasibility = "moderate"
            session_impact = "moderate"
            success_probability = 0.5
        else:
            risk_level = "low"
            feasibility = "safe"
            session_impact = "minimal"
            success_probability = 0.7
        
        concerns = []
        if risk_score > 0:
            concerns.append("Contains potentially risky operations")
        if "session" not in solution_lower and "preserve" not in solution_lower:
            concerns.append("May not consider session preservation")
        
        return {
            "feasible": True,
            "feasibility": feasibility,
            "risk_level": risk_level,
            "session_impact": session_impact,
            "success_probability": success_probability,
            "concerns": "; ".join(concerns) if concerns else "None identified"
        }
    
    def _execute_chosen_option(self, option: NegotiationOption, context: ImpasseContext):
        """Execute the chosen negotiation option"""
        
        print(f"\n🔧 EXECUTING NEGOTIATED SOLUTION: {option.title}")
        print(f"🤖 AI: Implementing: {option.description}")
        
        # Execute the option using the protocol's execution method
        success, breadcrumbs = self.protocol._execute_negotiated_option(option, context)
        
        if success:
            print(f"✅ NEGOTIATION SUCCESSFUL!")
            print(f"🤖 AI: Solution executed successfully!")
            print(f"🤖 AI: Breadcrumbs left: {len(breadcrumbs)}")
            
            # Create success result
            from negotiation_protocol import NegotiationResult
            return NegotiationResult(
                negotiation_id=f"interactive_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                impasse_resolved=True,
                chosen_option=option,
                human_approved=True,
                session_preserved=True,
                breadcrumbs_left=breadcrumbs,
                resolution_attempted=True,
                success=True,
                error_message=None,
                negotiated_at=datetime.now()
            )
        else:
            print(f"❌ NEGOTIATION FAILED!")
            print(f"🤖 AI: Solution execution failed.")
            print(f"🤖 AI: Let's try a different approach.")
            
            # Create failure result
            from negotiation_protocol import NegotiationResult
            return NegotiationResult(
                negotiation_id=f"interactive_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                impasse_resolved=False,
                chosen_option=option,
                human_approved=True,
                session_preserved=True,
                breadcrumbs_left=breadcrumbs,
                resolution_attempted=True,
                success=False,
                error_message="Execution failed",
                negotiated_at=datetime.now()
            )
    
    def _create_abandonment_result(self, context: ImpasseContext):
        """Create result for abandoned negotiation"""
        
        from negotiation_protocol import NegotiationResult
        return NegotiationResult(
            negotiation_id=f"abandoned_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            impasse_resolved=False,
            chosen_option=None,
            human_approved=False,
            session_preserved=True,
            breadcrumbs_left=["Negotiation abandoned by human choice"],
            resolution_attempted=False,
            success=False,
            error_message="Negotiation abandoned",
            negotiated_at=datetime.now()
        )


def main():
    """Main function to run interactive negotiation CLI"""
    
    print("🚀 INTERACTIVE NEGOTIATION CLI")
    print("=" * 50)
    print("This CLI provides real interactive negotiation between")
    print("AI and human counterparty for impasse resolution.")
    print("=" * 50)
    
    # Create example impasse context
    context = create_impasse_context(
        impasse_type="technical",
        severity_level="very_stuck",
        evidence_summary="LangGraph workflow node execution failing with cryptic error messages. The ghostbusters_consultation_node is throwing PregelNode errors that cannot be resolved through normal debugging.",
        attempted_resolutions=[
            "Restart the specific failing node",
            "Clear node state and retry execution",
            "Switch to alternative node implementation",
            "Enable debug mode and trace execution step by step"
        ],
        failure_reasons=[
            "Node state corruption detected in PregelNode wrapper",
            "Alternative implementation not available in current codebase",
            "Debug mode reveals no obvious issues in node logic",
            "Error messages are non-descriptive and generic"
        ],
        current_state={
            "current_node": "ghostbusters_consultation_node",
            "workflow_state": "executing",
            "error_count": 3,
            "session_data": {"important_context": "preserve_this"}
        }
    )
    
    # Start interactive negotiation
    cli = InteractiveNegotiationCLI()
    result = cli.start_negotiation_session(context)
    
    # Display results
    print(f"\n📊 NEGOTIATION SESSION RESULTS:")
    if result:
        print(f"   Success: {'✅' if result.success else '❌'}")
        print(f"   Impasse Resolved: {'✅' if result.impasse_resolved else '❌'}")
        print(f"   Session Preserved: {'✅' if result.session_preserved else '❌'}")
        print(f"   Human Approved: {'✅' if result.human_approved else '❌'}")
        print(f"   Breadcrumbs Left: {len(result.breadcrumbs_left)}")
        
        if result.chosen_option:
            print(f"   Chosen Solution: {result.chosen_option.title}")
    else:
        print(f"   Negotiation was abandoned or failed")
    
    return result


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Interactive negotiation interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
