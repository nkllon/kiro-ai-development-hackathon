"""
Task timeout escalation system implementing the "alarm clock → family → cops → reaper" model.

This module provides a graduated response system for handling stuck tasks,
from gentle reminders to hard termination.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from enum import Enum, auto
from dataclasses import dataclass, field
import uuid

from .models import TaskContext, TaskState


class EscalationLevel(Enum):
    """Task timeout escalation levels."""
    PERSONAL_ALARM = auto()      # Self-managed timeout
    FAMILY_CHECK = auto()        # Gentle supervisor intervention  
    SEND_COPS = auto()          # Contract enforcement
    THE_REAPER = auto()         # Hard termination (kill -9)


class InterventionType(Enum):
    """Types of timeout interventions."""
    GENTLE_REMINDER = auto()     # "Tap on the shoulder"
    PROGRESS_CHECK = auto()      # "How's it going?"
    CONTRACT_WARNING = auto()    # "You have a deadline"
    HARD_TERMINATION = auto()    # "Time's up"


@dataclass
class TimeoutContract:
    """Represents a contractual timeout obligation."""
    contract_id: str
    task_id: str
    contractor_id: str  # Who made the promise
    client_id: str      # Who expects delivery
    promised_completion: datetime
    max_extension_minutes: int = 30
    signature_hash: str = ""
    verified: bool = False
    penalty_clause: Optional[str] = None


@dataclass
class EscalationEvent:
    """Represents a timeout escalation event."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = ""
    escalation_level: EscalationLevel = EscalationLevel.PERSONAL_ALARM
    intervention_type: InterventionType = InterventionType.GENTLE_REMINDER
    triggered_at: datetime = field(default_factory=datetime.now)
    message: str = ""
    callback_url: Optional[str] = None
    requires_response: bool = False
    response_deadline: Optional[datetime] = None
    escalation_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskTimeoutProfile:
    """Defines timeout behavior for a task."""
    task_id: str
    
    # Personal alarm clock settings
    self_timeout_minutes: int = 15
    progress_check_interval_minutes: int = 5
    
    # Family check settings  
    supervisor_check_minutes: int = 20
    gentle_reminder_count: int = 2
    
    # Contract enforcement settings
    contract: Optional[TimeoutContract] = None
    contract_warning_minutes: int = 5  # Before contract deadline
    
    # Reaper settings (universal timeout)
    hard_timeout_minutes: int = 60
    kill_signal_delay_seconds: int = 30
    
    # Callback configuration
    callback_urls: Dict[EscalationLevel, str] = field(default_factory=dict)
    notification_preferences: Dict[str, Any] = field(default_factory=dict)


