#!/usr/bin/env python3
"""
GCP State Manager - Centralized State Management for GCP Setup
Eliminates the state management nightmare with proper state tracking
"""

import os
import json
import time
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import threading
import queue

class SetupState(Enum):
    """Setup state enumeration"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

class SetupType(Enum):
    """Setup type enumeration"""
    PERSONAL = "personal"
    ENTERPRISE = "enterprise"
    AUTHORIZATION = "authorization"

@dataclass
class SetupStep:
    """Individual setup step"""
    step_id: str
    step_name: str
    state: SetupState
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    dependencies: List[str] = None

@dataclass
class SetupSession:
    """Complete setup session"""
    session_id: str
    setup_type: SetupType
    state: SetupState
    created_at: datetime
    updated_at: datetime
    steps: List[SetupStep]
    configuration: Dict[str, Any]
    results: Dict[str, Any]

class GCPStateManager:
    """Centralized state management for GCP setup"""
    
    def __init__(self, state_file: str = "gcp_setup_state.json"):
        self.state_file = state_file
        self.current_session: Optional[SetupSession] = None
        self.state_lock = threading.Lock()
        self.event_queue = queue.Queue()
        
        # Load existing state
        self.load_state()
    
    def load_state(self):
        """Load state from file"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.current_session = self._deserialize_session(data)
            except Exception as e:
                print(f"⚠️ Failed to load state: {e}")
                self.current_session = None
    
    def save_state(self):
        """Save state to file"""
        with self.state_lock:
            if self.current_session:
                try:
                    with open(self.state_file, 'w') as f:
                        json.dump(self._serialize_session(self.current_session), f, indent=2, default=str)
                except Exception as e:
                    print(f"❌ Failed to save state: {e}")
    
    def create_session(self, setup_type: SetupType, configuration: Dict[str, Any]) -> str:
        """Create new setup session"""
        session_id = str(uuid.uuid4())
        
        # Define steps based on setup type
        steps = self._get_steps_for_setup_type(setup_type)
        
        self.current_session = SetupSession(
            session_id=session_id,
            setup_type=setup_type,
            state=SetupState.NOT_STARTED,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            steps=steps,
            configuration=configuration,
            results={}
        )
        
        self.save_state()
        print(f"✅ Created setup session: {session_id}")
        return session_id
    
    def start_step(self, step_id: str) -> bool:
        """Start a setup step"""
        if not self.current_session:
            return False
        
        with self.state_lock:
            step = self._find_step(step_id)
            if not step:
                return False
            
            # Check dependencies
            if not self._check_dependencies(step):
                print(f"❌ Dependencies not met for step: {step_id}")
                return False
            
            step.state = SetupState.IN_PROGRESS
            step.start_time = datetime.now()
            self.current_session.updated_at = datetime.now()
            self.save_state()
            
            print(f"🚀 Started step: {step.step_name}")
            return True
    
    def complete_step(self, step_id: str, result_data: Dict[str, Any] = None) -> bool:
        """Complete a setup step"""
        if not self.current_session:
            return False
        
        with self.state_lock:
            step = self._find_step(step_id)
            if not step:
                return False
            
            step.state = SetupState.COMPLETED
            step.end_time = datetime.now()
            step.result_data = result_data
            self.current_session.updated_at = datetime.now()
            self.save_state()
            
            print(f"✅ Completed step: {step.step_name}")
            return True
    
    def fail_step(self, step_id: str, error_message: str) -> bool:
        """Fail a setup step"""
        if not self.current_session:
            return False
        
        with self.state_lock:
            step = self._find_step(step_id)
            if not step:
                return False
            
            step.state = SetupState.FAILED
            step.end_time = datetime.now()
            step.error_message = error_message
            self.current_session.state = SetupState.FAILED
            self.current_session.updated_at = datetime.now()
            self.save_state()
            
            print(f"❌ Failed step: {step.step_name} - {error_message}")
            return True
    
    def rollback_session(self) -> bool:
        """Rollback the entire session"""
        if not self.current_session:
            return False
        
        with self.state_lock:
            print("🔄 Rolling back setup session...")
            
            # Rollback completed steps in reverse order
            completed_steps = [s for s in self.current_session.steps if s.state == SetupState.COMPLETED]
            completed_steps.reverse()
            
            for step in completed_steps:
                print(f"🔄 Rolling back: {step.step_name}")
                # Here you would implement actual rollback logic
                step.state = SetupState.ROLLED_BACK
            
            self.current_session.state = SetupState.ROLLED_BACK
            self.current_session.updated_at = datetime.now()
            self.save_state()
            
            print("✅ Rollback completed")
            return True
    
    def get_session_status(self) -> Dict[str, Any]:
        """Get current session status"""
        if not self.current_session:
            return {"status": "no_session"}
        
        return {
            "session_id": self.current_session.session_id,
            "setup_type": self.current_session.setup_type.value,
            "state": self.current_session.state.value,
            "created_at": self.current_session.created_at.isoformat(),
            "updated_at": self.current_session.updated_at.isoformat(),
            "steps": [
                {
                    "step_id": step.step_id,
                    "step_name": step.step_name,
                    "state": step.state.value,
                    "start_time": step.start_time.isoformat() if step.start_time else None,
                    "end_time": step.end_time.isoformat() if step.end_time else None,
                    "error_message": step.error_message
                }
                for step in self.current_session.steps
            ]
        }
    
    def get_next_step(self) -> Optional[SetupStep]:
        """Get the next step to execute"""
        if not self.current_session:
            return None
        
        # Find the first step that's not started and has dependencies met
        for step in self.current_session.steps:
            if step.state == SetupState.NOT_STARTED and self._check_dependencies(step):
                return step
        
        return None
    
    def is_session_complete(self) -> bool:
        """Check if session is complete"""
        if not self.current_session:
            return False
        
        return all(step.state == SetupState.COMPLETED for step in self.current_session.steps)
    
    def _get_steps_for_setup_type(self, setup_type: SetupType) -> List[SetupStep]:
        """Get steps for specific setup type"""
        if setup_type == SetupType.PERSONAL:
            return [
                SetupStep("create_billing", "Create Billing Account", SetupState.NOT_STARTED),
                SetupStep("create_project", "Create Project", SetupState.NOT_STARTED, dependencies=["create_billing"]),
                SetupStep("link_billing", "Link Project to Billing", SetupState.NOT_STARTED, dependencies=["create_project"]),
                SetupStep("enable_apis", "Enable APIs", SetupState.NOT_STARTED, dependencies=["link_billing"]),
                SetupStep("create_gke", "Create GKE Cluster", SetupState.NOT_STARTED, dependencies=["enable_apis"]),
                SetupStep("setup_billing", "Setup Billing Exports", SetupState.NOT_STARTED, dependencies=["create_gke"])
            ]
        elif setup_type == SetupType.ENTERPRISE:
            return [
                SetupStep("verify_billing", "Verify Billing Account", SetupState.NOT_STARTED),
                SetupStep("create_project", "Create Project", SetupState.NOT_STARTED, dependencies=["verify_billing"]),
                SetupStep("link_billing", "Link Project to Billing", SetupState.NOT_STARTED, dependencies=["create_project"]),
                SetupStep("setup_iam", "Setup IAM Permissions", SetupState.NOT_STARTED, dependencies=["link_billing"]),
                SetupStep("enable_apis", "Enable APIs", SetupState.NOT_STARTED, dependencies=["setup_iam"]),
                SetupStep("create_gke", "Create GKE Cluster", SetupState.NOT_STARTED, dependencies=["enable_apis"])
            ]
        elif setup_type == SetupType.AUTHORIZATION:
            return [
                SetupStep("request_auth", "Request Authorization", SetupState.NOT_STARTED),
                SetupStep("admin_review", "Admin Review", SetupState.NOT_STARTED, dependencies=["request_auth"]),
                SetupStep("verify_auth", "Verify Authorization", SetupState.NOT_STARTED, dependencies=["admin_review"]),
                SetupStep("link_project", "Link Project with Auth", SetupState.NOT_STARTED, dependencies=["verify_auth"]),
                SetupStep("apply_iam", "Apply IAM Permissions", SetupState.NOT_STARTED, dependencies=["link_project"])
            ]
        else:
            return []
    
    def _find_step(self, step_id: str) -> Optional[SetupStep]:
        """Find step by ID"""
        if not self.current_session:
            return None
        
        for step in self.current_session.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def _check_dependencies(self, step: SetupStep) -> bool:
        """Check if step dependencies are met"""
        if not step.dependencies:
            return True
        
        for dep_id in step.dependencies:
            dep_step = self._find_step(dep_id)
            if not dep_step or dep_step.state != SetupState.COMPLETED:
                return False
        
        return True
    
    def _serialize_session(self, session: SetupSession) -> Dict[str, Any]:
        """Serialize session to dictionary"""
        return {
            "session_id": session.session_id,
            "setup_type": session.setup_type.value,
            "state": session.state.value,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "steps": [
                {
                    "step_id": step.step_id,
                    "step_name": step.step_name,
                    "state": step.state.value,
                    "start_time": step.start_time.isoformat() if step.start_time else None,
                    "end_time": step.end_time.isoformat() if step.end_time else None,
                    "error_message": step.error_message,
                    "result_data": step.result_data,
                    "dependencies": step.dependencies
                }
                for step in session.steps
            ],
            "configuration": session.configuration,
            "results": session.results
        }
    
    def _deserialize_session(self, data: Dict[str, Any]) -> SetupSession:
        """Deserialize session from dictionary"""
        steps = [
            SetupStep(
                step_id=step_data["step_id"],
                step_name=step_data["step_name"],
                state=SetupState(step_data["state"]),
                start_time=datetime.fromisoformat(step_data["start_time"]) if step_data["start_time"] else None,
                end_time=datetime.fromisoformat(step_data["end_time"]) if step_data["end_time"] else None,
                error_message=step_data["error_message"],
                result_data=step_data["result_data"],
                dependencies=step_data["dependencies"]
            )
            for step_data in data["steps"]
        ]
        
        return SetupSession(
            session_id=data["session_id"],
            setup_type=SetupType(data["setup_type"]),
            state=SetupState(data["state"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            steps=steps,
            configuration=data["configuration"],
            results=data["results"]
        )

def main():
    """Test the state manager"""
    print("🎯 GCP State Manager Test")
    print("=" * 30)
    
    # Create state manager
    state_manager = GCPStateManager()
    
    # Create a test session
    config = {
        "project_name": "test-project",
        "billing_account_id": "test-billing-123"
    }
    
    session_id = state_manager.create_session(SetupType.PERSONAL, config)
    print(f"Created session: {session_id}")
    
    # Get status
    status = state_manager.get_session_status()
    print(f"Session status: {json.dumps(status, indent=2)}")
    
    # Get next step
    next_step = state_manager.get_next_step()
    if next_step:
        print(f"Next step: {next_step.step_name}")
    
    print("✅ State manager test complete")

if __name__ == "__main__":
    main()
