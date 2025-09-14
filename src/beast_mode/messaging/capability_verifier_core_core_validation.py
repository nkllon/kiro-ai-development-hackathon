"""
Capability Verifier Core Core Validation

This module was extracted from capability_verifier_core_core.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from .models import BeastModeMessage, MessageType, AgentCapabilities
from .agent_registry import AgentRegistry, DiscoveredAgent
from .help_system import HelpWantedSystem, CollaborationSession, CollaborationStatus
from src.rm_ddd.core.health import ModuleHealth


def create_capability_test(self, agent_id: str, capability: str, test_type: str='interaction', test_description: str='', timeout_minutes: int=30, success_criteria: Optional[Dict[str, Any]]=None) -> CapabilityTest:
    """
        Create a new capability verification test.
        
        Args:
            agent_id: Agent to test
            capability: Capability to verify
            test_type: Type of test (interaction, collaboration, performance)
            test_description: Description of what the test validates
            timeout_minutes: Test timeout in minutes
            success_criteria: Criteria for test success
            
        Returns:
            CapabilityTest: The created test
        """
    test_id = str(uuid.uuid4())
    test = CapabilityTest(test_id=test_id, agent_id=agent_id, capability=capability, test_type=test_type, test_description=test_description or f'Verify {capability} capability for {agent_id}', timeout_minutes=timeout_minutes, success_criteria=success_criteria or {})
    self.capability_tests[test_id] = test
    self.stats['tests_created'] += 1
    logger.info(f'Created capability test {test_id} for {agent_id}:{capability}')
    return test

def start_capability_test(self, test_id: str) -> bool:
    """
        Start a capability verification test.
        
        Args:
            test_id: ID of the test to start
            
        Returns:
            bool: True if test was started successfully
        """
    if test_id not in self.capability_tests:
        return False
    test = self.capability_tests[test_id]
    if test.status != VerificationStatus.PENDING:
        logger.warning(f'Cannot start test {test_id} in status {test.status}')
        return False
    test.status = VerificationStatus.IN_PROGRESS
    test.started_at = datetime.now()
    logger.info(f'Started capability test {test_id} for {test.agent_id}:{test.capability}')
    return True

def complete_capability_test(self, test_id: str, success: bool, result_data: Optional[Dict[str, Any]]=None, performance_metrics: Optional[Dict[str, float]]=None, error_messages: Optional[List[str]]=None) -> bool:
    """
        Complete a capability verification test.
        
        Args:
            test_id: ID of the test to complete
            success: Whether the test passed
            result_data: Test result data
            performance_metrics: Performance measurements
            error_messages: Any error messages from the test
            
        Returns:
            bool: True if test was completed successfully
        """
    if test_id not in self.capability_tests:
        return False
    test = self.capability_tests[test_id]
    if test.status != VerificationStatus.IN_PROGRESS:
        logger.warning(f'Cannot complete test {test_id} in status {test.status}')
        return False
    test.status = VerificationStatus.PASSED if success else VerificationStatus.FAILED
    test.completed_at = datetime.now()
    test.result_data = result_data or {}
    test.performance_metrics = performance_metrics or {}
    test.error_messages = error_messages or []
    if success:
        test.success_score = 1.0
        if performance_metrics:
            response_time = performance_metrics.get('response_time', 0)
            if response_time > 0:
                time_penalty = max(0, min(0.3, (response_time - 5.0) / 20.0))
                test.success_score = max(0.7, 1.0 - time_penalty)
    else:
        test.success_score = 0.0
    self._update_trust_score_from_test(test)
    self.stats['tests_completed'] += 1
    if success:
        self.stats['tests_passed'] += 1
    else:
        self.stats['tests_failed'] += 1
    if test.started_at:
        duration = (test.completed_at - test.started_at).total_seconds()
        current_avg = self.stats['average_verification_time']
        total_tests = self.stats['tests_completed']
        self.stats['average_verification_time'] = (current_avg * (total_tests - 1) + duration) / total_tests
    logger.info(f'Completed capability test {test_id} (success: {success}, score: {test.success_score:.2f})')
    return True

def cleanup_expired_tests(self) -> int:
    """
        Clean up expired capability tests.
        
        Returns:
            int: Number of tests cleaned up
        """
    now = datetime.now()
    expired_tests = []
    for test_id, test in self.capability_tests.items():
        if test.status == VerificationStatus.IN_PROGRESS and test.started_at and (now - test.started_at > timedelta(minutes=test.timeout_minutes)):
            expired_tests.append(test_id)
    for test_id in expired_tests:
        test = self.capability_tests[test_id]
        test.status = VerificationStatus.EXPIRED
        test.completed_at = now
        test.error_messages.append('Test expired due to timeout')
        logger.info(f'Marked capability test {test_id} as expired')
    return len(expired_tests)

def _update_trust_score_from_test(self, test: CapabilityTest) -> None:
    """Update trust score based on verification test results"""
    trust_key = (test.agent_id, test.capability)
    if trust_key not in self.trust_scores:
        self.trust_scores[trust_key] = TrustScore(agent_id=test.agent_id, capability=test.capability)
    trust_score = self.trust_scores[trust_key]
    if test.status == VerificationStatus.PASSED:
        trust_score.verification_tests_passed += 1
    elif test.status == VerificationStatus.FAILED:
        trust_score.verification_tests_failed += 1
    trust_score.last_verification = test.completed_at
    self._calculate_trust_level(trust_score)
