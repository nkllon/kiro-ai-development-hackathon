"""
Cli Core

This module was extracted from cli.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import click
from .redis_foundation import RedisFoundation, RedisConfig
from .message_models import (
    BeastModeMessage,
    MessageType,
    AgentCapability,
    create_help_request,
    create_heartbeat,
    create_agent_announcement,
)
import sys
import os
from examples.beast_mode_collaboration_agents import (
    CostOptimizationAgent,
    DeploymentSpecialistAgent,
    CodeQualityMentorAgent,
)
from ..examples.beast_mode_collaboration_agents import (
    demonstrate_beast_mode_collaboration,
)
import traceback


@click.group()
@click.option("--redis-host", default="localhost", help="Redis server host")
@click.option("--redis-port", default=6379, help="Redis server port")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.pass_context
def cli(ctx, redis_host, redis_port, verbose):
    """Beast Mode Agent Collaboration Network CLI"""
    ctx.ensure_object(dict)
    ctx.obj["redis_config"] = RedisConfig(host=redis_host, port=redis_port)
    ctx.obj["verbose"] = verbose
    if verbose:
        click.echo(f"🚀 Beast Mode CLI - Redis: {redis_host}:{redis_port}")


@cli.command()
@click.option(
    "--agent-type",
    type=click.Choice(["cost", "deployment", "quality", "all"]),
    default="all",
    help="Type of agent to start",
)
@click.option("--background", "-b", is_flag=True, help="Run agents in background")
@click.pass_context
def start_agents(ctx, agent_type, background):
    """Start Beast Mode collaboration agents"""
    click.echo("🤖 Starting Beast Mode agents...")

    async def _start_agents():
        import sys
        import os

        sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        from examples.beast_mode_collaboration_agents import (
            CostOptimizationAgent,
            DeploymentSpecialistAgent,
            CodeQualityMentorAgent,
        )

        agents = []
        if agent_type in ["cost", "all"]:
            agents.append(CostOptimizationAgent())
        if agent_type in ["deployment", "all"]:
            agents.append(DeploymentSpecialistAgent())
        if agent_type in ["quality", "all"]:
            agents.append(CodeQualityMentorAgent())
        for agent in agents:
            success = await agent.initialize(ctx.obj["redis_config"])
            if success:
                click.echo(f"✅ {agent.agent_name} started")
            else:
                click.echo(f"❌ {agent.agent_name} failed to start")
        if not background:
            click.echo("🔄 Agents running... Press Ctrl+C to stop")
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                click.echo("\n🛑 Stopping agents...")
                for agent in agents:
                    await agent.shutdown()
                click.echo("✅ All agents stopped")

    asyncio.run(_start_agents())


@cli.command()
@click.option(
    "--capability",
    multiple=True,
    type=click.Choice([cap.value for cap in AgentCapability]),
    help="Required capabilities (can specify multiple)",
)
@click.option(
    "--description", prompt="Help description", help="Description of what help you need"
)
@click.option(
    "--priority",
    type=click.Choice(["low", "normal", "high", "urgent"]),
    default="normal",
    help="Request priority",
)
@click.option("--sender-id", default="cli_user", help="Your agent ID")
@click.pass_context
def request_help(ctx, capability, description, priority, sender_id):
    """Send a help request to the agent network"""

    async def _send_help_request():
        redis_foundation = RedisFoundation(ctx.obj["redis_config"])
        if not await redis_foundation.initialize():
            click.echo("❌ Failed to connect to Redis")
            return
        required_caps = (
            [AgentCapability(cap) for cap in capability] if capability else []
        )
        help_request = create_help_request(
            sender_id=sender_id,
            required_capabilities=required_caps,
            description=description,
            priority=priority,
        )
        success = await redis_foundation.publish(
            "help_requests", help_request.to_dict()
        )
        if success:
            click.echo(f"📨 Help request sent (ID: {help_request.message_id})")
            click.echo(f"📋 Description: {description}")
            if required_caps:
                click.echo(
                    f"🎯 Required capabilities: {[cap.value for cap in required_caps]}"
                )
            click.echo(f"⚡ Priority: {priority}")
            click.echo("👂 Listening for responses...")
            responses = []

            def response_handler(message_data):
                try:
                    message = BeastModeMessage.from_dict(message_data)
                    if (
                        message.message_type == MessageType.HELP_RESPONSE
                        and message.correlation_id == help_request.message_id
                    ):
                        responses.append(message)
                        click.echo(f"\n💬 Response from {message.sender_id}:")
                        click.echo(f"   {json.dumps(message.content, indent=2)}")
                except Exception as e:
                    if ctx.obj["verbose"]:
                        click.echo(f"Error processing response: {e}")

            await redis_foundation.subscribe(f"direct_{sender_id}", response_handler)
            await asyncio.sleep(10)
            if not responses:
                click.echo("⏰ No responses received within 10 seconds")
            else:
                click.echo(f"\n✅ Received {len(responses)} response(s)")
        else:
            click.echo("❌ Failed to send help request")
        await redis_foundation.shutdown()

    asyncio.run(_send_help_request())


@cli.command()
@click.option("--channel", default="beast_mode_general", help="Channel to listen to")
@click.option("--timeout", default=30, help="Listen timeout in seconds")
@click.pass_context
def listen(ctx, channel, timeout):
    """Listen to messages on a channel"""

    async def _listen():
        redis_foundation = RedisFoundation(ctx.obj["redis_config"])
        if not await redis_foundation.initialize():
            click.echo("❌ Failed to connect to Redis")
            return
        click.echo(f"👂 Listening to channel '{channel}' for {timeout} seconds...")
        click.echo("Press Ctrl+C to stop early")
        message_count = 0

        def message_handler(message_data):
            nonlocal message_count
            message_count += 1
            try:
                message = BeastModeMessage.from_dict(message_data)
                timestamp = message.timestamp.strftime("%H:%M:%S")
                click.echo(
                    f"\n[{timestamp}] {message.message_type.value} from {message.sender_id}"
                )
                if message.subject:
                    click.echo(f"  📋 {message.subject}")
                if ctx.obj["verbose"] and message.content:
                    click.echo(f"  📄 Content: {json.dumps(message.content, indent=4)}")
            except Exception as e:
                click.echo(f"❌ Error parsing message: {e}")
                if ctx.obj["verbose"]:
                    click.echo(f"   Raw data: {message_data}")

        await redis_foundation.subscribe(channel, message_handler)
        try:
            await asyncio.sleep(timeout)
        except KeyboardInterrupt:
            click.echo("\n🛑 Stopping listener...")
        click.echo(f"\n📊 Received {message_count} messages")
        await redis_foundation.shutdown()

    asyncio.run(_listen())


@cli.command()
@click.pass_context
def status(ctx):
    """Check agent network status"""

    async def _check_status():
        redis_foundation = RedisFoundation(ctx.obj["redis_config"])
        if not await redis_foundation.initialize():
            click.echo("❌ Failed to connect to Redis")
            return
        click.echo("📊 Beast Mode Agent Network Status")
        click.echo("=" * 40)
        conn_info = await redis_foundation.get_connection_info()
        status_icon = "✅" if conn_info["connected"] else "❌"
        click.echo(
            f"{status_icon} Redis: {conn_info['host']}:{conn_info['port']} ({conn_info['status']})"
        )
        if conn_info["active_subscriptions"]:
            click.echo(
                f"📡 Active subscriptions: {len(conn_info['active_subscriptions'])}"
            )
        click.echo("\n🔍 Scanning for active agents...")
        active_agents = {}

        def heartbeat_handler(message_data):
            try:
                message = BeastModeMessage.from_dict(message_data)
                if message.message_type == MessageType.HEARTBEAT:
                    agent_info = message.content.get("status", {})
                    active_agents[message.sender_id] = {
                        "name": agent_info.get("agent_name", "Unknown"),
                        "capabilities": agent_info.get("capabilities", []),
                        "load": agent_info.get("current_load", 0),
                        "max_tasks": agent_info.get("max_tasks", 0),
                        "last_seen": datetime.now(),
                    }
            except Exception as e:
                if ctx.obj["verbose"]:
                    click.echo(f"Error processing heartbeat: {e}")

        await redis_foundation.subscribe("beast_mode_heartbeats", heartbeat_handler)
        await asyncio.sleep(5)
        if active_agents:
            click.echo(f"\n🤖 Active Agents ({len(active_agents)}):")
            for agent_id, info in active_agents.items():
                load_bar = "█" * info["load"] + "░" * (info["max_tasks"] - info["load"])
                click.echo(f"  • {info['name']} ({agent_id})")
                click.echo(f"    Load: [{load_bar}] {info['load']}/{info['max_tasks']}")
                click.echo(
                    f"    Capabilities: {', '.join(info['capabilities'][:3])}{('...' if len(info['capabilities']) > 3 else '')}"
                )
        else:
            click.echo("\n😴 No active agents detected")
            click.echo("   Try: beast-mode start-agents")
        await redis_foundation.shutdown()

    asyncio.run(_check_status())


@cli.command()
@click.option(
    "--message-type",
    type=click.Choice([mt.value for mt in MessageType]),
    default="direct_message",
    help="Type of message to send",
)
@click.option("--recipient", help="Recipient agent ID")
@click.option("--content", help="Message content (JSON string)")
@click.option("--subject", help="Message subject")
@click.option("--sender-id", default="cli_user", help="Your agent ID")
@click.pass_context
def send_message(ctx, message_type, recipient, content, subject, sender_id):
    """Send a custom message to the network"""

    async def _send_message():
        redis_foundation = RedisFoundation(ctx.obj["redis_config"])
        if not await redis_foundation.initialize():
            click.echo("❌ Failed to connect to Redis")
            return
        message_content = {}
        if content:
            try:
                message_content = json.loads(content)
            except json.JSONDecodeError:
                message_content = {"text": content}
        message = BeastModeMessage(
            message_type=MessageType(message_type),
            sender_id=sender_id,
            recipient_id=recipient,
            subject=subject,
            content=message_content,
        )
        if recipient:
            channel = f"direct_{recipient}"
        else:
            channel = "beast_mode_general"
        success = await redis_foundation.publish(channel, message.to_dict())
        if success:
            click.echo(f"📨 Message sent to {channel}")
            click.echo(f"   ID: {message.message_id}")
            if subject:
                click.echo(f"   Subject: {subject}")
        else:
            click.echo("❌ Failed to send message")
        await redis_foundation.shutdown()

    asyncio.run(_send_message())


@cli.command()
@click.pass_context
def demo(ctx):
    """Run a quick collaboration demo"""

    async def _run_demo():
        from ..examples.beast_mode_collaboration_agents import (
            demonstrate_beast_mode_collaboration,
        )

        click.echo("🎭 Running Beast Mode Collaboration Demo")
        click.echo("=" * 50)
        try:
            await demonstrate_beast_mode_collaboration()
        except Exception as e:
            click.echo(f"❌ Demo failed: {e}")
            if ctx.obj["verbose"]:
                import traceback

                traceback.print_exc()

    asyncio.run(_run_demo())


@cli.command()
@click.option("--message", help="Message to share with the network")
@click.option("--file", "file_path", help="File to share (markdown, text, etc.)")
@click.option(
    "--channel", default="beast_mode_network", help="Network channel to share to"
)
@click.option("--sender-id", default="network_contributor", help="Your contributor ID")
@click.pass_context
def share(ctx, message, file_path, channel, sender_id):
    """Share content with the Beast Mode network"""

    async def _share_content():
        redis_foundation = RedisFoundation(ctx.obj["redis_config"])
        if not await redis_foundation.initialize():
            click.echo("❌ Failed to connect to Redis")
            return
        content = {}
        if file_path:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                click.echo(f"❌ File not found: {file_path}")
                return
            try:
                content["file_content"] = file_path_obj.read_text(encoding="utf-8")
                content["file_name"] = file_path_obj.name
                content["file_type"] = file_path_obj.suffix
                click.echo(f"📄 Sharing file: {file_path_obj.name}")
            except Exception as e:
                click.echo(f"❌ Failed to read file: {e}")
                return
        if message:
            content["message"] = message
            click.echo(
                f"💬 Sharing message: {message[:50]}{('...' if len(message) > 50 else '')}"
            )
        if not content:
            click.echo("❌ No content to share. Provide --message or --file")
            return
        content["shared_at"] = datetime.now().isoformat()
        content["contributor"] = sender_id
        content["beast_mode_version"] = "1.0.0"
        share_message = BeastModeMessage(
            message_type=MessageType.BROADCAST_MESSAGE,
            sender_id=sender_id,
            subject=f"Network Share: {(file_path_obj.name if file_path else 'Message')}",
            content=content,
        )
        success = await redis_foundation.publish(channel, share_message.to_dict())
        if success:
            click.echo(f"🌐 Content shared to {channel}")
            click.echo(f"   Message ID: {share_message.message_id}")
            click.echo(f"   Timestamp: {share_message.timestamp}")
            if ctx.obj["verbose"]:
                click.echo(
                    f"   Content preview: {json.dumps(content, indent=2)[:200]}..."
                )
        else:
            click.echo("❌ Failed to share content")
        await redis_foundation.shutdown()

    asyncio.run(_share_content())


@cli.command()
@click.option(
    "--output-format",
    type=click.Choice(["json", "markdown", "text"]),
    default="markdown",
    help="Output format for network content",
)
@click.option("--filter-type", help="Filter by content type (e.g., feedback, analysis)")
@click.option("--timeout", default=30, help="Listen timeout in seconds")
@click.pass_context
def network_listen(ctx, output_format, filter_type, timeout):
    """Listen to Beast Mode network shares and contributions"""

    async def _network_listen():
        redis_foundation = RedisFoundation(ctx.obj["redis_config"])
        if not await redis_foundation.initialize():
            click.echo("❌ Failed to connect to Redis")
            return
        click.echo(f"🌐 Listening to Beast Mode network for {timeout} seconds...")
        click.echo(f"📋 Output format: {output_format}")
        if filter_type:
            click.echo(f"🔍 Filtering for: {filter_type}")
        click.echo("Press Ctrl+C to stop early\n")
        received_count = 0

        def network_handler(message_data):
            nonlocal received_count
            try:
                message = BeastModeMessage.from_dict(message_data)
                if (
                    filter_type
                    and filter_type.lower() not in str(message.content).lower()
                ):
                    return
                received_count += 1
                timestamp = message.timestamp.strftime("%H:%M:%S")
                if output_format == "json":
                    click.echo(json.dumps(message.to_dict(), indent=2))
                elif output_format == "markdown":
                    click.echo(f"## {message.subject or 'Network Share'}")
                    click.echo(f"**From:** {message.sender_id} | **Time:** {timestamp}")
                    if "file_name" in message.content:
                        click.echo(f"**File:** {message.content['file_name']}")
                    if "message" in message.content:
                        click.echo(f"\n{message.content['message']}")
                    if "file_content" in message.content:
                        click.echo(f"\n```{message.content.get('file_type', '')}")
                        click.echo(message.content["file_content"][:500])
                        if len(message.content["file_content"]) > 500:
                            click.echo("... [truncated]")
                        click.echo("```")
                    click.echo("\n---\n")
                else:
                    click.echo(f"[{timestamp}] {message.sender_id}: {message.subject}")
                    if "message" in message.content:
                        click.echo(f"  {message.content['message']}")
                    if "file_name" in message.content:
                        click.echo(f"  📄 Shared file: {message.content['file_name']}")
                    click.echo()
            except Exception as e:
                if ctx.obj["verbose"]:
                    click.echo(f"❌ Error processing network message: {e}")

        await redis_foundation.subscribe("beast_mode_network", network_handler)
        try:
            await asyncio.sleep(timeout)
        except KeyboardInterrupt:
            click.echo("\n🛑 Stopping network listener...")
        click.echo(f"\n📊 Received {received_count} network messages")
        await redis_foundation.shutdown()

    asyncio.run(_network_listen())


def message_handler(message_data):
    nonlocal message_count
    message_count += 1
    try:
        message = BeastModeMessage.from_dict(message_data)
        timestamp = message.timestamp.strftime("%H:%M:%S")
        click.echo(
            f"\n[{timestamp}] {message.message_type.value} from {message.sender_id}"
        )
        if message.subject:
            click.echo(f"  📋 {message.subject}")
        if ctx.obj["verbose"] and message.content:
            click.echo(f"  📄 Content: {json.dumps(message.content, indent=4)}")
    except Exception as e:
        click.echo(f"❌ Error parsing message: {e}")
        if ctx.obj["verbose"]:
            click.echo(f"   Raw data: {message_data}")


def heartbeat_handler(message_data):
    try:
        message = BeastModeMessage.from_dict(message_data)
        if message.message_type == MessageType.HEARTBEAT:
            agent_info = message.content.get("status", {})
            active_agents[message.sender_id] = {
                "name": agent_info.get("agent_name", "Unknown"),
                "capabilities": agent_info.get("capabilities", []),
                "load": agent_info.get("current_load", 0),
                "max_tasks": agent_info.get("max_tasks", 0),
                "last_seen": datetime.now(),
            }
    except Exception as e:
        if ctx.obj["verbose"]:
            click.echo(f"Error processing heartbeat: {e}")


def network_handler(message_data):
    nonlocal received_count
    try:
        message = BeastModeMessage.from_dict(message_data)
        if filter_type and filter_type.lower() not in str(message.content).lower():
            return
        received_count += 1
        timestamp = message.timestamp.strftime("%H:%M:%S")
        if output_format == "json":
            click.echo(json.dumps(message.to_dict(), indent=2))
        elif output_format == "markdown":
            click.echo(f"## {message.subject or 'Network Share'}")
            click.echo(f"**From:** {message.sender_id} | **Time:** {timestamp}")
            if "file_name" in message.content:
                click.echo(f"**File:** {message.content['file_name']}")
            if "message" in message.content:
                click.echo(f"\n{message.content['message']}")
            if "file_content" in message.content:
                click.echo(f"\n```{message.content.get('file_type', '')}")
                click.echo(message.content["file_content"][:500])
                if len(message.content["file_content"]) > 500:
                    click.echo("... [truncated]")
                click.echo("```")
            click.echo("\n---\n")
        else:
            click.echo(f"[{timestamp}] {message.sender_id}: {message.subject}")
            if "message" in message.content:
                click.echo(f"  {message.content['message']}")
            if "file_name" in message.content:
                click.echo(f"  📄 Shared file: {message.content['file_name']}")
            click.echo()
    except Exception as e:
        if ctx.obj["verbose"]:
            click.echo(f"❌ Error processing network message: {e}")


def response_handler(message_data):
    try:
        message = BeastModeMessage.from_dict(message_data)
        if (
            message.message_type == MessageType.HELP_RESPONSE
            and message.correlation_id == help_request.message_id
        ):
            responses.append(message)
            click.echo(f"\n💬 Response from {message.sender_id}:")
            click.echo(f"   {json.dumps(message.content, indent=2)}")
    except Exception as e:
        if ctx.obj["verbose"]:
            click.echo(f"Error processing response: {e}")
