"""
Network Communication Coordinator for Node B Management

Implements structured message processing, Redis pub/sub integration, message routing,
and delivery confirmation with retry logic for Node B network coordination.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum

from ..core.node_b_component import NodeBComponent
from ..core.interfaces import INetworkCommunication, NetworkMessage


class MessageType(Enum):
    """Network message types for Node B coordination"""
    HEARTBEAT = "heartbeat"
    CHALLENGE = "challenge"
    CHALLENGE_RESPONSE = "challenge_response"
    CONSENSUS_PROPOSAL = "consensus_proposal"
    CONSENSUS_VOTE = "consensus_vote"
    COLLABORATION_REQUEST = "collaboration_request"
    COLLABORATION_RESPONSE = "collaboration_response"
    TOPOLOGY_UPDATE = "topology_update"
    STATUS_UPDATE = "status_update"
    ERROR_REPORT = "error_report"


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class MessageDeliveryStatus:
    """Message delivery tracking information"""
    message_id: str
    status: str  # "pending", "delivered", "failed", "expired"
    attempts: int
    last_attempt: datetime
    next_retry: Optional[datetime]
    error_message: Optional[str] = None


@dataclass
class NetworkTopology:
    """Network topology information"""
    active_nodes: List[str]
    node_capabilities: Dict[str, List[str]]
    connection_matrix: Dict[str, List[str]]
    last_updated: datetime


class NetworkCommunicationCoordinator(NodeBComponent, INetworkCommunication):
    """
    Network Communication Coordinator for Node B instances
    
    Implements structured message processing with proper metadata, Redis pub/sub
    integration for network communication, message routing and delivery confirmation,
    and retry logic with exponential backoff for failed deliveries.
    
    Requirements: 2.1, 2.2, 2.7, 6.6
    """

    def __init__(self, node_id: str):
        """
        Initialize Network Communication Coordinator
        
        Args:
            node_id: Unique identifier for the Node B instance
        """
        super().__init__("network_communication", node_id)
        
        # Message processing state
        self._message_queue: List[NetworkMessage] = []
        self._outbound_queue: List[NetworkMessage] = []
        self._delivery_tracking: Dict[str, MessageDeliveryStatus] = {}
        
        # Network topology state
        self._network_topology: Optional[NetworkTopology] = None
        self._known_nodes: Set[str] = set()
        self._node_capabilities: Dict[str, List[str]] = {}
        
        # Redis pub/sub state
        self._pubsub = None
        self._subscribed_channels: Set[str] = set()
        self._message_handlers: Dict[str, callable] = {}
        
        # Configuration
        self._max_retry_attempts = 5
        self._base_retry_delay = 1.0  # seconds
        self._max_retry_delay = 60.0  # seconds
        self._message_ttl = 3600  # seconds
        self._heartbeat_interval = 30  # seconds
        
        # Processing state
        self._processing_active = False
        self._heartbeat_task = None
        
        # Setup message handlers
        self._setup_message_handlers()
        
        self._logger.info(f"NetworkCommunicationCoordinator initialized for node {node_id}")

    async def start_communication(self) -> bool:
        """
        Start network communication services
        
        Returns:
            bool: True if started successfully, False otherwise
            
        Requirements: 2.1, 2.2, 6.6
        """
        try:
            # Get Redis connection
            redis_manager = await self.get_redis_manager()
            
            # Setup pub/sub subscription
            await self._setup_pubsub_subscription()
            
            # Start message processing
            self._processing_active = True
            asyncio.create_task(self._process_message_queue())
            asyncio.create_task(self._process_outbound_queue())
            asyncio.create_task(self._cleanup_expired_messages())
            
            # Start heartbeat
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            
            # Announce node presence
            await self._announce_node_presence()
            
            self._logger.info("Network communication started successfully")
            return True
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to start network communication: {e}")
            return False

    async def stop_communication(self) -> bool:
        """
        Stop network communication services
        
        Returns:
            bool: True if stopped successfully, False otherwise
        """
        try:
            self._processing_active = False
            
            # Cancel heartbeat
            if self._heartbeat_task:
                self._heartbeat_task.cancel()
                try:
                    await self._heartbeat_task
                except asyncio.CancelledError:
                    pass
            
            # Announce node departure
            await self._announce_node_departure()
            
            # Close pub/sub
            if self._pubsub:
                await self._pubsub.unsubscribe()
                await self._pubsub.close()
                self._pubsub = None
            
            self._logger.info("Network communication stopped successfully")
            return True
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to stop network communication: {e}")
            return False

    async def send_message(self, message: NetworkMessage) -> bool:
        """
        Send a message through the network
        
        Args:
            message: NetworkMessage to send
            
        Returns:
            bool: True if message queued successfully, False otherwise
            
        Requirements: 2.1, 2.2, 2.7
        """
        try:
            # Validate message
            if not self._validate_message(message):
                self._logger.error(f"Invalid message format: {message.message_id}")
                return False
            
            # Add to outbound queue
            self._outbound_queue.append(message)
            
            # Track delivery
            self._delivery_tracking[message.message_id] = MessageDeliveryStatus(
                message_id=message.message_id,
                status="pending",
                attempts=0,
                last_attempt=datetime.now(),
                next_retry=datetime.now()
            )
            
            self.increment_message_count("sent")
            self._logger.debug(f"Message queued for delivery: {message.message_id}")
            return True
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to send message {message.message_id}: {e}")
            return False

    async def receive_messages(self, node_id: str) -> List[NetworkMessage]:
        """
        Receive pending messages for a node
        
        Args:
            node_id: Unique identifier for the node
            
        Returns:
            List[NetworkMessage]: List of pending messages
            
        Requirements: 2.1, 2.2
        """
        try:
            # Filter messages for this node
            node_messages = [
                msg for msg in self._message_queue
                if msg.recipient_id == node_id or msg.recipient_id is None
            ]
            
            # Remove processed messages from queue
            self._message_queue = [
                msg for msg in self._message_queue
                if msg not in node_messages
            ]
            
            self.increment_message_count("processed")
            self._logger.debug(f"Retrieved {len(node_messages)} messages for node {node_id}")
            return node_messages
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to receive messages for node {node_id}: {e}")
            return []

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
        try:
            # Create consensus vote message
            vote_message = NetworkMessage(
                message_id=str(uuid.uuid4()),
                sender_id=node_id,
                recipient_id=None,  # Broadcast
                message_type=MessageType.CONSENSUS_VOTE.value,
                payload={
                    "proposal_id": proposal.get("proposal_id"),
                    "vote": self._evaluate_consensus_proposal(proposal),
                    "node_capabilities": self._node_capabilities.get(node_id, []),
                    "timestamp": datetime.now().isoformat()
                },
                timestamp=datetime.now().isoformat(),
                correlation_id=proposal.get("correlation_id", str(uuid.uuid4())),
                priority=MessagePriority.HIGH.value
            )
            
            # Send vote
            success = await self.send_message(vote_message)
            
            if success:
                self._logger.info(f"Consensus vote sent for proposal {proposal.get('proposal_id')}")
            else:
                self._logger.error(f"Failed to send consensus vote for proposal {proposal.get('proposal_id')}")
            
            return success
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to participate in consensus: {e}")
            return False

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
        try:
            # Evaluate challenge
            response_data = {
                "challenge_id": challenge.get("challenge_id"),
                "node_id": node_id,
                "capabilities": self._node_capabilities.get(node_id, []),
                "availability": await self._assess_node_availability(node_id),
                "performance_metrics": await self._get_performance_metrics(),
                "response_timestamp": datetime.now().isoformat()
            }
            
            # Create response message
            response_message = NetworkMessage(
                message_id=str(uuid.uuid4()),
                sender_id=node_id,
                recipient_id=challenge.get("challenger_id"),
                message_type=MessageType.CHALLENGE_RESPONSE.value,
                payload=response_data,
                timestamp=datetime.now().isoformat(),
                correlation_id=challenge.get("correlation_id", str(uuid.uuid4())),
                priority=MessagePriority.HIGH.value
            )
            
            # Send response
            await self.send_message(response_message)
            
            self._logger.info(f"Challenge response sent for challenge {challenge.get('challenge_id')}")
            return response_data
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to handle challenge response: {e}")
            return {"error": str(e)}

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
        try:
            # Update network topology
            self._network_topology = NetworkTopology(
                active_nodes=topology.get("active_nodes", []),
                node_capabilities=topology.get("node_capabilities", {}),
                connection_matrix=topology.get("connection_matrix", {}),
                last_updated=datetime.now()
            )
            
            # Update known nodes
            self._known_nodes = set(self._network_topology.active_nodes)
            self._node_capabilities.update(self._network_topology.node_capabilities)
            
            # Adapt subscription channels
            await self._adapt_subscription_channels()
            
            # Update routing tables
            await self._update_routing_tables()
            
            self.increment_network_events()
            self._logger.info(f"Adapted to topology change: {len(self._known_nodes)} active nodes")
            return True
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to adapt to topology change: {e}")
            return False

    async def _setup_pubsub_subscription(self):
        """Setup Redis pub/sub subscription for network communication"""
        try:
            redis_manager = await self.get_redis_manager()
            connection = await redis_manager.get_connection()
            
            self._pubsub = connection.pubsub()
            
            # Subscribe to node-specific channel
            node_channel = f"node_b_{self.node_id}"
            await self._pubsub.subscribe(node_channel)
            self._subscribed_channels.add(node_channel)
            
            # Subscribe to broadcast channel
            broadcast_channel = "node_b_broadcast"
            await self._pubsub.subscribe(broadcast_channel)
            self._subscribed_channels.add(broadcast_channel)
            
            # Start message listener
            asyncio.create_task(self._pubsub_message_listener())
            
            self._logger.info(f"Subscribed to channels: {self._subscribed_channels}")
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to setup pub/sub subscription: {e}")
            raise

    async def _pubsub_message_listener(self):
        """Listen for pub/sub messages and process them"""
        try:
            async for message in self._pubsub.listen():
                if message['type'] == 'message':
                    await self._handle_pubsub_message(message)
                    
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Pub/sub message listener error: {e}")

    async def _handle_pubsub_message(self, redis_message: Dict[str, Any]):
        """Handle incoming pub/sub message"""
        try:
            # Parse message data
            message_data = json.loads(redis_message['data'])
            
            # Create NetworkMessage object
            network_message = NetworkMessage(
                message_id=message_data['message_id'],
                sender_id=message_data['sender_id'],
                recipient_id=message_data.get('recipient_id'),
                message_type=message_data['message_type'],
                payload=message_data['payload'],
                timestamp=message_data['timestamp'],
                correlation_id=message_data['correlation_id'],
                retry_count=message_data.get('retry_count', 0),
                priority=message_data.get('priority', 0)
            )
            
            # Add to message queue
            self._message_queue.append(network_message)
            
            # Handle message based on type
            handler = self._message_handlers.get(network_message.message_type)
            if handler:
                await handler(network_message)
            
            self.increment_message_count("processed")
            self._logger.debug(f"Processed pub/sub message: {network_message.message_id}")
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to handle pub/sub message: {e}")

    async def _process_outbound_queue(self):
        """Process outbound message queue with retry logic"""
        while self._processing_active:
            try:
                if self._outbound_queue:
                    message = self._outbound_queue.pop(0)
                    await self._deliver_message(message)
                else:
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                self._increment_error_count()
                self._logger.error(f"Error processing outbound queue: {e}")
                await asyncio.sleep(1.0)

    async def _deliver_message(self, message: NetworkMessage):
        """Deliver message with retry logic and exponential backoff"""
        try:
            delivery_status = self._delivery_tracking.get(message.message_id)
            if not delivery_status:
                return
            
            # Check if retry is needed
            if delivery_status.next_retry and datetime.now() < delivery_status.next_retry:
                # Re-queue for later
                self._outbound_queue.append(message)
                return
            
            # Attempt delivery
            delivery_status.attempts += 1
            delivery_status.last_attempt = datetime.now()
            
            # Determine target channel
            if message.recipient_id:
                channel = f"node_b_{message.recipient_id}"
            else:
                channel = "node_b_broadcast"
            
            # Serialize message
            message_data = {
                "message_id": message.message_id,
                "sender_id": message.sender_id,
                "recipient_id": message.recipient_id,
                "message_type": message.message_type,
                "payload": message.payload,
                "timestamp": message.timestamp,
                "correlation_id": message.correlation_id,
                "retry_count": message.retry_count,
                "priority": message.priority
            }
            
            # Publish message
            redis_manager = await self.get_redis_manager()
            success = await redis_manager.publish_message(channel, json.dumps(message_data))
            
            if success:
                delivery_status.status = "delivered"
                self._logger.debug(f"Message delivered: {message.message_id}")
            else:
                await self._handle_delivery_failure(message, delivery_status, "Redis publish failed")
                
        except Exception as e:
            delivery_status = self._delivery_tracking.get(message.message_id)
            if delivery_status:
                await self._handle_delivery_failure(message, delivery_status, str(e))

    async def _handle_delivery_failure(self, message: NetworkMessage, delivery_status: MessageDeliveryStatus, error: str):
        """Handle message delivery failure with exponential backoff"""
        delivery_status.error_message = error
        
        if delivery_status.attempts >= self._max_retry_attempts:
            delivery_status.status = "failed"
            self._logger.error(f"Message delivery failed permanently: {message.message_id} - {error}")
        else:
            # Calculate next retry time with exponential backoff
            delay = min(
                self._base_retry_delay * (2 ** delivery_status.attempts),
                self._max_retry_delay
            )
            delivery_status.next_retry = datetime.now() + timedelta(seconds=delay)
            delivery_status.status = "pending"
            
            # Re-queue message
            message.retry_count += 1
            self._outbound_queue.append(message)
            
            self._logger.warning(f"Message delivery failed, retrying in {delay}s: {message.message_id} - {error}")

    async def _process_message_queue(self):
        """Process incoming message queue"""
        while self._processing_active:
            try:
                # Process messages based on priority
                if self._message_queue:
                    # Sort by priority (higher priority first)
                    self._message_queue.sort(key=lambda m: m.priority, reverse=True)
                    
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self._increment_error_count()
                self._logger.error(f"Error processing message queue: {e}")
                await asyncio.sleep(1.0)

    async def _cleanup_expired_messages(self):
        """Clean up expired messages and delivery tracking"""
        while self._processing_active:
            try:
                current_time = datetime.now()
                expired_threshold = current_time - timedelta(seconds=self._message_ttl)
                
                # Clean up expired delivery tracking
                expired_deliveries = [
                    msg_id for msg_id, status in self._delivery_tracking.items()
                    if status.last_attempt < expired_threshold
                ]
                
                for msg_id in expired_deliveries:
                    del self._delivery_tracking[msg_id]
                
                if expired_deliveries:
                    self._logger.debug(f"Cleaned up {len(expired_deliveries)} expired delivery records")
                
                await asyncio.sleep(300)  # Clean up every 5 minutes
                
            except Exception as e:
                self._increment_error_count()
                self._logger.error(f"Error cleaning up expired messages: {e}")
                await asyncio.sleep(60)

    async def _heartbeat_loop(self):
        """Send periodic heartbeat messages"""
        while self._processing_active:
            try:
                heartbeat_message = NetworkMessage(
                    message_id=str(uuid.uuid4()),
                    sender_id=self.node_id,
                    recipient_id=None,  # Broadcast
                    message_type=MessageType.HEARTBEAT.value,
                    payload={
                        "node_id": self.node_id,
                        "timestamp": datetime.now().isoformat(),
                        "capabilities": self._node_capabilities.get(self.node_id, []),
                        "status": "active"
                    },
                    timestamp=datetime.now().isoformat(),
                    correlation_id=str(uuid.uuid4()),
                    priority=MessagePriority.LOW.value
                )
                
                await self.send_message(heartbeat_message)
                await asyncio.sleep(self._heartbeat_interval)
                
            except Exception as e:
                self._increment_error_count()
                self._logger.error(f"Heartbeat error: {e}")
                await asyncio.sleep(self._heartbeat_interval)

    def _setup_message_handlers(self):
        """Setup message type handlers"""
        self._message_handlers = {
            MessageType.HEARTBEAT.value: self._handle_heartbeat,
            MessageType.CHALLENGE.value: self._handle_challenge,
            MessageType.CONSENSUS_PROPOSAL.value: self._handle_consensus_proposal,
            MessageType.COLLABORATION_REQUEST.value: self._handle_collaboration_request,
            MessageType.TOPOLOGY_UPDATE.value: self._handle_topology_update,
            MessageType.STATUS_UPDATE.value: self._handle_status_update,
            MessageType.ERROR_REPORT.value: self._handle_error_report
        }

    async def _handle_heartbeat(self, message: NetworkMessage):
        """Handle heartbeat message"""
        sender_id = message.sender_id
        self._known_nodes.add(sender_id)
        
        # Update node capabilities if provided
        if "capabilities" in message.payload:
            self._node_capabilities[sender_id] = message.payload["capabilities"]
        
        self._logger.debug(f"Received heartbeat from {sender_id}")

    async def _handle_challenge(self, message: NetworkMessage):
        """Handle challenge message"""
        challenge_data = message.payload
        response = await self.handle_challenge_response(self.node_id, challenge_data)
        self._logger.info(f"Handled challenge from {message.sender_id}")

    async def _handle_consensus_proposal(self, message: NetworkMessage):
        """Handle consensus proposal message"""
        proposal = message.payload
        await self.participate_in_consensus(self.node_id, proposal)
        self._logger.info(f"Participated in consensus for proposal {proposal.get('proposal_id')}")

    async def _handle_collaboration_request(self, message: NetworkMessage):
        """Handle collaboration request message"""
        request = message.payload
        # Evaluate collaboration request and respond
        response_data = await self._evaluate_collaboration_request(request)
        
        response_message = NetworkMessage(
            message_id=str(uuid.uuid4()),
            sender_id=self.node_id,
            recipient_id=message.sender_id,
            message_type=MessageType.COLLABORATION_RESPONSE.value,
            payload=response_data,
            timestamp=datetime.now().isoformat(),
            correlation_id=message.correlation_id,
            priority=MessagePriority.NORMAL.value
        )
        
        await self.send_message(response_message)
        self._logger.info(f"Responded to collaboration request from {message.sender_id}")

    async def _handle_topology_update(self, message: NetworkMessage):
        """Handle topology update message"""
        topology = message.payload
        await self.adapt_to_topology_change(self.node_id, topology)
        self._logger.info("Processed topology update")

    async def _handle_status_update(self, message: NetworkMessage):
        """Handle status update message"""
        status = message.payload
        sender_id = message.sender_id
        
        # Update node status information
        if sender_id not in self._node_capabilities:
            self._node_capabilities[sender_id] = []
        
        self._logger.debug(f"Received status update from {sender_id}")

    async def _handle_error_report(self, message: NetworkMessage):
        """Handle error report message"""
        error_report = message.payload
        self._logger.warning(f"Received error report from {message.sender_id}: {error_report}")

    def _validate_message(self, message: NetworkMessage) -> bool:
        """Validate message format and content"""
        try:
            # Check required fields
            required_fields = ['message_id', 'sender_id', 'message_type', 'payload', 'timestamp', 'correlation_id']
            for field in required_fields:
                if not hasattr(message, field) or getattr(message, field) is None:
                    return False
            
            # Validate message type
            valid_types = [mt.value for mt in MessageType]
            if message.message_type not in valid_types:
                return False
            
            # Validate payload is dict
            if not isinstance(message.payload, dict):
                return False
            
            return True
            
        except Exception as e:
            self._logger.error(f"Message validation error: {e}")
            return False

    def _evaluate_consensus_proposal(self, proposal: Dict[str, Any]) -> str:
        """Evaluate consensus proposal and return vote"""
        # Simple evaluation logic - can be enhanced based on requirements
        proposal_type = proposal.get("type", "unknown")
        
        if proposal_type == "node_addition":
            return "approve"
        elif proposal_type == "node_removal":
            return "approve"
        elif proposal_type == "capability_update":
            return "approve"
        else:
            return "abstain"

    async def _assess_node_availability(self, node_id: str) -> Dict[str, Any]:
        """Assess node availability for challenge response"""
        try:
            # Get performance metrics
            metrics = self.get_node_b_metrics()
            
            return {
                "available": True,
                "load_factor": 0.5,  # Placeholder
                "response_time": metrics.get("average_response_time", 0.0),
                "error_rate": metrics.get("error_rate", 0.0),
                "uptime": metrics.get("uptime_seconds", 0.0)
            }
            
        except Exception as e:
            self._logger.error(f"Failed to assess node availability: {e}")
            return {"available": False, "error": str(e)}

    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        try:
            return self.get_node_b_metrics()
        except Exception as e:
            self._logger.error(f"Failed to get performance metrics: {e}")
            return {}

    async def _evaluate_collaboration_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate collaboration request and generate response"""
        try:
            request_type = request.get("type", "unknown")
            
            response = {
                "request_id": request.get("request_id"),
                "response": "accepted",  # Simple acceptance logic
                "capabilities_offered": self._node_capabilities.get(self.node_id, []),
                "estimated_completion": "1h",  # Placeholder
                "conditions": []
            }
            
            return response
            
        except Exception as e:
            self._logger.error(f"Failed to evaluate collaboration request: {e}")
            return {"response": "rejected", "reason": str(e)}

    async def _adapt_subscription_channels(self):
        """Adapt subscription channels based on topology"""
        try:
            # Subscribe to channels for known nodes if needed
            for node_id in self._known_nodes:
                channel = f"node_b_{node_id}_updates"
                if channel not in self._subscribed_channels:
                    await self._pubsub.subscribe(channel)
                    self._subscribed_channels.add(channel)
            
            self._logger.debug(f"Adapted subscription channels: {len(self._subscribed_channels)} channels")
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to adapt subscription channels: {e}")

    async def _update_routing_tables(self):
        """Update message routing tables based on topology"""
        try:
            # Update routing logic based on network topology
            if self._network_topology:
                # Simple routing - can be enhanced with more sophisticated algorithms
                self._logger.debug("Updated routing tables based on topology")
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to update routing tables: {e}")

    async def _announce_node_presence(self):
        """Announce node presence to the network"""
        try:
            presence_message = NetworkMessage(
                message_id=str(uuid.uuid4()),
                sender_id=self.node_id,
                recipient_id=None,  # Broadcast
                message_type=MessageType.STATUS_UPDATE.value,
                payload={
                    "node_id": self.node_id,
                    "status": "online",
                    "capabilities": self._node_capabilities.get(self.node_id, []),
                    "timestamp": datetime.now().isoformat()
                },
                timestamp=datetime.now().isoformat(),
                correlation_id=str(uuid.uuid4()),
                priority=MessagePriority.HIGH.value
            )
            
            await self.send_message(presence_message)
            self._logger.info(f"Announced node presence: {self.node_id}")
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to announce node presence: {e}")

    async def _announce_node_departure(self):
        """Announce node departure from the network"""
        try:
            departure_message = NetworkMessage(
                message_id=str(uuid.uuid4()),
                sender_id=self.node_id,
                recipient_id=None,  # Broadcast
                message_type=MessageType.STATUS_UPDATE.value,
                payload={
                    "node_id": self.node_id,
                    "status": "offline",
                    "timestamp": datetime.now().isoformat()
                },
                timestamp=datetime.now().isoformat(),
                correlation_id=str(uuid.uuid4()),
                priority=MessagePriority.HIGH.value
            )
            
            await self.send_message(departure_message)
            self._logger.info(f"Announced node departure: {self.node_id}")
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to announce node departure: {e}")

    def get_network_status(self) -> Dict[str, Any]:
        """
        Get current network communication status
        
        Returns:
            Dict[str, Any]: Network status information
        """
        return {
            "node_id": self.node_id,
            "processing_active": self._processing_active,
            "known_nodes": list(self._known_nodes),
            "subscribed_channels": list(self._subscribed_channels),
            "message_queue_size": len(self._message_queue),
            "outbound_queue_size": len(self._outbound_queue),
            "delivery_tracking_count": len(self._delivery_tracking),
            "network_topology": asdict(self._network_topology) if self._network_topology else None,
            "node_capabilities": self._node_capabilities.copy()
        }

    def get_delivery_statistics(self) -> Dict[str, Any]:
        """
        Get message delivery statistics
        
        Returns:
            Dict[str, Any]: Delivery statistics
        """
        total_messages = len(self._delivery_tracking)
        delivered = sum(1 for status in self._delivery_tracking.values() if status.status == "delivered")
        failed = sum(1 for status in self._delivery_tracking.values() if status.status == "failed")
        pending = sum(1 for status in self._delivery_tracking.values() if status.status == "pending")
        
        return {
            "total_messages": total_messages,
            "delivered": delivered,
            "failed": failed,
            "pending": pending,
            "delivery_rate": delivered / total_messages if total_messages > 0 else 0.0,
            "failure_rate": failed / total_messages if total_messages > 0 else 0.0
        }

    def __repr__(self) -> str:
        """String representation of NetworkCommunicationCoordinator"""
        return f"NetworkCommunicationCoordinator(node_id='{self.node_id}', active={self._processing_active}, known_nodes={len(self._known_nodes)})"