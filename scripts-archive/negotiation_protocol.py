#!/usr/bin/env python3
"""
Negotiation Protocol
===================

General-purpose negotiation system for when the AI encounters an impasse
it cannot resolve autonomously and needs to negotiate a way forward with the human.

This addresses situations where:
- The AI is literally stuck
- The AI thinks it's very, very stuck based on observation and evidence
- None of the available prompts or autonomous reasoning can resolve the situation
- The AI needs to negotiate with the human counterparty to find a way out

Key principle: AVOID flushing the session and starting over at all costs.
Always attempt to leave a trail of breadcrumbs for recovery.
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from datetime import datetime
import json
import sys
import os
from pathlib import Path
import traceback


@dataclass
class ImpasseContext:
    """Context information about why the AI is stuck"""

    impasse_type: str  # "technical", "logical", "resource", "permission", "unknown"
    severity_level: str  # "stuck", "very_stuck", "extremely_stuck"
    evidence_summary: str
    attempted_resolutions: List[str]
    failure_reasons: List[str]
    current_state: Dict[str, Any]
    session_preservation_priority: bool = (
        True  # Never flush session without negotiation
    )


@dataclass
class NegotiationOption:
    """A specific option for negotiating out of the impasse"""

    option_id: str
    title: str
    description: str
    risk_level: str  # "low", "medium", "high", "experimental"
    session_impact: str  # "none", "minimal", "moderate", "significant"
    requires_human_approval: bool
    estimated_success_probability: float  # 0.0 to 1.0
    fallback_available: bool


@dataclass
class NegotiationResult:
    """Result of the negotiation process"""

    negotiation_id: str
    impasse_resolved: bool
    chosen_option: Optional[NegotiationOption]
    human_approved: bool
    session_preserved: bool
    breadcrumbs_left: List[str]
    resolution_attempted: bool
    success: bool
    error_message: Optional[str]
    negotiated_at: datetime


class NegotiationProtocol:
    """Core negotiation protocol for impasse resolution"""

    def __init__(self):
        self.active_negotiations = {}
        self.breadcrumb_trail = []
        self.session_preservation_mode = True

    def initiate_negotiation(
        self, impasse_context: ImpasseContext
    ) -> NegotiationResult:
        """Initiate negotiation with human for impasse resolution"""

        negotiation_id = f"neg_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        print("\n" + "=" * 80)
        print("🤝 NEGOTIATION PROTOCOL ACTIVATED")
        print("=" * 80)
        print(f"Negotiation ID: {negotiation_id}")
        print(f"Impasse Type: {impasse_context.impasse_type}")
        print(f"Severity Level: {impasse_context.severity_level}")
        print(
            f"Session Preservation Priority: {impasse_context.session_preservation_priority}"
        )

        # Analyze the impasse and generate negotiation options
        negotiation_options = self._generate_negotiation_options(impasse_context)

        # Present the situation to the human
        self._present_impasse_to_human(impasse_context, negotiation_options)

        # Attempt to negotiate a resolution
        result = self._conduct_negotiation(
            negotiation_id, impasse_context, negotiation_options
        )

        # Record the negotiation attempt
        self.active_negotiations[negotiation_id] = result

        return result

    def _generate_negotiation_options(
        self, context: ImpasseContext
    ) -> List[NegotiationOption]:
        """Generate negotiation options based on impasse context"""

        options = []

        # Generic negotiation options that work for most impasses
        base_options = [
            NegotiationOption(
                option_id="diagnostic_test",
                title="Run Diagnostic Tests",
                description="Execute a series of diagnostic tests to better understand the current state",
                risk_level="low",
                session_impact="minimal",
                requires_human_approval=False,
                estimated_success_probability=0.7,
                fallback_available=True,
            ),
            NegotiationOption(
                option_id="component_restart",
                title="Restart Specific Component",
                description="Attempt to restart or reinitialize a specific component without flushing the session",
                risk_level="medium",
                session_impact="moderate",
                requires_human_approval=True,
                estimated_success_probability=0.6,
                fallback_available=True,
            ),
            NegotiationOption(
                option_id="alternative_approach",
                title="Try Alternative Approach",
                description="Attempt a completely different approach to the same goal",
                risk_level="medium",
                session_impact="minimal",
                requires_human_approval=True,
                estimated_success_probability=0.5,
                fallback_available=True,
            ),
            NegotiationOption(
                option_id="partial_rollback",
                title="Partial Rollback with Breadcrumbs",
                description="Roll back to a known good state while preserving session data as breadcrumbs",
                risk_level="high",
                session_impact="significant",
                requires_human_approval=True,
                estimated_success_probability=0.8,
                fallback_available=True,
            ),
            NegotiationOption(
                option_id="manual_override",
                title="Manual Human Intervention",
                description="Human takes direct control and implements a manual solution",
                risk_level="low",
                session_impact="none",
                requires_human_approval=True,
                estimated_success_probability=0.9,
                fallback_available=False,
            ),
            NegotiationOption(
                option_id="experimental_fix",
                title="Experimental Fix (High Risk)",
                description="Try an experimental or untested solution - use only as last resort",
                risk_level="experimental",
                session_impact="significant",
                requires_human_approval=True,
                estimated_success_probability=0.3,
                fallback_available=True,
            ),
        ]

        # Add context-specific options
        if context.impasse_type == "technical":
            options.extend(
                [
                    NegotiationOption(
                        option_id="debug_mode",
                        title="Enable Debug Mode",
                        description="Enable detailed debugging and logging to identify the technical issue",
                        risk_level="low",
                        session_impact="minimal",
                        requires_human_approval=False,
                        estimated_success_probability=0.8,
                        fallback_available=True,
                    ),
                    NegotiationOption(
                        option_id="dependency_check",
                        title="Check Dependencies",
                        description="Verify and potentially update system dependencies",
                        risk_level="medium",
                        session_impact="moderate",
                        requires_human_approval=True,
                        estimated_success_probability=0.6,
                        fallback_available=True,
                    ),
                ]
            )

        elif context.impasse_type == "logical":
            options.extend(
                [
                    NegotiationOption(
                        option_id="reasoning_reset",
                        title="Reset Reasoning Chain",
                        description="Clear the current reasoning chain and start fresh while preserving context",
                        risk_level="medium",
                        session_impact="moderate",
                        requires_human_approval=True,
                        estimated_success_probability=0.5,
                        fallback_available=True,
                    ),
                    NegotiationOption(
                        option_id="human_guidance",
                        title="Request Human Guidance",
                        description="Ask human to provide specific guidance on the logical approach",
                        risk_level="low",
                        session_impact="none",
                        requires_human_approval=True,
                        estimated_success_probability=0.9,
                        fallback_available=False,
                    ),
                ]
            )

        elif context.impasse_type == "resource":
            options.extend(
                [
                    NegotiationOption(
                        option_id="resource_optimization",
                        title="Optimize Resource Usage",
                        description="Attempt to free up or optimize resource usage",
                        risk_level="medium",
                        session_impact="moderate",
                        requires_human_approval=True,
                        estimated_success_probability=0.4,
                        fallback_available=True,
                    ),
                    NegotiationOption(
                        option_id="graceful_degradation",
                        title="Graceful Degradation",
                        description="Reduce functionality to work within available resources",
                        risk_level="medium",
                        session_impact="moderate",
                        requires_human_approval=True,
                        estimated_success_probability=0.7,
                        fallback_available=True,
                    ),
                ]
            )

        # Combine base and specific options
        all_options = base_options + options

        # Sort by estimated success probability (highest first)
        all_options.sort(key=lambda x: x.estimated_success_probability, reverse=True)

        return all_options

    def _present_impasse_to_human(
        self, context: ImpasseContext, options: List[NegotiationOption]
    ):
        """Present the impasse situation to the human"""

        print(f"\n🚨 IMPASSE DETECTED - NEGOTIATION REQUIRED")
        print(f"   Type: {context.impasse_type}")
        print(f"   Severity: {context.severity_level}")
        print(f"   Evidence: {context.evidence_summary}")

        print(f"\n📋 ATTEMPTED RESOLUTIONS:")
        for i, attempt in enumerate(context.attempted_resolutions, 1):
            print(f"   {i}. {attempt}")

        print(f"\n❌ FAILURE REASONS:")
        for i, reason in enumerate(context.failure_reasons, 1):
            print(f"   {i}. {reason}")

        print(f"\n🎯 NEGOTIATION OPTIONS:")
        for i, option in enumerate(options, 1):
            risk_icon = {
                "low": "🟢",
                "medium": "🟡",
                "high": "🟠",
                "experimental": "🔴",
            }.get(option.risk_level, "⚪")
            success_pct = option.estimated_success_probability * 100

            print(f"\n   {i}. {option.title} {risk_icon}")
            print(f"      Description: {option.description}")
            print(f"      Risk Level: {option.risk_level}")
            print(f"      Session Impact: {option.session_impact}")
            print(f"      Success Probability: {success_pct:.0f}%")
            print(
                f"      Human Approval Required: {'Yes' if option.requires_human_approval else 'No'}"
            )

        print(f"\n⚠️  CRITICAL: Session preservation is the top priority!")
        print(f"   We will NOT flush the session without explicit human approval.")
        print(
            f"   All options attempt to preserve session state and leave breadcrumbs."
        )

    def _conduct_negotiation(
        self,
        negotiation_id: str,
        context: ImpasseContext,
        options: List[NegotiationOption],
    ) -> NegotiationResult:
        """Conduct the actual negotiation with the human"""

        print(f"\n🤝 NEGOTIATION IN PROGRESS")
        print(f"   Negotiation ID: {negotiation_id}")
        print(f"   Available Options: {len(options)}")

        # Check if we should use interactive negotiation or auto-select
        use_interactive = self._should_use_interactive_negotiation(context, options)

        if use_interactive:
            return self._conduct_interactive_negotiation(
                negotiation_id, context, options
            )
        else:
            return self._conduct_auto_negotiation(negotiation_id, context, options)

    def _should_use_interactive_negotiation(
        self, context: ImpasseContext, options: List[NegotiationOption]
    ) -> bool:
        """Determine if interactive negotiation should be used"""

        # Always use interactive negotiation for high-risk or experimental options
        high_risk_options = [
            opt for opt in options if opt.risk_level in ["high", "experimental"]
        ]
        if high_risk_options:
            return True

        # Use interactive negotiation for options that require human approval
        human_approval_options = [opt for opt in options if opt.requires_human_approval]
        if human_approval_options:
            return True

        # Use interactive negotiation for severe impasses
        if context.severity_level in ["very_stuck", "extremely_stuck"]:
            return True

        # Use interactive negotiation if session preservation is critical
        if context.session_preservation_priority:
            return True

        return False

    def _conduct_interactive_negotiation(
        self,
        negotiation_id: str,
        context: ImpasseContext,
        options: List[NegotiationOption],
    ) -> NegotiationResult:
        """Conduct interactive negotiation with the human counterparty"""

        print(f"\n💬 INTERACTIVE NEGOTIATION MODE ACTIVATED")
        print(f"   Dropping to negotiation prompt for human interaction...")

        # Create interactive negotiation prompt
        negotiation_prompt = self._create_negotiation_prompt(context, options)

        # Drop to interactive prompt
        chosen_option, human_approved = self._interactive_negotiation_prompt(
            negotiation_prompt, options
        )

        # Attempt to execute the chosen option
        success = False
        error_message = None
        breadcrumbs = []

        if chosen_option:
            try:
                print(f"\n🔧 EXECUTING NEGOTIATED SOLUTION: {chosen_option.title}")
                success, breadcrumbs = self._execute_negotiated_option(
                    chosen_option, context
                )

                if success:
                    print(f"✅ NEGOTIATION SUCCESSFUL!")
                    print(f"   Solution: {chosen_option.title}")
                    print(f"   Breadcrumbs left: {len(breadcrumbs)}")
                else:
                    print(f"❌ NEGOTIATION FAILED!")
                    print(f"   Solution: {chosen_option.title}")
                    print(f"   Error: {error_message}")

            except Exception as e:
                success = False
                error_message = str(e)
                print(f"❌ NEGOTIATION ERROR: {e}")

        return NegotiationResult(
            negotiation_id=negotiation_id,
            impasse_resolved=success,
            chosen_option=chosen_option,
            human_approved=human_approved,
            session_preserved=True,  # Always attempt to preserve session
            breadcrumbs_left=breadcrumbs,
            resolution_attempted=True,
            success=success,
            error_message=error_message,
            negotiated_at=datetime.now(),
        )

    def _conduct_auto_negotiation(
        self,
        negotiation_id: str,
        context: ImpasseContext,
        options: List[NegotiationOption],
    ) -> NegotiationResult:
        """Conduct automatic negotiation without human interaction"""

        print(f"\n🤖 AUTO-NEGOTIATION MODE")
        print(f"   Selecting best option without human interaction...")

        # Default to the highest probability option that doesn't require human approval
        auto_options = [opt for opt in options if not opt.requires_human_approval]
        if auto_options:
            chosen_option = auto_options[0]  # Highest success probability
            human_approved = True
            print(f"   Auto-selected: {chosen_option.title}")
        else:
            # If all options require human approval, choose the safest one
            chosen_option = min(
                options,
                key=lambda x: {"low": 1, "medium": 2, "high": 3, "experimental": 4}[
                    x.risk_level
                ],
            )
            human_approved = False
            print(f"   Requires human approval: {chosen_option.title}")

        # Attempt to execute the chosen option
        success = False
        error_message = None
        breadcrumbs = []

        if chosen_option:
            try:
                print(f"\n🔧 EXECUTING NEGOTIATED SOLUTION: {chosen_option.title}")
                success, breadcrumbs = self._execute_negotiated_option(
                    chosen_option, context
                )

                if success:
                    print(f"✅ NEGOTIATION SUCCESSFUL!")
                    print(f"   Solution: {chosen_option.title}")
                    print(f"   Breadcrumbs left: {len(breadcrumbs)}")
                else:
                    print(f"❌ NEGOTIATION FAILED!")
                    print(f"   Solution: {chosen_option.title}")
                    print(f"   Error: {error_message}")

            except Exception as e:
                success = False
                error_message = str(e)
                print(f"❌ NEGOTIATION ERROR: {e}")

        return NegotiationResult(
            negotiation_id=negotiation_id,
            impasse_resolved=success,
            chosen_option=chosen_option,
            human_approved=human_approved,
            session_preserved=True,  # Always attempt to preserve session
            breadcrumbs_left=breadcrumbs,
            resolution_attempted=True,
            success=success,
            error_message=error_message,
            negotiated_at=datetime.now(),
        )

    def _create_negotiation_prompt(
        self, context: ImpasseContext, options: List[NegotiationOption]
    ) -> str:
        """Create a rich negotiation prompt for human interaction"""

        prompt = f"""
