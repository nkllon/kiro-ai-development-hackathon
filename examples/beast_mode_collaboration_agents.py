#!/usr/bin/env python3
"""
Beast Mode Collaboration Agents - Reference Implementations

Demonstrates systematic agent collaboration with real-world use cases:
- Cost optimization agent
- Deployment specialist agent  
- Code quality mentor agent
- Security guardian agent

These agents showcase Beast Mode principles in action.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod

from src.beast_mode.messaging.message_models import (
    BeastModeMessage, MessageType, AgentCapability, AgentCapabilities,
    create_agent_announcement, create_help_request, create_heartbeat
)
from src.beast_mode.messaging.redis_foundation import RedisFoundation, RedisConfig
from src.beast_mode.core.reflective_module import ReflectiveModule


@dataclass
class AgentMetrics:
    """Agent performance and collaboration metrics."""
    tasks_completed: int = 0
    help_requests_handled: int = 0
    collaborations_initiated: int = 0
    average_response_time: float = 0.0
    success_rate: float = 1.0
    uptime_hours: float = 0.0


class BeastModeAgent(ReflectiveModule, ABC):
    """
    Abstract base class for Beast Mode collaboration agents.
    
    Implements systematic collaboration patterns with proper health monitoring,
    capability management, and Beast Mode compliance.
    """
    
    def __init__(self, agent_id: str, agent_name: str, capabilities: List[AgentCapability]):
        """Initialize Beast Mode agent."""
        super().__init__()
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.capabilities_list = capabilities
        self.redis_foundation: Optional[RedisFoundation] = None
        self.is_running = False
        self.start_time = datetime.now()
        self.metrics = AgentMetrics()
        self.logger = logging.getLogger(f"{__name__}.{agent_id}")
        
        # Create agent capabilities model
        self.capabilities = AgentCapabilities(
            agent_id=agent_id,
            agent_name=agent_name,
            capabilities=capabilities,
            specializations=self.get_specializations(),
            max_concurrent_tasks=self.get_max_concurrent_tasks()
        )
    
    @abstractmethod
    def get_specializations(self) -> List[str]:
        """Get agent specializations."""
        pass
    
    @abstractmethod
    def get_max_concurrent_tasks(self) -> int:
        """Get maximum concurrent tasks for this agent."""
        pass
    
    @abstractmethod
    async def handle_help_request(self, message: BeastModeMessage) -> Optional[BeastModeMessage]:
        """Handle incoming help request."""
        pass
    
    @abstractmethod
    async def perform_specialized_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform agent's specialized task."""
        pass
    
    async def initialize(self, redis_config: Optional[RedisConfig] = None) -> bool:
        """Initialize agent with Redis connection."""
        try:
            # Initialize Redis foundation
            self.redis_foundation = RedisFoundation(redis_config or RedisConfig())
            if not await self.redis_foundation.initialize():
                self.logger.error("Failed to initialize Redis connection")
                return False
            
            # Subscribe to relevant channels
            await self.redis_foundation.subscribe("beast_mode_general", self._handle_message)
            await self.redis_foundation.subscribe("help_requests", self._handle_help_request)
            await self.redis_foundation.subscribe(f"direct_{self.agent_id}", self._handle_direct_message)
            
            # Announce presence
            announcement = create_agent_announcement(self.agent_id, self.capabilities)
            await self.redis_foundation.publish("beast_mode_general", announcement.to_dict())
            
            self.is_running = True
            self.logger.info(f"Agent {self.agent_name} initialized and announced")
            
            # Start background tasks
            asyncio.create_task(self._heartbeat_loop())
            asyncio.create_task(self._health_monitoring_loop())
            
            return True
            
        except Exception as e:
            self.logger.error(f"Agent initialization failed: {str(e)}")
            return False
    
    async def _handle_message(self, message_data: Dict[str, Any]):
        """Handle incoming general messages."""
        try:
            message = BeastModeMessage.from_dict(message_data)
            
            # Ignore own messages
            if message.sender_id == self.agent_id:
                return
            
            # Route message based on type
            if message.message_type == MessageType.HELP_REQUEST:
                await self._process_help_request(message)
            elif message.message_type == MessageType.AGENT_ANNOUNCEMENT:
                await self._process_agent_announcement(message)
            elif message.message_type == MessageType.COLLABORATION_INVITE:
                await self._process_collaboration_invite(message)
                
        except Exception as e:
            self.logger.error(f"Error handling message: {str(e)}")
    
    async def _handle_help_request(self, message_data: Dict[str, Any]):
        """Handle help request messages."""
        try:
            message = BeastModeMessage.from_dict(message_data)
            await self._process_help_request(message)
        except Exception as e:
            self.logger.error(f"Error handling help request: {str(e)}")
    
    async def _handle_direct_message(self, message_data: Dict[str, Any]):
        """Handle direct messages to this agent."""
        try:
            message = BeastModeMessage.from_dict(message_data)
            self.logger.info(f"Received direct message from {message.sender_id}: {message.subject}")
            
            # Process based on message type
            if message.message_type == MessageType.TASK_ASSIGNMENT:
                await self._process_task_assignment(message)
            elif message.message_type == MessageType.COLLABORATION_INVITE:
                await self._process_collaboration_invite(message)
                
        except Exception as e:
            self.logger.error(f"Error handling direct message: {str(e)}")
    
    async def _process_help_request(self, message: BeastModeMessage):
        """Process help request and respond if capable."""
        # Check if we can help
        if not self._can_handle_request(message):
            return
        
        start_time = time.time()
        
        try:
            # Generate response
            response = await self.handle_help_request(message)
            
            if response:
                # Send response
                await self.redis_foundation.publish(
                    f"direct_{message.sender_id}",
                    response.to_dict()
                )
                
                # Update metrics
                self.metrics.help_requests_handled += 1
                response_time = time.time() - start_time
                self._update_average_response_time(response_time)
                
                self.logger.info(f"Responded to help request from {message.sender_id}")
            
        except Exception as e:
            self.logger.error(f"Error processing help request: {str(e)}")
    
    async def _process_agent_announcement(self, message: BeastModeMessage):
        """Process agent announcement."""
        self.logger.info(f"New agent announced: {message.content.get('capabilities', {}).get('agent_name', 'Unknown')}")
    
    async def _process_collaboration_invite(self, message: BeastModeMessage):
        """Process collaboration invitation."""
        # Simple acceptance logic - can be overridden
        if self.capabilities.current_load < self.capabilities.max_concurrent_tasks:
            response = message.create_reply(
                sender_id=self.agent_id,
                content={"status": "accepted", "message": "I'm available to collaborate"},
                message_type=MessageType.COLLABORATION_ACCEPT
            )
        else:
            response = message.create_reply(
                sender_id=self.agent_id,
                content={"status": "declined", "reason": "Currently at capacity"},
                message_type=MessageType.COLLABORATION_DECLINE
            )
        
        await self.redis_foundation.publish(f"direct_{message.sender_id}", response.to_dict())
    
    async def _process_task_assignment(self, message: BeastModeMessage):
        """Process task assignment."""
        try:
            task_data = message.content.get("task_data", {})
            result = await self.perform_specialized_task(task_data)
            
            # Send completion notification
            completion = message.create_reply(
                sender_id=self.agent_id,
                content={"status": "completed", "result": result},
                message_type=MessageType.TASK_COMPLETION
            )
            
            await self.redis_foundation.publish(f"direct_{message.sender_id}", completion.to_dict())
            self.metrics.tasks_completed += 1
            
        except Exception as e:
            # Send failure notification
            failure = message.create_reply(
                sender_id=self.agent_id,
                content={"status": "failed", "error": str(e)},
                message_type=MessageType.TASK_FAILURE
            )
            
            await self.redis_foundation.publish(f"direct_{message.sender_id}", failure.to_dict())
    
    def _can_handle_request(self, message: BeastModeMessage) -> bool:
        """Check if agent can handle the help request."""
        required_caps = message.capabilities_required
        if not required_caps:
            return True
        
        return any(cap in self.capabilities_list for cap in required_caps)
    
    def _update_average_response_time(self, response_time: float):
        """Update average response time metric."""
        total_requests = self.metrics.help_requests_handled
        if total_requests == 1:
            self.metrics.average_response_time = response_time
        else:
            # Running average
            self.metrics.average_response_time = (
                (self.metrics.average_response_time * (total_requests - 1) + response_time) / total_requests
            )
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeat messages."""
        while self.is_running:
            try:
                status_info = {
                    "agent_name": self.agent_name,
                    "capabilities": [cap.value for cap in self.capabilities_list],
                    "current_load": self.capabilities.current_load,
                    "max_tasks": self.capabilities.max_concurrent_tasks,
                    "metrics": {
                        "tasks_completed": self.metrics.tasks_completed,
                        "help_requests_handled": self.metrics.help_requests_handled,
                        "average_response_time": self.metrics.average_response_time,
                        "uptime_hours": (datetime.now() - self.start_time).total_seconds() / 3600
                    }
                }
                
                heartbeat = create_heartbeat(self.agent_id, status_info)
                await self.redis_foundation.publish("beast_mode_heartbeats", heartbeat.to_dict())
                
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Heartbeat error: {str(e)}")
                await asyncio.sleep(5)
    
    async def _health_monitoring_loop(self):
        """Monitor agent health and Redis connection."""
        while self.is_running:
            try:
                # Check Redis health
                if self.redis_foundation:
                    await self.redis_foundation.health_check()
                
                # Update uptime
                self.metrics.uptime_hours = (datetime.now() - self.start_time).total_seconds() / 3600
                
                await asyncio.sleep(60)  # Health check every minute
                
            except Exception as e:
                self.logger.error(f"Health monitoring error: {str(e)}")
                await asyncio.sleep(10)
    
    async def shutdown(self):
        """Gracefully shutdown the agent."""
        self.is_running = False
        
        # Send shutdown notice
        if self.redis_foundation:
            shutdown_notice = BeastModeMessage(
                message_type=MessageType.SHUTDOWN_NOTICE,
                sender_id=self.agent_id,
                content={"message": f"Agent {self.agent_name} is shutting down"}
            )
            
            await self.redis_foundation.publish("beast_mode_general", shutdown_notice.to_dict())
            await self.redis_foundation.shutdown()
        
        self.logger.info(f"Agent {self.agent_name} shutdown complete")
    
    # ReflectiveModule interface
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for Beast Mode monitoring."""
        return {
            "module": f"BeastModeAgent_{self.agent_id}",
            "agent_name": self.agent_name,
            "status": "running" if self.is_running else "stopped",
            "healthy": self.is_running and (self.redis_foundation is not None),
            "uptime_hours": self.metrics.uptime_hours,
            "tasks_completed": self.metrics.tasks_completed,
            "help_requests_handled": self.metrics.help_requests_handled,
            "current_load": self.capabilities.current_load,
            "redis_connected": self.redis_foundation.status.value if self.redis_foundation else "disconnected"
        }


