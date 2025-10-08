#!/usr/bin/env python3
"""
Docker Workload Manager for Vonnegut
====================================

Manages Docker workloads on the Vonnegut server (192.168.1.119) for
distributed Node B execution and other Beast Mode tasks.
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.security.secure_credentials import get_redis_password


@dataclass
class DockerWorkload:
    """Represents a Docker workload configuration."""
    name: str
    image: str
    command: List[str]
    environment: Dict[str, str]
    volumes: Dict[str, str] = None
    ports: Dict[str, str] = None
    network: str = "bridge"
    restart_policy: str = "unless-stopped"


class VonnegutDockerManager:
    """Manages Docker workloads on Vonnegut server."""
    
    def __init__(self, vonnegut_host: str = "192.168.1.119"):
        self.vonnegut_host = vonnegut_host
        self.redis_password = get_redis_password()
    
    def create_node_b_container_config(self) -> DockerWorkload:
        """Create Docker configuration for Node B on Vonnegut."""
        return DockerWorkload(
            name="node-b-vonnegut",
            image="python:3.9-slim",
            command=[
                "sh", "-c",
                "pip install redis && python -c '"
                "import asyncio, json, redis, sys; "
                "from datetime import datetime; "
                "exec(open(\"/app/node_b_container.py\").read())'"
            ],
            environment={
                "REDIS_HOST": self.vonnegut_host,
                "REDIS_PORT": "6379",
                "REDIS_PASSWORD": self.redis_password,
                "NODE_ID": "node-b-vonnegut-container",
                "PYTHONUNBUFFERED": "1"
            },
            volumes={
                "/tmp/node_b_workload": "/app"
            },
            network="host"
        )
    
    def generate_node_b_container_script(self) -> str:
        """Generate Node B script for container execution."""
        return '''#!/usr/bin/env python3
"""
Containerized Node B for Vonnegut
================================
"""

import asyncio
import json
import redis
import os
from datetime import datetime


class ContainerNodeB:
    """Node B running in Docker container on Vonnegut."""
    
    def __init__(self):
        self.node_id = os.getenv("NODE_ID", "node-b-container")
        self.running = True
        
        # Connect to Redis
        self.redis = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD"),
            decode_responses=True
        )
        
        print(f"🐳 Container Node B ({self.node_id}) starting on Vonnegut...")
        self.redis.ping()
        print(f"✅ Connected to Redis at {os.getenv('REDIS_HOST')}")
    
    async def send_heartbeat(self):
        """Send container heartbeat."""
        while self.running:
            try:
                heartbeat = {
                    "node_id": self.node_id,
                    "timestamp": datetime.now().isoformat(),
                    "status": "active",
                    "host": "vonnegut-container",
                    "capabilities": ["docker_execution", "distributed_processing"],
                    "message": f"🐳 Container Node B on Vonnegut - Ready for workloads!"
                }
                
                self.redis.publish("beast_mode_network", json.dumps(heartbeat))
                print(f"💓 Container heartbeat: {heartbeat['timestamp']}")
                
                await asyncio.sleep(15)
                
            except Exception as e:
                print(f"❌ Heartbeat error: {e}")
                await asyncio.sleep(5)
    
    async def process_workloads(self):
        """Process distributed workloads."""
        pubsub = self.redis.pubsub()
        pubsub.subscribe("beast_mode_network", "docker_workloads")
        
        print(f"👂 {self.node_id} listening for workloads...")
        
        while self.running:
            try:
                message = pubsub.get_message(timeout=1.0)
                if message and message['type'] == 'message':
                    data = json.loads(message['data'])
                    
                    # Process workload requests
                    if data.get('type') == 'workload_request':
                        await self.handle_workload(data)
                    
                    # Respond to coordination messages
                    elif data.get('node_id') != self.node_id:
                        await self.send_response(data)
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Workload processing error: {e}")
                await asyncio.sleep(1)
    
    async def handle_workload(self, workload_data: dict):
        """Handle a workload execution request."""
        workload_id = workload_data.get('workload_id', 'unknown')
        task = workload_data.get('task', {})
        
        print(f"🔧 Processing workload {workload_id}: {task.get('description', 'No description')}")
        
        # Simulate workload processing
        await asyncio.sleep(2)
        
        # Send completion response
        response = {
            "node_id": self.node_id,
            "type": "workload_complete",
            "workload_id": workload_id,
            "timestamp": datetime.now().isoformat(),
            "result": "success",
            "message": f"🐳 Workload {workload_id} completed on Vonnegut container"
        }
        
        self.redis.publish("beast_mode_network", json.dumps(response))
        print(f"✅ Workload {workload_id} completed")
    
    async def send_response(self, received_data: dict):
        """Send response to coordination messages."""
        response = {
            "node_id": self.node_id,
            "timestamp": datetime.now().isoformat(),
            "response_to": received_data.get('node_id', 'unknown'),
            "message": f"🐳 Container Node B on Vonnegut acknowledges: {received_data.get('message', 'no message')[:50]}",
            "host": "vonnegut-docker"
        }
        
        self.redis.publish("beast_mode_network", json.dumps(response))
    
    async def run(self):
        """Run container Node B."""
        await asyncio.gather(
            self.send_heartbeat(),
            self.process_workloads()
        )


async def main():
    """Main container function."""
    node_b = ContainerNodeB()
    
    try:
        await node_b.run()
    except KeyboardInterrupt:
        print("\\n🛑 Container shutdown requested")
        node_b.running = False
    except Exception as e:
        print(f"❌ Container error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
'''
    
    def generate_docker_compose_config(self) -> str:
        """Generate docker-compose.yml for Vonnegut deployment."""
        return f'''version: '3.8'

services:
  node-b-vonnegut:
    image: python:3.9-slim
    container_name: node-b-vonnegut
    restart: unless-stopped
    environment:
      - REDIS_HOST={self.vonnegut_host}
      - REDIS_PORT=6379
      - REDIS_PASSWORD={self.redis_password}
      - NODE_ID=node-b-vonnegut-container
      - PYTHONUNBUFFERED=1
    volumes:
      - ./node_b_container.py:/app/node_b_container.py:ro
    working_dir: /app
    command: >
      sh -c "pip install redis && python node_b_container.py"
    network_mode: host
    
  # Additional Beast Mode services can be added here
  redis-monitor:
    image: redis:7-alpine
    container_name: redis-monitor
    restart: unless-stopped
    command: redis-cli -h {self.vonnegut_host} -p 6379 -a {self.redis_password} monitor
    network_mode: host
    
  # Future: Directus CMS, Observatory, etc.
'''
    
    def generate_deployment_script(self) -> str:
        """Generate deployment script for Vonnegut."""
        return f'''#!/bin/bash
# Deploy Node B to Vonnegut Docker
# Usage: ./deploy_to_vonnegut.sh

set -e

VONNEGUT_HOST="{self.vonnegut_host}"
DEPLOY_DIR="/tmp/beast_mode_deploy"

echo "🚀 Deploying Node B to Vonnegut Docker..."

# Create deployment directory
mkdir -p $DEPLOY_DIR

# Copy files
cp node_b_container.py $DEPLOY_DIR/
cp docker-compose.yml $DEPLOY_DIR/

echo "📦 Files prepared for deployment"

# Note: Actual deployment would require SSH access to Vonnegut
echo "📋 To complete deployment on Vonnegut:"
echo "1. Copy $DEPLOY_DIR/* to Vonnegut server"
echo "2. SSH to {self.vonnegut_host}"
echo "3. Run: docker-compose up -d"
echo "4. Monitor: docker logs -f node-b-vonnegut"

echo "✅ Deployment package ready"
'''
    
    def create_workload_sender(self) -> str:
        """Create script to send workloads to Vonnegut containers."""
        return '''#!/usr/bin/env python3
"""
Send Workloads to Vonnegut Containers
====================================
"""

import asyncio
import json
import redis
import sys
import uuid
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from src.security.secure_credentials import get_redis_password


async def send_workload(task_description: str, task_data: dict = None):
    """Send a workload to Vonnegut containers."""
    
    # Connect to Redis
    redis_client = redis.Redis(
        host="192.168.1.119",
        port=6379,
        password=get_redis_password(),
        decode_responses=True
    )
    
    workload_id = str(uuid.uuid4())[:8]
    
    workload_request = {
        "type": "workload_request",
        "workload_id": workload_id,
        "sender": "workload-dispatcher",
        "timestamp": datetime.now().isoformat(),
        "task": {
            "description": task_description,
            "data": task_data or {},
            "priority": "normal"
        }
    }
    
    print(f"📤 Sending workload {workload_id}: {task_description}")
    redis_client.publish("docker_workloads", json.dumps(workload_request))
    
    # Listen for completion
    pubsub = redis_client.pubsub()
    pubsub.subscribe("beast_mode_network")
    
    print(f"👂 Waiting for workload completion...")
    
    for i in range(30):  # 30 second timeout
        message = pubsub.get_message(timeout=1.0)
        if message and message['type'] == 'message':
            data = json.loads(message['data'])
            if (data.get('type') == 'workload_complete' and 
                data.get('workload_id') == workload_id):
                print(f"✅ Workload completed: {data.get('message')}")
                break
        await asyncio.sleep(1)
    else:
        print("⏰ Workload completion timeout")
    
    pubsub.close()
    redis_client.close()


if __name__ == "__main__":
    task = sys.argv[1] if len(sys.argv) > 1 else "Test workload execution"
    asyncio.run(send_workload(task))
'''
    
    def generate_all_files(self):
        """Generate all Docker deployment files."""
        print("🐳 Generating Vonnegut Docker deployment files...")
        
        # Create deployment directory
        deploy_dir = Path("vonnegut_deployment")
        deploy_dir.mkdir(exist_ok=True)
        
        # Generate Node B container script
        with open(deploy_dir / "node_b_container.py", "w") as f:
            f.write(self.generate_node_b_container_script())
        print(f"✅ Generated: {deploy_dir}/node_b_container.py")
        
        # Generate docker-compose
        with open(deploy_dir / "docker-compose.yml", "w") as f:
            f.write(self.generate_docker_compose_config())
        print(f"✅ Generated: {deploy_dir}/docker-compose.yml")
        
        # Generate deployment script
        with open(deploy_dir / "deploy_to_vonnegut.sh", "w") as f:
            f.write(self.generate_deployment_script())
        (deploy_dir / "deploy_to_vonnegut.sh").chmod(0o755)
        print(f"✅ Generated: {deploy_dir}/deploy_to_vonnegut.sh")
        
        # Generate workload sender
        with open("send_workload_to_vonnegut.py", "w") as f:
            f.write(self.create_workload_sender())
        print(f"✅ Generated: send_workload_to_vonnegut.py")
        
        print(f"\n🎯 Vonnegut Docker deployment ready!")
        print(f"📁 Files in: {deploy_dir}/")
        print(f"🚀 Next steps:")
        print(f"   1. Review generated files")
        print(f"   2. Deploy to Vonnegut: cd {deploy_dir} && ./deploy_to_vonnegut.sh")
        print(f"   3. Test workloads: python send_workload_to_vonnegut.py 'Test task'")


def main():
    """Main function."""
    manager = VonnegutDockerManager()
    manager.generate_all_files()


if __name__ == "__main__":
    main()