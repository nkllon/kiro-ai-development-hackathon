#!/usr/bin/env python3
"""
Discovery Emergency Interface
============================

Simple interface for integrating emergency protocols into discovery sessions.
Provides easy-to-use methods for manual emergency protocol triggering.
"""

import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from discovery_emergency_protocol_integration import DiscoveryEmergencyProtocol


class DiscoveryEmergencyInterface:
    """Simple interface for discovery session emergency protocols"""
    
    def __init__(self):
        self.discovery_emergency = None
        self.is_initialized = False
    
    def initialize_for_discovery_session(self, session_data: Dict[str, Any]):
        """Initialize emergency protocols for a discovery session"""
        
        if self.is_initialized:
            print("⚠️ Discovery emergency protocols already initialized")
            return True
        
        try:
            self.discovery_emergency = DiscoveryEmergencyProtocol()
            self.discovery_emergency.initialize_emergency_capability(session_data)
            self.is_initialized = True
            
            print("✅ Discovery emergency protocols initialized")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize discovery emergency protocols: {e}")
            return False
    
    def trigger_emergency_protocols(self, reason: str = "User detected changes", additional_context: Dict[str, Any] = None):
        """Trigger emergency protocols during discovery session"""
        
        if not self.is_initialized:
            print("❌ Discovery emergency protocols not initialized. Call initialize_for_discovery_session() first.")
            return None
        
        print(f"\n🚨 MANUAL EMERGENCY PROTOCOL TRIGGER")
        print("=" * 50)
        print(f"Reason: {reason}")
        print("=" * 50)
        
        try:
            result = self.discovery_emergency.manual_emergency_trigger(reason, additional_context)
            
            if result["success"]:
                print("✅ Emergency protocols activated successfully")
                print("⏸️ Waiting for your instructions...")
                return result
            else:
                print(f"❌ Failed to activate emergency protocols: {result.get('error')}")
                return result
                
        except Exception as e:
            print(f"❌ Exception during emergency protocol activation: {e}")
            return {"success": False, "error": str(e)}
    
    def execute_action(self, action_id: str, additional_params: Dict[str, Any] = None):
        """Execute a discovery action after emergency protocols are activated"""
        
        if not self.is_initialized or not self.discovery_emergency.is_active:
            print("❌ Emergency protocols not active. Call trigger_emergency_protocols() first.")
            return None
        
        try:
            result = self.discovery_emergency.execute_discovery_action(action_id, additional_params)
            
            if result["success"]:
                print(f"✅ Action '{action_id}' executed successfully")
                return result
            else:
                print(f"❌ Failed to execute action '{action_id}': {result.get('error')}")
                return result
                
        except Exception as e:
            print(f"❌ Exception during action execution: {e}")
            return {"success": False, "error": str(e)}
    
    def get_available_actions(self):
        """Get list of available actions"""
        
        if not self.is_initialized or not self.discovery_emergency.is_active:
            return []
        
        return self.discovery_emergency.available_actions
    
    def is_waiting_for_instructions(self):
        """Check if system is waiting for user instructions"""
        
        if not self.is_initialized:
            return False
        
        return self.discovery_emergency.waiting_for_instructions
    
    def get_status(self):
        """Get current status of discovery emergency protocols"""
        
        if not self.is_initialized:
            return {"status": "not_initialized"}
        
        return {
            "status": "initialized",
            "is_active": self.discovery_emergency.is_active,
            "waiting_for_instructions": self.discovery_emergency.waiting_for_instructions,
            "manual_trigger_reason": self.discovery_emergency.manual_trigger_reason,
            "activation_timestamp": self.discovery_emergency.activation_timestamp,
            "available_actions_count": len(self.discovery_emergency.available_actions)
        }


# Convenience functions for easy integration
def create_discovery_emergency_interface():
    """Create a new discovery emergency interface instance"""
    return DiscoveryEmergencyInterface()


def quick_emergency_trigger(session_data: Dict[str, Any], reason: str = "User detected changes"):
    """Quick way to trigger emergency protocols for a discovery session"""
    
    interface = create_discovery_emergency_interface()
    
    # Initialize
    if not interface.initialize_for_discovery_session(session_data):
        return None
    
    # Trigger emergency protocols
    return interface.trigger_emergency_protocols(reason)