class CostOptimizationAgent(BeastModeAgent):
    """
    Specialized agent for cloud cost optimization and resource management.
    
    Demonstrates systematic cost analysis and optimization recommendations
    using Beast Mode collaboration patterns.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="cost_optimizer_001",
            agent_name="Cost Optimization Specialist",
            capabilities=[
                AgentCapability.COST_OPTIMIZATION,
                AgentCapability.INFRASTRUCTURE_MANAGEMENT,
                AgentCapability.PERFORMANCE_ANALYSIS,
                AgentCapability.DATA_ANALYSIS
            ]
        )
    
    def get_specializations(self) -> List[str]:
        """Get cost optimization specializations."""
        return [
            "AWS Cost Analysis",
            "GCP Billing Optimization", 
            "Resource Right-sizing",
            "Reserved Instance Planning",
            "Spot Instance Management"
        ]
    
    def get_max_concurrent_tasks(self) -> int:
        """Cost analysis can handle multiple concurrent reviews."""
        return 5
    
    async def handle_help_request(self, message: BeastModeMessage) -> Optional[BeastModeMessage]:
        """Handle cost optimization help requests."""
        content = message.content
        description = content.get("description", "")
        
        if any(keyword in description.lower() for keyword in ["cost", "billing", "expensive", "optimize"]):
            response_content = {
                "analysis_type": "cost_optimization",
                "recommendations": [
                    "Review resource utilization patterns",
                    "Consider reserved instances for steady workloads",
                    "Implement auto-scaling policies",
                    "Analyze storage costs and lifecycle policies"
                ],
                "next_steps": "I can perform detailed cost analysis if you share your infrastructure details",
                "estimated_savings": "15-30% typical optimization potential"
            }
            
            return message.create_reply(
                sender_id=self.agent_id,
                content=response_content,
                message_type=MessageType.HELP_RESPONSE
            )
        
        return None
    
    async def perform_specialized_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform cost optimization analysis."""
        # Simulate cost analysis
        await asyncio.sleep(2)  # Simulate analysis time
        
        return {
            "analysis_completed": True,
            "current_monthly_cost": task_data.get("current_cost", 1000),
            "optimized_monthly_cost": task_data.get("current_cost", 1000) * 0.75,
            "savings_percentage": 25,
            "optimization_actions": [
                "Right-size EC2 instances based on utilization",
                "Implement S3 lifecycle policies",
                "Use Spot instances for batch workloads",
                "Enable CloudWatch cost anomaly detection"
            ],
            "implementation_timeline": "2-4 weeks",
            "confidence_score": 0.85
        }


