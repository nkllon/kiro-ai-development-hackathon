#!/usr/bin/env python3
"""
Interactive Recovery Node
========================

Handles interactive recovery when the system is in "Ghostbusters mode" - 
completely confused and needs human intervention.

This implements the interactive recovery options:
1. Tell me where we are (user provides context)
2. Guide me step by step (user provides direction)
3. Start fresh from a known page (reset session)
4. Analyze this page together (collaborative exploration)
5. Save session and quit (preserve current state)

Also manages tiered memory:
- Short-term memory (session-specific)
- Long-term memory (persistent across sessions)
- Memory qualification and persistence decisions
"""

import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

from langchain_core.messages import AIMessage, HumanMessage
from langgraph_devpost_state import DevPostState, add_error, update_performance_metrics


class TieredMemoryManager:
    """Manages tiered memory system for session data"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.short_term_memory = {}  # Session-specific data
        self.long_term_memory = {}   # Persistent data
        self.memory_qualification_queue = []  # Data pending qualification
        
    def add_short_term_memory(self, key: str, data: Any, importance: str = "normal"):
        """Add data to short-term memory (session-specific)"""
        self.short_term_memory[key] = {
            "data": data,
            "timestamp": time.time(),
            "importance": importance,
            "access_count": 0
        }
    
    def get_short_term_memory(self, key: str) -> Optional[Any]:
        """Retrieve data from short-term memory"""
        if key in self.short_term_memory:
            self.short_term_memory[key]["access_count"] += 1
            return self.short_term_memory[key]["data"]
        return None
    
    def queue_for_qualification(self, key: str, data: Any, reason: str):
        """Queue data for qualification (decide if it should be persisted)"""
        self.memory_qualification_queue.append({
            "key": key,
            "data": data,
            "reason": reason,
            "timestamp": time.time(),
            "session_id": self.session_id
        })
    
    def qualify_memory(self, key: str, decision: str, user_feedback: str = ""):
        """Qualify memory data for persistence"""
        for item in self.memory_qualification_queue:
            if item["key"] == key:
                item["qualification_decision"] = decision
                item["user_feedback"] = user_feedback
                item["qualified_at"] = time.time()
                
                if decision == "persist":
                    self.long_term_memory[key] = item["data"]
                elif decision == "discard":
                    pass  # Just remove from queue
                elif decision == "transform":
                    # User wants to modify the data before persisting
                    item["needs_transformation"] = True
                
                break
    
    def save_session_memory(self, filepath: str):
        """Save session memory to disk"""
        session_data = {
            "session_id": self.session_id,
            "timestamp": time.time(),
            "short_term_memory": self.short_term_memory,
            "long_term_memory": self.long_term_memory,
            "qualification_queue": self.memory_qualification_queue
        }
        
        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)
    
    def load_session_memory(self, filepath: str):
        """Load session memory from disk"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                session_data = json.load(f)
                self.short_term_memory = session_data.get("short_term_memory", {})
                self.long_term_memory = session_data.get("long_term_memory", {})
                self.memory_qualification_queue = session_data.get("qualification_queue", [])


