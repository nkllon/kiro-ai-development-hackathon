#!/usr/bin/env python3
"""
Prompt Mode Node
================

Implements "Prompt Mode" - conversational decision-making where the system
discusses the situation with the user before deciding whether to call Ghostbusters.

This is the intermediate confidence level where the system is uncertain but
not completely lost. It's like a military briefing where you discuss the
situation before making a decision.
"""

import time
import random
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_core.messages import AIMessage, HumanMessage
from langgraph_devpost_state import DevPostState, add_error, update_performance_metrics


class PromptModeManager:
    """Manages Prompt Mode conversations and decision-making"""
    
    def __init__(self):
        self.conversation_history = []
        self.decision_points = []
        self.ghostbusters_consultations = []
    
    def start_prompt_conversation(self, state: DevPostState) -> str:
        """Start a Prompt Mode conversation about the current situation"""
        
        confidence = state.get("session_recovery", {}).get("confidence", 0.0)
        similarity_type = state.get("session_recovery", {}).get("similarity_type", "unknown")
        current_page_data = state.get("session_save_data", {}).get("current_page_data", {})
        
        # Military-derived exclamations for moderate uncertainty
        prompt_mode_exclamations = [
            "This is it! The moment we should have trained for!",
            "Situation report: We're in uncharted territory, but I've got a plan!",
            "Stand by for briefing: Current situation requires tactical discussion!",
            "All units, this is what we trained for - time to execute the plan!",
            "Situation unclear, but we're not out of options yet!",
            "This is exactly the scenario we prepared for - let's discuss our approach!",
            "Mission briefing: We're in a complex situation that requires careful analysis!",
            "Stand down from autonomous mode - time for strategic consultation!",
            "This is our moment to shine - let's figure this out together!",
            "Situation requires human-AI collaboration - time to strategize!"
        ]
        
        exclamation = random.choice(prompt_mode_exclamations)
        
        conversation_start = f"🎖️ PROMPT MODE ACTIVATED 🎖️\n\n"
        conversation_start += f"{exclamation}\n\n"
        
        conversation_start += "📊 SITUATION BRIEFING:\n"
        conversation_start += f"   • Confidence Level: {confidence:.2f} (moderate uncertainty)\n"
        conversation_start += f"   • Similarity Type: {similarity_type}\n"
        conversation_start += f"   • Current URL: {current_page_data.get('url', 'Unknown')}\n"
        conversation_start += f"   • Page Title: {current_page_data.get('title', 'Unknown')}\n\n"
        
        conversation_start += "🤔 TACTICAL DISCUSSION POINTS:\n"
        conversation_start += "   1. What type of page are we dealing with?\n"
        conversation_start += "   2. What navigation strategies should we consider?\n"
        conversation_start += "   3. Are there any specific elements we should focus on?\n"
        conversation_start += "   4. Should we proceed cautiously or call in Ghostbusters?\n\n"
        
        conversation_start += "💭 CONVERSATION OPTIONS:\n"
        conversation_start += "   • Discuss the situation (tell me what you think)\n"
        conversation_start += "   • Call Ghostbusters for consultation (let them investigate)\n"
        conversation_start += "   • Proceed with caution (try autonomous navigation)\n"
        conversation_start += "   • Reset and start fresh (go back to known state)\n\n"
        
        conversation_start += "What's your assessment of the situation?"
        
        # Store conversation start
        self.conversation_history.append({
            "timestamp": time.time(),
            "type": "system_briefing",
            "content": conversation_start,
            "confidence": confidence,
            "similarity_type": similarity_type
        })
        
        return conversation_start
    
    def handle_user_response(self, user_input: str, state: DevPostState) -> Dict[str, Any]:
        """Handle user response in Prompt Mode"""
        
        user_input_lower = user_input.lower()
        
        # Store user input
        self.conversation_history.append({
            "timestamp": time.time(),
            "type": "user_response",
            "content": user_input,
            "length": len(user_input)
        })
        
        # Analyze user intent
        if any(phrase in user_input_lower for phrase in ["call ghostbusters", "ghostbusters", "consult", "investigate"]):
            return self._handle_ghostbusters_request(state)
        elif any(phrase in user_input_lower for phrase in ["proceed", "continue", "try", "go ahead"]):
            return self._handle_proceed_request(state)
        elif any(phrase in user_input_lower for phrase in ["reset", "start fresh", "restart", "begin again"]):
            return self._handle_reset_request(state)
        elif any(phrase in user_input_lower for phrase in ["discuss", "talk", "think", "consider"]):
            return self._handle_discussion_request(user_input, state)
        else:
            return self._handle_general_response(user_input, state)
    
    def _handle_ghostbusters_request(self, state: DevPostState) -> Dict[str, Any]:
        """Handle request to call Ghostbusters"""
        
        response = "🚨 CALLING GHOSTBUSTERS FOR CONSULTATION 🚨\n\n"
        response += "Excellent decision! Ghostbusters will investigate the situation\n"
        response += "and return with their findings. They'll run autonomous analysis\n"
        response += "and come back with recommendations.\n\n"
        response += "⏳ Ghostbusters consultation in progress...\n"
        response += "📡 They'll return shortly with their assessment.\n\n"
        response += "This is exactly the kind of situation they're trained for!"
        
        # Store decision point
        self.decision_points.append({
            "timestamp": time.time(),
            "decision": "call_ghostbusters",
            "reasoning": "User requested Ghostbusters consultation",
            "confidence": state.get("session_recovery", {}).get("confidence", 0.0)
        })
        
        return {
            "action": "call_ghostbusters",
            "message": response,
            "next_mode": "ghostbusters_consultation"
        }
    
    def _handle_proceed_request(self, state: DevPostState) -> Dict[str, Any]:
        """Handle request to proceed with caution"""
        
        response = "⚠️ PROCEEDING WITH CAUTION ⚠️\n\n"
        response += "Roger that! We'll proceed with cautious autonomous navigation.\n"
        response += "I'll use the most conservative approach available and\n"
        response += "report back on any issues.\n\n"
        response += "🛡️ Cautious mode activated\n"
        response += "📊 Enhanced monitoring enabled\n"
        response += "🔄 Fallback strategies ready\n\n"
        response += "Moving out!"
        
        # Store decision point
        self.decision_points.append({
            "timestamp": time.time(),
            "decision": "proceed_cautiously",
            "reasoning": "User approved cautious autonomous navigation",
            "confidence": state.get("session_recovery", {}).get("confidence", 0.0)
        })
        
        return {
            "action": "proceed_cautiously",
            "message": response,
            "next_mode": "cautious_navigation"
        }
    
    def _handle_reset_request(self, state: DevPostState) -> Dict[str, Any]:
        """Handle request to reset and start fresh"""
        
        response = "🔄 RESET AND START FRESH 🔄\n\n"
        response += "Copy that! We're resetting to a known state.\n"
        response += "This will clear our current session and start\n"
        response += "from a clean slate.\n\n"
        response += "🧹 Clearing session state\n"
        response += "🆕 Initializing fresh navigation model\n"
        response += "📍 Returning to last known good state\n\n"
        response += "Mission reset complete!"
        
        # Store decision point
        self.decision_points.append({
            "timestamp": time.time(),
            "decision": "reset_fresh",
            "reasoning": "User requested fresh start",
            "confidence": state.get("session_recovery", {}).get("confidence", 0.0)
        })
        
        return {
            "action": "reset_fresh",
            "message": response,
            "next_mode": "fresh_start"
        }
    
    def _handle_discussion_request(self, user_input: str, state: DevPostState) -> Dict[str, Any]:
        """Handle discussion/analysis request"""
        
        response = "💭 TACTICAL DISCUSSION CONTINUES 💭\n\n"
        response += f"Your input: {user_input}\n\n"
        
        # Analyze the discussion content
        if "form" in user_input.lower():
            response += "🎯 FORM DETECTED: This looks like a form page.\n"
            response += "   Strategy: Focus on form field analysis and completion.\n"
        elif "navigation" in user_input.lower():
            response += "🧭 NAVIGATION DETECTED: This appears to be a navigation page.\n"
            response += "   Strategy: Analyze navigation elements and flow.\n"
        elif "error" in user_input.lower():
            response += "⚠️ ERROR DETECTED: There may be an error condition.\n"
            response += "   Strategy: Investigate error state and recovery options.\n"
        else:
            response += "🤔 GENERAL ANALYSIS: Let's break this down further.\n"
            response += "   Strategy: Continue analysis and gather more information.\n"
        
        response += "\nWhat's your next thought on this situation?"
        
        # Store discussion point
        self.conversation_history.append({
            "timestamp": time.time(),
            "type": "tactical_discussion",
            "content": user_input,
            "analysis": "discussion_continued"
        })
        
        return {
            "action": "continue_discussion",
            "message": response,
            "next_mode": "prompt_mode"
        }
    
    def _handle_general_response(self, user_input: str, state: DevPostState) -> Dict[str, Any]:
        """Handle general user response"""
        
        response = "📝 RESPONSE RECEIVED 📝\n\n"
        response += f"Thank you for your input: {user_input}\n\n"
        response += "Based on your response, I need to clarify our next steps:\n\n"
        response += "🤔 What would you like to do?\n"
        response += "   1. Continue discussing the situation\n"
        response += "   2. Call Ghostbusters for consultation\n"
        response += "   3. Proceed with cautious navigation\n"
        response += "   4. Reset and start fresh\n\n"
        response += "Please let me know your preference."
        
        return {
            "action": "clarify_intent",
            "message": response,
            "next_mode": "prompt_mode"
        }
    
    def receive_ghostbusters_report(self, ghostbusters_findings: Dict[str, Any]) -> str:
        """Receive and process Ghostbusters consultation report"""
        
        report = "📡 GHOSTBUSTERS CONSULTATION COMPLETE 📡\n\n"
        report += "Ghostbusters have completed their investigation and\n"
        report += "returned with their findings:\n\n"
        
        report += "🔍 THEIR ASSESSMENT:\n"
        report += f"   • Confidence Level: {ghostbusters_findings.get('confidence', 'Unknown')}\n"
        report += f"   • Primary Strategy: {ghostbusters_findings.get('primary_strategy', 'Unknown')}\n"
        report += f"   • Similarity Type: {ghostbusters_findings.get('similarity_type', 'Unknown')}\n"
        report += f"   • Recommendation: {ghostbusters_findings.get('recommendation', 'Unknown')}\n\n"
        
        if ghostbusters_findings.get('test_results'):
            report += "🧪 TEST RESULTS:\n"
            for test, result in ghostbusters_findings['test_results'].items():
                report += f"   • {test}: {result}\n"
            report += "\n"
        
        report += "💭 GHOSTBUSTERS RECOMMENDATION:\n"
        report += f"{ghostbusters_findings.get('detailed_recommendation', 'No detailed recommendation provided')}\n\n"
        
        report += "🤔 NOW WE NEED YOUR INPUT:\n"
        report += "Based on Ghostbusters' findings, what do you think?\n"
        report += "Should we follow their recommendation or do you have\n"
        report += "a different approach in mind?\n\n"
        report += "This is our moment to make the final call!"
        
        # Store Ghostbusters consultation
        self.ghostbusters_consultations.append({
            "timestamp": time.time(),
            "findings": ghostbusters_findings,
            "status": "completed"
        })
        
        return report