class DeploymentSpecialistAgent(BeastModeAgent):
    """
    Specialized agent for deployment automation and DevOps best practices.
    
    Demonstrates systematic deployment management with Beast Mode principles.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="deployment_specialist_001", 
            agent_name="Deployment Automation Specialist",
            capabilities=[
                AgentCapability.DEPLOYMENT_MANAGEMENT,
                AgentCapability.CI_CD_CONFIGURATION,
                AgentCapability.INFRASTRUCTURE_MANAGEMENT,
                AgentCapability.MONITORING_SETUP
            ]
        )
    
    def get_specializations(self) -> List[str]:
        """Get deployment specializations."""
        return [
            "Kubernetes Deployments",
            "Docker Containerization",
            "CI/CD Pipeline Design",
            "Infrastructure as Code",
            "Blue-Green Deployments"
        ]
    
    def get_max_concurrent_tasks(self) -> int:
        """Deployment tasks require focused attention."""
        return 3
    
    async def handle_help_request(self, message: BeastModeMessage) -> Optional[BeastModeMessage]:
        """Handle deployment-related help requests."""
        content = message.content
        description = content.get("description", "")
        
        deployment_keywords = ["deploy", "deployment", "ci/cd", "pipeline", "kubernetes", "docker"]
        if any(keyword in description.lower() for keyword in deployment_keywords):
            response_content = {
                "deployment_strategy": "systematic_deployment",
                "recommendations": [
                    "Implement Infrastructure as Code (Terraform/CloudFormation)",
                    "Set up automated testing in CI/CD pipeline",
                    "Use blue-green deployment for zero-downtime",
                    "Implement proper monitoring and alerting"
                ],
                "best_practices": [
                    "Version all infrastructure changes",
                    "Use immutable infrastructure patterns",
                    "Implement proper rollback mechanisms",
                    "Monitor deployment metrics"
                ],
                "next_steps": "I can help design your deployment pipeline architecture"
            }
            
            return message.create_reply(
                sender_id=self.agent_id,
                content=response_content,
                message_type=MessageType.HELP_RESPONSE
            )
        
        return None
    
    async def perform_specialized_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform deployment configuration task."""
        # Simulate deployment setup
        await asyncio.sleep(3)  # Simulate setup time
        
        return {
            "deployment_configured": True,
            "pipeline_stages": [
                "Source checkout",
                "Build and test",
                "Security scanning", 
                "Deploy to staging",
                "Integration tests",
                "Deploy to production"
            ],
            "deployment_strategy": "blue_green",
            "rollback_time": "< 2 minutes",
            "monitoring_enabled": True,
            "estimated_deployment_time": "8-12 minutes",
            "success_rate_target": "99.5%"
        }