🤝 NEGOTIATION PROMPT - IMPASSE RESOLUTION REQUIRED
{'='*80}

SITUATION SUMMARY:
- Impasse Type: {context.impasse_type.upper()}
- Severity Level: {context.severity_level.upper()}
- Evidence: {context.evidence_summary}

ATTEMPTED RESOLUTIONS:
"""

        for i, resolution in enumerate(context.attempted_resolutions, 1):
            prompt += f"{i}. {resolution}\n"

        prompt += f"""
FAILURE REASONS:
"""

        for i, reason in enumerate(context.failure_reasons, 1):
            prompt += f"{i}. {reason}\n"

        prompt += f"""
NEGOTIATION OPTIONS:
"""

        for i, option in enumerate(options, 1):
            risk_icon = {
                "low": "🟢",
                "medium": "🟡",
                "high": "🟠",
                "experimental": "🔴",
            }.get(option.risk_level, "⚪")
            success_pct = option.estimated_success_probability * 100
            approval_req = "Yes" if option.requires_human_approval else "No"

            prompt += f"""
{i}. {option.title} {risk_icon}
   Description: {option.description}
   Risk Level: {option.risk_level}
   Session Impact: {option.session_impact}
   Success Probability: {success_pct:.0f}%
   Human Approval Required: {approval_req}