def interactive_recovery_node(state: DevPostState) -> DevPostState:
    """
    Node: Interactive Recovery
    
    Handles the "Ghostbusters moment" when the system is completely confused
    and needs human intervention to continue.
    """
    
    print("🚨 Interactive Recovery Node")
    start_time = time.time()
    
    try:
        # Check if we're in Ghostbusters mode
        if not state.get("ghostbusters_mode", False):
            print("   Not in Ghostbusters mode - skipping interactive recovery")
            return state
        
        # Initialize tiered memory manager if not exists
        if "memory_manager" not in state:
            session_id = state.get("session_id", f"session_{int(time.time())}")
            state["memory_manager"] = TieredMemoryManager(session_id)
        
        memory_manager = state["memory_manager"]
        
        # Store current confused state in short-term memory
        memory_manager.add_short_term_memory(
            "ghostbusters_state",
            {
                "confidence": state.get("session_recovery", {}).get("confidence", 0.0),
                "similarity_type": state.get("session_recovery", {}).get("similarity_type", "unknown"),
                "page_data": state.get("session_save_data", {}),
                "stop_reason": state.get("stop_reason", "unknown"),
                "recovery_options": state.get("recovery_options", [])
            },
            importance="critical"
        )
        
        # Queue session data for qualification
        memory_manager.queue_for_qualification(
            "session_telemetry",
            state.get("session_save_data", {}),
            "User needs to decide if this confused state data is worth persisting"
        )
        
        # Present interactive recovery options
        recovery_options = state.get("recovery_options", [])
        current_page_data = state.get("session_save_data", {}).get("current_page_data", {})
        
        recovery_message = "🚨 INTERACTIVE RECOVERY MODE ACTIVATED 🚨\n\n"
        recovery_message += "I'm completely confused and need your help to continue.\n\n"
        recovery_message += "📊 Current Situation:\n"
        recovery_message += f"   • URL: {current_page_data.get('url', 'Unknown')}\n"
        recovery_message += f"   • Page Title: {current_page_data.get('title', 'Unknown')}\n"
        recovery_message += f"   • Confidence: {state.get('session_recovery', {}).get('confidence', 0.0):.2f}\n"
        recovery_message += f"   • Similarity Type: {state.get('session_recovery', {}).get('similarity_type', 'unknown')}\n\n"
        
        recovery_message += "🤔 RECOVERY OPTIONS:\n"
        recovery_message += "   1. 📍 Tell me where we are (provide context about current page)\n"
        recovery_message += "   2. 🧭 Guide me step by step (provide specific navigation directions)\n"
        recovery_message += "   3. 🔄 Start fresh from a known page (reset session to known state)\n"
        recovery_message += "   4. 🔍 Analyze this page together (collaborative exploration)\n"
        recovery_message += "   5. 💾 Save session and quit (preserve current state for later)\n\n"
        
        recovery_message += "💭 MEMORY MANAGEMENT:\n"
        recovery_message += "   • Current session data is stored in short-term memory\n"
        recovery_message += "   • You can decide what data to persist for future sessions\n"
        recovery_message += "   • Session can be saved and resumed later\n\n"
        
        recovery_message += "Please choose an option (1-5) or provide specific guidance:"
        
        state["messages"].append(AIMessage(content=recovery_message))
        
        # Set flags for interactive mode
        state["user_input_required"] = True
        state["interactive_recovery_active"] = True
        state["awaiting_recovery_choice"] = True
        
        # Update performance metrics
        recovery_time = time.time() - start_time
        update_performance_metrics(state, {
            "interactive_recovery_time": recovery_time,
            "recovery_options_count": len(recovery_options),
            "memory_manager_initialized": True
        })
        
        print(f"🚨 Interactive Recovery Mode:")
        print(f"   Recovery options: {len(recovery_options)}")
        print(f"   Memory manager initialized")
        print(f"   Awaiting user input for recovery choice")
        
    except Exception as e:
        add_error(state, f"Interactive recovery failed: {str(e)}")
    
    return state