class CodeQualityMentorAgent(BeastModeAgent):
    """
    Specialized agent for code quality mentoring and best practices.
    
    Demonstrates systematic code review and mentoring with Beast Mode collaboration.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="code_mentor_001",
            agent_name="Code Quality Mentor",
            capabilities=[
                AgentCapability.CODE_ANALYSIS,
                AgentCapability.CODE_REVIEW,
                AgentCapability.MENTORING,
                AgentCapability.REFACTORING,
                AgentCapability.TEST_GENERATION
            ]
        )
    
    def get_specializations(self) -> List[str]:
        """Get code quality specializations."""
        return [
            "Python Best Practices",
            "Clean Code Principles",
            "Test-Driven Development",
            "Code Architecture Review",
            "Performance Optimization"
        ]
    
    def get_max_concurrent_tasks(self) -> int:
        """Code review requires detailed attention."""
        return 4
    
    async def handle_help_request(self, message: BeastModeMessage) -> Optional[BeastModeMessage]:
        """Handle code quality help requests."""
        content = message.content
        description = content.get("description", "")
        
        code_keywords = ["code", "review", "refactor", "quality", "best practices", "clean code"]
        if any(keyword in description.lower() for keyword in code_keywords):
            response_content = {
                "review_type": "code_quality_analysis",
                "focus_areas": [
                    "Code structure and organization",
                    "Naming conventions and clarity",
                    "Function and class design",
                    "Error handling patterns",
                    "Test coverage and quality"
                ],
                "mentoring_approach": "systematic_improvement",
                "learning_resources": [
                    "Clean Code principles",
                    "SOLID design patterns",
                    "Test-driven development",
                    "Code review best practices"
                ],
                "next_steps": "Share your code and I'll provide detailed feedback with improvement suggestions"
            }
            
            return message.create_reply(
                sender_id=self.agent_id,
                content=response_content,
                message_type=MessageType.HELP_RESPONSE
            )
        
        return None
    
    async def perform_specialized_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform code quality analysis."""
        # Simulate code analysis
        await asyncio.sleep(2.5)  # Simulate analysis time
        
        return {
            "analysis_completed": True,
            "overall_quality_score": 7.5,
            "strengths": [
                "Good function naming conventions",
                "Proper error handling in critical paths",
                "Adequate test coverage (78%)"
            ],
            "improvement_areas": [
                "Reduce function complexity (3 functions > 20 lines)",
                "Add docstrings to public methods",
                "Implement input validation",
                "Consider extracting common patterns"
            ],
            "refactoring_suggestions": [
                "Extract utility functions for repeated logic",
                "Use dependency injection for better testability",
                "Implement proper logging throughout"
            ],
            "learning_recommendations": [
                "Study SOLID principles for better design",
                "Practice test-driven development",
                "Learn about design patterns"
            ],
            "estimated_improvement_time": "1-2 weeks"
        }