# Example integration for existing discovery sessions
def integrate_with_discovery_session(discovery_session):
    """Example of how to integrate with existing discovery session"""
    
    # Create emergency interface
    emergency_interface = create_discovery_emergency_interface()
    
    # Initialize with discovery session data
    session_data = {
        "session_id": getattr(discovery_session, 'session_id', 'unknown'),
        "current_page": getattr(discovery_session, 'current_page', {}),
        "navigation_state": getattr(discovery_session, 'navigation_state', {}),
        "discovery_progress": getattr(discovery_session, 'discovery_progress', {}),
        "user_detected_changes": True,
        "state_management_status": getattr(discovery_session, 'state_status', 'normal')
    }
    
    emergency_interface.initialize_for_discovery_session(session_data)
    
    # Add emergency trigger method to discovery session
    def emergency_trigger(reason="User detected changes"):
        return emergency_interface.trigger_emergency_protocols(reason)
    
    def execute_emergency_action(action_id, params=None):
        return emergency_interface.execute_action(action_id, params)
    
    def get_emergency_actions():
        return emergency_interface.get_available_actions()
    
    def emergency_status():
        return emergency_interface.get_status()
    
    # Attach methods to discovery session
    discovery_session.emergency_trigger = emergency_trigger
    discovery_session.execute_emergency_action = execute_emergency_action
    discovery_session.get_emergency_actions = get_emergency_actions
    discovery_session.emergency_status = emergency_status
    
    print("✅ Emergency protocols integrated with discovery session")
    print("   Available methods:")
    print("   - discovery_session.emergency_trigger(reason)")
    print("   - discovery_session.execute_emergency_action(action_id, params)")
    print("   - discovery_session.get_emergency_actions()")
    print("   - discovery_session.emergency_status()")
    
    return emergency_interface


def main():
    """Main function demonstrating the discovery emergency interface"""
    
    print("🚨 DISCOVERY EMERGENCY INTERFACE DEMONSTRATION")
    print("=" * 60)
    
    # Example discovery session data
    session_data = {
        "session_id": "demo_discovery_001",
        "current_page": {
            "url": "https://example.com/discovery/current",
            "title": "Current Discovery Page",
            "page_type": "discovery"
        },
        "navigation_state": {
            "path": ["/home", "/discovery", "/current"],
            "previous_pages": ["/home", "/discovery"]
        },
        "discovery_progress": {
            "pages_discovered": 3,
            "forms_found": 2,
            "completion_percentage": 15
        },
        "user_detected_changes": True,
        "state_management_status": "normal"
    }
    
    try:
        # Create and initialize interface
        emergency_interface = create_discovery_emergency_interface()
        
        print("\n1. Initializing emergency protocols...")
        if emergency_interface.initialize_for_discovery_session(session_data):
            print("   ✅ Initialized successfully")
        else:
            print("   ❌ Initialization failed")
            return
        
        # Check status
        print("\n2. Checking status...")
        status = emergency_interface.get_status()
        print(f"   Status: {status}")
        
        # Trigger emergency protocols
        print("\n3. Triggering emergency protocols...")
        result = emergency_interface.trigger_emergency_protocols(
            reason="User detected page changes that state management missed"
        )
        
        if result and result["success"]:
            print("   ✅ Emergency protocols activated")
            
            # Get available actions
            print("\n4. Getting available actions...")
            actions = emergency_interface.get_available_actions()
            print(f"   Available actions: {len(actions)}")
            
            for i, action in enumerate(actions, 1):
                print(f"   {i}. {action['title']}: {action['description']}")
            
            # Execute an action
            print("\n5. Executing action...")
            if actions:
                action_result = emergency_interface.execute_action(actions[0]["id"])
                print(f"   Action result: {action_result}")
        
        print("\n✅ Discovery emergency interface demonstration complete")
        
    except Exception as e:
        print(f"\n💥 ERROR: {e}")


if __name__ == "__main__":
    main()