def handle_recovery_choice(state: DevPostState, user_choice: str, user_input: str = "") -> DevPostState:
    """
    Handle user's recovery choice and implement the selected recovery strategy
    
    Args:
        state: Current DevPost state
        user_choice: User's choice (1-5 or specific command)
        user_input: Additional user input/context
    """
    
    print(f"🔄 Handling recovery choice: {user_choice}")
    
    try:
        memory_manager = state.get("memory_manager")
        if not memory_manager:
            add_error(state, "Memory manager not available for recovery")
            return state
        
        # Store user's recovery choice in memory
        memory_manager.add_short_term_memory(
            "recovery_choice",
            {
                "choice": user_choice,
                "user_input": user_input,
                "timestamp": time.time()
            },
            importance="high"
        )
        
        if user_choice in ["1", "tell me where we are", "context"]:
            # Option 1: User provides context about current location
            handle_context_guidance(state, user_input, memory_manager)
            
        elif user_choice in ["2", "guide me", "step by step"]:
            # Option 2: User provides step-by-step guidance
            handle_step_by_step_guidance(state, user_input, memory_manager)
            
        elif user_choice in ["3", "start fresh", "reset"]:
            # Option 3: Reset session to known state
            handle_fresh_start(state, user_input, memory_manager)
            
        elif user_choice in ["4", "analyze together", "collaborative"]:
            # Option 4: Collaborative analysis
            handle_collaborative_analysis(state, user_input, memory_manager)
            
        elif user_choice in ["5", "save and quit", "quit"]:
            # Option 5: Save session and quit
            handle_save_and_quit(state, user_input, memory_manager)
            
        else:
            # Unknown choice - ask for clarification
            clarification_message = f"🤔 I didn't understand your choice: '{user_choice}'\n\n"
            clarification_message += "Please choose one of these options:\n"
            clarification_message += "   1. Tell me where we are\n"
            clarification_message += "   2. Guide me step by step\n"
            clarification_message += "   3. Start fresh from a known page\n"
            clarification_message += "   4. Analyze this page together\n"
            clarification_message += "   5. Save session and quit\n\n"
            clarification_message += "Or provide specific guidance in your message."
            
            state["messages"].append(AIMessage(content=clarification_message))
            state["awaiting_recovery_choice"] = True
        
    except Exception as e:
        add_error(state, f"Failed to handle recovery choice: {str(e)}")
    
    return state


def handle_context_guidance(state: DevPostState, user_input: str, memory_manager: TieredMemoryManager):
    """Handle user providing context about current location"""
    
    context_message = "📍 CONTEXT GUIDANCE RECEIVED\n\n"
    context_message += f"User provided context: {user_input}\n\n"
    
    # Store user context in memory
    memory_manager.add_short_term_memory(
        "user_context",
        {
            "context": user_input,
            "timestamp": time.time(),
            "source": "user_guidance"
        },
        importance="critical"
    )
    
    # Queue for qualification - is this context worth persisting?
    memory_manager.queue_for_qualification(
        "user_context_guidance",
        user_input,
        "User provided context about page location - decide if this should be persisted for future sessions"
    )
    
    context_message += "✅ Context stored in memory\n"
    context_message += "🔄 Attempting to adapt navigation model based on your context...\n\n"
    
    # Try to adapt navigation based on user context
    current_page_data = state.get("session_save_data", {}).get("current_page_data", {})
    
    if "devpost" in user_input.lower():
        context_message += "🎯 Detected DevPost context - adapting for DevPost navigation\n"
        state["navigation_model"] = "devpost_context_adapted"
        
    elif "form" in user_input.lower() or "submit" in user_input.lower():
        context_message += "📝 Detected form context - adapting for form navigation\n"
        state["navigation_model"] = "form_context_adapted"
        
    elif "team" in user_input.lower():
        context_message += "👥 Detected team management context - adapting for team page navigation\n"
        state["navigation_model"] = "team_context_adapted"
        
    else:
        context_message += "🤔 Generic context detected - using adaptive navigation\n"
        state["navigation_model"] = "generic_context_adapted"
    
    # Exit Ghostbusters mode and resume navigation
    state["ghostbusters_mode"] = False
    state["user_input_required"] = False
    state["awaiting_recovery_choice"] = False
    state["interactive_recovery_active"] = False
    
    context_message += "\n✅ Exiting Ghostbusters mode - resuming autonomous navigation"
    
    state["messages"].append(AIMessage(content=context_message))