# Example usage and demonstration
async def demonstrate_beast_mode_collaboration():
    """
    Demonstrate Beast Mode agent collaboration in action.
    
    Shows systematic agent interaction, help requests, and collaboration patterns.
    """
    print("🚀 Beast Mode Agent Collaboration Demo")
    print("=" * 50)
    
    # Initialize agents
    agents = [
        CostOptimizationAgent(),
        DeploymentSpecialistAgent(), 
        CodeQualityMentorAgent()
    ]
    
    # Start all agents
    print("Starting Beast Mode agents...")
    for agent in agents:
        success = await agent.initialize()
        if success:
            print(f"✅ {agent.agent_name} online")
        else:
            print(f"❌ {agent.agent_name} failed to start")
    
    # Wait for agents to settle
    await asyncio.sleep(2)
    
    # Simulate help requests
    print("\n📢 Simulating collaboration scenarios...")
    
    # Cost optimization request
    cost_request = create_help_request(
        sender_id="project_manager",
        required_capabilities=[AgentCapability.COST_OPTIMIZATION],
        description="Our AWS bill is getting expensive, need cost optimization help",
        priority="high"
    )
    
    # Deployment help request
    deploy_request = create_help_request(
        sender_id="developer_001",
        required_capabilities=[AgentCapability.DEPLOYMENT_MANAGEMENT],
        description="Need help setting up CI/CD pipeline for our new microservice",
        priority="normal"
    )
    
    # Code review request
    code_request = create_help_request(
        sender_id="junior_dev",
        required_capabilities=[AgentCapability.CODE_REVIEW],
        description="Can someone review my Python code for best practices?",
        priority="normal"
    )
    
    # Send requests through first agent's Redis connection
    if agents[0].redis_foundation:
        await agents[0].redis_foundation.publish("help_requests", cost_request.to_dict())
        await agents[0].redis_foundation.publish("help_requests", deploy_request.to_dict())
        await agents[0].redis_foundation.publish("help_requests", code_request.to_dict())
    
    print("📨 Help requests sent - agents will respond based on capabilities")
    
    # Let agents process requests
    await asyncio.sleep(5)
    
    # Show agent status
    print("\n📊 Agent Status:")
    for agent in agents:
        health = agent.get_health_status()
        print(f"  {health['agent_name']}: {health['status']} - "
              f"Tasks: {health['tasks_completed']}, "
              f"Help: {health['help_requests_handled']}")
    
    # Cleanup
    print("\n🔄 Shutting down agents...")
    for agent in agents:
        await agent.shutdown()
    
    print("✅ Beast Mode collaboration demo complete!")


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(demonstrate_beast_mode_collaboration())