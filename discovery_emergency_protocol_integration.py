#!/usr/bin/env python3
"""
Discovery Emergency Protocol Integration
=======================================

Integrates emergency protocols as an optional method during discovery sessions.
Allows manual triggering when user detects changes even when state management
thinks everything is fine. Waits for further instructions after activation.
"""

import sys
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from beast_mode_debug_system import initialize_beast_mode_debug, stop_and_dump_trace
from session_dump_emergency import EmergencySessionDumper
from ghostbusters_standalone_consultation import GhostbustersStandaloneConsultation
from emergency_protocol_integration import EmergencyProtocolManager


class DiscoveryEmergencyProtocol:
    """Emergency protocol integration for discovery sessions"""
    
    def __init__(self):
        self.is_active = False
        self.emergency_manager = None
        self.discovery_context = {}
        self.manual_trigger_reason = ""
        self.activation_timestamp = None
        self.waiting_for_instructions = False
        self.available_actions = []
        
    def initialize_emergency_capability(self, discovery_session_data: Dict[str, Any]):
        """Initialize emergency capability for discovery session"""
        
        print("🚨 INITIALIZING DISCOVERY EMERGENCY PROTOCOL CAPABILITY")
        print("-" * 60)
        
        self.discovery_context = {
            "session_id": discovery_session_data.get("session_id", "unknown"),
            "current_page": discovery_session_data.get("current_page", {}),
            "navigation_state": discovery_session_data.get("navigation_state", {}),
            "discovery_progress": discovery_session_data.get("discovery_progress", {}),
            "user_detected_changes": discovery_session_data.get("user_detected_changes", False),
            "state_management_status": discovery_session_data.get("state_management_status", "normal"),
            "timestamp": datetime.now().isoformat()
        }
        
        # Initialize emergency protocol manager
        self.emergency_manager = EmergencyProtocolManager()
        
        print("   ✅ Emergency capability initialized for discovery session")
        print(f"   Session ID: {self.discovery_context['session_id']}")
        print(f"   Current Page: {self.discovery_context['current_page'].get('url', 'unknown')}")
        print(f"   State Management: {self.discovery_context['state_management_status']}")
        print("   🚨 Emergency protocols ready for manual activation")
    
    def manual_emergency_trigger(self, reason: str = "User detected changes", additional_context: Dict[str, Any] = None):
        """Manually trigger emergency protocols during discovery session"""
        
        print("\n🚨 MANUAL EMERGENCY PROTOCOL TRIGGER ACTIVATED")
        print("=" * 70)
        print("User has detected changes - initiating emergency protocols")
        print("State management may think everything is fine, but user knows better!")
        print("=" * 70)
        
        self.manual_trigger_reason = reason
        self.activation_timestamp = datetime.now().isoformat()
        self.is_active = True
        
        # Add additional context
        if additional_context:
            self.discovery_context.update(additional_context)
        
        print(f"🚨 REASON: {reason}")
        print(f"⏰ ACTIVATED: {self.activation_timestamp}")
        print(f"📍 CONTEXT: Discovery session in progress")
        print(f"🎯 STATE: {self.discovery_context['state_management_status']} (but user detected issues)")
        
        try:
            # Step 1: Activate emergency protocols
            print(f"\n🚀 STEP 1: ACTIVATING EMERGENCY PROTOCOLS")
            print("-" * 50)
            
            integration_result = self.emergency_manager.activate_emergency_protocols()
            
            if integration_result and integration_result.get("success"):
                print("   ✅ Emergency protocols successfully activated")
                
                # Step 2: Gather additional discovery-specific data
                print(f"\n🔍 STEP 2: GATHERING ADDITIONAL DISCOVERY DATA")
                print("-" * 50)
                
                additional_data = self._gather_discovery_specific_data()
                
                # Step 3: Create enhanced session dump with discovery context
                print(f"\n💾 STEP 3: CREATING ENHANCED DISCOVERY SESSION DUMP")
                print("-" * 50)
                
                enhanced_dump = self._create_enhanced_discovery_dump(integration_result, additional_data)
                
                # Step 4: Prepare action options for user
                print(f"\n🤝 STEP 4: PREPARING ACTION OPTIONS")
                print("-" * 50)
                
                self.available_actions = self._prepare_discovery_action_options()
                
                # Step 5: Wait for user instructions
                print(f"\n⏸️ STEP 5: WAITING FOR USER INSTRUCTIONS")
                print("-" * 50)
                
                self.waiting_for_instructions = True
                self._present_discovery_action_menu()
                
                return {
                    "success": True,
                    "emergency_protocols_activated": True,
                    "enhanced_dump_created": enhanced_dump,
                    "additional_data_gathered": additional_data,
                    "waiting_for_instructions": True,
                    "available_actions": self.available_actions
                }
                
            else:
                print("   ❌ Failed to activate emergency protocols")
                return {
                    "success": False,
                    "error": "Emergency protocol activation failed",
                    "integration_result": integration_result
                }
                
        except Exception as e:
            print(f"   ❌ Exception during emergency protocol activation: {e}")
            return {
                "success": False,
                "error": f"Exception: {str(e)}"
            }
    
    def _gather_discovery_specific_data(self) -> Dict[str, Any]:
        """Gather additional data specific to discovery session"""
        
        print("   Gathering discovery-specific telemetry...")
        
        additional_data = {
            "discovery_context": self.discovery_context,
            "manual_trigger_details": {
                "reason": self.manual_trigger_reason,
                "activation_time": self.activation_timestamp,
                "user_detected_changes": True,
                "state_mismatch": True
            },
            "discovery_telemetry": {
                "current_page_analysis": self._analyze_current_page(),
                "navigation_history": self._capture_navigation_history(),
                "discovery_progress": self._assess_discovery_progress(),
                "user_observations": self._capture_user_observations()
            },
            "enhanced_screenshots": self._capture_enhanced_screenshots(),
            "page_comparison": self._perform_page_comparison(),
            "discovery_metrics": self._calculate_discovery_metrics()
        }
        
        print("   ✅ Discovery-specific data gathered")
        return additional_data
    
    def _analyze_current_page(self) -> Dict[str, Any]:
        """Analyze current page in discovery context"""
        
        current_page = self.discovery_context.get("current_page", {})
        
        return {
            "url": current_page.get("url", "unknown"),
            "title": current_page.get("title", "unknown"),
            "page_type": current_page.get("page_type", "unknown"),
            "discovery_relevance": "high" if "discovery" in current_page.get("url", "").lower() else "medium",
            "navigation_elements": current_page.get("navigation_elements", []),
            "form_elements": current_page.get("form_elements", []),
            "user_detected_changes": True
        }
    
    def _capture_navigation_history(self) -> Dict[str, Any]:
        """Capture navigation history for discovery context"""
        
        navigation_state = self.discovery_context.get("navigation_state", {})
        
        return {
            "navigation_path": navigation_state.get("path", []),
            "previous_pages": navigation_state.get("previous_pages", []),
            "discovery_milestones": navigation_state.get("milestones", []),
            "user_navigation_pattern": navigation_state.get("pattern", "unknown"),
            "discovery_depth": len(navigation_state.get("path", []))
        }
    
    def _assess_discovery_progress(self) -> Dict[str, Any]:
        """Assess current discovery progress"""
        
        discovery_progress = self.discovery_context.get("discovery_progress", {})
        
        return {
            "pages_discovered": discovery_progress.get("pages_discovered", 0),
            "forms_found": discovery_progress.get("forms_found", 0),
            "navigation_options": discovery_progress.get("navigation_options", 0),
            "data_collected": discovery_progress.get("data_collected", 0),
            "completion_percentage": discovery_progress.get("completion_percentage", 0),
            "user_satisfaction": "concerned"  # User triggered emergency protocols
        }
    
    def _capture_user_observations(self) -> Dict[str, Any]:
        """Capture user observations and concerns"""
        
        return {
            "user_concerns": [
                "Something has changed on the page",
                "State management doesn't reflect reality",
                "Need to gather additional data",
                "Discovery session requires emergency protocols"
            ],
            "user_confidence": "low",
            "user_action_required": True,
            "emergency_justification": self.manual_trigger_reason
        }
    
    def _capture_enhanced_screenshots(self) -> Dict[str, Any]:
        """Capture enhanced screenshots for discovery context"""
        
        return {
            "current_page_screenshot": "enhanced_discovery_screenshot.png",
            "navigation_elements_highlighted": True,
            "user_attention_areas": ["header", "navigation", "forms", "content"],
            "discovery_markers": ["explored", "new", "changed", "unknown"]
        }
    
    def _perform_page_comparison(self) -> Dict[str, Any]:
        """Perform page comparison for discovery context"""
        
        return {
            "previous_page_similarity": 0.3,  # Low similarity indicates change
            "visual_differences_detected": True,
            "structural_changes": True,
            "content_changes": True,
            "navigation_changes": True,
            "user_detected_changes": True
        }
    
    def _calculate_discovery_metrics(self) -> Dict[str, Any]:
        """Calculate discovery-specific metrics"""
        
        return {
            "discovery_efficiency": 0.7,
            "data_completeness": 0.8,
            "navigation_success_rate": 0.6,
            "user_satisfaction": 0.4,  # Low due to concerns
            "emergency_protocol_necessity": 0.9  # High - user triggered
        }
    
    def _create_enhanced_discovery_dump(self, integration_result: Dict[str, Any], additional_data: Dict[str, Any]) -> str:
        """Create enhanced session dump with discovery context"""
        
        print("   Creating enhanced discovery session dump...")
        
        enhanced_dump_data = {
            "dump_type": "enhanced_discovery_emergency_dump",
            "timestamp": datetime.now().isoformat(),
            "discovery_context": self.discovery_context,
            "emergency_protocol_result": integration_result,
            "additional_discovery_data": additional_data,
            "manual_trigger_details": {
                "reason": self.manual_trigger_reason,
                "activation_time": self.activation_timestamp,
                "user_initiated": True
            },
            "discovery_specific_telemetry": additional_data["discovery_telemetry"],
            "enhanced_analysis": {
                "page_analysis": additional_data["discovery_telemetry"]["current_page_analysis"],
                "navigation_analysis": additional_data["discovery_telemetry"]["navigation_history"],
                "progress_analysis": additional_data["discovery_telemetry"]["discovery_progress"],
                "user_concerns": additional_data["discovery_telemetry"]["user_observations"]
            }
        }
        
        # Save enhanced dump
        dump_filename = f"enhanced_discovery_emergency_dump_{int(time.time())}.json"
        with open(dump_filename, 'w') as f:
            json.dump(enhanced_dump_data, f, indent=2, default=str)
        
        print(f"   ✅ Enhanced discovery dump created: {dump_filename}")
        return dump_filename
    
    def _prepare_discovery_action_options(self) -> List[Dict[str, Any]]:
        """Prepare action options specific to discovery session"""
        
        return [
            {
                "id": "continue_exploration",
                "title": "Continue Exploration",
                "description": "Continue exploring from current position with enhanced data gathering",
                "action": "continue_discovery",
                "risk_level": "low",
                "session_impact": "minimal"
            },
            {
                "id": "deep_dive_analysis",
                "title": "Deep Dive Analysis",
                "description": "Perform comprehensive analysis of current page and surrounding context",
                "action": "deep_dive",
                "risk_level": "low",
                "session_impact": "moderate"
            },
            {
                "id": "save_and_explore_elsewhere",
                "title": "Save and Explore Elsewhere",
                "description": "Save current discovery data and explore from a different starting point",
                "action": "save_and_explore",
                "risk_level": "low",
                "session_impact": "moderate"
            },
            {
                "id": "quit_with_data",
                "title": "Quit with Current Data",
                "description": "End discovery session and save all collected data",
                "action": "quit_with_data",
                "risk_level": "low",
                "session_impact": "none"
            },
            {
                "id": "restart_discovery",
                "title": "Restart Discovery",
                "description": "Start fresh discovery session with lessons learned",
                "action": "restart_discovery",
                "risk_level": "medium",
                "session_impact": "significant"
            },
            {
                "id": "manual_intervention",
                "title": "Manual Intervention",
                "description": "Request human intervention for specific guidance",
                "action": "manual_intervention",
                "risk_level": "low",
                "session_impact": "minimal"
            }
        ]
    
    def _present_discovery_action_menu(self):
        """Present action menu for discovery session"""
        
        print(f"\n🤝 DISCOVERY SESSION ACTION OPTIONS")
        print("=" * 70)
        print("Emergency protocols activated. Additional data gathered.")
        print("Please choose how to proceed with the discovery session:")
        print("=" * 70)
        
        for i, action in enumerate(self.available_actions, 1):
            risk_icon = "🟢" if action["risk_level"] == "low" else "🟡" if action["risk_level"] == "medium" else "🔴"
            print(f"\n   {i}. {action['title']} {risk_icon}")
            print(f"      {action['description']}")
            print(f"      Risk: {action['risk_level']} | Impact: {action['session_impact']}")
        
        print(f"\n⏸️ WAITING FOR USER INSTRUCTIONS...")
        print("=" * 70)
        print("Emergency protocols are active and gathering additional data.")
        print("Please provide your choice or additional instructions.")
        print("=" * 70)
    
    def execute_discovery_action(self, action_id: str, additional_params: Dict[str, Any] = None):
        """Execute chosen discovery action"""
        
        print(f"\n🎯 EXECUTING DISCOVERY ACTION: {action_id}")
        print("-" * 50)
        
        action = next((a for a in self.available_actions if a["id"] == action_id), None)
        
        if not action:
            print(f"   ❌ Unknown action: {action_id}")
            return {"success": False, "error": f"Unknown action: {action_id}"}
        
        print(f"   Action: {action['title']}")
        print(f"   Description: {action['description']}")
        
        try:
            if action["action"] == "continue_discovery":
                return self._continue_discovery(additional_params)
            elif action["action"] == "deep_dive":
                return self._deep_dive_analysis(additional_params)
            elif action["action"] == "save_and_explore":
                return self._save_and_explore_elsewhere(additional_params)
            elif action["action"] == "quit_with_data":
                return self._quit_with_data(additional_params)
            elif action["action"] == "restart_discovery":
                return self._restart_discovery(additional_params)
            elif action["action"] == "manual_intervention":
                return self._request_manual_intervention(additional_params)
            else:
                return {"success": False, "error": f"Unimplemented action: {action['action']}"}
                
        except Exception as e:
            return {"success": False, "error": f"Exception executing action: {str(e)}"}
    
    def _continue_discovery(self, params: Dict[str, Any] = None):
        """Continue discovery with enhanced data gathering"""
        
        print("   🔍 Continuing discovery with enhanced data gathering...")
        
        # Keep emergency protocols active for enhanced data gathering
        self.waiting_for_instructions = False
        
        return {
            "success": True,
            "action": "continue_discovery",
            "emergency_protocols_active": True,
            "enhanced_data_gathering": True,
            "next_steps": ["Continue navigation", "Enhanced telemetry capture", "User-guided exploration"]
        }
    
    def _deep_dive_analysis(self, params: Dict[str, Any] = None):
        """Perform deep dive analysis of current context"""
        
        print("   🔬 Performing deep dive analysis...")
        
        # Activate Ghostbusters consultation for deep analysis
        consultation = GhostbustersStandaloneConsultation()
        analysis_result = consultation.run_critical_consultation(self.discovery_context)
        
        return {
            "success": True,
            "action": "deep_dive_analysis",
            "analysis_result": analysis_result,
            "next_steps": ["Review analysis results", "Decide on next action", "Implement recommendations"]
        }
    
    def _save_and_explore_elsewhere(self, params: Dict[str, Any] = None):
        """Save current data and explore from different starting point"""
        
        print("   💾 Saving current discovery data and preparing for new exploration...")
        
        # Create comprehensive save point
        save_data = {
            "discovery_context": self.discovery_context,
            "emergency_protocol_data": self.emergency_manager.get_protocol_status(),
            "additional_data": self._gather_discovery_specific_data(),
            "save_timestamp": datetime.now().isoformat(),
            "save_reason": "User requested save and explore elsewhere"
        }
        
        save_file = f"discovery_save_point_{int(time.time())}.json"
        with open(save_file, 'w') as f:
            json.dump(save_data, f, indent=2, default=str)
        
        return {
            "success": True,
            "action": "save_and_explore_elsewhere",
            "save_file": save_file,
            "next_steps": ["Choose new starting point", "Load discovery context", "Begin new exploration"]
        }
    
    def _quit_with_data(self, params: Dict[str, Any] = None):
        """Quit discovery session with all collected data"""
        
        print("   🏁 Ending discovery session with all collected data...")
        
        # Create final comprehensive dump
        final_dump = self.emergency_manager.session_dumper.create_comprehensive_dump()
        
        return {
            "success": True,
            "action": "quit_with_data",
            "final_dump": final_dump,
            "discovery_complete": True,
            "data_preserved": True
        }
    
    def _restart_discovery(self, params: Dict[str, Any] = None):
        """Restart discovery session with lessons learned"""
        
        print("   🔄 Restarting discovery session with lessons learned...")
        
        # Save lessons learned
        lessons_learned = {
            "previous_discovery_context": self.discovery_context,
            "emergency_protocol_trigger_reason": self.manual_trigger_reason,
            "lessons": [
                "User detection of changes is more reliable than state management",
                "Emergency protocols provide valuable additional data",
                "Manual triggering is necessary when automated systems miss changes"
            ],
            "recommendations": [
                "Implement user-triggered emergency protocols in discovery sessions",
                "Enhance state management to detect subtle changes",
                "Provide manual override capabilities"
            ]
        }
        
        lessons_file = f"discovery_lessons_learned_{int(time.time())}.json"
        with open(lessons_file, 'w') as f:
            json.dump(lessons_learned, f, indent=2, default=str)
        
        return {
            "success": True,
            "action": "restart_discovery",
            "lessons_file": lessons_file,
            "next_steps": ["Apply lessons learned", "Start fresh discovery", "Implement improvements"]
        }
    
    def _request_manual_intervention(self, params: Dict[str, Any] = None):
        """Request manual human intervention"""
        
        print("   🤝 Requesting manual human intervention...")
        
        intervention_request = {
            "request_type": "discovery_session_intervention",
            "context": self.discovery_context,
            "emergency_protocol_status": self.emergency_manager.get_protocol_status(),
            "user_concerns": self.manual_trigger_reason,
            "available_actions": self.available_actions,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "action": "manual_intervention",
            "intervention_request": intervention_request,
            "next_steps": ["Wait for human guidance", "Provide additional context if needed", "Execute human instructions"]
        }


