"""
Node B Network Communication Components

Contains components for network communication, message routing,
and coordination between Node B instances.
"""

from .network_communication_coordinator import NetworkCommunicationCoordinator, MessageType, MessagePriority, NetworkTopology
from .network_topology_manager import NetworkTopologyManager, ConsensusState, CollaborationStatus, NodeCapabilities

__all__ = [
    'NetworkCommunicationCoordinator',
    'NetworkTopologyManager',
    'MessageType', 
    'MessagePriority',
    'NetworkTopology',
    'ConsensusState',
    'CollaborationStatus',
    'NodeCapabilities'
]