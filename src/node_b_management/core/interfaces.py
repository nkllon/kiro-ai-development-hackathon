"""
Core Interfaces for Node B Management System

Defines the fundamental interfaces that all Node B management components must implement.
These interfaces ensure consistent behavior across all Node B instances and provide
clear contracts for lifecycle management, health monitoring, and network communication.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass
import os


class NodeState(Enum):
    """Node B operational states"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    FAILED = "failed"
    RESTARTING = "restarting"


@dataclass
class HealthMetrics:
    """Comprehensive health metrics for a Node B instance"""
    redis_connectivity: bool
    message_processing_rate: float
    response_time_avg: float
    memory_usage_mb: float
    cpu_usage_percent: float
    network_status: str
    last_heartbeat: str
    error_count: int = 0
    warning_count: int = 0
    uptime_seconds: float = 0.0


@dataclass
class NetworkMessage:
    """Structured network message for Node B communication"""
    message_id: str
    sender_id: str
    recipient_id: Optional[str]
    message_type: str
    payload: Dict[str, Any]
    timestamp: str
    correlation_id: str
    retry_count: int = 0
    priority: int = 0


class INodeLifecycle(ABC):
    """
    Interface for Node B lifecycle management
    
    Handles the complete lifecycle of Node B instances including startup,
    shutdown, restart, and state management with proper Redis coordination.
    """

    @abstractmethod
    async def start_node(self, node_id: str, config: Dict[str, Any]) -> bool:
        """
        Start a Node B instance with given configuration
        
        Args:
            node_id: Unique identifier for the node
            config: Configuration dictionary containing node settings
            
        Returns:
            bool: True if node started successfully, False otherwise
            
        Requirements: 1.1, 1.2, 1.3
        """
        pass

    @abstractmethod
    async def stop_node(self, node_id: str, graceful: bool = True) -> bool:
        """
        Stop a Node B instance gracefully or forcefully
        
        Args:
            node_id: Unique identifier for the node
            graceful: Whether to perform graceful shutdown
            
        Returns:
            bool: True if node stopped successfully, False otherwise
            
        Requirements: 1.4
        """
        pass

    @abstractmethod
    async def restart_node(self, node_id: str) -> bool:
        """
        Restart a Node B instance with exponential backoff
        
        Args:
            node_id: Unique identifier for the node
            
        Returns:
            bool: True if node restarted successfully, False otherwise
            
        Requirements: 1.5
        """
        pass

    @abstractmethod
    async def get_node_state(self, node_id: str) -> NodeState:
        """
        Get current state of a Node B instance
        
        Args:
            node_id: Unique identifier for the node
            
        Returns:
            NodeState: Current operational state of the node
            
        Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
        """
        pass

    @abstractmethod
    async def validate_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Validate Node B configuration before deployment
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            bool: True if configuration is valid, False otherwise
            
        Requirements: 1.6, 1.7
        """
        pass


class IHealthMonitoring(ABC):
    """
    Interface for Node B health monitoring and diagnostics
    
    Provides comprehensive health monitoring capabilities including Redis
    connectivity, performance metrics, and diagnostic reporting.
    """

    @abstractmethod
    async def get_health_status(self, node_id: str) -> HealthMetrics:
        """
        Get comprehensive health metrics for a node
        
        Args:
            node_id: Unique identifier for the node
            
        Returns:
            HealthMetrics: Complete health status and metrics
            
        Requirements: 3.1, 3.2, 3.3, 3.6
        """
        pass

    @abstractmethod
    async def generate_diagnostic_report(self, node_id: str) -> Dict[str, Any]:
        """
        Generate detailed diagnostic information
        
        Args:
            node_id: Unique identifier for the node
            
        Returns:
            Dict[str, Any]: Comprehensive diagnostic report
            
        Requirements: 3.4, 3.5, 3.7
        """
        pass

    @abstractmethod
    async def check_redis_connectivity(self, node_id: str) -> bool:
        """
        Validate Redis connection health
        
        Args:
            node_id: Unique identifier for the node
            
        Returns:
            bool: True if Redis connection is healthy, False otherwise
            
        Requirements: 3.1, 3.2
        """
        pass

    @abstractmethod
    async def monitor_performance(self, node_id: str) -> Dict[str, float]:
        """
        Monitor performance metrics and resource utilization
        
        Args:
            node_id: Unique identifier for the node
            
        Returns:
            Dict[str, float]: Performance metrics including CPU, memory, network
            
        Requirements: 3.6, 3.7
        """
        pass


class INetworkCommunication(ABC):
    """
    Interface for Node B network communication and coordination
    
    Manages Redis pub/sub communication, message routing, and network
    topology adaptation for distributed Node B coordination.
    """

    @abstractmethod
    async def send_message(self, message: NetworkMessage) -> bool:
        """
        Send a message through the network
        
        Args:
            message: NetworkMessage to send
            
        Returns:
            bool: True if message sent successfully, False otherwise
            
        Requirements: 2.1, 2.2, 2.7
        """
        pass

    @abstractmethod
    async def receive_messages(self, node_id: str) -> List[NetworkMessage]:
        """
        Receive pending messages for a node
        
        Args:
            node_id: Unique identifier for the node
            
        Returns:
            List[NetworkMessage]: List of pending messages
            
        Requirements: 2.1, 2.2
        """
        pass

    @abstractmethod
    async def participate_in_consensus(self, node_id: str, proposal: Dict[str, Any]) -> bool:
        """
        Participate in network consensus decision
        
        Args:
            node_id: Unique identifier for the node
            proposal: Consensus proposal to vote on
            
        Returns:
            bool: True if participation successful, False otherwise
            
        Requirements: 2.4, 2.5
        """
        pass

    @abstractmethod
    async def handle_challenge_response(self, node_id: str, challenge: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle network challenge and provide response
        
        Args:
            node_id: Unique identifier for the node
            challenge: Challenge request from network
            
        Returns:
            Dict[str, Any]: Challenge response with capabilities and availability
            
        Requirements: 2.3
        """
        pass

    @abstractmethod
    async def adapt_to_topology_change(self, node_id: str, topology: Dict[str, Any]) -> bool:
        """
        Adapt communication patterns to network topology changes
        
        Args:
            node_id: Unique identifier for the node
            topology: New network topology information
            
        Returns:
            bool: True if adaptation successful, False otherwise
            
        Requirements: 2.6
        """
        pass


