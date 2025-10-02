"""
Node Lifecycle Manager

Implements comprehensive lifecycle management for Node B instances including
startup, shutdown, restart, and state management with Redis coordination.
"""

import os
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import signal
import psutil

from ..core.interfaces import INodeLifecycle, NodeState, NetworkMessage
from ..core.node_b_component import NodeBComponent


class RestartStrategy(Enum):
    """Restart strategy options"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    FIXED_DELAY = "fixed_delay"
    IMMEDIATE = "immediate"
    MANUAL = "manual"


class NodeLifecycleManager(NodeBComponent, INodeLifecycle):
    """
    Node B Lifecycle Manager
    
    Manages the complete lifecycle of Node B instances including startup,
    shutdown, restart, and state management with proper Redis coordination.
    
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7
    """

    def __init__(self, node_id: str = None):
        """
        Initialize Node Lifecycle Manager
        
        Args:
            node_id: Optional Node B instance ID
        """
        super().__init__("lifecycle_manager", node_id)
        
        # Node state management
        self._node_states: Dict[str, NodeState] = {}
        self._node_processes: Dict[str, Dict[str, Any]] = {}
        self._node_configs: Dict[str, Dict[str, Any]] = {}
        
        # Restart management
        self._restart_attempts: Dict[str, int] = {}
        self._restart_delays: Dict[str, float] = {}
        self._max_restart_attempts = 5
        self._base_restart_delay = 1.0
        self._max_restart_delay = 300.0  # 5 minutes
        
        # Shutdown management
        self._shutdown_timeout = 30.0  # 30 seconds
        self._graceful_shutdown_handlers: Dict[str, List[callable]] = {}
        
        # Network coordination
        self._network_channel = "node_b_lifecycle"
        self._coordination_lock_timeout = 60  # 1 minute
        
        self._logger.info(f"NodeLifecycleManager initialized for managing Node B instances")

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
        try:
            self._logger.info(f"Starting Node B instance: {node_id}")
            
            # Validate configuration first
            if not await self.validate_configuration(config):
                self._logger.error(f"Configuration validation failed for node {node_id}")
                return False
            
            # Check if node is already running
            current_state = await self.get_node_state(node_id)
            if current_state in [NodeState.RUNNING, NodeState.STARTING]:
                self._logger.warning(f"Node {node_id} is already {current_state.value}")
                return True
            
            # Set starting state
            self._node_states[node_id] = NodeState.STARTING
            self._node_configs[node_id] = config.copy()
            
            # Validate Redis connectivity before startup
            if not await self._validate_redis_connectivity():
                self._logger.error(f"Redis connectivity validation failed for node {node_id}")
                self._node_states[node_id] = NodeState.FAILED
                return False
            
            # Coordinate with other instances to avoid conflicts
            if not await self._coordinate_deployment(node_id, config):
                self._logger.error(f"Deployment coordination failed for node {node_id}")
                self._node_states[node_id] = NodeState.FAILED
                return False
            
            # Register node with network
            if not await self._register_with_network(node_id, config):
                self._logger.error(f"Network registration failed for node {node_id}")
                self._node_states[node_id] = NodeState.FAILED
                return False
            
            # Start the actual node process/service
            if not await self._start_node_process(node_id, config):
                self._logger.error(f"Node process startup failed for node {node_id}")
                self._node_states[node_id] = NodeState.FAILED
                return False
            
            # Set running state
            self._node_states[node_id] = NodeState.RUNNING
            self._restart_attempts[node_id] = 0  # Reset restart attempts on successful start
            
            # Announce startup to network
            await self._announce_node_startup(node_id, config)
            
            self.increment_message_count("processed")
            self._logger.info(f"Node B instance {node_id} started successfully")
            return True
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to start node {node_id}: {e}")
            self._node_states[node_id] = NodeState.FAILED
            return False

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
        try:
            self._logger.info(f"Stopping Node B instance: {node_id} (graceful={graceful})")
            
            # Check if node exists
            if node_id not in self._node_states:
                self._logger.warning(f"Node {node_id} not found in managed nodes")
                return True  # Consider it stopped if not managed
            
            current_state = self._node_states[node_id]
            if current_state in [NodeState.STOPPED, NodeState.STOPPING]:
                self._logger.info(f"Node {node_id} is already {current_state.value}")
                return True
            
            # Set stopping state
            self._node_states[node_id] = NodeState.STOPPING
            
            # Notify network about shutdown
            await self._announce_node_shutdown(node_id, graceful)
            
            if graceful:
                # Perform graceful shutdown
                success = await self._graceful_shutdown(node_id)
            else:
                # Perform forceful shutdown
                success = await self._forceful_shutdown(node_id)
            
            if success:
                self._node_states[node_id] = NodeState.STOPPED
                # Clean up node data
                self._cleanup_node_data(node_id)
                self._logger.info(f"Node B instance {node_id} stopped successfully")
            else:
                self._node_states[node_id] = NodeState.FAILED
                self._logger.error(f"Failed to stop node {node_id}")
            
            self.increment_message_count("processed")
            return success
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to stop node {node_id}: {e}")
            self._node_states[node_id] = NodeState.FAILED
            return False

    async def restart_node(self, node_id: str) -> bool:
        """
        Restart a Node B instance with exponential backoff
        
        Args:
            node_id: Unique identifier for the node
            
        Returns:
            bool: True if node restarted successfully, False otherwise
            
        Requirements: 1.5
        """
        try:
            self._logger.info(f"Restarting Node B instance: {node_id}")
            
            # Check restart attempts
            attempts = self._restart_attempts.get(node_id, 0)
            if attempts >= self._max_restart_attempts:
                self._logger.error(f"Maximum restart attempts ({self._max_restart_attempts}) reached for node {node_id}")
                self._node_states[node_id] = NodeState.FAILED
                return False
            
            # Increment restart attempts
            self._restart_attempts[node_id] = attempts + 1
            
            # Set restarting state
            self._node_states[node_id] = NodeState.RESTARTING
            
            # Calculate exponential backoff delay
            delay = min(
                self._base_restart_delay * (2 ** attempts),
                self._max_restart_delay
            )
            self._restart_delays[node_id] = delay
            
            self._logger.info(f"Restart attempt {attempts + 1} for node {node_id}, waiting {delay} seconds")
            await asyncio.sleep(delay)
            
            # Get node configuration
            config = self._node_configs.get(node_id, {})
            if not config:
                self._logger.error(f"No configuration found for node {node_id}")
                return False
            
            # Stop the node first (graceful)
            if not await self.stop_node(node_id, graceful=True):
                self._logger.warning(f"Graceful stop failed for node {node_id}, attempting forceful stop")
                await self.stop_node(node_id, graceful=False)
            
            # Wait a moment before starting
            await asyncio.sleep(1.0)
            
            # Start the node
            success = await self.start_node(node_id, config)
            
            if success:
                self._logger.info(f"Node B instance {node_id} restarted successfully after {attempts + 1} attempts")
                # Reset restart attempts on successful restart
                self._restart_attempts[node_id] = 0
            else:
                self._logger.error(f"Restart attempt {attempts + 1} failed for node {node_id}")
            
            self.increment_message_count("processed")
            return success
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to restart node {node_id}: {e}")
            self._node_states[node_id] = NodeState.FAILED
            return False

    async def get_node_state(self, node_id: str) -> NodeState:
        """
        Get current state of a Node B instance
        
        Args:
            node_id: Unique identifier for the node
            
        Returns:
            NodeState: Current operational state of the node
            
        Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
        """
        try:
            # Return cached state if available
            if node_id in self._node_states:
                state = self._node_states[node_id]
                
                # Validate state by checking actual process status
                if state == NodeState.RUNNING:
                    if not await self._verify_node_running(node_id):
                        self._logger.warning(f"Node {node_id} reported as running but process not found")
                        self._node_states[node_id] = NodeState.FAILED
                        return NodeState.FAILED
                
                return state
            
            # Node not found in managed nodes
            return NodeState.STOPPED
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to get state for node {node_id}: {e}")
            return NodeState.FAILED

    async def validate_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Validate Node B configuration before deployment
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            bool: True if configuration is valid, False otherwise
            
        Requirements: 1.6, 1.7
        """
        try:
            self._logger.debug("Validating Node B configuration")
            
            # Required configuration fields
            required_fields = [
                'node_id',
                'capabilities',
                'redis_config'
            ]
            
            # Check required fields
            for field in required_fields:
                if field not in config:
                    self._logger.error(f"Missing required configuration field: {field}")
                    return False
            
            # Validate node_id
            node_id = config.get('node_id')
            if not isinstance(node_id, str) or not node_id.strip():
                self._logger.error("Invalid node_id: must be non-empty string")
                return False
            
            # Validate capabilities
            capabilities = config.get('capabilities')
            if not isinstance(capabilities, list) or not capabilities:
                self._logger.error("Invalid capabilities: must be non-empty list")
                return False
            
            # Validate Redis configuration
            redis_config = config.get('redis_config', {})
            if not await self._validate_redis_config(redis_config):
                return False
            
            # Validate security configuration if present
            security_config = config.get('security_config', {})
            if security_config and not await self._validate_security_config(security_config):
                return False
            
            # Validate performance limits if present
            performance_limits = config.get('performance_limits', {})
            if performance_limits and not self._validate_performance_limits(performance_limits):
                return False
            
            # Check for deployment conflicts
            if not await self._check_deployment_conflicts(config):
                return False
            
            self._logger.info("Node B configuration validation passed")
            return True
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Configuration validation failed: {e}")
            return False

    async def get_managed_nodes(self) -> List[str]:
        """
        Get list of all managed Node B instances
        
        Returns:
            List[str]: List of managed node IDs
        """
        return list(self._node_states.keys())

    async def get_node_info(self, node_id: str) -> Dict[str, Any]:
        """
        Get comprehensive information about a Node B instance
        
        Args:
            node_id: Unique identifier for the node
            
        Returns:
            Dict[str, Any]: Node information including state, config, and metrics
        """
        try:
            if node_id not in self._node_states:
                return {"error": f"Node {node_id} not found"}
            
            state = await self.get_node_state(node_id)
            config = self._node_configs.get(node_id, {})
            process_info = self._node_processes.get(node_id, {})
            
            return {
                "node_id": node_id,
                "state": state.value,
                "config": config,
                "process_info": process_info,
                "restart_attempts": self._restart_attempts.get(node_id, 0),
                "last_restart_delay": self._restart_delays.get(node_id, 0),
                "managed_by": self.component_name,
                "manager_node_id": self.node_id
            }
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to get info for node {node_id}: {e}")
            return {"error": str(e)}

    # Private helper methods

    async def _validate_redis_connectivity(self) -> bool:
        """Validate Redis connectivity before node startup"""
        try:
            redis_manager = await self.get_redis_manager()
            return await redis_manager.test_connection()
        except Exception as e:
            self._logger.error(f"Redis connectivity validation failed: {e}")
            return False

    async def _coordinate_deployment(self, node_id: str, config: Dict[str, Any]) -> bool:
        """Coordinate with other instances to avoid deployment conflicts"""
        try:
            redis_manager = await self.get_redis_manager()
            
            # Use Redis lock to coordinate deployment
            lock_key = f"node_b_deployment_lock:{node_id}"
            
            async with redis_manager.get_connection_context() as redis_conn:
                # Try to acquire deployment lock
                lock_acquired = await redis_conn.set(
                    lock_key, 
                    self.node_id, 
                    nx=True, 
                    ex=self._coordination_lock_timeout
                )
                
                if not lock_acquired:
                    existing_manager = await redis_conn.get(lock_key)
                    self._logger.error(f"Deployment conflict: node {node_id} is being managed by {existing_manager}")
                    return False
                
                # Store deployment info
                deployment_info = {
                    "manager_id": self.node_id,
                    "node_id": node_id,
                    "timestamp": datetime.now().isoformat(),
                    "config_hash": hash(str(sorted(config.items())))
                }
                
                await redis_conn.hset(
                    f"node_b_deployments:{node_id}",
                    mapping=deployment_info
                )
                
                self._logger.info(f"Deployment coordination successful for node {node_id}")
                return True
                
        except Exception as e:
            self._logger.error(f"Deployment coordination failed for node {node_id}: {e}")
            return False

    async def _register_with_network(self, node_id: str, config: Dict[str, Any]) -> bool:
        """Register node with the Beast Mode network"""
        try:
            redis_manager = await self.get_redis_manager()
            
            registration_data = {
                "node_id": node_id,
                "capabilities": config.get('capabilities', []),
                "manager_id": self.node_id,
                "registered_at": datetime.now().isoformat(),
                "status": "starting"
            }
            
            # Publish registration message
            message = json.dumps(registration_data)
            success = await redis_manager.publish_message(
                f"{self._network_channel}:registration",
                message
            )
            
            if success:
                self._logger.info(f"Node {node_id} registered with network")
            else:
                self._logger.error(f"Failed to register node {node_id} with network")
            
            return success
            
        except Exception as e:
            self._logger.error(f"Network registration failed for node {node_id}: {e}")
            return False

    async def _start_node_process(self, node_id: str, config: Dict[str, Any]) -> bool:
        """Start the actual Node B process/service"""
        try:
            # This is a placeholder for actual node process startup
            # In a real implementation, this would start the Node B service
            
            process_info = {
                "started_at": datetime.now().isoformat(),
                "config": config,
                "status": "running"
            }
            
            self._node_processes[node_id] = process_info
            
            self._logger.info(f"Node B process started for {node_id}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to start node process for {node_id}: {e}")
            return False

    async def _announce_node_startup(self, node_id: str, config: Dict[str, Any]):
        """Announce node startup to the network"""
        try:
            redis_manager = await self.get_redis_manager()
            
            announcement = {
                "event": "node_startup",
                "node_id": node_id,
                "manager_id": self.node_id,
                "capabilities": config.get('capabilities', []),
                "timestamp": datetime.now().isoformat()
            }
            
            await redis_manager.publish_message(
                f"{self._network_channel}:events",
                json.dumps(announcement)
            )
            
            self.increment_network_events()
            
        except Exception as e:
            self._logger.error(f"Failed to announce startup for node {node_id}: {e}")

    async def _announce_node_shutdown(self, node_id: str, graceful: bool):
        """Announce node shutdown to the network"""
        try:
            redis_manager = await self.get_redis_manager()
            
            announcement = {
                "event": "node_shutdown",
                "node_id": node_id,
                "manager_id": self.node_id,
                "graceful": graceful,
                "timestamp": datetime.now().isoformat()
            }
            
            await redis_manager.publish_message(
                f"{self._network_channel}:events",
                json.dumps(announcement)
            )
            
            self.increment_network_events()
            
        except Exception as e:
            self._logger.error(f"Failed to announce shutdown for node {node_id}: {e}")

    async def _graceful_shutdown(self, node_id: str) -> bool:
        """Perform graceful shutdown of a node"""
        try:
            # Execute graceful shutdown handlers
            handlers = self._graceful_shutdown_handlers.get(node_id, [])
            for handler in handlers:
                try:
                    await handler(node_id)
                except Exception as e:
                    self._logger.warning(f"Graceful shutdown handler failed for node {node_id}: {e}")
            
            # Wait for graceful shutdown timeout
            await asyncio.sleep(min(self._shutdown_timeout, 10.0))
            
            # Clean up process
            if node_id in self._node_processes:
                del self._node_processes[node_id]
            
            return True
            
        except Exception as e:
            self._logger.error(f"Graceful shutdown failed for node {node_id}: {e}")
            return False

    async def _forceful_shutdown(self, node_id: str) -> bool:
        """Perform forceful shutdown of a node"""
        try:
            # Force terminate process
            if node_id in self._node_processes:
                del self._node_processes[node_id]
            
            self._logger.warning(f"Forceful shutdown completed for node {node_id}")
            return True
            
        except Exception as e:
            self._logger.error(f"Forceful shutdown failed for node {node_id}: {e}")
            return False

    def _cleanup_node_data(self, node_id: str):
        """Clean up node data after shutdown"""
        # Remove from tracking dictionaries
        self._node_processes.pop(node_id, None)
        # Keep config and state for potential restart
        
        self._logger.debug(f"Cleaned up data for node {node_id}")

    async def _verify_node_running(self, node_id: str) -> bool:
        """Verify that a node is actually running"""
        try:
            # Check if process info exists
            if node_id not in self._node_processes:
                return False
            
            process_info = self._node_processes[node_id]
            return process_info.get("status") == "running"
            
        except Exception as e:
            self._logger.error(f"Failed to verify node {node_id} status: {e}")
            return False

    async def _validate_redis_config(self, redis_config: Dict[str, Any]) -> bool:
        """Validate Redis configuration"""
        try:
            # Basic validation - more comprehensive validation would be in RedisConnectionManager
            required_fields = ['host', 'port']
            
            for field in required_fields:
                if field not in redis_config:
                    self._logger.error(f"Missing Redis config field: {field}")
                    return False
            
            return True
            
        except Exception as e:
            self._logger.error(f"Redis config validation failed: {e}")
            return False

    async def _validate_security_config(self, security_config: Dict[str, Any]) -> bool:
        """Validate security configuration"""
        try:
            # Placeholder for security config validation
            return True
            
        except Exception as e:
            self._logger.error(f"Security config validation failed: {e}")
            return False

    def _validate_performance_limits(self, performance_limits: Dict[str, Any]) -> bool:
        """Validate performance limits configuration"""
        try:
            # Placeholder for performance limits validation
            return True
            
        except Exception as e:
            self._logger.error(f"Performance limits validation failed: {e}")
            return False

    async def _check_deployment_conflicts(self, config: Dict[str, Any]) -> bool:
        """Check for deployment conflicts with existing nodes"""
        try:
            node_id = config.get('node_id')
            
            # Check if node is already managed by another manager
            if node_id in self._node_states:
                current_state = self._node_states[node_id]
                if current_state in [NodeState.RUNNING, NodeState.STARTING]:
                    self._logger.error(f"Deployment conflict: node {node_id} is already {current_state.value}")
                    return False
            
            return True
            
        except Exception as e:
            self._logger.error(f"Deployment conflict check failed: {e}")
            return False