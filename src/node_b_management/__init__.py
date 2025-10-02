"""
Node B Management System

Systematic lifecycle management, monitoring, and coordination for Node B instances
within the Beast Mode decentralized AI coordination network.
"""

__version__ = "1.0.0"
__author__ = "Beast Mode Framework"

from .core.interfaces import (
    INodeLifecycle,
    IHealthMonitoring, 
    INetworkCommunication,
    NodeState
)
from .core.node_b_component import NodeBComponent
from .core.redis_connection_manager import RedisConnectionManager

__all__ = [
    "INodeLifecycle",
    "IHealthMonitoring", 
    "INetworkCommunication",
    "NodeState",
    "NodeBComponent",
    "RedisConnectionManager"
]