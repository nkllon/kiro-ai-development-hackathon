#!/usr/bin/env python3
"""
Site Navigation Session
=======================

Manages site-specific navigation, forms, and business logic.
Separate from browser instance management.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class NavigationIntent(Enum):
    """Types of navigation actions"""
    EXPLORE = "explore"
    FORM_FILL = "form_fill"
    FORM_SUBMIT = "form_submit"
    STEP_NAVIGATION = "step_navigation"
    SEARCH = "search"
    LOGIN = "login"
    LOGOUT = "logout"
    UNKNOWN = "unknown"


class FormCompletionStatus(Enum):
    """Status of form completion"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    VALIDATION_ERROR = "validation_error"
    COMPLETED = "completed"
    SUBMITTED = "submitted"


@dataclass
class NavigationAction:
    """Represents a navigation action taken"""
    action_type: NavigationIntent
    target_element: str
    target_url: str
    timestamp: str
    success: bool
    error_message: Optional[str] = None
    form_data: Optional[Dict[str, Any]] = None
    page_state_before: Optional[Dict[str, Any]] = None
    page_state_after: Optional[Dict[str, Any]] = None


@dataclass
class FormField:
    """Represents a form field"""
    name: str
    field_type: str
    value: str
    placeholder: str
    is_required: bool
    is_filled: bool
    validation_message: str = ""
    auto_fill_source: str = ""  # "1password", "manual", "auto", etc.


@dataclass
class FormSession:
    """Represents a form completion session"""
    form_id: str
    form_name: str
    page_url: str
    fields: List[FormField]
    completion_status: FormCompletionStatus
    start_time: str
    last_modified: str
    auto_fill_attempts: int = 0
    manual_edits: int = 0


@dataclass
class SiteNavigationSession:
    """Complete site navigation session"""
    session_id: str
    site_domain: str
    start_time: str
    end_time: Optional[str] = None
    
    # Navigation tracking
    navigation_actions: List[NavigationAction] = None
    current_page: Optional[str] = None
    page_history: List[str] = None
    
    # Form tracking
    active_forms: List[FormSession] = None
    completed_forms: List[FormSession] = None
    
    # Session metadata
    user_agent: str = ""
    browser_capabilities: Dict[str, Any] = None
    site_specific_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.navigation_actions is None:
            self.navigation_actions = []
        if self.page_history is None:
            self.page_history = []
        if self.active_forms is None:
            self.active_forms = []
        if self.completed_forms is None:
            self.completed_forms = []
        if self.browser_capabilities is None:
            self.browser_capabilities = {}
        if self.site_specific_data is None:
            self.site_specific_data = {}


