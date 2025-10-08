"""
System Architecture Models

Data models for system architecture discovery and analysis.
"""

from .tunnel_configuration import (
    TunnelIngressRule,
    DNSRouting,
    TunnelConfiguration,
    WebSocketConnectivityTest,
    TunnelPerformanceMetrics,
    TunnelCredentialInfo
)

from .sequence_models import (
    SequenceType,
    ParticipantType,
    MessageType,
    TimingType,
    SequenceParticipant,
    SequenceMessage,
    SequenceActivation,
    TunnelStartSequence,
    TunnelStopSequence,
    DashboardLifecycleSequence,
    DashboardStatusSequence,
    EmergencyProtocolSequence,
    ObservatorySequenceCollection
)

__all__ = [
    "TunnelIngressRule",
    "DNSRouting", 
    "TunnelConfiguration",
    "WebSocketConnectivityTest",
    "TunnelPerformanceMetrics",
    "TunnelCredentialInfo",
    "SequenceType",
    "ParticipantType",
    "MessageType",
    "TimingType",
    "SequenceParticipant",
    "SequenceMessage",
    "SequenceActivation",
    "TunnelStartSequence",
    "TunnelStopSequence",
    "DashboardLifecycleSequence",
    "DashboardStatusSequence",
    "EmergencyProtocolSequence",
    "ObservatorySequenceCollection"
]