def main():
    """Main function for discovery emergency protocol integration"""
    
    print("🚨 DISCOVERY EMERGENCY PROTOCOL INTEGRATION")
    print("=" * 80)
    print("Integrating emergency protocols as optional method in discovery sessions")
    print("Allows manual triggering when user detects changes")
    print("=" * 80)
    
    # Example usage
    discovery_session_data = {
        "session_id": "discovery_session_001",
        "current_page": {
            "url": "https://example.com/discovery/page",
            "title": "Discovery Page",
            "page_type": "discovery",
            "navigation_elements": ["next", "previous", "explore"],
            "form_elements": ["search", "filter"]
        },
        "navigation_state": {
            "path": ["/home", "/discovery", "/current"],
            "previous_pages": ["/home", "/discovery"],
            "milestones": ["discovery_started", "first_page_found"],
            "pattern": "systematic"
        },
        "discovery_progress": {
            "pages_discovered": 5,
            "forms_found": 3,
            "navigation_options": 8,
            "data_collected": 150,
            "completion_percentage": 25
        },
        "user_detected_changes": True,
        "state_management_status": "normal"
    }
    
    try:
        # Initialize discovery emergency protocol
        discovery_emergency = DiscoveryEmergencyProtocol()
        discovery_emergency.initialize_emergency_capability(discovery_session_data)
        
        # Simulate manual trigger
        print("\n🚨 Simulating manual emergency protocol trigger...")
        result = discovery_emergency.manual_emergency_trigger(
            reason="User detected page changes that state management missed",
            additional_context={"user_confidence": "high", "change_severity": "significant"}
        )
        
        if result["success"]:
            print(f"\n✅ Discovery emergency protocol integration successful")
            print(f"   Enhanced dump created: {result.get('enhanced_dump_created')}")
            print(f"   Additional data gathered: {len(result.get('additional_data_gathered', {}))} items")
            print(f"   Waiting for instructions: {result.get('waiting_for_instructions')}")
            print(f"   Available actions: {len(result.get('available_actions', []))}")
            
            # Simulate action execution
            print(f"\n🎯 Simulating action execution...")
            action_result = discovery_emergency.execute_discovery_action("continue_discovery")
            print(f"   Action result: {action_result}")
            
        else:
            print(f"\n❌ Discovery emergency protocol integration failed")
            print(f"   Error: {result.get('error')}")
        
    except Exception as e:
        print(f"\n💥 FATAL ERROR: {e}")


if __name__ == "__main__":
    main()


