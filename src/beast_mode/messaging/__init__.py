"""
Beast Mode Messaging Module

Provides Redis-based pub/sub messaging infrastructure for agent collaboration.
"""

from .models import BeastModeMessage, MessageType, AgentCapabilities
from .bus_client import BeastModeBusClient
from .pubsub import PubSubManager, MessageHandler
from .agent_registry import AgentRegistry, DiscoveredAgent
from .capability_verifier import (
    CapabilityVerifier, CapabilityTest, TrustScore, CapabilityRecommendation,
    VerificationStatus, TrustLevel
)
from .mailbox_logger import MailboxLogger, MailboxLoggerManager
from .spore_manager import SporeManager
from .help_system import HelpWantedSystem, HelpRequest, HelpResponse, HelpUrgency, CollaborationStatus
from .message_history import MessageHistoryManager
from .collaboration_scheduler import CollaborationScheduler

__all__ = [
    'BeastModeMessage',
    'MessageType', 
    'AgentCapabilities',
    'BeastModeBusClient',
    'PubSubManager',
    'MessageHandler',
    'AgentRegistry',
    'DiscoveredAgent',
    'CapabilityVerifier',
    'CapabilityTest',
    'TrustScore',
    'CapabilityRecommendation',
    'VerificationStatus',
    'TrustLevel',
    'MailboxLogger',
    'MailboxLoggerManager',
    'SporeManager',
    'HelpWantedSystem',
    'HelpRequest',
    'HelpResponse',
    'HelpUrgency',
    'CollaborationStatus',
    'MessageHistoryManager',
    'CollaborationScheduler'
]