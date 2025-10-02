"""
Network Topology Manager for Node B Management

Implements automatic adaptation to network topology changes, challenge response system
for network participation, consensus participation and voting mechanisms, and
collaboration request evaluation and response system.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from ..core.node_b_component import NodeBComponent
from ..core.interfaces import NetworkMessage
from .network_communication_coordinator import MessageType, MessagePriority, NetworkTopology


class ConsensusState(Enum):
    """Consensus participation states"""
    IDLE = "idle"
    PROPOSING = "proposing"
    VOTING = "voting"
    DECIDED = "decided"


class CollaborationStatus(Enum):
    """Collaboration request status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ConsensusProposal:
    """Consensus proposal information"""
    proposal_id: str
    proposer_id: str
    proposal_type: str
    proposal_data: Dict[str, Any]
    votes: Dict[str, str]  # node_id -> vote
    created_at: datetime
    deadline: datetime
    state: ConsensusState


@dataclass
class CollaborationRequest:
    """Collaboration request information"""
    request_id: str
    requester_id: str
    request_type: str
    request_data: Dict[str, Any]
    status: CollaborationStatus
    created_at: datetime
    deadline: Optional[datetime]
    response_data: Optional[Dict[str, Any]] = None


@dataclass
class NodeCapabilities:
    """Node capabilities and specializations"""
    node_id: str
    capabilities: List[str]
    specializations: List[str]
    performance_metrics: Dict[str, float]
    availability: Dict[str, Any]
    last_updated: datetime


@dataclass
class ChallengeRequest:
    """Network challenge request"""
    challenge_id: str
    challenger_id: str
    challenge_type: str
    challenge_data: Dict[str, Any]
    created_at: datetime
    deadline: datetime
    responses: Dict[str, Dict[str, Any]]  # node_id -> response