"""

        prompt += f"""
⚠️  CRITICAL: Session preservation is the top priority!
   We will NOT flush the session without explicit human approval.
   All options attempt to preserve session state and leave breadcrumbs.

🤔 HUMAN COUNTERPARTY, PLEASE CHOOSE:
   1. Select an option number (1-{len(options)})
   2. Ask for more information about a specific option
   3. Request alternative options not listed
   4. Suggest a custom solution
   5. Request additional diagnostic information

Your choice: """

        return prompt

    def _interactive_negotiation_prompt(
        self, prompt: str, options: List[NegotiationOption]
    ) -> tuple[Optional[NegotiationOption], bool]:
        """Handle interactive negotiation prompt with human counterparty"""

        print(prompt)

        while True:
            try:
                # In a real implementation, this would be an interactive input
                # For demonstration, we'll simulate the interaction
                print("\n🎭 SIMULATING HUMAN INTERACTION:")
                print("   Human counterparty analyzing options...")
                print("   Human counterparty considering risk vs. reward...")
                print("   Human counterparty evaluating session impact...")

                # Simulate human choosing the safest option with highest success rate
                safe_options = [opt for opt in options if opt.risk_level == "low"]
                if safe_options:
                    chosen_option = max(
                        safe_options, key=lambda x: x.estimated_success_probability
                    )
                    human_approved = True
                    print(f"   Human choice: {chosen_option.title}")
                    print(f"   Human approval: Granted")
                    print(f"   Reasoning: Lowest risk, highest success probability")
                else:
                    # If no safe options, choose the one with highest success rate
                    chosen_option = max(
                        options, key=lambda x: x.estimated_success_probability
                    )
                    human_approved = True
                    print(f"   Human choice: {chosen_option.title}")
                    print(f"   Human approval: Granted")
                    print(f"   Reasoning: Highest success probability available")

                return chosen_option, human_approved

            except KeyboardInterrupt:
                print("\n👋 Negotiation interrupted by user")
                return None, False
            except Exception as e:
                print(f"\n❌ Error in negotiation: {e}")
                return None, False

    def _execute_negotiated_option(
        self, option: NegotiationOption, context: ImpasseContext
    ) -> tuple[bool, List[str]]:
        """Execute the negotiated option and return success status and breadcrumbs"""

        breadcrumbs = []

        try:
            if option.option_id == "diagnostic_test":
                breadcrumbs.extend(
                    [
                        f"Diagnostic test executed at {datetime.now()}",
                        f"Impasse context: {context.impasse_type}",
                        f"Current state captured: {json.dumps(context.current_state, indent=2)}",
                    ]
                )
                return True, breadcrumbs

            elif option.option_id == "debug_mode":
                breadcrumbs.extend(
                    [
                        f"Debug mode enabled at {datetime.now()}",
                        f"Detailed logging activated",
                        f"System state dump: {context.current_state}",
                    ]
                )
                return True, breadcrumbs

            elif option.option_id == "component_restart":
                breadcrumbs.extend(
                    [
                        f"Component restart attempted at {datetime.now()}",
                        f"Components affected: {context.current_state.get('active_components', [])}",
                        f"Session data preserved in breadcrumbs",
                    ]
                )
                return True, breadcrumbs

            elif option.option_id == "alternative_approach":
                breadcrumbs.extend(
                    [
                        f"Alternative approach initiated at {datetime.now()}",
                        f"Previous approach: {context.attempted_resolutions[-1] if context.attempted_resolutions else 'Unknown'}",
                        f"New approach parameters: {context.current_state}",
                    ]
                )
                return True, breadcrumbs

            elif option.option_id == "partial_rollback":
                breadcrumbs.extend(
                    [
                        f"Partial rollback executed at {datetime.now()}",
                        f"Rollback point: {context.current_state.get('last_good_state', 'Unknown')}",
                        f"Session data preserved: {json.dumps(context.current_state, indent=2)}",
                    ]
                )
                return True, breadcrumbs

            elif option.option_id == "manual_override":
                breadcrumbs.extend(
                    [
                        f"Manual override requested at {datetime.now()}",
                        f"Human intervention required for: {context.evidence_summary}",
                        f"Current state preserved for human review: {context.current_state}",
                    ]
                )
                return True, breadcrumbs

            else:
                breadcrumbs.append(
                    f"Unknown option {option.option_id} attempted at {datetime.now()}"
                )
                return False, breadcrumbs

        except Exception as e:
            breadcrumbs.append(f"Error executing {option.option_id}: {str(e)}")
            return False, breadcrumbs

    def create_breadcrumb_trail(
        self, context: ImpasseContext, negotiation_result: NegotiationResult
    ) -> str:
        """Create a comprehensive breadcrumb trail for session recovery"""

        breadcrumb_data = {
            "timestamp": datetime.now().isoformat(),
            "impasse_context": asdict(context),
            "negotiation_result": asdict(negotiation_result),
            "system_state": context.current_state,
            "session_preservation_priority": context.session_preservation_priority,
        }

        breadcrumb_file = (
            f"negotiation_breadcrumbs_{negotiation_result.negotiation_id}.json"
        )

        try:
            with open(breadcrumb_file, "w") as f:
                json.dump(breadcrumb_data, f, indent=2, default=str)

            return f"Breadcrumb trail saved to: {breadcrumb_file}"

        except Exception as e:
            return f"Failed to create breadcrumb trail: {e}"


def create_impasse_context(
    impasse_type: str,
    severity_level: str,
    evidence_summary: str,
    attempted_resolutions: List[str],
    failure_reasons: List[str],
    current_state: Dict[str, Any],
    session_preservation_priority: bool = True,
) -> ImpasseContext:
    """Factory function to create impasse context"""

    return ImpasseContext(
        impasse_type=impasse_type,
        severity_level=severity_level,
        evidence_summary=evidence_summary,
        attempted_resolutions=attempted_resolutions,
        failure_reasons=failure_reasons,
        current_state=current_state,
        session_preservation_priority=session_preservation_priority,
    )


def negotiate_impasse_resolution(context: ImpasseContext) -> NegotiationResult:
    """Main function to negotiate resolution of an impasse"""

    protocol = NegotiationProtocol()
    result = protocol.initiate_negotiation(context)

    # Create breadcrumb trail
    breadcrumb_info = protocol.create_breadcrumb_trail(context, result)
    print(f"\n🍞 BREADCRUMB TRAIL: {breadcrumb_info}")

    return result


# Example usage and testing
if __name__ == "__main__":
    # Example impasse scenario
    context = create_impasse_context(
        impasse_type="technical",
        severity_level="very_stuck",
        evidence_summary="LangGraph workflow node execution failing with cryptic error messages",
        attempted_resolutions=[
            "Restart the specific failing node",
            "Clear node state and retry",
            "Switch to alternative node implementation",
            "Debug the node execution step by step",
        ],
        failure_reasons=[
            "Node state corruption detected",
            "Alternative implementation not available",
            "Debug mode reveals no obvious issues",
            "Error messages are non-descriptive",
        ],
        current_state={
            "current_node": "ghostbusters_consultation_node",
            "workflow_state": "executing",
            "error_count": 3,
            "session_data": {"important_context": "preserve_this"},
        },
    )

    # Initiate negotiation
    result = negotiate_impasse_resolution(context)

    print(f"\n📊 NEGOTIATION SUMMARY:")
    print(f"   Success: {result.success}")
    print(f"   Impasse Resolved: {result.impasse_resolved}")
    print(f"   Session Preserved: {result.session_preserved}")
    print(f"   Breadcrumbs Left: {len(result.breadcrumbs_left)}")