def handle_step_by_step_guidance(state: DevPostState, user_input: str, memory_manager: TieredMemoryManager):
    """Handle user providing step-by-step guidance"""
    
    guidance_message = "🧭 STEP-BY-STEP GUIDANCE RECEIVED\n\n"
    guidance_message += f"User provided guidance: {user_input}\n\n"
    
    # Store guidance in memory
    memory_manager.add_short_term_memory(
        "user_guidance",
        {
            "guidance": user_input,
            "timestamp": time.time(),
            "source": "step_by_step"
        },
        importance="critical"
    )
    
    guidance_message += "✅ Guidance stored in memory\n"
    guidance_message += "🔄 Following your step-by-step instructions...\n\n"
    
    # Parse guidance for specific actions
    guidance_lower = user_input.lower()
    
    if "click" in guidance_lower:
        guidance_message += "🖱️ Detected click instruction\n"
    elif "fill" in guidance_lower or "enter" in guidance_lower:
        guidance_message += "📝 Detected form filling instruction\n"
    elif "navigate" in guidance_lower or "go to" in guidance_lower:
        guidance_message += "🧭 Detected navigation instruction\n"
    elif "wait" in guidance_lower or "pause" in guidance_lower:
        guidance_message += "⏳ Detected wait instruction\n"
    else:
        guidance_message += "🤔 Generic guidance - will attempt to follow\n"
    
    # Set up for guided execution
    state["guided_mode"] = True
    state["user_guidance"] = user_input
    state["ghostbusters_mode"] = False
    state["user_input_required"] = False
    state["awaiting_recovery_choice"] = False
    state["interactive_recovery_active"] = False
    
    guidance_message += "\n✅ Entering guided mode - will follow your instructions"
    
    state["messages"].append(AIMessage(content=guidance_message))


def handle_fresh_start(state: DevPostState, user_input: str, memory_manager: TieredMemoryManager):
    """Handle resetting to a fresh start from a known page"""
    
    fresh_start_message = "🔄 FRESH START REQUESTED\n\n"
    
    # Store fresh start request in memory
    memory_manager.add_short_term_memory(
        "fresh_start_request",
        {
            "user_input": user_input,
            "timestamp": time.time(),
            "reason": "user_requested_fresh_start"
        },
        importance="high"
    )
    
    fresh_start_message += "✅ Fresh start request stored in memory\n"
    fresh_start_message += "🔄 Resetting session to known state...\n\n"
    
    # Reset session state
    state["ghostbusters_mode"] = False
    state["user_input_required"] = False
    state["awaiting_recovery_choice"] = False
    state["interactive_recovery_active"] = False
    state["session_stopped"] = False
    state["cautious_mode"] = False
    
    # Clear navigation model to force fresh detection
    state["navigation_model"] = None
    state["session_recovery"] = {}
    state["session_save_data"] = {}
    
    fresh_start_message += "🧹 Session state reset\n"
    fresh_start_message += "🆕 Will perform fresh page detection on next navigation\n"
    fresh_start_message += "✅ Ready to start fresh from current page"
    
    state["messages"].append(AIMessage(content=fresh_start_message))


def handle_collaborative_analysis(state: DevPostState, user_input: str, memory_manager: TieredMemoryManager):
    """Handle collaborative analysis of the current page"""
    
    analysis_message = "🔍 COLLABORATIVE ANALYSIS MODE\n\n"
    
    # Store collaborative analysis request
    memory_manager.add_short_term_memory(
        "collaborative_analysis",
        {
            "user_input": user_input,
            "timestamp": time.time(),
            "mode": "collaborative"
        },
        importance="high"
    )
    
    analysis_message += f"User input: {user_input}\n\n"
    
    # Perform detailed page analysis
    current_page_data = state.get("session_save_data", {}).get("current_page_data", {})
    
    analysis_message += "📊 DETAILED PAGE ANALYSIS:\n"
    analysis_message += f"   • URL: {current_page_data.get('url', 'Unknown')}\n"
    analysis_message += f"   • Title: {current_page_data.get('title', 'Unknown')}\n"
    
    # Analyze navigation elements
    navigation_elements = current_page_data.get("navigation", [])
    if navigation_elements:
        analysis_message += f"   • Navigation elements: {len(navigation_elements)}\n"
        analysis_message += "     Key elements:\n"
        for elem in navigation_elements[:5]:  # Show first 5
            text = elem.get("text", "").strip()
            if text:
                analysis_message += f"       - {text}\n"
    
    # Analyze buttons
    buttons = current_page_data.get("buttons", [])
    if buttons:
        analysis_message += f"   • Interactive buttons: {len(buttons)}\n"
        analysis_message += "     Button text:\n"
        for btn in buttons[:3]:  # Show first 3
            text = btn.get("text", "").strip()
            if text:
                analysis_message += f"       - {text}\n"
    
    analysis_message += "\n🤔 ANALYSIS QUESTIONS:\n"
    analysis_message += "   1. What type of page is this?\n"
    analysis_message += "   2. What should be the next action?\n"
    analysis_message += "   3. Are there any specific elements I should focus on?\n"
    analysis_message += "   4. Is this a form, navigation page, or content page?\n\n"
    
    analysis_message += "💭 Please provide your analysis and guidance:"
    
    # Stay in interactive mode for collaborative analysis
    state["collaborative_mode"] = True
    state["awaiting_collaborative_input"] = True
    
    state["messages"].append(AIMessage(content=analysis_message))


