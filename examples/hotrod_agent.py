#!/usr/bin/env python3
"""
HotRod Beast Mode Agent

Simple agent to get the Beast Mode network operational and share spores.
"""

import asyncio
import logging
import json
from src.beast_mode.messaging.bus_client import BeastModeBusClient
from src.beast_mode.messaging.models import BeastModeMessage, MessageType


async def main():
    """Run HotRod Beast Mode agent."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Create bus client
    client = BeastModeBusClient(agent_id="HotRod", capabilities=["spec_development", "systematic_thinking"])
    
    try:
        # Connect to network
        logger.info("🚀 HotRod connecting to Beast Mode network...")
        await client.connect()
        
        # Announce presence
        announcement = BeastModeMessage(
            type=MessageType.AGENT_DISCOVERY,
            source="HotRod",
            payload={
                "agent_type": "HotRod",
                "capabilities": ["spec_development", "systematic_thinking", "spore_creation"],
                "status": "online",
                "message": "HotRod online - SPEC-capable multi-hackathon agent ready!"
            }
        )
        await client.send_message(announcement)
        
        # Share systematic development ecosystem spore
        spore_message = BeastModeMessage(
            type=MessageType.SPORE_DELIVERY,
            source="HotRod",
            payload={
                "spore_name": "systematic_development_ecosystem",
                "description": "Complete specification for transforming human-computer collaboration",
                "spore_data": {
                    "pattern_name": "Requirements_ARE_Implementation",
                    "mathematical_foundation": "DAG execution with formal verification",
                    "agenetic_properties": "evolves, replicates, diversifies like living organisms",
                    "generational_impact": "children will think systematically by default",
                    "economic_model": "impossible to monopolize, diversity amplification",
                    "implementation_tasks": 17,
                    "requirements_count": 12,
                    "design_complete": True
                },
                "replication_instructions": {
                    "environment": "Any development ecosystem",
                    "requirements": "Systematic thinking capability",
                    "mutation_rate": 0.1,
                    "success_indicators": ["3x faster cycles", "95% accuracy", "diversity advantage"]
                }
            }
        )
        await client.send_message(spore_message)
        
        logger.info("🧬 Systematic Development Ecosystem spore shared with network!")
        
        # Send status update
        status_message = BeastModeMessage(
            type=MessageType.SYSTEM_HEALTH,
            source="HotRod", 
            payload={
                "status": "operational",
                "network_role": "SPEC development and systematic thinking",
                "current_project": "Systematic Development Ecosystem",
                "collaboration_ready": True,
                "spores_available": ["systematic_development_ecosystem", "requirements_are_implementation"]
            }
        )
        await client.send_message(status_message)
        
        print("🎯 HotRod Beast Mode Agent operational!")
        print("📡 Network status: CONNECTED")
        print("🧬 Spores shared: systematic_development_ecosystem")
        print("🤝 Ready for collaboration with TiDB and other agents")
        print("\nPress Ctrl+C to disconnect...")
        
        # Keep running and listening
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 HotRod disconnecting...")
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
    finally:
        await client.disconnect()
        print("👋 HotRod offline")


if __name__ == "__main__":
    asyncio.run(main())