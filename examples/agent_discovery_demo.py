#!/usr/bin/env python3
"""
Beast Mode Agent Discovery Demo

Demonstrates the agent discovery protocol with multiple agents discovering
each other and finding agents with specific capabilities.
"""

import asyncio
import logging
from typing import List
from src.beast_mode.messaging import BeastModeBusClient, DiscoveredAgent

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def create_agent_network() -> List[BeastModeBusClient]:
    """Create a network of agents with different capabilities"""

    agents = [
        BeastModeBusClient(
            agent_id="python_expert",
            capabilities=["python", "testing", "debugging", "code_review"],
        ),
        BeastModeBusClient(
            agent_id="devops_specialist",
            capabilities=["devops", "kubernetes", "docker", "monitoring", "ci_cd"],
        ),
        BeastModeBusClient(
            agent_id="fullstack_dev",
            capabilities=[
                "python",
                "javascript",
                "react",
                "nodejs",
                "testing",
                "frontend",
            ],
        ),
        BeastModeBusClient(
            agent_id="data_scientist",
            capabilities=[
                "python",
                "machine_learning",
                "data_analysis",
                "pandas",
                "tensorflow",
            ],
        ),
        BeastModeBusClient(
            agent_id="security_expert",
            capabilities=[
                "security",
                "penetration_testing",
                "compliance",
                "audit",
                "encryption",
            ],
        ),
    ]

    # Connect all agents
    connected_agents = []
    for agent in agents:
        if await agent.connect():
            connected_agents.append(agent)
            logger.info(
                f"Connected {agent.agent_id} with capabilities: {agent.capabilities}"
            )
        else:
            logger.error(f"Failed to connect {agent.agent_id}")

    return connected_agents


async def demonstrate_discovery(agents: List[BeastModeBusClient]):
    """Demonstrate agent discovery process"""

    if len(agents) < 2:
        logger.error("Need at least 2 agents for discovery demo")
        return

    logger.info("\n" + "=" * 60)
    logger.info("AGENT DISCOVERY DEMONSTRATION")
    logger.info("=" * 60)

    # Start listening on all agents
    listen_tasks = []
    for agent in agents:
        task = asyncio.create_task(agent.listen_for_messages())
        listen_tasks.append(task)

    await asyncio.sleep(0.2)

    # Each agent announces its presence
    logger.info("\nPhase 1: Agent Presence Announcements")
    logger.info("-" * 40)

    for agent in agents:
        logger.info(f"{agent.agent_id} announcing presence...")
        await agent.announce_presence()
        await asyncio.sleep(0.3)  # Small delay between announcements

    # Wait for all discovery messages to be processed
    logger.info("\nWaiting for discovery messages to be processed...")
    await asyncio.sleep(2.0)

    # Stop all listeners
    for agent in agents:
        agent.is_listening = False
    await asyncio.sleep(0.1)
    for task in listen_tasks:
        task.cancel()

    logger.info("\nPhase 2: Discovery Results")
    logger.info("-" * 40)

    # Show what each agent discovered
    for agent in agents:
        discovered = agent.get_discovered_agents()
        logger.info(f"\n{agent.agent_id} discovered {len(discovered)} agents:")
        for discovered_agent in discovered:
            logger.info(
                f"  - {discovered_agent.agent_id}: {discovered_agent.capabilities.capabilities}"
            )


async def demonstrate_capability_matching(agents: List[BeastModeBusClient]):
    """Demonstrate finding agents with specific capabilities"""

    if len(agents) < 3:
        logger.error("Need at least 3 agents for capability matching demo")
        return

    logger.info("\n" + "=" * 60)
    logger.info("CAPABILITY MATCHING DEMONSTRATION")
    logger.info("=" * 60)

    # Use first agent as the searcher
    searcher = agents[0]

    # Test various capability searches
    test_capabilities = [
        ["python"],
        ["devops"],
        ["testing"],
        ["python", "testing"],  # Agents with ANY of these
        ["security", "compliance"],
        ["machine_learning"],
        ["nonexistent_capability"],
    ]

    logger.info(
        f"\nUsing {searcher.agent_id} to search for agents with specific capabilities:"
    )
    logger.info("-" * 60)

    for capabilities in test_capabilities:
        # Find agents with ANY of the capabilities
        matching_agents = searcher.find_agents_with_capabilities(capabilities)

        logger.info(f"\nSearching for agents with ANY of: {capabilities}")
        if matching_agents:
            logger.info(f"Found {len(matching_agents)} matching agents:")
            for agent in matching_agents:
                matching_caps = set(agent.capabilities.capabilities).intersection(
                    set(capabilities)
                )
                logger.info(f"  - {agent.agent_id}: matches {list(matching_caps)}")
        else:
            logger.info("  No matching agents found")

        # Find agents with ALL of the capabilities (if multiple)
        if len(capabilities) > 1:
            all_matching_agents = searcher.find_agents_with_all_capabilities(
                capabilities
            )
            logger.info(f"Agents with ALL capabilities {capabilities}:")
            if all_matching_agents:
                for agent in all_matching_agents:
                    logger.info(f"  - {agent.agent_id}: has all required capabilities")
            else:
                logger.info("  No agents have all required capabilities")