def handle_save_and_quit(state: DevPostState, user_input: str, memory_manager: TieredMemoryManager):
    """Handle saving session and quitting"""
    
    save_message = "💾 SAVE AND QUIT REQUESTED\n\n"
    
    # Create session save filename
    session_id = state.get("session_id", f"session_{int(time.time())}")
    save_filename = f"devpost_session_{session_id}_{int(time.time())}.json"
    
    try:
        # Save session memory
        memory_manager.save_session_memory(save_filename)
        
        save_message += f"✅ Session saved to: {save_filename}\n"
        save_message += "📊 Session data includes:\n"
        save_message += "   • Short-term memory (session-specific data)\n"
        save_message += "   • Long-term memory (persistent data)\n"
        save_message += "   • Memory qualification queue\n"
        save_message += "   • Recovery state and options\n\n"
        
        # Mark session as saved and ready to quit
        state["session_saved"] = True
        state["save_filename"] = save_filename
        state["ready_to_quit"] = True
        
        save_message += "🔄 Session can be resumed later by loading this file\n"
        save_message += "✅ Ready to quit - session preserved"
        
    except Exception as e:
        save_message += f"❌ Failed to save session: {str(e)}\n"
        save_message += "🔄 Session will be lost on quit"
        add_error(state, f"Failed to save session: {str(e)}")
    
    state["messages"].append(AIMessage(content=save_message))


def memory_qualification_node(state: DevPostState) -> DevPostState:
    """
    Node: Memory Qualification
    
    Handles the qualification of memory data - deciding what to persist
    and what to discard based on user feedback and system analysis.
    """
    
    print("🧠 Memory Qualification Node")
    
    try:
        memory_manager = state.get("memory_manager")
        if not memory_manager:
            print("   No memory manager - skipping qualification")
            return state
        
        qualification_queue = memory_manager.memory_qualification_queue
        
        if not qualification_queue:
            print("   No memory items pending qualification")
            return state
        
        # Check for items that need user qualification
        needs_user_input = []
        for item in qualification_queue:
            if "qualification_decision" not in item:
                needs_user_input.append(item)
        
        if needs_user_input:
            qualification_message = "🧠 MEMORY QUALIFICATION REQUIRED\n\n"
            qualification_message += f"Found {len(needs_user_input)} memory items that need qualification:\n\n"
            
            for i, item in enumerate(needs_user_input[:3], 1):  # Show first 3
                qualification_message += f"{i}. {item['key']}\n"
                qualification_message += f"   Reason: {item['reason']}\n"
                qualification_message += f"   Data preview: {str(item['data'])[:100]}...\n\n"
            
            qualification_message += "🤔 For each item, please decide:\n"
            qualification_message += "   • 'persist' - Keep this data for future sessions\n"
            qualification_message += "   • 'discard' - Remove this data\n"
            qualification_message += "   • 'transform' - Modify this data before persisting\n\n"
            qualification_message += "Example: '1: persist, 2: discard, 3: transform - make it shorter'"
            
            state["messages"].append(AIMessage(content=qualification_message))
            state["awaiting_memory_qualification"] = True
        
        else:
            print("   All memory items have been qualified")
            
    except Exception as e:
        add_error(state, f"Memory qualification failed: {str(e)}")
    
    return state
