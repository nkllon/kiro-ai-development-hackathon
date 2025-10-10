"""
Unit tests for timeout escalation system

Tests the "alarm clock → family → cops → reaper" escalation model
for handling stuck tasks with graduated responses.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from src.beast_mode.task_queue.models import TaskContext, TaskState
from src.beast_mode.task_queue.timeout_escalation import (
    TaskTimeoutEscalationManager,
    TaskTimeoutProfile,
    TimeoutContract,
    EscalationLevel,
    InterventionType,
    EscalationEvent,
)


class TestTaskTimeoutEscalationManager:
    """Test suite for TaskTimeoutEscalationManager."""
    
    @pytest.fixture
    def escalation_manager(self):
        """Create TaskTimeoutEscalationManager instance."""
        return TaskTimeoutEscalationManager()
    
    @pytest.fixture
    def basic_timeout_profile(self):
        """Create basic timeout profile."""
        return TaskTimeoutProfile(
            task_id="test-task-001",
            self_timeout_minutes=10,
            supervisor_check_minutes=15,
            hard_timeout_minutes=30,
            callback_urls={
                EscalationLevel.PERSONAL_ALARM: "http://localhost/personal",
                EscalationLevel.FAMILY_CHECK: "http://localhost/supervisor",
                EscalationLevel.THE_REAPER: "http://localhost/reaper"
            }
        )
    
    @pytest.fixture
    def contract_timeout_profile(self):
        """Create timeout profile with contract."""
        contract = TimeoutContract(
            contract_id="contract-001",
            task_id="contract-task-001",
            contractor_id="agent-123",
            client_id="client-456",
            promised_completion=datetime.now() + timedelta(minutes=20),
            signature_hash="abc123def456",
            verified=True
        )
        
        return TaskTimeoutProfile(
            task_id="contract-task-001",
            self_timeout_minutes=5,
            supervisor_check_minutes=10,
            contract=contract,
            contract_warning_minutes=5,
            hard_timeout_minutes=25
        )
    
    @pytest.fixture
    def running_task(self):
        """Create a task that's currently executing."""
        return TaskContext(
            task_id="test-task-001",
            task_type="code_generation",
            task_content="Generate complex algorithm",
            created_at=datetime.now() - timedelta(minutes=20),
            execution_start=datetime.now() - timedelta(minutes=12),
            task_state=TaskState.EXECUTING
        )
    
    @pytest.fixture
    def contract_task(self):
        """Create a task with contract obligations."""
        return TaskContext(
            task_id="contract-task-001",
            task_type="urgent_delivery",
            task_content="Complete contracted work",
            created_at=datetime.now() - timedelta(minutes=15),
            execution_start=datetime.now() - timedelta(minutes=8),
            task_state=TaskState.EXECUTING
        )
    
    def test_register_timeout_profile(self, escalation_manager, basic_timeout_profile):
        """Test registering a timeout profile."""
        escalation_manager.register_task_timeout_profile(basic_timeout_profile)
        
        assert basic_timeout_profile.task_id in escalation_manager._active_timeouts
        assert escalation_manager._active_timeouts[basic_timeout_profile.task_id] == basic_timeout_profile
    
    @pytest.mark.asyncio
    async def test_personal_alarm_escalation(self, escalation_manager, basic_timeout_profile, running_task):
        """Test Level 1: Personal alarm clock escalation."""
        # Task has been running for 12 minutes, threshold is 10 minutes
        escalation_manager.register_task_timeout_profile(basic_timeout_profile)
        
        events = await escalation_manager.check_task_timeouts(running_task)
        
        # Should trigger personal alarm
        personal_alarms = [e for e in events if e.escalation_level == EscalationLevel.PERSONAL_ALARM]
        assert len(personal_alarms) == 1
        
        alarm = personal_alarms[0]
        assert alarm.task_id == running_task.task_id
        assert alarm.intervention_type == InterventionType.GENTLE_REMINDER
        assert "Personal timeout alert" in alarm.message
        assert not alarm.requires_response
        assert "Check task progress" in alarm.escalation_data["suggested_actions"]
    
    @pytest.mark.asyncio
    async def test_family_check_escalation(self, escalation_manager, basic_timeout_profile, running_task):
        """Test Level 2: Family check (supervisor intervention) escalation."""
        # Task has been running for 12 minutes, supervisor threshold is 15 minutes
        # Let's make it run longer
        running_task.execution_start = datetime.now() - timedelta(minutes=18)
        
        escalation_manager.register_task_timeout_profile(basic_timeout_profile)
        
        events = await escalation_manager.check_task_timeouts(running_task)
        
        # Should trigger both personal alarm and family check
        family_checks = [e for e in events if e.escalation_level == EscalationLevel.FAMILY_CHECK]
        assert len(family_checks) == 1
        
        family_check = family_checks[0]
        assert family_check.task_id == running_task.task_id
        assert family_check.intervention_type == InterventionType.GENTLE_REMINDER
        assert "Hey, you've been at task" in family_check.message
        assert family_check.requires_response is True
        assert family_check.response_deadline is not None
    
    @pytest.mark.asyncio
    async def test_contract_enforcement_escalation(self, escalation_manager, contract_timeout_profile, contract_task):
        """Test Level 3: Contract enforcement escalation."""
        # Set contract deadline to be very soon
        contract_timeout_profile.contract.promised_completion = datetime.now() + timedelta(minutes=3)
        
        escalation_manager.register_task_timeout_profile(contract_timeout_profile)
        
        events = await escalation_manager.check_task_timeouts(contract_task)
        
        # Should trigger contract enforcement
        contract_events = [e for e in events if e.escalation_level == EscalationLevel.SEND_COPS]
        assert len(contract_events) == 1
        
        contract_event = contract_events[0]
        assert contract_event.task_id == contract_task.task_id
        assert contract_event.intervention_type == InterventionType.CONTRACT_WARNING
        assert "CONTRACT ENFORCEMENT" in contract_event.message
        assert contract_event.requires_response is True
        assert "contract_id" in contract_event.escalation_data
        assert "client_id" in contract_event.escalation_data
    
    @pytest.mark.asyncio
    async def test_reaper_escalation(self, escalation_manager, basic_timeout_profile, running_task):
        """Test Level 4: The Reaper (hard termination) escalation."""
        # Task has been running way too long
        running_task.execution_start = datetime.now() - timedelta(minutes=35)
        
        escalation_manager.register_task_timeout_profile(basic_timeout_profile)
        
        with patch.object(escalation_manager, '_schedule_task_termination') as mock_schedule:
            events = await escalation_manager.check_task_timeouts(running_task)
        
        # Should trigger reaper
        reaper_events = [e for e in events if e.escalation_level == EscalationLevel.THE_REAPER]
        assert len(reaper_events) == 1
        
        reaper_event = reaper_events[0]
        assert reaper_event.task_id == running_task.task_id
        assert reaper_event.intervention_type == InterventionType.HARD_TERMINATION
        assert "UNIVERSAL TIMEOUT REACHED" in reaper_event.message
        assert "kill -9" in reaper_event.message or "killed" in reaper_event.message
        assert reaper_event.requires_response is False  # No negotiation
        assert "final_warning" in reaper_event.escalation_data
        
        # Should schedule termination
        mock_schedule.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_escalation_deduplication(self, escalation_manager, basic_timeout_profile, running_task):
        """Test that escalations are not duplicated within time windows."""
        escalation_manager.register_task_timeout_profile(basic_timeout_profile)
        
        # First check - should generate events
        events1 = await escalation_manager.check_task_timeouts(running_task)
        personal_alarms1 = [e for e in events1 if e.escalation_level == EscalationLevel.PERSONAL_ALARM]
        assert len(personal_alarms1) == 1
        
        # Immediate second check - should not generate duplicate events
        events2 = await escalation_manager.check_task_timeouts(running_task)
        personal_alarms2 = [e for e in events2 if e.escalation_level == EscalationLevel.PERSONAL_ALARM]
        assert len(personal_alarms2) == 0  # No duplicates
    
    @pytest.mark.asyncio
    async def test_multiple_family_check_escalations(self, escalation_manager, basic_timeout_profile, running_task):
        """Test multiple family check escalations with increasing urgency."""
        # Task running long enough for supervisor checks
        running_task.execution_start = datetime.now() - timedelta(minutes=18)
        
        escalation_manager.register_task_timeout_profile(basic_timeout_profile)
        
        # First family check
        events1 = await escalation_manager.check_task_timeouts(running_task)
        family_checks1 = [e for e in events1 if e.escalation_level == EscalationLevel.FAMILY_CHECK]
        assert len(family_checks1) == 1
        assert family_checks1[0].intervention_type == InterventionType.GENTLE_REMINDER
        
        # Simulate time passing and second check (mock the recent escalation check)
        with patch.object(escalation_manager, '_has_recent_escalation', return_value=False):
            events2 = await escalation_manager.check_task_timeouts(running_task)
            family_checks2 = [e for e in events2 if e.escalation_level == EscalationLevel.FAMILY_CHECK]
            
            if family_checks2:  # Might escalate to progress check
                assert family_checks2[0].intervention_type in [InterventionType.GENTLE_REMINDER, InterventionType.PROGRESS_CHECK]
    
    @pytest.mark.asyncio
    async def test_contract_verification_requirement(self, escalation_manager, contract_timeout_profile, contract_task):
        """Test that contract enforcement requires verified contracts."""
        # Make contract unverified
        contract_timeout_profile.contract.verified = False
        contract_timeout_profile.contract.promised_completion = datetime.now() + timedelta(minutes=2)
        
        escalation_manager.register_task_timeout_profile(contract_timeout_profile)
        
        events = await escalation_manager.check_task_timeouts(contract_task)
        
        # Should NOT trigger contract enforcement for unverified contract
        contract_events = [e for e in events if e.escalation_level == EscalationLevel.SEND_COPS]
        assert len(contract_events) == 0
    
    @pytest.mark.asyncio
    async def test_reaper_termination_scheduling(self, escalation_manager):
        """Test that reaper schedules actual task termination."""
        task_id = "doomed-task"
        delay_seconds = 1  # Short delay for testing
        
        # Mock the termination to avoid actual delays
        with patch('asyncio.sleep') as mock_sleep:
            await escalation_manager._schedule_task_termination(task_id, delay_seconds)
        
        mock_sleep.assert_called_once_with(delay_seconds)
        
        # Check that termination event was logged
        history = escalation_manager.get_escalation_history(task_id)
        termination_events = [e for e in history if "terminated by the Reaper" in e.message]
        assert len(termination_events) == 1
        assert termination_events[0].escalation_data["termination_executed"] is True
    
    def test_create_timeout_contract(self, escalation_manager):
        """Test creating a verified timeout contract."""
        task_id = "contract-task"
        contractor_id = "agent-123"
        client_id = "client-456"
        deadline = datetime.now() + timedelta(hours=2)
        signature = "verified_signature_hash"
        
        contract = escalation_manager.create_timeout_contract(
            task_id, contractor_id, client_id, deadline, signature
        )
        
        assert contract.task_id == task_id
        assert contract.contractor_id == contractor_id
        assert contract.client_id == client_id
        assert contract.promised_completion == deadline
        assert contract.signature_hash == signature
        assert contract.verified is True  # Should be verified with signature
        assert contract.contract_id is not None
    
    def test_create_unverified_contract(self, escalation_manager):
        """Test creating an unverified timeout contract."""
        contract = escalation_manager.create_timeout_contract(
            "task", "agent", "client", datetime.now() + timedelta(hours=1)
            # No signature provided
        )
        
        assert contract.verified is False  # Should be unverified without signature
    
    def test_escalation_history_tracking(self, escalation_manager):
        """Test escalation history tracking and retrieval."""
        # Create some test events
        event1 = EscalationEvent(
            task_id="task-1",
            escalation_level=EscalationLevel.PERSONAL_ALARM,
            message="Test alarm"
        )
        event2 = EscalationEvent(
            task_id="task-2", 
            escalation_level=EscalationLevel.FAMILY_CHECK,
            message="Test family check"
        )
        
        escalation_manager._escalation_history.extend([event1, event2])
        
        # Test getting all history
        all_history = escalation_manager.get_escalation_history()
        assert len(all_history) == 2
        
        # Test getting task-specific history
        task1_history = escalation_manager.get_escalation_history("task-1")
        assert len(task1_history) == 1
        assert task1_history[0].task_id == "task-1"
    
    def test_escalation_counting(self, escalation_manager):
        """Test escalation counting functionality."""
        task_id = "test-task"
        
        # Add some escalation events
        for i in range(3):
            event = EscalationEvent(
                task_id=task_id,
                escalation_level=EscalationLevel.FAMILY_CHECK,
                message=f"Check {i}"
            )
            escalation_manager._escalation_history.append(event)
        
        # Test counting
        count = escalation_manager._count_escalations(task_id, EscalationLevel.FAMILY_CHECK)
        assert count == 3
        
        # Test counting different level
        count = escalation_manager._count_escalations(task_id, EscalationLevel.PERSONAL_ALARM)
        assert count == 0
    
    def test_recent_escalation_detection(self, escalation_manager):
        """Test recent escalation detection."""
        task_id = "test-task"
        
        # Add recent event
        recent_event = EscalationEvent(
            task_id=task_id,
            escalation_level=EscalationLevel.PERSONAL_ALARM,
            triggered_at=datetime.now() - timedelta(minutes=2)
        )
        escalation_manager._escalation_history.append(recent_event)
        
        # Should detect recent escalation
        has_recent = escalation_manager._has_recent_escalation(
            task_id, EscalationLevel.PERSONAL_ALARM, minutes=5
        )
        assert has_recent is True
        
        # Should not detect if looking for different level
        has_recent = escalation_manager._has_recent_escalation(
            task_id, EscalationLevel.FAMILY_CHECK, minutes=5
        )
        assert has_recent is False
    
    @pytest.mark.asyncio
    async def test_no_escalation_for_unregistered_task(self, escalation_manager, running_task):
        """Test that no escalations occur for unregistered tasks."""
        # Don't register timeout profile
        
        events = await escalation_manager.check_task_timeouts(running_task)
        
        assert len(events) == 0
    
    @pytest.mark.asyncio
    async def test_callback_url_inclusion(self, escalation_manager, basic_timeout_profile, running_task):
        """Test that callback URLs are included in escalation events."""
        escalation_manager.register_task_timeout_profile(basic_timeout_profile)
        
        events = await escalation_manager.check_task_timeouts(running_task)
        
        personal_alarms = [e for e in events if e.escalation_level == EscalationLevel.PERSONAL_ALARM]
        assert len(personal_alarms) == 1
        assert personal_alarms[0].callback_url == "http://localhost/personal"


