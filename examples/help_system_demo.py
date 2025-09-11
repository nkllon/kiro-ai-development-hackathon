#!/usr/bin/env python3
"""
Beast Mode Help System Demo

Demonstrates the help wanted system functionality including:
- Creating help requests with different urgency levels
- Capability matching and agent discovery
- Help response processing and collaboration tracking
- Success metrics and statistics
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import List

from src.beast_mode.messaging.bus_client import BeastModeBusClient
from src.beast_mode.messaging.help_system import HelpUrgency
from src.beast_mode.messaging.models import AgentCapabilities
from src.beast_mode.messaging.agent_registry import DiscoveredAgent


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HelpSystemDemo:
    """Demo class for help system functionality"""
    
    def __init__(self):
        self.clients = {}
        self.demo_agents = [
            {
                "agent_id": "python_expert",
                "capabilities": ["python", "machine_learning", "data_science", "testing"],
                "collaboration_score": 5.0
            },
            {
                "agent_id": "devops_specialist", 
                "capabilities": ["docker", "kubernetes", "terraform", "python", "monitoring"],
                "collaboration_score": 4.2
            },
            {
                "agent_id": "frontend_developer",
                "capabilities": ["javascript", "react", "css", "testing", "ui_design"],
                "collaboration_score": 3.8
            },
            {
                "agent_id": "junior_developer",
                "capabilities": ["python", "git", "documentation"],
                "collaboration_score": 1.5
            },
            {
                "agent_id": "security_expert",
                "capabilities": ["security", "penetration_testing", "compliance", "python"],
                "collaboration_score": 4.8
            }
        ]
    
    async def setup_demo_environment(self):
        """Set up demo environment with mock agents"""
        logger.info("Setting up demo environment...")
        
        # Create bus clients for each demo agent
        for agent_data in self.demo_agents:
            client = BeastModeBusClient(
                agent_id=agent_data["agent_id"],
                capabilities=agent_data["capabilities"],
                redis_url="redis://localhost:6379"
            )
            
            # Mock connection (in real scenario, would connect to Redis)
            client.is_connected = True
            client.client = True  # Mock Redis client
            
            # Add agent to registry with collaboration score
            agent_caps = AgentCapabilities(
                agent_id=agent_data["agent_id"],
                capabilities=agent_data["capabilities"],
                availability="ready_for_business"
            )
            
            discovered_agent = DiscoveredAgent(
                agent_id=agent_data["agent_id"],
                capabilities=agent_caps,
                collaboration_score=agent_data["collaboration_score"]
            )
            
            client.agent_registry.agents[agent_data["agent_id"]] = discovered_agent
            self.clients[agent_data["agent_id"]] = client
        
        # Cross-populate registries so all agents know about each other
        for client in self.clients.values():
            for other_client in self.clients.values():
                if client.agent_id != other_client.agent_id:
                    other_agent = other_client.agent_registry.agents[other_client.agent_id]
                    client.agent_registry.agents[other_client.agent_id] = other_agent
        
        logger.info(f"Created {len(self.clients)} demo agents")
    
    async def demo_basic_help_request(self):
        """Demonstrate basic help request workflow"""
        logger.info("\n" + "="*60)
        logger.info("DEMO: Basic Help Request Workflow")
        logger.info("="*60)
        
        requester = self.clients["junior_developer"]
        
        # Send help request
        logger.info("Junior developer needs help with Python testing...")
        request_id = await requester.send_help_request(
            required_capabilities=["python", "testing"],
            description="I'm struggling with writing unit tests for my Python project. Need guidance on best practices and test structure.",
            urgency=HelpUrgency.NORMAL,
            max_helpers=1
        )
        
        logger.info(f"Created help request: {request_id}")
        
        # Find matching agents
        matches = requester.find_agents_for_capabilities(["python", "testing"])
        logger.info(f"Found {len(matches)} potential helpers:")
        
        for match in matches[:3]:  # Show top 3 matches
            logger.info(f"  - {match['agent_id']}: {match['match_score']:.2f} match score, "
                       f"collaboration score: {match['collaboration_score']:.1f}")
        
        # Simulate the best match responding
        if matches:
            best_helper = matches[0]
            helper_client = self.clients[best_helper["agent_id"]]
            
            # Create mock help request message
            from src.beast_mode.messaging.models import BeastModeMessage, MessageType
            help_request_message = BeastModeMessage(
                type=MessageType.HELP_WANTED,
                source=requester.agent_id,
                payload={
                    "request_id": request_id,
                    "required_capabilities": ["python", "testing"],
                    "description": "I'm struggling with writing unit tests for my Python project.",
                    "urgency": HelpUrgency.NORMAL,
                    "max_helpers": 1
                }
            )
            
            # Process help request
            help_response = helper_client.help_system.process_help_request(
                help_request_message,
                helper_client.agent_id
            )
            
            if help_response:
                logger.info(f"{best_helper['agent_id']} responded with confidence {help_response.confidence_score:.2f}")
                logger.info(f"Matching capabilities: {help_response.matching_capabilities}")
                
                # Simulate processing the response
                response_message = BeastModeMessage(
                    type=MessageType.HELP_RESPONSE,
                    source=helper_client.agent_id,
                    payload={
                        "response_id": help_response.response_id,
                        "request_id": request_id,
                        "matching_capabilities": help_response.matching_capabilities,
                        "confidence_score": help_response.confidence_score,
                        "availability": "ready_for_business",
                        "message": help_response.message
                    }
                )
                
                await requester._handle_help_response(response_message)
                
                # Accept the help
                success = requester.accept_help_response(request_id, help_response.response_id)
                if success:
                    logger.info("Help response accepted! Collaboration session started.")
                    
                    # Show collaboration session
                    sessions = requester.get_collaboration_sessions()
                    if sessions:
                        session = sessions[-1]  # Get latest session
                        logger.info(f"Session ID: {session['session_id']}")
                        logger.info(f"Capabilities being used: {session['capabilities_used']}")
                        
                        # Simulate successful collaboration
                        await asyncio.sleep(0.1)  # Simulate time passing
                        
                        success = requester.complete_collaboration(
                            session['session_id'],
                            True,
                            {
                                "tests_written": 12,
                                "coverage_improvement": "45%",
                                "learning_objectives_met": ["test_structure", "mocking", "assertions"]
                            }
                        )
                        
                        if success:
                            logger.info("Collaboration completed successfully!")
                            logger.info("Metrics: 12 tests written, 45% coverage improvement")
    
    async def demo_multiple_helpers(self):
        """Demonstrate requesting help from multiple agents"""
        logger.info("\n" + "="*60)
        logger.info("DEMO: Multiple Helpers Workflow")
        logger.info("="*60)
        
        requester = self.clients["devops_specialist"]
        
        # Send help request for multiple helpers
        logger.info("DevOps specialist needs help with a complex security audit...")
        request_id = await requester.send_help_request(
            required_capabilities=["security", "python", "compliance"],
            description="Need help conducting a comprehensive security audit of our Python microservices. Looking for multiple perspectives.",
            urgency=HelpUrgency.HIGH,
            max_helpers=2,
            context={
                "project_type": "microservices",
                "tech_stack": ["python", "docker", "kubernetes"],
                "compliance_requirements": ["SOC2", "GDPR"]
            }
        )
        
        logger.info(f"Created help request for multiple helpers: {request_id}")
        
        # Find all potential helpers
        matches = requester.find_agents_for_capabilities(["security", "python", "compliance"])
        logger.info(f"Found {len(matches)} potential helpers:")
        
        responses = []
        for match in matches[:3]:  # Process top 3 matches
            helper_client = self.clients[match["agent_id"]]
            logger.info(f"  - {match['agent_id']}: {match['match_score']:.2f} match score")
            
            # Simulate help response
            from src.beast_mode.messaging.models import BeastModeMessage, MessageType
            help_request_message = BeastModeMessage(
                type=MessageType.HELP_WANTED,
                source=requester.agent_id,
                payload={
                    "request_id": request_id,
                    "required_capabilities": ["security", "python", "compliance"],
                    "description": "Need help conducting a comprehensive security audit",
                    "urgency": HelpUrgency.HIGH,
                    "max_helpers": 2
                }
            )
            
            help_response = helper_client.help_system.process_help_request(
                help_request_message,
                helper_client.agent_id
            )
            
            if help_response:
                responses.append((helper_client.agent_id, help_response))
                
                # Process response
                response_message = BeastModeMessage(
                    type=MessageType.HELP_RESPONSE,
                    source=helper_client.agent_id,
                    payload={
                        "response_id": help_response.response_id,
                        "request_id": request_id,
                        "matching_capabilities": help_response.matching_capabilities,
                        "confidence_score": help_response.confidence_score,
                        "availability": "ready_for_business"
                    }
                )
                
                await requester._handle_help_response(response_message)
        
        # Accept the best responses (up to max_helpers)
        accepted_count = 0
        for agent_id, response in responses:
            if accepted_count < 2:  # max_helpers = 2
                success = requester.accept_help_response(request_id, response.response_id)
                if success:
                    logger.info(f"Accepted help from {agent_id} (confidence: {response.confidence_score:.2f})")
                    accepted_count += 1
        
        # Show active collaboration sessions
        sessions = requester.get_collaboration_sessions()
        active_sessions = [s for s in sessions if s["request_id"] == request_id]
        logger.info(f"Started {len(active_sessions)} collaboration sessions")
        
        for session in active_sessions:
            logger.info(f"  - Session with {session['helper_id']}: {session['capabilities_used']}")
    
    async def demo_capability_matching(self):
        """Demonstrate capability matching algorithm"""
        logger.info("\n" + "="*60)
        logger.info("DEMO: Capability Matching Algorithm")
        logger.info("="*60)
        
        requester = self.clients["frontend_developer"]
        
        # Test different capability combinations
        test_cases = [
            {
                "name": "Exact Match",
                "capabilities": ["python", "testing"],
                "description": "Looking for exact capability matches"
            },
            {
                "name": "Specialized Skills",
                "capabilities": ["machine_learning", "data_science"],
                "description": "Looking for specialized ML expertise"
            },
            {
                "name": "Mixed Requirements",
                "capabilities": ["python", "security", "docker"],
                "description": "Need combination of different skills"
            },
            {
                "name": "Common Skills",
                "capabilities": ["git", "documentation"],
                "description": "Looking for basic development skills"
            }
        ]
        
        for test_case in test_cases:
            logger.info(f"\nTesting: {test_case['name']}")
            logger.info(f"Required capabilities: {test_case['capabilities']}")
            
            matches = requester.find_agents_for_capabilities(test_case["capabilities"])
            
            if matches:
                logger.info(f"Found {len(matches)} matches:")
                for match in matches:
                    agent_caps = set(match["capabilities"])
                    required_caps = set(test_case["capabilities"])
                    overlap = agent_caps.intersection(required_caps)
                    
                    logger.info(f"  - {match['agent_id']}: {match['match_score']:.3f} "
                               f"(has: {list(overlap)}, collab: {match['collaboration_score']:.1f})")
            else:
                logger.info("  No matches found")
    
    async def demo_urgency_levels(self):
        """Demonstrate different urgency levels"""
        logger.info("\n" + "="*60)
        logger.info("DEMO: Help Request Urgency Levels")
        logger.info("="*60)
        
        requester = self.clients["python_expert"]
        
        urgency_tests = [
            (HelpUrgency.LOW, "Code review for non-critical feature"),
            (HelpUrgency.NORMAL, "Help with implementing new functionality"),
            (HelpUrgency.HIGH, "Production issue needs investigation"),
            (HelpUrgency.CRITICAL, "System down! Need immediate assistance!")
        ]
        
        for urgency, description in urgency_tests:
            logger.info(f"\nCreating {urgency} priority request...")
            
            request_id = await requester.send_help_request(
                required_capabilities=["python", "debugging"],
                description=description,
                urgency=urgency
            )
            
            # Show how urgency affects message priority
            help_request = requester.help_system.active_requests[request_id]
            message = requester.help_system.create_help_request_message(help_request)
            
            logger.info(f"  Request ID: {request_id}")
            logger.info(f"  Message priority: {message.priority} (1=highest, 10=lowest)")
            logger.info(f"  Description: {description}")
    
    async def demo_statistics_tracking(self):
        """Demonstrate statistics and metrics tracking"""
        logger.info("\n" + "="*60)
        logger.info("DEMO: Statistics and Metrics Tracking")
        logger.info("="*60)
        
        # Get initial statistics
        requester = self.clients["junior_developer"]
        initial_stats = requester.get_help_system_stats()
        
        logger.info("Initial Help System Statistics:")
        logger.info(f"  Total requests created: {initial_stats['requests_created']}")
        logger.info(f"  Active requests: {initial_stats['active_requests']}")
        logger.info(f"  Collaborations started: {initial_stats['collaborations_started']}")
        logger.info(f"  Collaborations completed: {initial_stats['collaborations_completed']}")
        
        # Show agent registry statistics
        registry_stats = requester.get_discovery_stats()
        logger.info(f"\nAgent Registry Statistics:")
        logger.info(f"  Total agents discovered: {registry_stats['total_agents_discovered']}")
        logger.info(f"  Active agents: {registry_stats['active_agents']}")
        logger.info(f"  Unique capabilities: {registry_stats['unique_capabilities']}")
        
        # Show capability distribution
        if 'capability_distribution' in registry_stats:
            logger.info("\nCapability Distribution:")
            for capability, count in registry_stats['capability_distribution'].items():
                logger.info(f"  {capability}: {count} agents")
        
        # Show collaboration scores
        logger.info("\nAgent Collaboration Scores:")
        for agent_id, client in self.clients.items():
            if agent_id in client.agent_registry.agents:
                agent = client.agent_registry.agents[agent_id]
                logger.info(f"  {agent_id}: {agent.collaboration_score:.1f}")
    
    async def run_demo(self):
        """Run the complete help system demo"""
        try:
            await self.setup_demo_environment()
            
            logger.info("\n🚀 Starting Beast Mode Help System Demo")
            logger.info("This demo showcases the help wanted system functionality")
            
            await self.demo_basic_help_request()
            await asyncio.sleep(0.5)
            
            await self.demo_multiple_helpers()
            await asyncio.sleep(0.5)
            
            await self.demo_capability_matching()
            await asyncio.sleep(0.5)
            
            await self.demo_urgency_levels()
            await asyncio.sleep(0.5)
            
            await self.demo_statistics_tracking()
            
            logger.info("\n✅ Demo completed successfully!")
            logger.info("\nThe help system demonstrates:")
            logger.info("  ✓ Intelligent capability matching")
            logger.info("  ✓ Multi-agent collaboration support")
            logger.info("  ✓ Urgency-based prioritization")
            logger.info("  ✓ Comprehensive statistics tracking")
            logger.info("  ✓ Robust error handling")
            
        except Exception as e:
            logger.error(f"Demo failed: {e}")
            raise


async def main():
    """Main demo function"""
    demo = HelpSystemDemo()
    await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main())