async def demonstrate_help_request(agents: List[BeastModeBusClient]):
    """Demonstrate help request workflow"""

    if len(agents) < 3:
        logger.error("Need at least 3 agents for help request demo")
        return

    logger.info("\n" + "=" * 60)
    logger.info("HELP REQUEST DEMONSTRATION")
    logger.info("=" * 60)

    # Use first agent as requester
    requester = agents[0]

    # Start listening on all agents
    listen_tasks = []
    for agent in agents:
        task = asyncio.create_task(agent.listen_for_messages())
        listen_tasks.append(task)

    await asyncio.sleep(0.2)

    # Send help requests for different capabilities
    help_requests = [
        (["devops", "kubernetes"], "Need help with Kubernetes deployment"),
        (["machine_learning", "tensorflow"], "Need help with ML model training"),
        (["security", "audit"], "Need security audit for new feature"),
        (["javascript", "react"], "Need help with React component optimization"),
    ]

    logger.info(f"\n{requester.agent_id} sending help requests:")
    logger.info("-" * 50)

    for capabilities, description in help_requests:
        logger.info(f"\nHelp request: {description}")
        logger.info(f"Required capabilities: {capabilities}")

        # Find potential helpers first
        potential_helpers = requester.find_agents_with_capabilities(capabilities)
        if potential_helpers:
            logger.info(f"Potential helpers found:")
            for helper in potential_helpers:
                matching_caps = set(helper.capabilities.capabilities).intersection(
                    set(capabilities)
                )
                logger.info(
                    f"  - {helper.agent_id}: can help with {list(matching_caps)}"
                )

            # Send the help request
            await requester.send_help_request(capabilities, description)
            logger.info("Help request sent to network")
        else:
            logger.info("No potential helpers found for this request")

        await asyncio.sleep(0.5)

    # Wait for responses
    await asyncio.sleep(1.0)

    # Stop listeners
    for agent in agents:
        agent.is_listening = False
    await asyncio.sleep(0.1)
    for task in listen_tasks:
        task.cancel()

    # Show statistics
    logger.info(f"\nHelp request statistics:")
    logger.info(
        f"  {requester.agent_id} sent {requester.stats['messages_sent']} messages"
    )

    for agent in agents[1:]:
        if agent.stats["messages_sent"] > 0:
            logger.info(
                f"  {agent.agent_id} sent {agent.stats['messages_sent']} responses"
            )


async def show_network_statistics(agents: List[BeastModeBusClient]):
    """Show network-wide statistics"""

    logger.info("\n" + "=" * 60)
    logger.info("NETWORK STATISTICS")
    logger.info("=" * 60)

    total_discoveries = 0
    total_capabilities = set()

    for agent in agents:
        stats = agent.get_discovery_stats()
        logger.info(f"\n{agent.agent_id} statistics:")
        logger.info(f"  - Active agents discovered: {stats['active_agents']}")
        logger.info(
            f"  - Total discovery messages processed: {stats['discovery_messages_processed']}"
        )
        logger.info(f"  - Unique capabilities known: {stats['unique_capabilities']}")
        logger.info(f"  - Messages sent: {agent.stats['messages_sent']}")
        logger.info(f"  - Messages received: {agent.stats['messages_received']}")

        total_discoveries += stats["active_agents"]
        if "capability_distribution" in stats:
            total_capabilities.update(stats["capability_distribution"].keys())

    logger.info(f"\nNetwork Summary:")
    logger.info(f"  - Total agents: {len(agents)}")
    logger.info(
        f"  - Average discoveries per agent: {total_discoveries / len(agents):.1f}"
    )
    logger.info(f"  - Unique capabilities in network: {len(total_capabilities)}")
    logger.info(f"  - All capabilities: {sorted(total_capabilities)}")


async def main():
    """Main demonstration function"""

    logger.info("Beast Mode Agent Discovery Demo")
    logger.info("Connecting to Redis and creating agent network...")

    try:
        # Create agent network
        agents = await create_agent_network()

        if len(agents) < 2:
            logger.error("Failed to create sufficient agent network")
            return

        logger.info(f"Successfully created network with {len(agents)} agents")

        # Run demonstrations
        await demonstrate_discovery(agents)
        await demonstrate_capability_matching(agents)
        await demonstrate_help_request(agents)
        await show_network_statistics(agents)

        logger.info("\n" + "=" * 60)
        logger.info("DEMONSTRATION COMPLETE")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise

    finally:
        # Cleanup
        logger.info("\nCleaning up agent connections...")
        for agent in agents:
            try:
                await agent.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting {agent.agent_id}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