def prompt_mode_node(state: DevPostState) -> DevPostState:
    """
    Node: Prompt Mode
    
    Handles conversational decision-making when confidence is moderate.
    This is the intermediate state where the system discusses the situation
    with the user before deciding on next steps.
    """
    
    print("🎖️ Prompt Mode Node")
    start_time = time.time()
    
    try:
        # Initialize prompt mode manager if not exists
        if "prompt_mode_manager" not in state:
            state["prompt_mode_manager"] = PromptModeManager()
        
        prompt_manager = state["prompt_mode_manager"]
        
        # Check if this is the start of prompt mode or continuation
        if not state.get("prompt_mode_active", False):
            # Starting prompt mode
            state["prompt_mode_active"] = True
            state["user_input_required"] = True
            state["awaiting_prompt_response"] = True
            
            # Start the conversation
            conversation_start = prompt_manager.start_prompt_conversation(state)
            state["messages"].append(AIMessage(content=conversation_start))
            
            print("   Starting Prompt Mode conversation")
            
        else:
            # Continuation of prompt mode - handle user response
            user_input = state.get("last_user_input", "")
            if user_input:
                response = prompt_manager.handle_user_response(user_input, state)
                
                state["messages"].append(AIMessage(content=response["message"]))
                
                # Determine next action based on response
                if response["action"] == "call_ghostbusters":
                    state["next_mode"] = "ghostbusters_consultation"
                    state["awaiting_prompt_response"] = False
                    state["user_input_required"] = False
                    
                elif response["action"] == "proceed_cautiously":
                    state["next_mode"] = "cautious_navigation"
                    state["awaiting_prompt_response"] = False
                    state["user_input_required"] = False
                    
                elif response["action"] == "reset_fresh":
                    state["next_mode"] = "fresh_start"
                    state["awaiting_prompt_response"] = False
                    state["user_input_required"] = False
                    
                else:
                    # Continue in prompt mode
                    state["awaiting_prompt_response"] = True
                    state["user_input_required"] = True
        
        # Update performance metrics
        prompt_time = time.time() - start_time
        update_performance_metrics(state, {
            "prompt_mode_time": prompt_time,
            "conversation_turns": len(prompt_manager.conversation_history),
            "decision_points": len(prompt_manager.decision_points)
        })
        
        print(f"   Prompt Mode: {len(prompt_manager.conversation_history)} conversation turns")
        
    except Exception as e:
        add_error(state, f"Prompt mode failed: {str(e)}")
    
    return state


def handle_prompt_mode_input(state: DevPostState, user_input: str) -> DevPostState:
    """Handle user input in Prompt Mode"""
    
    # Store the user input
    state["last_user_input"] = user_input
    
    # Process the input through prompt mode
    return prompt_mode_node(state)
