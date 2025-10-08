#!/usr/bin/env python3
"""
Robust Node B Launcher
=====================

Launches Node B with proper environment validation and graceful degradation.
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.security.secure_credentials import get_redis_password


class NodeBLauncher:
    """Robust launcher for Node B with environment validation."""
    
    def __init__(self):
        self.node_id = "robust-node-b"
        self.issues = []
    
    def validate_environment(self) -> bool:
        """Validate environment before launching Node B."""
        print("🔍 Validating Node B environment...")
        
        # Check Redis credentials
        try:
            redis_password = get_redis_password()
            if redis_password:
                print("✅ Redis credentials: Available")
            else:
                self.issues.append("Redis password not found in environment")
        except Exception as e:
            self.issues.append(f"Redis credential error: {e}")
        
        # Check Redis connectivity
        try:
            import redis
            client = redis.Redis(
                host="192.168.1.119",
                port=6379,
                password=get_redis_password(),
                socket_timeout=5
            )
            client.ping()
            print("✅ Redis connectivity: Connected")
        except Exception as e:
            self.issues.append(f"Redis connection failed: {e}")
        
        # Check messaging infrastructure
        try:
            from beast_mode.messaging import BeastModeBusClient, BeastModeMessage, MessageType
            print("✅ Messaging infrastructure: Available")
        except ImportError as e:
            self.issues.append(f"Messaging infrastructure missing: {e}")
        
        return len(self.issues) == 0
    
    def print_remediation_steps(self):
        """Print steps to fix environment issues."""
        print("\n🔧 REMEDIATION STEPS:")
        print("1. Ensure ~/.env contains: REDIS_PASSWORD=beastmode2025")
        print("2. Verify Redis is running on 192.168.1.119:6379")
        print("3. Run: python scripts/fix_node_b_infrastructure.py")
        print("4. Install missing packages: pip install redis")
    
    async def launch_node_b(self):
        """Launch Node B with proper error handling."""
        if not self.validate_environment():
            print("\n❌ Environment validation failed:")
            for issue in self.issues:
                print(f"  • {issue}")
            self.print_remediation_steps()
            return False
        
        print("\n🚀 Launching Node B...")
        
        try:
            from beast_mode.messaging import BeastModeBusClient, MessageType
            
            # Create Node B client
            client = BeastModeBusClient(
                agent_id=self.node_id,
                capabilities=[
                    "coordination",
                    "messaging",
                    "task_processing"
                ]
            )
            
            # Register message handlers
            async def handle_coordination(message):
                print(f"📨 Coordination message from {message.sender}: {message.content}")
            
            async def handle_task(message):
                print(f"📋 Task message from {message.sender}: {message.content}")
                # Echo back a response
                await client.send_message(
                    message.sender,
                    MessageType.RESPONSE,
                    {"status": "received", "task_id": message.content.get("task_id")}
                )
            
            client.register_handler(MessageType.COORDINATION, handle_coordination)
            client.register_handler(MessageType.TASK, handle_task)
            
            print(f"✅ Node B ({self.node_id}) is now active and listening...")
            
            # Send initial heartbeat
            await client.send_heartbeat()
            
            # Listen for messages
            await client.listen_for_messages()
            
        except KeyboardInterrupt:
            print("\n🛑 Node B shutdown requested")
            return True
        except Exception as e:
            print(f"\n❌ Node B error: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Main launcher function."""
    launcher = NodeBLauncher()
    success = await launcher.launch_node_b()
    return success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Launch failed: {e}")
        sys.exit(1)