class NetworkTopologyManager(NodeBComponent):
    """
    Network Topology Manager for Node B instances
    
    Implements automatic adaptation to network topology changes, challenge response
    system for network participation, consensus participation and voting mechanisms,
    and collaboration request evaluation and response system.
    
    Requirements: 2.3, 2.4, 2.5, 2.6
    """

    def __init__(self, node_id: str, communication_coordinator):
        """
        Initialize Network Topology Manager
        
        Args:
            node_id: Unique identifier for the Node B instance
            communication_coordinator: NetworkCommunicationCoordinator instance
        """
        super().__init__("network_topology", node_id)
        
        self._communication_coordinator = communication_coordinator
        
        # Topology state
        self._current_topology: Optional[NetworkTopology] = None
        self._node_capabilities: Dict[str, NodeCapabilities] = {}
        self._topology_history: List[NetworkTopology] = []
        
        # Consensus state
        self._active_proposals: Dict[str, ConsensusProposal] = {}
        self._consensus_history: List[ConsensusProposal] = []
        self._voting_power = 1.0
        
        # Collaboration state
        self._active_collaborations: Dict[str, CollaborationRequest] = {}
        self._collaboration_history: List[CollaborationRequest] = []
        
        # Challenge state
        self._active_challenges: Dict[str, ChallengeRequest] = {}
        self._challenge_history: List[ChallengeRequest] = []
        
        # Configuration
        self._topology_update_interval = 60  # seconds
        self._consensus_timeout = 300  # seconds
        self._collaboration_timeout = 3600  # seconds
        self._challenge_timeout = 120  # seconds
        
        # Processing state
        self._topology_monitoring_active = False
        self._topology_monitor_task = None
        
        self._logger.info(f"NetworkTopologyManager initialized for node {node_id}")

    async def start_topology_management(self) -> bool:
        """
        Start network topology management services
        
        Returns:
            bool: True if started successfully, False otherwise
            
        Requirements: 2.3, 2.4, 2.5, 2.6
        """
        try:
            # Initialize node capabilities
            await self._initialize_node_capabilities()
            
            # Start topology monitoring
            self._topology_monitoring_active = True
            self._topology_monitor_task = asyncio.create_task(self._topology_monitoring_loop())
            
            # Start cleanup tasks
            asyncio.create_task(self._cleanup_expired_proposals())
            asyncio.create_task(self._cleanup_expired_collaborations())
            asyncio.create_task(self._cleanup_expired_challenges())
            
            # Discover initial topology
            await self._discover_network_topology()
            
            self._logger.info("Network topology management started successfully")
            return True
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to start topology management: {e}")
            return False

    async def stop_topology_management(self) -> bool:
        """
        Stop network topology management services
        
        Returns:
            bool: True if stopped successfully, False otherwise
        """
        try:
            self._topology_monitoring_active = False
            
            # Cancel monitoring task
            if self._topology_monitor_task:
                self._topology_monitor_task.cancel()
                try:
                    await self._topology_monitor_task
                except asyncio.CancelledError:
                    pass
            
            self._logger.info("Network topology management stopped successfully")
            return True
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to stop topology management: {e}")
            return False

    async def adapt_to_topology_change(self, topology_data: Dict[str, Any]) -> bool:
        """
        Automatically adapt to network topology changes
        
        Args:
            topology_data: New network topology information
            
        Returns:
            bool: True if adaptation successful, False otherwise
            
        Requirements: 2.6
        """
        try:
            # Create new topology object
            new_topology = NetworkTopology(
                active_nodes=topology_data.get("active_nodes", []),
                node_capabilities=topology_data.get("node_capabilities", {}),
                connection_matrix=topology_data.get("connection_matrix", {}),
                last_updated=datetime.now()
            )
            
            # Analyze topology changes
            changes = await self._analyze_topology_changes(new_topology)
            
            # Update current topology
            if self._current_topology:
                self._topology_history.append(self._current_topology)
            self._current_topology = new_topology
            
            # Adapt to changes
            await self._adapt_to_changes(changes)
            
            # Update node capabilities
            await self._update_node_capabilities(new_topology.node_capabilities)
            
            # Notify communication coordinator
            await self._communication_coordinator.adapt_to_topology_change(
                self.node_id, topology_data
            )
            
            self.increment_network_events()
            self._logger.info(f"Adapted to topology change: {len(changes)} changes processed")
            return True
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to adapt to topology change: {e}")
            return False

    async def handle_challenge_request(self, challenge_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle network challenge and provide comprehensive response
        
        Args:
            challenge_data: Challenge request from network
            
        Returns:
            Dict[str, Any]: Challenge response with capabilities and availability
            
        Requirements: 2.3
        """
        try:
            challenge_id = challenge_data.get("challenge_id", str(uuid.uuid4()))
            challenger_id = challenge_data.get("challenger_id")
            challenge_type = challenge_data.get("type", "capability_assessment")
            
            # Create challenge record
            challenge = ChallengeRequest(
                challenge_id=challenge_id,
                challenger_id=challenger_id,
                challenge_type=challenge_type,
                challenge_data=challenge_data,
                created_at=datetime.now(),
                deadline=datetime.now() + timedelta(seconds=self._challenge_timeout),
                responses={}
            )
            
            self._active_challenges[challenge_id] = challenge
            
            # Generate response based on challenge type
            response_data = await self._generate_challenge_response(challenge)
            
            # Record our response
            challenge.responses[self.node_id] = response_data
            
            # Send response via communication coordinator
            await self._send_challenge_response(challenger_id, challenge_id, response_data)
            
            self._logger.info(f"Handled challenge {challenge_id} from {challenger_id}")
            return response_data
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to handle challenge request: {e}")
            return {"error": str(e), "success": False}

    async def participate_in_consensus(self, proposal_data: Dict[str, Any]) -> bool:
        """
        Participate in network consensus decision with voting mechanisms
        
        Args:
            proposal_data: Consensus proposal to vote on
            
        Returns:
            bool: True if participation successful, False otherwise
            
        Requirements: 2.4, 2.5
        """
        try:
            proposal_id = proposal_data.get("proposal_id", str(uuid.uuid4()))
            proposer_id = proposal_data.get("proposer_id")
            proposal_type = proposal_data.get("type", "unknown")
            
            # Create or update proposal record
            if proposal_id not in self._active_proposals:
                proposal = ConsensusProposal(
                    proposal_id=proposal_id,
                    proposer_id=proposer_id,
                    proposal_type=proposal_type,
                    proposal_data=proposal_data,
                    votes={},
                    created_at=datetime.now(),
                    deadline=datetime.now() + timedelta(seconds=self._consensus_timeout),
                    state=ConsensusState.VOTING
                )
                self._active_proposals[proposal_id] = proposal
            else:
                proposal = self._active_proposals[proposal_id]
            
            # Generate vote based on proposal evaluation
            vote = await self._evaluate_consensus_proposal(proposal)
            
            # Record vote
            proposal.votes[self.node_id] = vote
            
            # Send vote via communication coordinator
            await self._send_consensus_vote(proposal_id, vote, proposal_data)
            
            # Check if consensus is reached
            await self._check_consensus_completion(proposal)
            
            self._logger.info(f"Participated in consensus for proposal {proposal_id} with vote: {vote}")
            return True
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to participate in consensus: {e}")
            return False

    async def evaluate_collaboration_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate collaboration request and provide response
        
        Args:
            request_data: Collaboration request to evaluate
            
        Returns:
            Dict[str, Any]: Collaboration response with decision and terms
            
        Requirements: 2.5, 2.6
        """
        try:
            request_id = request_data.get("request_id", str(uuid.uuid4()))
            requester_id = request_data.get("requester_id")
            request_type = request_data.get("type", "unknown")
            
            # Create collaboration record
            collaboration = CollaborationRequest(
                request_id=request_id,
                requester_id=requester_id,
                request_type=request_type,
                request_data=request_data,
                status=CollaborationStatus.PENDING,
                created_at=datetime.now(),
                deadline=datetime.now() + timedelta(seconds=self._collaboration_timeout)
            )
            
            self._active_collaborations[request_id] = collaboration
            
            # Evaluate request
            evaluation_result = await self._evaluate_collaboration_feasibility(collaboration)
            
            # Generate response
            response_data = await self._generate_collaboration_response(collaboration, evaluation_result)
            
            # Update collaboration status
            collaboration.status = CollaborationStatus.ACCEPTED if evaluation_result["accepted"] else CollaborationStatus.REJECTED
            collaboration.response_data = response_data
            
            # Send response via communication coordinator
            await self._send_collaboration_response(requester_id, request_id, response_data)
            
            self._logger.info(f"Evaluated collaboration request {request_id}: {collaboration.status.value}")
            return response_data
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to evaluate collaboration request: {e}")
            return {"accepted": False, "reason": str(e)}

    async def initiate_consensus_proposal(self, proposal_type: str, proposal_data: Dict[str, Any]) -> str:
        """
        Initiate a new consensus proposal
        
        Args:
            proposal_type: Type of consensus proposal
            proposal_data: Proposal data and parameters
            
        Returns:
            str: Proposal ID if successful, empty string if failed
        """
        try:
            proposal_id = str(uuid.uuid4())
            
            # Create proposal
            proposal = ConsensusProposal(
                proposal_id=proposal_id,
                proposer_id=self.node_id,
                proposal_type=proposal_type,
                proposal_data=proposal_data,
                votes={self.node_id: "approve"},  # Proposer votes approve by default
                created_at=datetime.now(),
                deadline=datetime.now() + timedelta(seconds=self._consensus_timeout),
                state=ConsensusState.PROPOSING
            )
            
            self._active_proposals[proposal_id] = proposal
            
            # Broadcast proposal
            await self._broadcast_consensus_proposal(proposal)
            
            proposal.state = ConsensusState.VOTING
            
            self._logger.info(f"Initiated consensus proposal {proposal_id} of type {proposal_type}")
            return proposal_id
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to initiate consensus proposal: {e}")
            return ""

    async def initiate_challenge(self, challenge_type: str, target_nodes: List[str], challenge_data: Dict[str, Any]) -> str:
        """
        Initiate a network challenge
        
        Args:
            challenge_type: Type of challenge
            target_nodes: List of nodes to challenge
            challenge_data: Challenge data and parameters
            
        Returns:
            str: Challenge ID if successful, empty string if failed
        """
        try:
            challenge_id = str(uuid.uuid4())
            
            # Create challenge
            challenge = ChallengeRequest(
                challenge_id=challenge_id,
                challenger_id=self.node_id,
                challenge_type=challenge_type,
                challenge_data=challenge_data,
                created_at=datetime.now(),
                deadline=datetime.now() + timedelta(seconds=self._challenge_timeout),
                responses={}
            )
            
            self._active_challenges[challenge_id] = challenge
            
            # Send challenge to target nodes
            await self._send_challenge_to_nodes(challenge, target_nodes)
            
            self._logger.info(f"Initiated challenge {challenge_id} to {len(target_nodes)} nodes")
            return challenge_id
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to initiate challenge: {e}")
            return ""

    async def _initialize_node_capabilities(self):
        """Initialize this node's capabilities"""
        try:
            capabilities = NodeCapabilities(
                node_id=self.node_id,
                capabilities=["coordination", "consensus", "collaboration", "monitoring"],
                specializations=["network_topology", "message_routing"],
                performance_metrics=await self._get_performance_metrics(),
                availability=await self._assess_availability(),
                last_updated=datetime.now()
            )
            
            self._node_capabilities[self.node_id] = capabilities
            self._logger.info(f"Initialized capabilities for node {self.node_id}")
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to initialize node capabilities: {e}")

    async def _topology_monitoring_loop(self):
        """Monitor network topology changes"""
        while self._topology_monitoring_active:
            try:
                # Discover current topology
                await self._discover_network_topology()
                
                # Check for topology changes
                await self._detect_topology_changes()
                
                # Update node capabilities
                await self._refresh_node_capabilities()
                
                await asyncio.sleep(self._topology_update_interval)
                
            except Exception as e:
                self._increment_error_count()
                self._logger.error(f"Topology monitoring error: {e}")
                await asyncio.sleep(self._topology_update_interval)

    async def _discover_network_topology(self):
        """Discover current network topology"""
        try:
            # Get network status from communication coordinator
            network_status = self._communication_coordinator.get_network_status()
            
            # Create topology from discovered information
            topology_data = {
                "active_nodes": network_status.get("known_nodes", []),
                "node_capabilities": {
                    node_id: caps.capabilities if isinstance(caps, NodeCapabilities) else caps
                    for node_id, caps in self._node_capabilities.items()
                },
                "connection_matrix": self._build_connection_matrix(network_status.get("known_nodes", []))
            }
            
            # Update topology if changed
            if not self._current_topology or self._topology_changed(topology_data):
                await self.adapt_to_topology_change(topology_data)
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to discover network topology: {e}")

    def _build_connection_matrix(self, active_nodes: List[str]) -> Dict[str, List[str]]:
        """Build connection matrix from active nodes"""
        # Simple full-mesh connectivity assumption
        connection_matrix = {}
        for node in active_nodes:
            connection_matrix[node] = [n for n in active_nodes if n != node]
        return connection_matrix

    def _topology_changed(self, new_topology_data: Dict[str, Any]) -> bool:
        """Check if topology has changed"""
        if not self._current_topology:
            return True
        
        current_nodes = set(self._current_topology.active_nodes)
        new_nodes = set(new_topology_data.get("active_nodes", []))
        
        return current_nodes != new_nodes

    async def _analyze_topology_changes(self, new_topology: NetworkTopology) -> List[Dict[str, Any]]:
        """Analyze changes between current and new topology"""
        changes = []
        
        if not self._current_topology:
            changes.append({
                "type": "initial_topology",
                "data": {"nodes": new_topology.active_nodes}
            })
            return changes
        
        # Detect node additions
        current_nodes = set(self._current_topology.active_nodes)
        new_nodes = set(new_topology.active_nodes)
        
        added_nodes = new_nodes - current_nodes
        removed_nodes = current_nodes - new_nodes
        
        for node in added_nodes:
            changes.append({
                "type": "node_added",
                "data": {"node_id": node}
            })
        
        for node in removed_nodes:
            changes.append({
                "type": "node_removed",
                "data": {"node_id": node}
            })
        
        # Detect capability changes
        for node_id in new_nodes & current_nodes:
            old_caps = self._current_topology.node_capabilities.get(node_id, [])
            new_caps = new_topology.node_capabilities.get(node_id, [])
            
            if set(old_caps) != set(new_caps):
                changes.append({
                    "type": "capabilities_changed",
                    "data": {
                        "node_id": node_id,
                        "old_capabilities": old_caps,
                        "new_capabilities": new_caps
                    }
                })
        
        return changes

    async def _adapt_to_changes(self, changes: List[Dict[str, Any]]):
        """Adapt to topology changes"""
        for change in changes:
            change_type = change["type"]
            change_data = change["data"]
            
            if change_type == "node_added":
                await self._handle_node_addition(change_data["node_id"])
            elif change_type == "node_removed":
                await self._handle_node_removal(change_data["node_id"])
            elif change_type == "capabilities_changed":
                await self._handle_capability_change(change_data)
            
            self._logger.debug(f"Processed topology change: {change_type}")

    async def _handle_node_addition(self, node_id: str):
        """Handle new node addition to network"""
        try:
            # Send welcome challenge to new node
            challenge_data = {
                "type": "welcome_assessment",
                "message": "Welcome to the network",
                "timestamp": datetime.now().isoformat()
            }
            
            await self.initiate_challenge("welcome_assessment", [node_id], challenge_data)
            self._logger.info(f"Sent welcome challenge to new node: {node_id}")
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to handle node addition {node_id}: {e}")

    async def _handle_node_removal(self, node_id: str):
        """Handle node removal from network"""
        try:
            # Clean up any active interactions with removed node
            await self._cleanup_node_interactions(node_id)
            
            # Remove from capabilities
            if node_id in self._node_capabilities:
                del self._node_capabilities[node_id]
            
            self._logger.info(f"Handled removal of node: {node_id}")
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to handle node removal {node_id}: {e}")

    async def _handle_capability_change(self, change_data: Dict[str, Any]):
        """Handle node capability changes"""
        try:
            node_id = change_data["node_id"]
            new_capabilities = change_data["new_capabilities"]
            
            # Update capabilities record
            if node_id in self._node_capabilities:
                self._node_capabilities[node_id].capabilities = new_capabilities
                self._node_capabilities[node_id].last_updated = datetime.now()
            
            self._logger.info(f"Updated capabilities for node {node_id}")
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to handle capability change for {change_data.get('node_id')}: {e}")

    async def _cleanup_node_interactions(self, node_id: str):
        """Clean up interactions with removed node"""
        try:
            # Remove from active proposals
            for proposal in self._active_proposals.values():
                if node_id in proposal.votes:
                    del proposal.votes[node_id]
            
            # Remove from active collaborations
            collaborations_to_remove = [
                req_id for req_id, collab in self._active_collaborations.items()
                if collab.requester_id == node_id
            ]
            
            for req_id in collaborations_to_remove:
                del self._active_collaborations[req_id]
            
            # Remove from active challenges
            challenges_to_remove = [
                challenge_id for challenge_id, challenge in self._active_challenges.items()
                if challenge.challenger_id == node_id
            ]
            
            for challenge_id in challenges_to_remove:
                del self._active_challenges[challenge_id]
            
            self._logger.debug(f"Cleaned up interactions with removed node: {node_id}")
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to cleanup interactions for node {node_id}: {e}")

    async def _generate_challenge_response(self, challenge: ChallengeRequest) -> Dict[str, Any]:
        """Generate response to network challenge"""
        try:
            challenge_type = challenge.challenge_type
            
            base_response = {
                "challenge_id": challenge.challenge_id,
                "responder_id": self.node_id,
                "response_timestamp": datetime.now().isoformat(),
                "success": True
            }
            
            if challenge_type == "capability_assessment":
                capabilities = self._node_capabilities.get(self.node_id)
                base_response.update({
                    "capabilities": capabilities.capabilities if capabilities else [],
                    "specializations": capabilities.specializations if capabilities else [],
                    "performance_metrics": capabilities.performance_metrics if capabilities else {},
                    "availability": capabilities.availability if capabilities else {}
                })
            
            elif challenge_type == "welcome_assessment":
                base_response.update({
                    "message": "Welcome received, ready to participate",
                    "node_status": "active",
                    "capabilities": self._node_capabilities.get(self.node_id, {}).capabilities or []
                })
            
            elif challenge_type == "performance_test":
                base_response.update({
                    "performance_metrics": await self._get_performance_metrics(),
                    "load_capacity": await self._assess_load_capacity(),
                    "response_time": 0.1  # Placeholder
                })
            
            else:
                base_response.update({
                    "message": f"Challenge type {challenge_type} acknowledged",
                    "capabilities": self._node_capabilities.get(self.node_id, {}).capabilities or []
                })
            
            return base_response
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to generate challenge response: {e}")
            return {
                "challenge_id": challenge.challenge_id,
                "responder_id": self.node_id,
                "success": False,
                "error": str(e)
            }

    async def _evaluate_consensus_proposal(self, proposal: ConsensusProposal) -> str:
        """Evaluate consensus proposal and return vote"""
        try:
            proposal_type = proposal.proposal_type
            proposal_data = proposal.proposal_data
            
            # Simple evaluation logic - can be enhanced based on requirements
            if proposal_type == "node_addition":
                # Generally approve node additions
                return "approve"
            
            elif proposal_type == "node_removal":
                # Evaluate based on node behavior
                target_node = proposal_data.get("target_node")
                if target_node and target_node in self._node_capabilities:
                    # Check if node has been problematic
                    return "approve"  # Simplified logic
                return "abstain"
            
            elif proposal_type == "capability_update":
                # Approve capability updates
                return "approve"
            
            elif proposal_type == "network_policy":
                # Evaluate policy changes
                policy_type = proposal_data.get("policy_type")
                if policy_type in ["security", "performance"]:
                    return "approve"
                return "abstain"
            
            else:
                # Unknown proposal type
                return "abstain"
                
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to evaluate consensus proposal: {e}")
            return "abstain"

    async def _evaluate_collaboration_feasibility(self, collaboration: CollaborationRequest) -> Dict[str, Any]:
        """Evaluate collaboration request feasibility"""
        try:
            request_type = collaboration.request_type
            request_data = collaboration.request_data
            
            # Base evaluation
            evaluation = {
                "accepted": False,
                "confidence": 0.0,
                "estimated_effort": 0.0,
                "resource_requirements": {},
                "conditions": []
            }
            
            # Evaluate based on request type
            if request_type == "task_execution":
                task_complexity = request_data.get("complexity", "medium")
                required_capabilities = request_data.get("required_capabilities", [])
                
                # Check if we have required capabilities
                our_capabilities = self._node_capabilities.get(self.node_id, NodeCapabilities(
                    node_id=self.node_id, capabilities=[], specializations=[], 
                    performance_metrics={}, availability={}, last_updated=datetime.now()
                )).capabilities
                
                has_capabilities = all(cap in our_capabilities for cap in required_capabilities)
                
                if has_capabilities:
                    evaluation.update({
                        "accepted": True,
                        "confidence": 0.8,
                        "estimated_effort": self._estimate_task_effort(task_complexity),
                        "resource_requirements": {"cpu": 0.5, "memory": 0.3}
                    })
            
            elif request_type == "data_sharing":
                data_type = request_data.get("data_type")
                data_size = request_data.get("data_size", 0)
                
                # Simple acceptance for small data sharing
                if data_size < 1000000:  # 1MB
                    evaluation.update({
                        "accepted": True,
                        "confidence": 0.9,
                        "estimated_effort": 0.1,
                        "resource_requirements": {"bandwidth": 0.1}
                    })
            
            elif request_type == "monitoring":
                monitoring_duration = request_data.get("duration", 3600)
                
                # Accept short-term monitoring
                if monitoring_duration <= 7200:  # 2 hours
                    evaluation.update({
                        "accepted": True,
                        "confidence": 0.7,
                        "estimated_effort": monitoring_duration / 3600,
                        "resource_requirements": {"cpu": 0.1}
                    })
            
            return evaluation
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to evaluate collaboration feasibility: {e}")
            return {"accepted": False, "error": str(e)}

    def _estimate_task_effort(self, complexity: str) -> float:
        """Estimate effort required for task based on complexity"""
        complexity_map = {
            "low": 0.5,
            "medium": 1.0,
            "high": 2.0,
            "very_high": 4.0
        }
        return complexity_map.get(complexity, 1.0)

    async def _generate_collaboration_response(self, collaboration: CollaborationRequest, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate collaboration response based on evaluation"""
        try:
            response = {
                "request_id": collaboration.request_id,
                "responder_id": self.node_id,
                "accepted": evaluation["accepted"],
                "response_timestamp": datetime.now().isoformat()
            }
            
            if evaluation["accepted"]:
                response.update({
                    "estimated_completion_time": evaluation.get("estimated_effort", 1.0) * 3600,  # Convert to seconds
                    "resource_commitment": evaluation.get("resource_requirements", {}),
                    "conditions": evaluation.get("conditions", []),
                    "confidence_level": evaluation.get("confidence", 0.5)
                })
            else:
                response.update({
                    "rejection_reason": evaluation.get("error", "Resource constraints"),
                    "alternative_suggestions": []
                })
            
            return response
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to generate collaboration response: {e}")
            return {
                "request_id": collaboration.request_id,
                "responder_id": self.node_id,
                "accepted": False,
                "error": str(e)
            }

    async def _send_challenge_response(self, challenger_id: str, challenge_id: str, response_data: Dict[str, Any]):
        """Send challenge response via communication coordinator"""
        try:
            message = NetworkMessage(
                message_id=str(uuid.uuid4()),
                sender_id=self.node_id,
                recipient_id=challenger_id,
                message_type=MessageType.CHALLENGE_RESPONSE.value,
                payload=response_data,
                timestamp=datetime.now().isoformat(),
                correlation_id=challenge_id,
                priority=MessagePriority.HIGH.value
            )
            
            await self._communication_coordinator.send_message(message)
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to send challenge response: {e}")

    async def _send_consensus_vote(self, proposal_id: str, vote: str, proposal_data: Dict[str, Any]):
        """Send consensus vote via communication coordinator"""
        try:
            vote_payload = {
                "proposal_id": proposal_id,
                "vote": vote,
                "voter_id": self.node_id,
                "voting_power": self._voting_power,
                "timestamp": datetime.now().isoformat()
            }
            
            message = NetworkMessage(
                message_id=str(uuid.uuid4()),
                sender_id=self.node_id,
                recipient_id=None,  # Broadcast
                message_type=MessageType.CONSENSUS_VOTE.value,
                payload=vote_payload,
                timestamp=datetime.now().isoformat(),
                correlation_id=proposal_id,
                priority=MessagePriority.HIGH.value
            )
            
            await self._communication_coordinator.send_message(message)
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to send consensus vote: {e}")

    async def _send_collaboration_response(self, requester_id: str, request_id: str, response_data: Dict[str, Any]):
        """Send collaboration response via communication coordinator"""
        try:
            message = NetworkMessage(
                message_id=str(uuid.uuid4()),
                sender_id=self.node_id,
                recipient_id=requester_id,
                message_type=MessageType.COLLABORATION_RESPONSE.value,
                payload=response_data,
                timestamp=datetime.now().isoformat(),
                correlation_id=request_id,
                priority=MessagePriority.NORMAL.value
            )
            
            await self._communication_coordinator.send_message(message)
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to send collaboration response: {e}")

    async def _broadcast_consensus_proposal(self, proposal: ConsensusProposal):
        """Broadcast consensus proposal to network"""
        try:
            proposal_payload = {
                "proposal_id": proposal.proposal_id,
                "proposer_id": proposal.proposer_id,
                "type": proposal.proposal_type,
                "data": proposal.proposal_data,
                "deadline": proposal.deadline.isoformat(),
                "timestamp": datetime.now().isoformat()
            }
            
            message = NetworkMessage(
                message_id=str(uuid.uuid4()),
                sender_id=self.node_id,
                recipient_id=None,  # Broadcast
                message_type=MessageType.CONSENSUS_PROPOSAL.value,
                payload=proposal_payload,
                timestamp=datetime.now().isoformat(),
                correlation_id=proposal.proposal_id,
                priority=MessagePriority.HIGH.value
            )
            
            await self._communication_coordinator.send_message(message)
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to broadcast consensus proposal: {e}")

    async def _send_challenge_to_nodes(self, challenge: ChallengeRequest, target_nodes: List[str]):
        """Send challenge to target nodes"""
        try:
            challenge_payload = {
                "challenge_id": challenge.challenge_id,
                "challenger_id": challenge.challenger_id,
                "type": challenge.challenge_type,
                "data": challenge.challenge_data,
                "deadline": challenge.deadline.isoformat(),
                "timestamp": datetime.now().isoformat()
            }
            
            for node_id in target_nodes:
                message = NetworkMessage(
                    message_id=str(uuid.uuid4()),
                    sender_id=self.node_id,
                    recipient_id=node_id,
                    message_type=MessageType.CHALLENGE.value,
                    payload=challenge_payload,
                    timestamp=datetime.now().isoformat(),
                    correlation_id=challenge.challenge_id,
                    priority=MessagePriority.HIGH.value
                )
                
                await self._communication_coordinator.send_message(message)
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to send challenge to nodes: {e}")

    async def _check_consensus_completion(self, proposal: ConsensusProposal):
        """Check if consensus is reached for proposal"""
        try:
            if not self._current_topology:
                return
            
            total_nodes = len(self._current_topology.active_nodes)
            total_votes = len(proposal.votes)
            
            # Simple majority consensus (can be enhanced)
            if total_votes >= (total_nodes // 2 + 1):
                approve_votes = sum(1 for vote in proposal.votes.values() if vote == "approve")
                
                if approve_votes > total_votes // 2:
                    proposal.state = ConsensusState.DECIDED
                    await self._handle_consensus_decision(proposal, "approved")
                elif total_votes == total_nodes:
                    # All votes collected, decision based on majority
                    if approve_votes > total_votes // 2:
                        proposal.state = ConsensusState.DECIDED
                        await self._handle_consensus_decision(proposal, "approved")
                    else:
                        proposal.state = ConsensusState.DECIDED
                        await self._handle_consensus_decision(proposal, "rejected")
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to check consensus completion: {e}")

    async def _handle_consensus_decision(self, proposal: ConsensusProposal, decision: str):
        """Handle consensus decision"""
        try:
            self._logger.info(f"Consensus reached for proposal {proposal.proposal_id}: {decision}")
            
            # Move to history
            self._consensus_history.append(proposal)
            
            # Apply decision if approved
            if decision == "approved":
                await self._apply_consensus_decision(proposal)
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to handle consensus decision: {e}")

    async def _apply_consensus_decision(self, proposal: ConsensusProposal):
        """Apply approved consensus decision"""
        try:
            proposal_type = proposal.proposal_type
            proposal_data = proposal.proposal_data
            
            if proposal_type == "node_addition":
                # Handle node addition
                new_node_id = proposal_data.get("node_id")
                self._logger.info(f"Applying consensus: Adding node {new_node_id}")
            
            elif proposal_type == "node_removal":
                # Handle node removal
                target_node = proposal_data.get("target_node")
                self._logger.info(f"Applying consensus: Removing node {target_node}")
            
            elif proposal_type == "capability_update":
                # Handle capability update
                node_id = proposal_data.get("node_id")
                new_capabilities = proposal_data.get("capabilities", [])
                if node_id in self._node_capabilities:
                    self._node_capabilities[node_id].capabilities = new_capabilities
                self._logger.info(f"Applying consensus: Updated capabilities for {node_id}")
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to apply consensus decision: {e}")

    async def _cleanup_expired_proposals(self):
        """Clean up expired consensus proposals"""
        while self._topology_monitoring_active:
            try:
                current_time = datetime.now()
                expired_proposals = [
                    proposal_id for proposal_id, proposal in self._active_proposals.items()
                    if proposal.deadline < current_time
                ]
                
                for proposal_id in expired_proposals:
                    proposal = self._active_proposals[proposal_id]
                    self._consensus_history.append(proposal)
                    del self._active_proposals[proposal_id]
                    self._logger.info(f"Expired consensus proposal: {proposal_id}")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self._increment_error_count()
                self._logger.error(f"Error cleaning up expired proposals: {e}")
                await asyncio.sleep(60)

    async def _cleanup_expired_collaborations(self):
        """Clean up expired collaboration requests"""
        while self._topology_monitoring_active:
            try:
                current_time = datetime.now()
                expired_collaborations = [
                    req_id for req_id, collab in self._active_collaborations.items()
                    if collab.deadline and collab.deadline < current_time
                ]
                
                for req_id in expired_collaborations:
                    collaboration = self._active_collaborations[req_id]
                    self._collaboration_history.append(collaboration)
                    del self._active_collaborations[req_id]
                    self._logger.info(f"Expired collaboration request: {req_id}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self._increment_error_count()
                self._logger.error(f"Error cleaning up expired collaborations: {e}")
                await asyncio.sleep(300)

    async def _cleanup_expired_challenges(self):
        """Clean up expired challenges"""
        while self._topology_monitoring_active:
            try:
                current_time = datetime.now()
                expired_challenges = [
                    challenge_id for challenge_id, challenge in self._active_challenges.items()
                    if challenge.deadline < current_time
                ]
                
                for challenge_id in expired_challenges:
                    challenge = self._active_challenges[challenge_id]
                    self._challenge_history.append(challenge)
                    del self._active_challenges[challenge_id]
                    self._logger.info(f"Expired challenge: {challenge_id}")
                
                await asyncio.sleep(120)  # Check every 2 minutes
                
            except Exception as e:
                self._increment_error_count()
                self._logger.error(f"Error cleaning up expired challenges: {e}")
                await asyncio.sleep(120)

    async def _detect_topology_changes(self):
        """Detect and handle topology changes"""
        try:
            # This would be called by the monitoring loop
            # Implementation depends on specific topology detection mechanisms
            pass
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Error detecting topology changes: {e}")

    async def _refresh_node_capabilities(self):
        """Refresh capabilities of known nodes"""
        try:
            # Update our own capabilities
            if self.node_id in self._node_capabilities:
                self._node_capabilities[self.node_id].performance_metrics = await self._get_performance_metrics()
                self._node_capabilities[self.node_id].availability = await self._assess_availability()
                self._node_capabilities[self.node_id].last_updated = datetime.now()
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Error refreshing node capabilities: {e}")

    async def _update_node_capabilities(self, capabilities_data: Dict[str, List[str]]):
        """Update node capabilities from topology data"""
        try:
            for node_id, capabilities in capabilities_data.items():
                if node_id not in self._node_capabilities:
                    self._node_capabilities[node_id] = NodeCapabilities(
                        node_id=node_id,
                        capabilities=capabilities,
                        specializations=[],
                        performance_metrics={},
                        availability={},
                        last_updated=datetime.now()
                    )
                else:
                    self._node_capabilities[node_id].capabilities = capabilities
                    self._node_capabilities[node_id].last_updated = datetime.now()
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Error updating node capabilities: {e}")

    async def _get_performance_metrics(self) -> Dict[str, float]:
        """Get current performance metrics"""
        try:
            metrics = self.get_node_b_metrics()
            return {
                "cpu_usage": metrics.get("cpu_usage", 0.0),
                "memory_usage": metrics.get("memory_usage", 0.0),
                "response_time": metrics.get("average_response_time", 0.0),
                "throughput": metrics.get("messages_processed", 0) / max(metrics.get("uptime_seconds", 1), 1)
            }
        except Exception as e:
            self._logger.error(f"Failed to get performance metrics: {e}")
            return {}

    async def _assess_availability(self) -> Dict[str, Any]:
        """Assess current node availability"""
        try:
            return {
                "available": True,
                "load_factor": 0.5,  # Placeholder
                "capacity_remaining": 0.7,  # Placeholder
                "estimated_response_time": 0.1
            }
        except Exception as e:
            self._logger.error(f"Failed to assess availability: {e}")
            return {"available": False}

    async def _assess_load_capacity(self) -> Dict[str, Any]:
        """Assess current load capacity"""
        try:
            return {
                "max_concurrent_tasks": 10,
                "current_tasks": 2,
                "capacity_utilization": 0.2
            }
        except Exception as e:
            self._logger.error(f"Failed to assess load capacity: {e}")
            return {}

    def get_topology_status(self) -> Dict[str, Any]:
        """
        Get current topology management status
        
        Returns:
            Dict[str, Any]: Topology status information
        """
        return {
            "node_id": self.node_id,
            "monitoring_active": self._topology_monitoring_active,
            "current_topology": asdict(self._current_topology) if self._current_topology else None,
            "known_nodes": len(self._node_capabilities),
            "active_proposals": len(self._active_proposals),
            "active_collaborations": len(self._active_collaborations),
            "active_challenges": len(self._active_challenges),
            "consensus_history_count": len(self._consensus_history),
            "collaboration_history_count": len(self._collaboration_history),
            "challenge_history_count": len(self._challenge_history)
        }

    def get_consensus_statistics(self) -> Dict[str, Any]:
        """
        Get consensus participation statistics
        
        Returns:
            Dict[str, Any]: Consensus statistics
        """
        total_proposals = len(self._consensus_history) + len(self._active_proposals)
        approved_proposals = sum(1 for p in self._consensus_history if p.state == ConsensusState.DECIDED and 
                               sum(1 for vote in p.votes.values() if vote == "approve") > len(p.votes) // 2)
        
        return {
            "total_proposals": total_proposals,
            "active_proposals": len(self._active_proposals),
            "approved_proposals": approved_proposals,
            "approval_rate": approved_proposals / total_proposals if total_proposals > 0 else 0.0,
            "voting_power": self._voting_power,
            "participation_rate": 1.0  # Placeholder
        }

    def __repr__(self) -> str:
        """String representation of NetworkTopologyManager"""
        return f"NetworkTopologyManager(node_id='{self.node_id}', active={self._topology_monitoring_active}, nodes={len(self._node_capabilities)})"