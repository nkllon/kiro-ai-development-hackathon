#!/usr/bin/env python3
"""
Broadcast GKE Hackathon Feedback to Beast Mode Network
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.append('src')

from beast_mode.messaging.redis_foundation import RedisFoundation, RedisConfig
from beast_mode.messaging.message_models import BeastModeMessage, MessageType


def json_serializer(obj):
    """JSON serializer for datetime objects"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


async def broadcast_feedback():
    """Broadcast the GKE feedback to the Beast Mode network"""
    
    # Read the feedback document
    feedback_path = Path("GKE_HACKATHON_FEEDBACK_BEAST_MODE.md")
    if not feedback_path.exists():
        print("❌ Feedback document not found")
        return False
    
    feedback_content = feedback_path.read_text()
    
    # Initialize Redis connection
    redis_config = RedisConfig(host='localhost', port=6379)
    redis_foundation = RedisFoundation(redis_config)
    
    if not await redis_foundation.initialize():
        print("❌ Failed to connect to Redis - Beast Mode network may not be running")
        return False
    
    print("✅ Connected to Beast Mode network")
    
    # Create broadcast message
    message = BeastModeMessage(
        message_type=MessageType.BROADCAST_MESSAGE,
        sender_id="kiro_main_agent",
        subject="GKE Autopilot MVP Hackathon Feedback - Beast Mode Analysis",
        content={
            "type": "hackathon_postmortem",
            "priority": "high",
            "summary": "Systematic analysis of GKE hackathon success with Beast Mode validation",
            "feedback_content": feedback_content,
            "tags": ["hackathon", "gke", "systematic_analysis", "beast_mode_validation"],
            "key_insights": [
                "DAG execution model validated under pressure",
                "85% completion rate with systematic quality gates", 
                "Production-ready posture beyond MVP demo",
                "Framework scope clarity prevented scope creep"
            ],
            "recommendations": [
                "Add observability layer for systematic measurement",
                "Integrate Spec Mode for end-to-end traceability",
                "Template this approach for future hackathons"
            ]
        }
    )
    
    # Broadcast to general channel
    message_dict = message.to_dict()
    # Convert to JSON string with custom serializer, then back to dict
    message_json = json.dumps(message_dict, default=json_serializer)
    message_dict = json.loads(message_json)
    
    success = await redis_foundation.publish("beast_mode_general", message_dict)
    
    if success:
        print("📡 GKE hackathon feedback broadcast to Beast Mode network")
        print(f"   Message ID: {message.message_id}")
        print(f"   Channel: beast_mode_general")
        print("   🎯 All network agents should receive this analysis")
    else:
        print("❌ Failed to broadcast message")
        return False
    
    # Also send to specific channels for targeted delivery
    channels = [
        "beast_mode_heartbeats",  # For active agents
        "help_requests",          # For agents monitoring help
        "collaboration_updates"   # For collaboration-focused agents
    ]
    
    for channel in channels:
        await redis_foundation.publish(channel, message_dict)
        print(f"   📤 Also sent to {channel}")
    
    await redis_foundation.shutdown()
    print("✅ Broadcast complete - feedback delivered to Beast Mode network")
    return True


if __name__ == "__main__":
    success = asyncio.run(broadcast_feedback())
    sys.exit(0 if success else 1)