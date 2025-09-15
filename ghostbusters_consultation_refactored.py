#!/usr/bin/env python3
"""
Ghostbusters Consultation Refactored
====================================

RMDDD-compliant refactored version of the Ghostbusters consultation system.
Uses modular investigation components and proper separation of concerns.
"""

import time
import random
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_core.messages import AIMessage
from langgraph_devpost_state import DevPostState, add_error, update_performance_metrics
from investigation_modules import InvestigationOrchestrator


class GhostbustersConsultationRefactored:
    """Refactored Ghostbusters consultation using RMDDD principles"""

    def __init__(self):
        self.investigation_orchestrator = InvestigationOrchestrator()
        self.consultation_history = []
        self.consultation_id = f"gb_consult_{int(time.time())}"

    def run_autonomous_investigation(self, state: DevPostState) -> Dict[str, Any]:
        """Run autonomous investigation using modular components"""

        print(
            f"🚨 Ghostbusters Consultation {self.consultation_id} - Starting Investigation"
        )
        start_time = time.time()

        current_page_data = state.get("session_save_data", {}).get(
            "current_page_data", {}
        )
        confidence = state.get("session_recovery", {}).get("confidence", 0.0)

        # Autonomous exclamations
        autonomous_exclamations = [
            "🚨 GHOSTBUSTERS AUTONOMOUS MODE - We're going in!",
            "🛑 Stand back! Ghostbusters are taking over!",
            "🚨 Emergency protocols activated - autonomous investigation initiated!",
            "🛑 This is too dangerous for human interaction - Ghostbusters deploying!",
        ]

        investigation_start = random.choice(autonomous_exclamations)

        # Store investigation start
        self.consultation_history.append(
            {
                "timestamp": time.time(),
                "phase": "investigation_start",
                "message": investigation_start,
                "confidence": confidence,
            }
        )

        # Run modular investigation
        print("   🔍 Running modular investigation...")
        investigation_results = self.investigation_orchestrator.run_investigation(
            current_page_data
        )

        # Generate recommendations based on investigation
        recommendations = self._generate_recommendations(
            investigation_results, confidence
        )

        # Create consultation report
        consultation_report = {
            "consultation_id": self.consultation_id,
            "start_time": start_time,
            "end_time": time.time(),
            "duration": time.time() - start_time,
            "confidence": confidence,
            "investigation_results": investigation_results,
            "recommendations": recommendations,
            "primary_strategy": recommendations.get("primary_strategy", "unknown"),
            "similarity_type": self._determine_similarity_type(investigation_results),
            "recommendation": recommendations.get("summary", "Investigation completed"),
            "detailed_recommendation": recommendations.get(
                "detailed", "Investigation completed"
            ),
            "risk_assessment": self._assess_risk(investigation_results),
            "next_steps": recommendations.get("next_steps", []),
        }

        # Store investigation completion
        self.consultation_history.append(
            {
                "timestamp": time.time(),
                "phase": "investigation_complete",
                "consultation_report": consultation_report,
                "success": True,
            }
        )

        print(
            f"   Ghostbusters investigation completed in {consultation_report['duration']:.2f}s"
        )

        return consultation_report

    def _generate_recommendations(
        self, investigation_results: Dict[str, Any], confidence: float
    ) -> Dict[str, Any]:
        """Generate recommendations based on investigation results"""

        recommendations = {
            "primary_strategy": "unknown",
            "summary": "Investigation completed",
            "detailed": "No specific recommendation available",
            "next_steps": [],
            "confidence_boost": 0.0,
        }

        # Analyze investigation results to determine strategy
        structure_analysis = (
            investigation_results["results"].get("PageStructureAnalyzer", {}).data
        )
        navigation_analysis = (
            investigation_results["results"].get("NavigationAnalyzer", {}).data
        )
        content_analysis = (
            investigation_results["results"].get("ContentAnalyzer", {}).data
        )

        # Determine primary strategy based on findings
        if structure_analysis.get("url_pattern", {}).get("pattern") == "devpost":
            recommendations["primary_strategy"] = "devpost_adapted"
            recommendations["summary"] = "Known DevPost page - use adapted navigation"
            recommendations["detailed"] = (
                "This appears to be a DevPost page with familiar patterns. Use DevPost-specific navigation strategies."
            )
            recommendations["next_steps"] = [
                "Apply DevPost navigation model",
                "Focus on form completion",
                "Use semantic navigation",
            ]
            recommendations["confidence_boost"] = 0.3

        elif structure_analysis.get("structure_type") in ["form_heavy", "form_light"]:
            recommendations["primary_strategy"] = "form_focused"
            recommendations["summary"] = "Form page detected - focus on form completion"
            recommendations["detailed"] = (
                "This appears to be a form page. Focus on identifying and completing form fields."
            )
            recommendations["next_steps"] = [
                "Analyze form fields",
                "Complete required fields",
                "Submit form",
            ]
            recommendations["confidence_boost"] = 0.2

        elif navigation_analysis.get("total_elements", 0) > 5:
            recommendations["primary_strategy"] = "navigation_focused"
            recommendations["summary"] = (
                "Navigation page detected - focus on navigation elements"
            )
            recommendations["detailed"] = (
                "This page has many navigation elements. Focus on identifying the correct navigation path."
            )
            recommendations["next_steps"] = [
                "Analyze navigation options",
                "Identify target navigation",
                "Execute navigation",
            ]
            recommendations["confidence_boost"] = 0.1

        elif content_analysis.get("content_type") == "project_content":
            recommendations["primary_strategy"] = "content_focused"
            recommendations["summary"] = (
                "Project content page - focus on content analysis"
            )
            recommendations["detailed"] = (
                "This appears to be a project information page. Focus on content analysis and navigation."
            )
            recommendations["next_steps"] = [
                "Analyze content",
                "Identify key information",
                "Navigate based on content",
            ]
            recommendations["confidence_boost"] = 0.15

        else:
            recommendations["primary_strategy"] = "exploratory"
            recommendations["summary"] = "Unknown page type - use exploratory approach"
            recommendations["detailed"] = (
                "This page type is not clearly identifiable. Use exploratory navigation with caution."
            )
            recommendations["next_steps"] = [
                "Explore page structure",
                "Identify interactive elements",
                "Proceed with caution",
            ]
            recommendations["confidence_boost"] = 0.0

        return recommendations

    def _determine_similarity_type(self, investigation_results: Dict[str, Any]) -> str:
        """Determine similarity type based on investigation results"""

        structure_analysis = (
            investigation_results["results"].get("PageStructureAnalyzer", {}).data
        )
        navigation_analysis = (
            investigation_results["results"].get("NavigationAnalyzer", {}).data
        )

        if structure_analysis.get("url_pattern", {}).get("pattern") == "devpost":
            return "devpost_known"
        elif structure_analysis.get("structure_type") in ["form_heavy", "form_light"]:
            return "form_based"
        elif navigation_analysis.get("total_elements", 0) > 5:
            return "navigation_heavy"
        else:
            return "unknown_pattern"

    def _assess_risk(self, investigation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk based on investigation results"""

        diagnostic_tests = (
            investigation_results["results"]
            .get("DiagnosticTester", {})
            .data.get("tests", {})
        )
        overall_confidence = investigation_results["overall_confidence"]

        # Calculate risk factors
        failed_tests = sum(
            1 for test_result in diagnostic_tests.values() if not test_result
        )
        total_tests = len(diagnostic_tests)

        risk_score = (failed_tests / total_tests if total_tests > 0 else 0.5) + (
            1.0 - overall_confidence
        ) * 0.5
        risk_score = max(0.0, min(1.0, risk_score))

        if risk_score < 0.3:
            risk_level = "low"
        elif risk_score < 0.6:
            risk_level = "medium"
        else:
            risk_level = "high"

        return {
            "level": risk_level,
            "score": risk_score,
            "failed_tests": failed_tests,
            "total_tests": total_tests,
            "confidence_factor": overall_confidence,
        }


def ghostbusters_consultation_refactored_node(state: DevPostState) -> DevPostState:
    """
    Node: Ghostbusters Consultation (Refactored)

    RMDDD-compliant version using modular investigation components.
    """

    print("🚨 Ghostbusters Consultation Node (Refactored)")
    start_time = time.time()

    try:
        # Initialize refactored consultation if not exists
        if "ghostbusters_consultation_refactored" not in state:
            state["ghostbusters_consultation_refactored"] = (
                GhostbustersConsultationRefactored()
            )

        consultation = state["ghostbusters_consultation_refactored"]

        # Run autonomous investigation
        consultation_report = consultation.run_autonomous_investigation(state)

        # Store the report in state
        state["ghostbusters_report"] = consultation_report

        # Create summary message
        summary_message = f"📡 GHOSTBUSTERS CONSULTATION COMPLETE (REFACTORED) 📡\n\n"
        summary_message += (
            f"Consultation ID: {consultation_report['consultation_id']}\n"
        )
        summary_message += (
            f"Investigation Duration: {consultation_report['duration']:.2f}s\n"
        )
        summary_message += f"Modules Used: {consultation_report['investigation_results']['successful_modules']}/{consultation_report['investigation_results']['total_modules']}\n"
        summary_message += (
            f"Primary Strategy: {consultation_report['primary_strategy']}\n"
        )
        summary_message += (
            f"Risk Assessment: {consultation_report['risk_assessment']['level']}\n"
        )
        summary_message += (
            f"Recommendation: {consultation_report['recommendation']}\n\n"
        )
        summary_message += "🎯 Returning to Prompt Mode for final decision..."

        state["messages"].append(AIMessage(content=summary_message))

        # Set up return to Prompt Mode
        state["ghostbusters_mode"] = False
        state["prompt_mode_active"] = True
        state["awaiting_ghostbusters_report"] = True
        state["user_input_required"] = True
        state["next_mode"] = "prompt_mode_consensus"

        # Update performance metrics
        consultation_time = time.time() - start_time
        update_performance_metrics(
            state,
            {
                "ghostbusters_consultation_time": consultation_time,
                "investigation_duration": consultation_report["duration"],
                "primary_strategy": consultation_report["primary_strategy"],
                "risk_level": consultation_report["risk_assessment"]["level"],
                "modules_used": consultation_report["investigation_results"][
                    "successful_modules"
                ],
                "total_modules": consultation_report["investigation_results"][
                    "total_modules"
                ],
            },
        )

        print(f"   Ghostbusters consultation completed in {consultation_time:.2f}s")
        print(f"   Primary strategy: {consultation_report['primary_strategy']}")
        print(
            f"   Modules used: {consultation_report['investigation_results']['successful_modules']}/{consultation_report['investigation_results']['total_modules']}"
        )

    except Exception as e:
        add_error(state, f"Ghostbusters consultation failed: {str(e)}")

    return state
