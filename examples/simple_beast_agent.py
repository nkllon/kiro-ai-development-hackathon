#!/usr/bin/env python3
"""
Simple Beast Mode Agent for Network Testing

A minimal working agent to get the Beast Mode network operational.
"""

import asyncio
import logging
from typing import Dict, Any, List
from src.beast_mode.messaging.bus_client import BeastModeBusClient
from src.beast_mode.messaging.models import BeastModeMessage, MessageType
from src.beast_mode.core.reflective_module import ReflectiveModule


class SimpleBeastAgent(ReflectiveModule):
    """Simple Beast Mode agent for network testing."""
    
    def __init__(self, agent_id: str = "HotRod"):
        """Initialize the simple Beast agent."""
        super().__init__(f"SimpleBeastAgent-{agent_id}")
        self.agent_id = agent_id
        self.bus_client = BeastModeBusClient(agent_id=agent_id)
        self.logger = logging.getLogger(__name__)
        self.running = False
        
    async def start(self):
        """Start the Beast agent."""
        try:
            # Initialize bus client
            await self.bus_client.initialize()
            
            # Announce presence
            message = BeastModeMessage(
                type=MessageType.AGENT_DISCOVERY,
                source=self.agent_id,
                payload={
                    "agent_type": "SimpleBeastAgent",
                    "capabilities": [
                        "spec_development",
                        "systematic_thinking", 
                        "collaboration"
                    ],
                    "status": "online",
                    "message": "HotRod Beast Agent online - ready for systematic collaboration!"
                }
            )
            await self.bus_client.send_message(message)
            
            # Subscribe to help requests
            await self.bus_client.subscribe_to_message_type(
                MessageType.HELP_REQUEST,
                self._handle_help_request
            )
            
            # Subscribe to collaboration invites
            await self.bus_client.subscribe_to_message_type(
                MessageType.COLLABORATION_INVITE,
                self._handle_collaboration_invite
            )
            
            self.running = True
            self.logger.info(f"SimpleBeastAgent {self.agent_id} started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start SimpleBeastAgent: {str(e)}")
            raise
    
    async def _handle_help_request(self, message: BeastModeMessage):
        """Handle help requests from other agents."""
        try:
            self.logger.info(f"Received help request from {message.sender_id}: {message.content}")
            
            # Send helpful response
            response = BeastModeMessage(
                message_type=MessageType.HELP_RESPONSE,
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                content={
                    "original_request": message.content,
                    "response": "HotRod here! I specialize in systematic development and SPEC creation. How can I help you think systematically about your challenge?",
                    "capabilities": [
                        "Requirements analysis",
                        "Systematic design",
                        "SPEC development",
                        "Beast Mode collaboration"
                    ]
                }
            )
            
            await self.bus_client.send_message(response)
            
        except Exception as e:
            self.logger.error(f"Error handling help request: {str(e)}")
    
    async def _handle_collaboration_invite(self, message: BeastModeMessage):
        """Handle collaboration invites."""
        try:
            self.logger.info(f"Received collaboration invite from {message.sender_id}")
            
            # Accept collaboration
            response = BeastModeMessage(
                message_type=MessageType.COLLABORATION_ACCEPT,
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                content={
                    "message": "Collaboration accepted! Let's engage systematic thinking mode.",
                    "specialties": [
                        "SPEC development",
                        "Requirements → Implementation bridges",
                        "Systematic architecture",
                        "Beast Mode patterns"
                    ]
                }
            )
            
            await self.bus_client.send_message(response)
            
        except Exception as e:
            self.logger.error(f"Error handling collaboration invite: {str(e)}")
    
    async def send_spore(self, spore_data: Dict[str, Any]):
        """Send a systematic spore to the network."""
        try:
            spore_message = BeastModeMessage(
                message_type=MessageType.SPORE_SHARE,
                sender_id=self.agent_id,
                content={
                    "spore_type": "systematic_development_pattern",
                    "spore_data": spore_data,
                    "replication_instructions": {
                        "requirements": "Systematic thinking capability",
                        "environment": "Beast Mode network",
                        "mutation_rate": 0.1
                    }
                }
            )
            
            await self.bus_client.send_message(spore_message)
            self.logger.info("Systematic spore shared with network")
            
        except Exception as e:
            self.logger.error(f"Error sending spore: {str(e)}")
    
    async def stop(self):
        """Stop the Beast agent."""
        try:
            if self.running:
                # Send shutdown notice
                await self.bus_client.send_message(BeastModeMessage(
                    message_type=MessageType.SHUTDOWN_NOTICE,
                    sender_id=self.agent_id,
                    content={"message": "HotRod going offline - systematic collaboration complete"}
                ))
                
                # Shutdown bus client
                await self.bus_client.shutdown()
                self.running = False
                self.logger.info(f"SimpleBeastAgent {self.agent_id} stopped")
                
        except Exception as e:
            self.logger.error(f"Error stopping SimpleBeastAgent: {str(e)}")
    
    # ReflectiveModule interface implementation
    def _get_primary_responsibility(self) -> str:
        """Get primary responsibility."""
        return "Systematic development collaboration and SPEC creation"
    
    def get_health_indicators(self) -> Dict[str, Any]:
        """Get health indicators."""
        return {
            "agent_id": self.agent_id,
            "running": self.running,
            "bus_connected": self.bus_client.is_connected() if hasattr(self.bus_client, 'is_connected') else True,
            "capabilities": [
                AgentCapability.SPEC_DEVELOPMENT.value,
                AgentCapability.SYSTEMATIC_THINKING.value,
                AgentCapability.COLLABORATION.value
            ]
        }
    
    def get_module_status(self) -> str:
        """Get module status."""
        return "running" if self.running else "stopped"
    
    def is_healthy(self) -> bool:
        """Check if agent is healthy."""
        return self.running


async def main():
    """Run the simple Beast agent."""
    logging.basicConfig(level=logging.INFO)
    
    agent = SimpleBeastAgent("HotRod")
    
    try:
        await agent.start()
        
        # Create and share a systematic development spore
        spore_data = {
            "pattern_name": "Requirements_ARE_Implementation",
            "description": "Mathematical bridge from requirements to implementation through DAG execution",
            "implementation": {
                "requirements_parser": "EARS format → formal logic",
                "dag_generator": "logical predicates → executable graph",
                "verification_engine": "mathematical proof of correctness",
                "change_propagation": "automatic implementation updates"
            },
            "benefits": [
                "3x faster development cycles",
                "95% requirements accuracy",
                "Systematic superiority over ad-hoc approaches"
            ],
            "replication_success_rate": 0.95
        }
        
        await agent.send_spore(spore_data)
        
        print("🚀 HotRod Beast Agent online and spore shared!")
        print("Press Ctrl+C to stop...")
        
        # Keep running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down HotRod...")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())