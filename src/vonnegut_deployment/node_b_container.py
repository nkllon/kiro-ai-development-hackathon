#!/usr/bin/env python3
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
        print("\n🛑 Container shutdown requested")
        node_b.running = False
    except Exception as e:
        print(f"❌ Container error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