class TestTimeoutContract:
    """Test suite for TimeoutContract functionality."""
    
    def test_timeout_contract_creation(self):
        """Test creating a timeout contract."""
        contract = TimeoutContract(
            contract_id="test-contract",
            task_id="test-task",
            contractor_id="agent-123",
            client_id="client-456",
            promised_completion=datetime.now() + timedelta(hours=2),
            signature_hash="abc123",
            verified=True
        )
        
        assert contract.contract_id == "test-contract"
        assert contract.task_id == "test-task"
        assert contract.contractor_id == "agent-123"
        assert contract.client_id == "client-456"
        assert contract.verified is True
        assert contract.max_extension_minutes == 30  # Default value


class TestTaskTimeoutProfile:
    """Test suite for TaskTimeoutProfile functionality."""
    
    def test_timeout_profile_creation(self):
        """Test creating a timeout profile."""
        profile = TaskTimeoutProfile(
            task_id="test-task",
            self_timeout_minutes=15,
            supervisor_check_minutes=25,
            hard_timeout_minutes=60
        )
        
        assert profile.task_id == "test-task"
        assert profile.self_timeout_minutes == 15
        assert profile.supervisor_check_minutes == 25
        assert profile.hard_timeout_minutes == 60
        assert profile.gentle_reminder_count == 2  # Default value
    
    def test_timeout_profile_with_contract(self):
        """Test timeout profile with contract."""
        contract = TimeoutContract(
            contract_id="contract-1",
            task_id="task-1",
            contractor_id="agent",
            client_id="client",
            promised_completion=datetime.now() + timedelta(hours=1)
        )
        
        profile = TaskTimeoutProfile(
            task_id="task-1",
            contract=contract
        )
        
        assert profile.contract == contract
        assert profile.contract.task_id == "task-1"