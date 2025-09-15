#!/usr/bin/env python3
"""
LangGraph DevPost State Model
============================

LangGraph state model for orchestrating DevPost automation workflow.
This serves as the central state management for the entire automation process.
"""

from typing import Dict, List, Any, Optional, TypedDict, Annotated
from datetime import datetime
from enum import Enum
import json

from langgraph.graph import StateGraph, END

# from langgraph.prebuilt import ToolExecutor, ToolInvocation  # Not available in current version
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage


class WorkflowPhase(Enum):
    """Current phase of the DevPost automation workflow"""

    INITIALIZATION = "initialization"
    BROWSER_CONNECTION = "browser_connection"
    PAGE_DETECTION = "page_detection"
    FORM_ANALYSIS = "form_analysis"
    FORM_POPULATION = "form_population"
    FORM_SUBMISSION = "form_submission"
    NAVIGATION = "navigation"
    VALIDATION = "validation"
    COMPLETION = "completion"
    ERROR_RECOVERY = "error_recovery"


class BrowserConnectionStatus(Enum):
    """Status of browser connection"""

    NOT_CONNECTED = "not_connected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    FAILED = "failed"
    EXTENSION_AVAILABLE = "extension_available"  # 1Password, etc.


class PageDetectionResult(Enum):
    """Result of page detection"""

    UNKNOWN = "unknown"
    LOGIN_REQUIRED = "login_required"
    PROJECT_OVERVIEW = "project_overview"
    PROJECT_DETAILS = "project_details"
    MANAGE_TEAM = "manage_team"
    ADDITIONAL_INFO = "additional_info"
    SUBMISSION_REVIEW = "submission_review"
    SUBMISSION_COMPLETE = "submission_complete"
    ERROR_PAGE = "error_page"


class FormCompletionStatus(Enum):
    """Status of form completion"""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    VALIDATION_ERROR = "validation_error"
    COMPLETED = "completed"
    SUBMITTED = "submitted"


class DevPostState(TypedDict):
    """
    LangGraph state for DevPost automation workflow.

    This is the central state that flows through all nodes in the graph.
    """

    # Core workflow state
    current_phase: WorkflowPhase
    workflow_start_time: datetime
    workflow_id: str

    # Messages for LangGraph communication
    messages: Annotated[List[BaseMessage], "Messages in the conversation"]

    # Browser management
    browser_status: BrowserConnectionStatus
    browser_port: Optional[int]
    user_data_dir: str
    target_page_url: Optional[str]

    # Page detection and analysis
    current_page_type: PageDetectionResult
    page_url: Optional[str]
    page_title: Optional[str]
    page_screenshot_path: Optional[str]
    page_visual_hash: Optional[str]

    # Form analysis and completion
    form_completion_status: Dict[str, FormCompletionStatus]  # form_name -> status
    form_data: Dict[str, Dict[str, Any]]  # form_name -> field_data
    form_errors: Dict[str, List[str]]  # form_name -> error_messages

    # Navigation and telemetry
    navigation_history: List[Dict[str, Any]]
    telemetry_data: Dict[str, Any]
    session_preserved: bool

    # Error handling and recovery
    errors: List[str]
    recovery_attempts: int
    max_recovery_attempts: int

    # Decision making and routing
    next_action: Optional[str]
    routing_decision: Optional[str]
    user_input_required: bool

    # Validation and quality assurance
    validation_results: Dict[str, Any]
    submission_ready: bool
    quality_score: Optional[float]

    # External integrations
    browser_session_manager: Optional[Any]  # BrowserSessionManager instance
    site_navigation_session: Optional[Any]  # SiteNavigationSession instance
    telemetry_graph: Optional[Any]  # TelemetryGraph instance
    state_model: Optional[Any]  # DevPostStateModel instance

    # Performance metrics
    performance_metrics: Dict[str, Any]
    session_duration: Optional[float]

    # User preferences and configuration
    user_preferences: Dict[str, Any]
    automation_mode: str  # "interactive", "automatic", "guided"


def create_initial_state(
    workflow_id: Optional[str] = None,
    user_data_dir: str = "/tmp/devpost-browser",
    automation_mode: str = "interactive",
) -> DevPostState:
    """Create initial state for DevPost automation workflow"""

    if workflow_id is None:
        workflow_id = f"devpost_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    return DevPostState(
        # Core workflow state
        current_phase=WorkflowPhase.INITIALIZATION,
        workflow_start_time=datetime.now(),
        workflow_id=workflow_id,
        # Messages for LangGraph communication
        messages=[
            HumanMessage(content=f"Starting DevPost automation workflow {workflow_id}")
        ],
        # Browser management
        browser_status=BrowserConnectionStatus.NOT_CONNECTED,
        browser_port=None,
        user_data_dir=user_data_dir,
        target_page_url=None,
        # Page detection and analysis
        current_page_type=PageDetectionResult.UNKNOWN,
        page_url=None,
        page_title=None,
        page_screenshot_path=None,
        page_visual_hash=None,
        # Form analysis and completion
        form_completion_status={
            "project_overview": FormCompletionStatus.NOT_STARTED,
            "project_details": FormCompletionStatus.NOT_STARTED,
            "manage_team": FormCompletionStatus.NOT_STARTED,
            "additional_info": FormCompletionStatus.NOT_STARTED,
        },
        form_data={},
        form_errors={},
        # Navigation and telemetry
        navigation_history=[],
        telemetry_data={},
        session_preserved=False,
        # Error handling and recovery
        errors=[],
        recovery_attempts=0,
        max_recovery_attempts=3,
        # Decision making and routing
        next_action=None,
        routing_decision=None,
        user_input_required=True,
        # Validation and quality assurance
        validation_results={},
        submission_ready=False,
        quality_score=None,
        # External integrations
        browser_session_manager=None,
        site_navigation_session=None,
        telemetry_graph=None,
        state_model=None,
        # Performance metrics
        performance_metrics={},
        session_duration=None,
        # User preferences and configuration
        user_preferences={},
        automation_mode=automation_mode,
    )