class ISecurityConfiguration(ABC):
    """
    Interface for Node B security and configuration management
    
    Handles secure credential management, SSL/TLS configuration,
    and security policy enforcement.
    """

    @abstractmethod
    async def load_credentials(self) -> Dict[str, str]:
        """
        Load credentials from environment variables
        
        Returns:
            Dict[str, str]: Loaded credentials
            
        Requirements: 4.1, 4.2
        """
        pass

    @abstractmethod
    async def validate_ssl_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate SSL/TLS configuration
        
        Args:
            config: SSL/TLS configuration to validate
            
        Returns:
            bool: True if configuration is valid, False otherwise
            
        Requirements: 4.2, 4.3
        """
        pass

    @abstractmethod
    async def enforce_security_policies(self, node_id: str) -> bool:
        """
        Enforce security policies and audit logging
        
        Args:
            node_id: Unique identifier for the node
            
        Returns:
            bool: True if policies enforced successfully, False otherwise
            
        Requirements: 4.4, 4.6, 4.7
        """
        pass

    @abstractmethod
    async def detect_security_violations(self, node_id: str) -> List[Dict[str, Any]]:
        """
        Detect security violations and isolation requirements
        
        Args:
            node_id: Unique identifier for the node
            
        Returns:
            List[Dict[str, Any]]: List of detected security violations
            
        Requirements: 4.5, 4.6
        """
        pass


class IMultiInstanceCoordination(ABC):
    """
    Interface for multi-instance Node B coordination
    
    Manages coordination between multiple Node B instances including
    load balancing, failure detection, and consensus mechanisms.
    """

    @abstractmethod
    async def discover_instances(self) -> List[str]:
        """
        Discover other Node B instances in the network
        
        Returns:
            List[str]: List of discovered instance IDs
            
        Requirements: 5.1
        """
        pass

    @abstractmethod
    async def distribute_tasks(self, tasks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Distribute tasks among available instances
        
        Args:
            tasks: List of tasks to distribute
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Task distribution by instance ID
            
        Requirements: 5.2, 5.3
        """
        pass

    @abstractmethod
    async def detect_instance_failure(self, instance_id: str) -> bool:
        """
        Detect if an instance has failed
        
        Args:
            instance_id: ID of instance to check
            
        Returns:
            bool: True if instance has failed, False otherwise
            
        Requirements: 5.4
        """
        pass

    @abstractmethod
    async def resolve_coordination_conflict(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve coordination conflicts through consensus
        
        Args:
            conflict: Conflict description and context
            
        Returns:
            Dict[str, Any]: Conflict resolution result
            
        Requirements: 5.5, 5.7
        """
        pass

    @abstractmethod
    async def handle_network_partition(self, partition_info: Dict[str, Any]) -> bool:
        """
        Handle network partition scenarios gracefully
        
        Args:
            partition_info: Information about the network partition
            
        Returns:
            bool: True if partition handled successfully, False otherwise
            
        Requirements: 5.5
        """
        pass