class DevPostNavigationSession(SiteNavigationSession):
    """DevPost-specific navigation session with domain knowledge"""
    
    def __init__(self, session_id: str = None):
        super().__init__(
            session_id=session_id or f"devpost_session_{int(time.time())}",
            site_domain="devpost.com",
            start_time=datetime.now().isoformat()
        )
        
        # DevPost-specific initialization
        self.site_specific_data = {
            "hackathon_id": None,
            "submission_id": None,
            "project_name": None,
            "current_step": None,
            "step_progress": {},
            "team_members": [],
            "form_templates": {}
        }
    
    def add_navigation_action(self, action_type: NavigationIntent, 
                            target_element: str, target_url: str,
                            success: bool, error_message: str = None,
                            form_data: Dict[str, Any] = None,
                            page_state_before: Dict[str, Any] = None,
                            page_state_after: Dict[str, Any] = None):
        """Add a navigation action to the session"""
        action = NavigationAction(
            action_type=action_type,
            target_element=target_element,
            target_url=target_url,
            timestamp=datetime.now().isoformat(),
            success=success,
            error_message=error_message,
            form_data=form_data,
            page_state_before=page_state_before,
            page_state_after=page_state_after
        )
        
        self.navigation_actions.append(action)
        
        # Update current page if navigation was successful
        if success and target_url:
            self.current_page = target_url
            if target_url not in self.page_history:
                self.page_history.append(target_url)
    
    def start_form_session(self, form_id: str, form_name: str, page_url: str, 
                          fields: List[FormField]) -> FormSession:
        """Start tracking a new form session"""
        form_session = FormSession(
            form_id=form_id,
            form_name=form_name,
            page_url=page_url,
            fields=fields,
            completion_status=FormCompletionStatus.NOT_STARTED,
            start_time=datetime.now().isoformat(),
            last_modified=datetime.now().isoformat()
        )
        
        self.active_forms.append(form_session)
        return form_session
    
    def update_form_field(self, form_id: str, field_name: str, 
                         value: str, auto_fill_source: str = "manual"):
        """Update a form field value"""
        for form in self.active_forms:
            if form.form_id == form_id:
                for field in form.fields:
                    if field.name == field_name:
                        field.value = value
                        field.is_filled = bool(value.strip())
                        field.auto_fill_source = auto_fill_source
                        form.last_modified = datetime.now().isoformat()
                        
                        if auto_fill_source != "manual":
                            form.auto_fill_attempts += 1
                        else:
                            form.manual_edits += 1
                        
                        # Update completion status
                        filled_fields = sum(1 for f in form.fields if f.is_filled)
                        if filled_fields == len(form.fields):
                            form.completion_status = FormCompletionStatus.COMPLETED
                        elif filled_fields > 0:
                            form.completion_status = FormCompletionStatus.IN_PROGRESS
                        
                        return True
        return False
    
    def complete_form_session(self, form_id: str, success: bool):
        """Mark a form session as completed"""
        for i, form in enumerate(self.active_forms):
            if form.form_id == form_id:
                form.completion_status = (
                    FormCompletionStatus.SUBMITTED if success 
                    else FormCompletionStatus.VALIDATION_ERROR
                )
                form.last_modified = datetime.now().isoformat()
                
                # Move to completed forms
                self.completed_forms.append(form)
                del self.active_forms[i]
                
                return True
        return False
    
    def get_session_analytics(self) -> Dict[str, Any]:
        """Get comprehensive session analytics"""
        total_actions = len(self.navigation_actions)
        successful_actions = sum(1 for action in self.navigation_actions if action.success)
        
        form_analytics = {
            "total_forms": len(self.active_forms) + len(self.completed_forms),
            "active_forms": len(self.active_forms),
            "completed_forms": len(self.completed_forms),
            "total_auto_fills": sum(form.auto_fill_attempts for form in self.active_forms + self.completed_forms),
            "total_manual_edits": sum(form.manual_edits for form in self.active_forms + self.completed_forms)
        }
        
        navigation_analytics = {
            "total_navigations": total_actions,
            "success_rate": (successful_actions / max(total_actions, 1)) * 100,
            "unique_pages_visited": len(set(self.page_history)),
            "action_types": {}
        }
        
        # Count action types
        for action in self.navigation_actions:
            action_type = action.action_type.value
            navigation_analytics["action_types"][action_type] = \
                navigation_analytics["action_types"].get(action_type, 0) + 1
        
        return {
            "session_id": self.session_id,
            "site_domain": self.site_domain,
            "duration": self._calculate_duration(),
            "navigation_analytics": navigation_analytics,
            "form_analytics": form_analytics,
            "devpost_specific": self.site_specific_data,
            "current_page": self.current_page,
            "session_status": "active" if not self.end_time else "completed"
        }
    
    def _calculate_duration(self) -> str:
        """Calculate session duration"""
        try:
            start_time = datetime.fromisoformat(self.start_time)
            end_time = datetime.fromisoformat(self.end_time) if self.end_time else datetime.now()
            duration = end_time - start_time
            return str(duration).split('.')[0]  # Remove microseconds
        except:
            return "unknown"
    
    def save_session(self, filename: str = None):
        """Save session to file"""
        if not filename:
            filename = f"devpost_navigation_session_{self.session_id}.json"
        
        session_data = {
            "session": asdict(self),
            "analytics": self.get_session_analytics(),
            "metadata": {
                "version": "1.0",
                "saved_at": datetime.now().isoformat(),
                "total_actions": len(self.navigation_actions),
                "total_forms": len(self.active_forms) + len(self.completed_forms)
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        print(f"💾 DevPost navigation session saved: {filename}")
        return filename


def create_devpost_session(session_id: str = None) -> DevPostNavigationSession:
    """Create a new DevPost navigation session"""
    return DevPostNavigationSession(session_id)


if __name__ == "__main__":
    # Test the navigation session
    session = create_devpost_session()
    
    # Simulate some navigation
    session.add_navigation_action(
        NavigationIntent.STEP_NAVIGATION,
        "project-overview-link",
        "https://devpost.com/submit-to/123/project-overview",
        True
    )
    
    session.add_navigation_action(
        NavigationIntent.FORM_FILL,
        "project-title-input",
        "https://devpost.com/submit-to/123/project-overview",
        True,
        form_data={"title": "My Awesome Project"}
    )
    
    # Simulate form session
    fields = [
        FormField("title", "text", "My Project", "Enter project title", True, True),
        FormField("description", "textarea", "", "Describe your project", True, False)
    ]
    
    form_session = session.start_form_session(
        "project-overview-form",
        "Project Overview",
        "https://devpost.com/submit-to/123/project-overview",
        fields
    )
    
    session.update_form_field("project-overview-form", "description", 
                            "An amazing project that does amazing things", "1password")
    
    session.complete_form_session("project-overview-form", True)
    
    # Save and show analytics
    filename = session.save_session()
    analytics = session.get_session_analytics()
    
    print("📊 Session Analytics:")
    print(json.dumps(analytics, indent=2))