def get_state_summary(state: DevPostState) -> Dict[str, Any]:
    """Get a summary of the current state for logging and debugging"""

    return {
        "workflow_id": state["workflow_id"],
        "current_phase": state["current_phase"].value,
        "browser_status": state["browser_status"].value,
        "current_page_type": state["current_page_type"].value,
        "form_completion_status": {
            k: v.value for k, v in state["form_completion_status"].items()
        },
        "errors": state["errors"],
        "recovery_attempts": state["recovery_attempts"],
        "submission_ready": state["submission_ready"],
        "user_input_required": state["user_input_required"],
        "session_preserved": state["session_preserved"],
        "automation_mode": state["automation_mode"],
        "workflow_duration": (
            (datetime.now() - state["workflow_start_time"]).total_seconds()
            if state["workflow_start_time"]
            else None
        ),
    }


def save_state_to_file(state: DevPostState, filepath: str) -> bool:
    """Save state to JSON file for persistence"""
    try:
        # Convert state to serializable format
        serializable_state = {}
        for key, value in state.items():
            if isinstance(value, Enum):
                serializable_state[key] = value.value
            elif isinstance(value, datetime):
                serializable_state[key] = value.isoformat()
            elif hasattr(value, "__dict__"):
                # Handle complex objects by converting to dict if possible
                try:
                    serializable_state[key] = value.__dict__
                except:
                    serializable_state[key] = str(value)
            else:
                serializable_state[key] = value

        with open(filepath, "w") as f:
            json.dump(serializable_state, f, indent=2, default=str)

        return True
    except Exception as e:
        print(f"Error saving state to {filepath}: {e}")
        return False


def load_state_from_file(filepath: str) -> Optional[DevPostState]:
    """Load state from JSON file"""
    try:
        with open(filepath, "r") as f:
            data = json.load(f)

        # Convert back to proper types
        state = DevPostState()

        for key, value in data.items():
            if key == "current_phase" and isinstance(value, str):
                state[key] = WorkflowPhase(value)
            elif key == "browser_status" and isinstance(value, str):
                state[key] = BrowserConnectionStatus(value)
            elif key == "current_page_type" and isinstance(value, str):
                state[key] = PageDetectionResult(value)
            elif key == "form_completion_status" and isinstance(value, dict):
                state[key] = {k: FormCompletionStatus(v) for k, v in value.items()}
            elif key == "workflow_start_time" and isinstance(value, str):
                state[key] = datetime.fromisoformat(value)
            elif key == "messages":
                # Handle messages separately - would need proper deserialization
                state[key] = []
            else:
                state[key] = value

        return state
    except Exception as e:
        print(f"Error loading state from {filepath}: {e}")
        return None


# State update helpers
def update_phase(state: DevPostState, new_phase: WorkflowPhase) -> DevPostState:
    """Update the current workflow phase"""
    state["current_phase"] = new_phase
    state["messages"].append(
        AIMessage(content=f"Workflow phase changed to: {new_phase.value}")
    )
    return state


def add_error(state: DevPostState, error: str) -> DevPostState:
    """Add an error to the state"""
    state["errors"].append(error)
    state["messages"].append(AIMessage(content=f"Error encountered: {error}"))
    return state


def increment_recovery_attempts(state: DevPostState) -> DevPostState:
    """Increment recovery attempts counter"""
    state["recovery_attempts"] += 1
    return state


def reset_recovery_attempts(state: DevPostState) -> DevPostState:
    """Reset recovery attempts counter"""
    state["recovery_attempts"] = 0
    return state


def update_form_status(
    state: DevPostState, form_name: str, status: FormCompletionStatus
) -> DevPostState:
    """Update the completion status of a specific form"""
    state["form_completion_status"][form_name] = status
    return state


def set_user_input_required(state: DevPostState, required: bool) -> DevPostState:
    """Set whether user input is required"""
    state["user_input_required"] = required
    return state


def update_performance_metrics(
    state: DevPostState, metrics: Dict[str, Any]
) -> DevPostState:
    """Update performance metrics"""
    state["performance_metrics"].update(metrics)
    return state