class TaskTimeoutEscalationManager:
    """Manages the escalation hierarchy for task timeouts."""
    
    def __init__(self):
        self._logger = logging.getLogger(f"{__name__}.TaskTimeoutEscalationManager")
        self._active_timeouts: Dict[str, TaskTimeoutProfile] = {}
        self._escalation_history: List[EscalationEvent] = []
        self._callback_handlers: Dict[EscalationLevel, Callable] = {}
        
        # Setup default callback handlers
        self._setup_default_handlers()
    
    def register_task_timeout_profile(self, profile: TaskTimeoutProfile):
        """Register a timeout profile for a task."""
        self._active_timeouts[profile.task_id] = profile
        
        self._logger.info(
            f"Registered timeout profile for task {profile.task_id}",
            extra={
                "task_id": profile.task_id,
                "self_timeout": profile.self_timeout_minutes,
                "supervisor_check": profile.supervisor_check_minutes,
                "hard_timeout": profile.hard_timeout_minutes,
                "has_contract": profile.contract is not None
            }
        )
    
    async def check_task_timeouts(self, task: TaskContext) -> List[EscalationEvent]:
        """Check if a task needs timeout intervention and return escalation events."""
        if task.task_id not in self._active_timeouts:
            return []
        
        profile = self._active_timeouts[task.task_id]
        events = []
        
        # Calculate task timing
        now = datetime.now()
        execution_time = self._get_execution_time_minutes(task)
        total_age = self._get_total_age_minutes(task)
        
        # Level 1: Personal Alarm Clock
        if execution_time >= profile.self_timeout_minutes:
            event = await self._create_personal_alarm_event(task, profile, execution_time)
            if event:
                events.append(event)
        
        # Level 2: Family Check (Gentle Intervention)
        if execution_time >= profile.supervisor_check_minutes:
            event = await self._create_family_check_event(task, profile, execution_time)
            if event:
                events.append(event)
        
        # Level 3: Contract Enforcement
        if profile.contract and self._is_contract_deadline_approaching(profile.contract, now):
            event = await self._create_contract_enforcement_event(task, profile)
            if event:
                events.append(event)
        
        # Level 4: The Reaper (Universal Timeout)
        if execution_time >= profile.hard_timeout_minutes:
            event = await self._create_reaper_event(task, profile, execution_time)
            if event:
                events.append(event)
        
        return events
    
    async def _create_personal_alarm_event(
        self, 
        task: TaskContext, 
        profile: TaskTimeoutProfile, 
        execution_time: float
    ) -> Optional[EscalationEvent]:
        """Create personal alarm clock event."""
        
        # Check if we've already sent this level of escalation recently
        if self._has_recent_escalation(task.task_id, EscalationLevel.PERSONAL_ALARM, minutes=5):
            return None
        
        message = (
            f"Personal timeout alert: Task {task.task_id} has been executing for "
            f"{execution_time:.1f} minutes (threshold: {profile.self_timeout_minutes} minutes). "
            f"Consider checking progress or requesting extension."
        )
        
        event = EscalationEvent(
            task_id=task.task_id,
            escalation_level=EscalationLevel.PERSONAL_ALARM,
            intervention_type=InterventionType.GENTLE_REMINDER,
            message=message,
            callback_url=profile.callback_urls.get(EscalationLevel.PERSONAL_ALARM),
            requires_response=False,
            escalation_data={
                "execution_time_minutes": execution_time,
                "threshold_minutes": profile.self_timeout_minutes,
                "suggested_actions": [
                    "Check task progress",
                    "Request timeout extension", 
                    "Report if stuck",
                    "Consider breaking down task"
                ]
            }
        )
        
        self._escalation_history.append(event)
        return event
    
    async def _create_family_check_event(
        self, 
        task: TaskContext, 
        profile: TaskTimeoutProfile, 
        execution_time: float
    ) -> Optional[EscalationEvent]:
        """Create family check (supervisor intervention) event."""
        
        # Check if we've already sent this level recently
        if self._has_recent_escalation(task.task_id, EscalationLevel.FAMILY_CHECK, minutes=10):
            return None
        
        # Count previous gentle reminders
        reminder_count = self._count_escalations(task.task_id, EscalationLevel.FAMILY_CHECK)
        
        if reminder_count < profile.gentle_reminder_count:
            message = (
                f"Supervisor check: Hey, you've been at task {task.task_id} for "
                f"{execution_time:.1f} minutes. Is everything okay? "
                f"Any blockers or need help?"
            )
            intervention_type = InterventionType.GENTLE_REMINDER
        else:
            message = (
                f"Supervisor escalation: Task {task.task_id} has been running for "
                f"{execution_time:.1f} minutes with {reminder_count} previous reminders. "
                f"Please provide status update or request assistance."
            )
            intervention_type = InterventionType.PROGRESS_CHECK
        
        event = EscalationEvent(
            task_id=task.task_id,
            escalation_level=EscalationLevel.FAMILY_CHECK,
            intervention_type=intervention_type,
            message=message,
            callback_url=profile.callback_urls.get(EscalationLevel.FAMILY_CHECK),
            requires_response=True,
            response_deadline=datetime.now() + timedelta(minutes=5),
            escalation_data={
                "execution_time_minutes": execution_time,
                "reminder_count": reminder_count,
                "supervisor_threshold": profile.supervisor_check_minutes,
                "suggested_actions": [
                    "Provide status update",
                    "Request help or resources",
                    "Explain any blockers",
                    "Estimate completion time"
                ]
            }
        )
        
        self._escalation_history.append(event)
        return event
    
    async def _create_contract_enforcement_event(
        self, 
        task: TaskContext, 
        profile: TaskTimeoutProfile
    ) -> Optional[EscalationEvent]:
        """Create contract enforcement event."""
        
        contract = profile.contract
        if not contract or not contract.verified:
            return None
        
        time_until_deadline = (contract.promised_completion - datetime.now()).total_seconds() / 60
        
        if time_until_deadline <= profile.contract_warning_minutes:
            message = (
                f"CONTRACT ENFORCEMENT: Task {task.task_id} has a verified contract "
                f"(ID: {contract.contract_id}) with deadline in {time_until_deadline:.1f} minutes. "
                f"Client {contract.client_id} expects delivery. Immediate action required."
            )
            
            event = EscalationEvent(
                task_id=task.task_id,
                escalation_level=EscalationLevel.SEND_COPS,
                intervention_type=InterventionType.CONTRACT_WARNING,
                message=message,
                callback_url=profile.callback_urls.get(EscalationLevel.SEND_COPS),
                requires_response=True,
                response_deadline=contract.promised_completion,
                escalation_data={
                    "contract_id": contract.contract_id,
                    "client_id": contract.client_id,
                    "contractor_id": contract.contractor_id,
                    "deadline": contract.promised_completion.isoformat(),
                    "time_remaining_minutes": time_until_deadline,
                    "penalty_clause": contract.penalty_clause,
                    "max_extension_minutes": contract.max_extension_minutes,
                    "suggested_actions": [
                        "Complete task immediately",
                        "Request contract extension",
                        "Escalate to contract manager",
                        "Prepare delivery status report"
                    ]
                }
            )
            
            self._escalation_history.append(event)
            return event
        
        return None
    
    async def _create_reaper_event(
        self, 
        task: TaskContext, 
        profile: TaskTimeoutProfile, 
        execution_time: float
    ) -> Optional[EscalationEvent]:
        """Create reaper (hard termination) event."""
        
        # The Reaper is final - only create once
        if self._has_escalation(task.task_id, EscalationLevel.THE_REAPER):
            return None
        
        message = (
            f"UNIVERSAL TIMEOUT REACHED: Task {task.task_id} has exceeded maximum "
            f"execution time ({execution_time:.1f} minutes > {profile.hard_timeout_minutes} minutes). "
            f"Initiating hard termination sequence. This is non-negotiable. "
            f"Task will be killed in {profile.kill_signal_delay_seconds} seconds."
        )
        
        event = EscalationEvent(
            task_id=task.task_id,
            escalation_level=EscalationLevel.THE_REAPER,
            intervention_type=InterventionType.HARD_TERMINATION,
            message=message,
            callback_url=profile.callback_urls.get(EscalationLevel.THE_REAPER),
            requires_response=False,  # No negotiation at this level
            escalation_data={
                "execution_time_minutes": execution_time,
                "hard_timeout_minutes": profile.hard_timeout_minutes,
                "kill_delay_seconds": profile.kill_signal_delay_seconds,
                "termination_reason": "Universal timeout exceeded",
                "final_warning": True,
                "actions": [
                    f"Task will be terminated in {profile.kill_signal_delay_seconds} seconds",
                    "No extensions available",
                    "Cleanup procedures initiated",
                    "Incident report will be generated"
                ]
            }
        )
        
        self._escalation_history.append(event)
        
        # Schedule the actual termination
        asyncio.create_task(
            self._schedule_task_termination(task.task_id, profile.kill_signal_delay_seconds)
        )
        
        return event
    
    async def _schedule_task_termination(self, task_id: str, delay_seconds: int):
        """Schedule hard termination of a task."""
        await asyncio.sleep(delay_seconds)
        
        self._logger.critical(
            f"REAPER: Executing hard termination of task {task_id}",
            extra={"task_id": task_id, "termination_type": "hard_timeout"}
        )
        
        # In a real implementation, this would:
        # 1. Send kill signal to task process
        # 2. Clean up resources
        # 3. Update task state to CANCELLED
        # 4. Generate incident report
        # 5. Notify stakeholders
        
        # For now, we'll just log the termination
        termination_event = EscalationEvent(
            task_id=task_id,
            escalation_level=EscalationLevel.THE_REAPER,
            intervention_type=InterventionType.HARD_TERMINATION,
            message=f"Task {task_id} has been terminated by the Reaper (kill -9)",
            escalation_data={
                "termination_executed": True,
                "termination_time": datetime.now().isoformat(),
                "method": "hard_kill"
            }
        )
        
        self._escalation_history.append(termination_event)
    
    def _get_execution_time_minutes(self, task: TaskContext) -> float:
        """Get task execution time in minutes."""
        if not task.execution_start:
            return 0.0
        
        end_time = task.execution_end or datetime.now()
        return (end_time - task.execution_start).total_seconds() / 60
    
    def _get_total_age_minutes(self, task: TaskContext) -> float:
        """Get total task age in minutes."""
        return (datetime.now() - task.created_at).total_seconds() / 60
    
    def _is_contract_deadline_approaching(self, contract: TimeoutContract, now: datetime) -> bool:
        """Check if contract deadline is approaching."""
        if not contract.verified:
            return False
        
        time_until_deadline = (contract.promised_completion - now).total_seconds() / 60
        return time_until_deadline <= 5  # 5 minutes warning
    
    def _has_recent_escalation(self, task_id: str, level: EscalationLevel, minutes: int) -> bool:
        """Check if there's been a recent escalation of this level."""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        
        for event in reversed(self._escalation_history):
            if (event.task_id == task_id and 
                event.escalation_level == level and 
                event.triggered_at > cutoff):
                return True
        
        return False
    
    def _has_escalation(self, task_id: str, level: EscalationLevel) -> bool:
        """Check if there's been any escalation of this level."""
        for event in self._escalation_history:
            if event.task_id == task_id and event.escalation_level == level:
                return True
        return False
    
    def _count_escalations(self, task_id: str, level: EscalationLevel) -> int:
        """Count escalations of a specific level for a task."""
        count = 0
        for event in self._escalation_history:
            if event.task_id == task_id and event.escalation_level == level:
                count += 1
        return count
    
    def _setup_default_handlers(self):
        """Setup default callback handlers for each escalation level."""
        self._callback_handlers = {
            EscalationLevel.PERSONAL_ALARM: self._handle_personal_alarm,
            EscalationLevel.FAMILY_CHECK: self._handle_family_check,
            EscalationLevel.SEND_COPS: self._handle_contract_enforcement,
            EscalationLevel.THE_REAPER: self._handle_reaper_termination
        }
    
    async def _handle_personal_alarm(self, event: EscalationEvent):
        """Handle personal alarm clock escalation."""
        self._logger.info(f"Personal alarm: {event.message}")
    
    async def _handle_family_check(self, event: EscalationEvent):
        """Handle family check (supervisor) escalation."""
        self._logger.warning(f"Supervisor intervention: {event.message}")
    
    async def _handle_contract_enforcement(self, event: EscalationEvent):
        """Handle contract enforcement escalation."""
        self._logger.error(f"Contract enforcement: {event.message}")
    
    async def _handle_reaper_termination(self, event: EscalationEvent):
        """Handle reaper (hard termination) escalation."""
        self._logger.critical(f"Reaper termination: {event.message}")
    
    def get_escalation_history(self, task_id: str = None) -> List[EscalationEvent]:
        """Get escalation history for a task or all tasks."""
        if task_id:
            return [event for event in self._escalation_history if event.task_id == task_id]
        return self._escalation_history.copy()
    
    def create_timeout_contract(
        self, 
        task_id: str, 
        contractor_id: str, 
        client_id: str, 
        promised_completion: datetime,
        signature_hash: str = ""
    ) -> TimeoutContract:
        """Create a verified timeout contract for a task."""
        contract = TimeoutContract(
            contract_id=str(uuid.uuid4()),
            task_id=task_id,
            contractor_id=contractor_id,
            client_id=client_id,
            promised_completion=promised_completion,
            signature_hash=signature_hash,
            verified=bool(signature_hash)  # Verified if signature provided
        )
        
        self._logger.info(
            f"Created timeout contract {contract.contract_id} for task {task_id}",
            extra={
                "contract_id": contract.contract_id,
                "task_id": task_id,
                "deadline": promised_completion.isoformat(),
                "verified": contract.verified
            }
        )
        
        return contract