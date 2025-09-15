#!/usr/bin/env python3
"""
DevPost State Model - Comprehensive navigation and form state tracking
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import os


class PageType(Enum):
    """Types of DevPost pages we can encounter"""

    LOGIN = "login"
    SUBMISSION_OVERVIEW = "submission_overview"
    PROJECT_OVERVIEW = "project_overview"
    PROJECT_DETAILS = "project_details"
    TEAM_MANAGEMENT = "team_management"
    ADDITIONAL_INFO = "additional_info"
    REVIEW_SUBMISSION = "review_submission"
    SUBMISSION_COMPLETE = "submission_complete"
    UNKNOWN = "unknown"


class FormStatus(Enum):
    """Status of form completion"""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VALIDATED = "validated"
    ERROR = "error"


@dataclass
class NavigationElement:
    """Represents a navigation element on the page"""

    text: str
    href: Optional[str]
    element_type: str  # 'link', 'button', 'step'
    is_clickable: bool
    is_current_step: bool = False
    step_number: Optional[int] = None


@dataclass
class FormField:
    """Represents a form field"""

    name: str
    field_type: str  # 'text', 'textarea', 'select', 'checkbox', etc.
    value: str
    placeholder: str
    is_required: bool
    is_filled: bool
    validation_message: str = ""


@dataclass
class PageState:
    """Complete state of a DevPost page"""

    url: str
    title: str
    page_type: PageType
    timestamp: str

    # Navigation state
    available_steps: List[NavigationElement]
    other_navigation_options: List[NavigationElement]
    form_fields: List[FormField]
    total_elements: int
    interactive_elements: List[Dict[str, Any]]

    # Optional fields with defaults
    current_step: Optional[NavigationElement] = None
    form_status: FormStatus = FormStatus.NOT_STARTED
    errors: List[str] = None
    warnings: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


@dataclass
class SessionState:
    """Complete session state tracking"""

    session_id: str
    start_time: str

    # Navigation history
    page_history: List[PageState]
    current_page: Optional[PageState] = None

    # Overall progress
    total_steps_identified: int = 0
    steps_completed: int = 0
    forms_completed: int = 0

    # Session metadata
    browser_connected: bool = False
    last_activity: str = ""
    errors_encountered: List[str] = None

    def __post_init__(self):
        if self.errors_encountered is None:
            self.errors_encountered = []


class DevPostStateModel:
    """Comprehensive state model for DevPost navigation"""

    def __init__(self, session_id: str = None):
        self.session_id = session_id or f"devpost_session_{int(time.time())}"
        self.session_state = SessionState(
            session_id=self.session_id,
            start_time=datetime.now().isoformat(),
            page_history=[],
        )
        self.state_file = f"devpost_state_{self.session_id}.json"

    def identify_page_type(
        self, url: str, title: str, page_content: Dict[str, Any]
    ) -> PageType:
        """Identify the type of DevPost page based on URL, title, and content"""
        url_lower = url.lower()
        title_lower = title.lower()

        # Extract step information from page content for blind detection
        step_indicators = []
        form_indicators = []

        # Analyze navigation elements for step detection
        for nav in page_content.get("navigationElements", []):
            nav_text = nav.get("text", "").lower()
            nav_class = nav.get("className", "").lower()

            if "current" in nav_class:
                step_indicators.append(f"current_step: {nav_text}")
            if "completed" in nav_class:
                step_indicators.append(f"completed_step: {nav_text}")
            if "step" in nav_class:
                step_indicators.append(f"step_navigation: {nav_text}")

        # Analyze form elements for page type detection
        for form in page_content.get("formElements", []):
            form_name = form.get("name", "").lower()
            form_id = form.get("id", "").lower()

            if "team" in form_name or "team" in form_id:
                form_indicators.append("team_management")
            elif "project" in form_name or "project" in form_id:
                form_indicators.append("project_form")
            elif "additional" in form_name or "additional" in form_id:
                form_indicators.append("additional_info")

        # Check for specific URL patterns
        if "login" in url_lower or "sign" in url_lower:
            return PageType.LOGIN
        elif (
            "manage-team" in url_lower
            or "team" in title_lower
            or "team_management" in form_indicators
        ):
            return PageType.TEAM_MANAGEMENT
        elif "project-overview" in url_lower or "overview" in title_lower:
            return PageType.PROJECT_OVERVIEW
        elif (
            "project-details" in url_lower
            or "details" in title_lower
            or "project_details" in url_lower
        ):
            return PageType.PROJECT_DETAILS
        elif (
            "additional-info" in url_lower
            or "additional" in title_lower
            or "additional_info" in form_indicators
        ):
            return PageType.ADDITIONAL_INFO
        elif (
            "review" in url_lower
            or "review" in title_lower
            or "finalization" in url_lower
        ):
            return PageType.REVIEW_SUBMISSION
        elif "complete" in url_lower or "submitted" in url_lower:
            return PageType.SUBMISSION_COMPLETE
        elif "submissions" in url_lower:
            return PageType.SUBMISSION_OVERVIEW
        else:
            # Blind detection - analyze content to determine page type
            if any("current_step" in indicator for indicator in step_indicators):
                current_step_text = next(
                    (
                        indicator.split(": ")[1]
                        for indicator in step_indicators
                        if "current_step" in indicator
                    ),
                    "",
                )
                if "team" in current_step_text.lower():
                    return PageType.TEAM_MANAGEMENT
                elif "overview" in current_step_text.lower():
                    return PageType.PROJECT_OVERVIEW
                elif "details" in current_step_text.lower():
                    return PageType.PROJECT_DETAILS
                elif "additional" in current_step_text.lower():
                    return PageType.ADDITIONAL_INFO
                elif "submit" in current_step_text.lower():
                    return PageType.REVIEW_SUBMISSION

            return PageType.UNKNOWN

    def extract_navigation_elements(
        self, page_content: Dict[str, Any]
    ) -> List[NavigationElement]:
        """Extract navigation elements from page content"""
        navigation_elements = []

        # Extract step navigation
        for nav in page_content.get("navigationElements", []):
            navigation_elements.append(
                NavigationElement(
                    text=nav.get("text", ""),
                    href=nav.get("href"),
                    element_type="step",
                    is_clickable=True,
                    step_number=self._extract_step_number(nav.get("text", "")),
                )
            )

        # Extract other navigation options
        for interactive in page_content.get("interactiveElements", []):
            if interactive.get("tag") in ["button", "a"]:
                navigation_elements.append(
                    NavigationElement(
                        text=interactive.get("text", ""),
                        href=interactive.get("href"),
                        element_type=(
                            "button" if interactive.get("tag") == "button" else "link"
                        ),
                        is_clickable=True,
                    )
                )

        return navigation_elements

    def _extract_step_number(self, text: str) -> Optional[int]:
        """Extract step number from navigation text"""
        import re

        match = re.search(r"step\s*(\d+)", text.lower())
        return int(match.group(1)) if match else None

    def extract_form_fields(self, page_content: Dict[str, Any]) -> List[FormField]:
        """Extract form fields from page content"""
        form_fields = []

        for form in page_content.get("formElements", []):
            if form.get("tag") in ["input", "textarea", "select"]:
                form_fields.append(
                    FormField(
                        name=form.get("name", form.get("id", "")),
                        field_type=form.get("type", form.get("tag", "")),
                        value=form.get("value", ""),
                        placeholder=form.get("placeholder", ""),
                        is_required="required" in form.get("className", "").lower(),
                        is_filled=bool(form.get("value", "").strip()),
                    )
                )

        return form_fields

    def update_page_state(
        self, url: str, title: str, page_content: Dict[str, Any]
    ) -> PageState:
        """Update the current page state with new information"""
        page_type = self.identify_page_type(url, title, page_content)
        navigation_elements = self.extract_navigation_elements(page_content)
        form_fields = self.extract_form_fields(page_content)

        # Determine current step
        current_step = None
        for nav in navigation_elements:
            if nav.is_current_step or "current" in nav.text.lower():
                current_step = nav
                break

        # Determine form status
        form_status = FormStatus.NOT_STARTED
        if form_fields:
            filled_fields = sum(1 for field in form_fields if field.is_filled)
            if filled_fields == len(form_fields):
                form_status = FormStatus.COMPLETED
            elif filled_fields > 0:
                form_status = FormStatus.IN_PROGRESS

        page_state = PageState(
            url=url,
            title=title,
            page_type=page_type,
            timestamp=datetime.now().isoformat(),
            available_steps=navigation_elements,
            other_navigation_options=[
                nav for nav in navigation_elements if nav.element_type != "step"
            ],
            current_step=current_step,
            form_fields=form_fields,
            form_status=form_status,
            total_elements=page_content.get("totalElements", 0),
            interactive_elements=page_content.get("interactiveElements", []),
        )

        # Update session state
        self.session_state.page_history.append(page_state)
        self.session_state.current_page = page_state
        self.session_state.last_activity = datetime.now().isoformat()

        # Update progress tracking
        self.session_state.total_steps_identified = len(
            [nav for nav in navigation_elements if nav.element_type == "step"]
        )
        self.session_state.steps_completed = len(
            [
                state
                for state in self.session_state.page_history
                if state.form_status == FormStatus.COMPLETED
            ]
        )
        self.session_state.forms_completed = len(
            [
                state
                for state in self.session_state.page_history
                if state.form_status == FormStatus.COMPLETED
            ]
        )

        return page_state

    def get_navigation_recommendations(self) -> Dict[str, Any]:
        """Get intelligent navigation recommendations based on current state"""
        if not self.session_state.current_page:
            return {"error": "No current page state"}

        current_page = self.session_state.current_page
        recommendations = {
            "current_step": (
                current_page.current_step.text
                if current_page.current_step
                else "Unknown"
            ),
            "next_actions": [],
            "warnings": [],
            "progress": {
                "steps_completed": self.session_state.steps_completed,
                "total_steps": self.session_state.total_steps_identified,
                "completion_percentage": (
                    self.session_state.steps_completed
                    / max(self.session_state.total_steps_identified, 1)
                )
                * 100,
            },
        }

        # Generate next action recommendations
        if current_page.form_status == FormStatus.NOT_STARTED:
            recommendations["next_actions"].append("Fill out the current form")
        elif current_page.form_status == FormStatus.IN_PROGRESS:
            recommendations["next_actions"].append("Complete remaining form fields")
        elif current_page.form_status == FormStatus.COMPLETED:
            recommendations["next_actions"].append("Navigate to next step")

        # Add warnings
        if current_page.form_status == FormStatus.ERROR:
            recommendations["warnings"].append("Form has validation errors")

        if not current_page.available_steps:
            recommendations["warnings"].append("No navigation steps found")

        return recommendations

    def save_state(self):
        """Save current state to file with session preservation info"""
        state_data = {
            "session_state": asdict(self.session_state),
            "session_preservation": {
                "browser_data_dir": "/tmp/devpost-browser",
                "preserves_cookies": True,
                "preserves_login_state": True,
                "preserves_form_data": True,
                "last_url": (
                    self.session_state.current_page.url
                    if self.session_state.current_page
                    else None
                ),
            },
            "metadata": {
                "version": "1.0",
                "last_saved": datetime.now().isoformat(),
                "total_pages_visited": len(self.session_state.page_history),
                "resume_instructions": "Browser session data preserved - can resume from last position",
            },
        }

        with open(self.state_file, "w") as f:
            json.dump(state_data, f, indent=2)

        print(f"💾 State saved with session preservation: {self.state_file}")

    def load_state(self) -> bool:
        """Load state from file"""
        if not os.path.exists(self.state_file):
            return False

        try:
            with open(self.state_file, "r") as f:
                state_data = json.load(f)

            # Reconstruct session state
            session_data = state_data["session_state"]
            self.session_state = SessionState(**session_data)
            return True
        except Exception as e:
            print(f"❌ Error loading state: {e}")
            return False

    def detect_current_condition(
        self, url: str, title: str, page_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Blind detection of current condition - no assumptions about starting state"""
        detection = {
            "session_state": "unknown",
            "page_type": "unknown",
            "current_step": "unknown",
            "progress": "unknown",
            "form_status": "unknown",
            "recommendations": [],
            "warnings": [],
            "confidence": "low",
        }

        # Analyze page content for current state indicators
        step_indicators = []
        form_indicators = []
        progress_indicators = []

        # Extract step information
        for nav in page_content.get("navigationElements", []):
            nav_text = nav.get("text", "").lower()
            nav_class = nav.get("className", "").lower()

            if "current" in nav_class:
                step_indicators.append(f"current: {nav_text}")
                detection["current_step"] = nav_text
                detection["confidence"] = "medium"
            if "completed" in nav_class:
                step_indicators.append(f"completed: {nav_text}")
                progress_indicators.append("has_completed_steps")
            if "step" in nav_class:
                step_indicators.append(f"available: {nav_text}")

        # Extract form information
        for form in page_content.get("formElements", []):
            form_name = form.get("name", "").lower()
            form_value = form.get("value", "").strip()

            if form_value:
                form_indicators.append(f"filled: {form_name}")
                detection["form_status"] = "in_progress"
            else:
                form_indicators.append(f"empty: {form_name}")

        # Analyze overall progress
        completed_count = len([s for s in step_indicators if "completed" in s])
        total_steps = len([s for s in step_indicators if "step" in s or "current" in s])

        if total_steps > 0:
            progress_percentage = (completed_count / total_steps) * 100
            detection["progress"] = (
                f"{completed_count}/{total_steps} ({progress_percentage:.1f}%)"
            )
            detection["confidence"] = "high" if progress_percentage > 0 else "medium"

        # Generate recommendations based on detected state
        if detection["form_status"] == "in_progress":
            detection["recommendations"].append("Complete current form fields")
        elif completed_count > 0:
            detection["recommendations"].append("Navigate to next incomplete step")
        else:
            detection["recommendations"].append("Start with first available step")

        # Add warnings
        if detection["confidence"] == "low":
            detection["warnings"].append(
                "Unable to determine current state with high confidence"
            )

        if not form_indicators:
            detection["warnings"].append("No form fields detected")

        detection["page_type"] = self.identify_page_type(url, title, page_content).value

        return detection

    def check_session_resume_capability(self) -> Dict[str, Any]:
        """Check if we can resume from existing session data"""
        import os

        resume_info = {
            "can_resume": False,
            "browser_data_exists": False,
            "state_file_exists": False,
            "last_url": None,
            "resume_instructions": [],
        }

        # Check browser data directory
        browser_data_path = "/tmp/devpost-browser"
        if os.path.exists(browser_data_path):
            resume_info["browser_data_exists"] = True
            resume_info["resume_instructions"].append(
                "💾 Browser session data preserved"
            )
            resume_info["can_resume"] = True

        # Check state file
        if os.path.exists(self.state_file):
            resume_info["state_file_exists"] = True
            try:
                with open(self.state_file, "r") as f:
                    state_data = json.load(f)
                    if "session_preservation" in state_data:
                        resume_info["last_url"] = state_data[
                            "session_preservation"
                        ].get("last_url")
                        resume_info["resume_instructions"].append(
                            "📄 Previous session state available"
                        )
                        resume_info["can_resume"] = True
            except:
                pass

        return resume_info

    def get_state_summary(self) -> str:
        """Get a human-readable summary of current state"""
        if not self.session_state.current_page:
            return "No current page state - use blind detection first"

        current = self.session_state.current_page
        progress = self.get_navigation_recommendations()["progress"]

        summary = f"""
🎯 DEVPOST STATE SUMMARY
{'='*50}
📊 Session: {self.session_id}
🕐 Started: {self.session_state.start_time}
📄 Current Page: {current.title}
🔗 URL: {current.url}
📋 Page Type: {current.page_type.value}
📍 Current Step: {current.current_step.text if current.current_step else 'Unknown'}

📈 Progress:
   • Steps Completed: {progress['steps_completed']}/{progress['total_steps']}
   • Completion: {progress['completion_percentage']:.1f}%
   • Forms Completed: {self.session_state.forms_completed}

🎮 Available Actions:
   • Step Navigation: {len([nav for nav in current.available_steps if nav.element_type == 'step'])}
   • Other Options: {len(current.other_navigation_options)}
   • Form Fields: {len(current.form_fields)}
   • Form Status: {current.form_status.value}

⚠️  Issues: {len(current.errors)} errors, {len(current.warnings)} warnings
"""
        return summary.strip()


def create_state_model(session_id: str = None) -> DevPostStateModel:
    """Create a new state model instance"""
    return DevPostStateModel(session_id)


if __name__ == "__main__":
    # Test the state model
    model = create_state_model()
    print("✅ DevPost State Model created successfully")
    print(f"📁 State file: {model.state_file}")
    print(model.get_state_summary())
