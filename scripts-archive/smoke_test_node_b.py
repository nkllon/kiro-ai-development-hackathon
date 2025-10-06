#!/usr/bin/env python3
"""
Node B Smoke Test - Distributed Workload
========================================

Sends real tasks to both local and Vonnegut Node B instances to test
distributed processing capabilities.
"""

import asyncio
import json
import redis
import sys
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.security.secure_credentials import get_redis_password


class NodeBSmokeTest:
    """Comprehensive smoke test for Node B distributed network."""
    
    def __init__(self):
        self.test_id = str(uuid.uuid4())[:8]
        
        # Connect to Redis
        redis_password = get_redis_password()
        self.redis = redis.Redis(
            host="192.168.1.119",
            port=6379,
            password=redis_password,
            decode_responses=True
        )
        
        # Test tracking
        self.responses = []
        self.test_start = datetime.now()
        
        print(f"🧪 Node B Smoke Test {self.test_id}")
        print("=" * 50)
    
    async def send_coordination_task(self, task_name: str, task_data: Dict[str, Any]):
        """Send a coordination task to all Node B instances."""
        
        task_message = {
            "test_id": self.test_id,
            "type": "coordination_task",
            "task_name": task_name,
            "sender": "smoke-test-client",
            "timestamp": datetime.now().isoformat(),
            "task_data": task_data,
            "expected_responses": ["simple-node-b", "node-b-vonnegut-container"]
        }
        
        print(f"📤 Sending task: {task_name}")
        print(f"   Data: {task_data}")
        
        # Send to beast_mode_network channel
        self.redis.publish("beast_mode_network", json.dumps(task_message))
        
        return task_message
    
    async def send_workload_task(self, workload_description: str):
        """Send a workload task specifically to Vonnegut container."""
        
        workload_id = f"{self.test_id}-workload"
        
        workload_request = {
            "type": "workload_request",
            "workload_id": workload_id,
            "sender": "smoke-test-client",
            "timestamp": datetime.now().isoformat(),
            "task": {
                "description": workload_description,
                "test_id": self.test_id,
                "complexity": "medium",
                "expected_duration": "5 seconds"
            }
        }
        
        print(f"🔧 Sending workload: {workload_description}")
        
        # Send to docker_workloads channel (for container)
        self.redis.publish("docker_workloads", json.dumps(workload_request))
        
        return workload_request
    
    async def listen_for_responses(self, timeout_seconds: int = 30):
        """Listen for responses from Node B instances."""
        
        pubsub = self.redis.pubsub()
        pubsub.subscribe("beast_mode_network")
        
        print(f"👂 Listening for responses (timeout: {timeout_seconds}s)...")
        
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < timeout_seconds:
            try:
                message = pubsub.get_message(timeout=1.0)
                if message and message['type'] == 'message':
                    data = json.loads(message['data'])
                    
                    # Check if this is a response to our test
                    if (data.get('test_id') == self.test_id or 
                        data.get('workload_id', '').startswith(self.test_id) or
                        'smoke-test-client' in data.get('response_to', '') or
                        'smoke test' in data.get('message', '').lower()):
                        
                        self.responses.append({
                            'timestamp': datetime.now().isoformat(),
                            'node_id': data.get('node_id', 'unknown'),
                            'response_type': data.get('type', 'message'),
                            'message': data.get('message', ''),
                            'data': data
                        })
                        
                        print(f"📨 Response from {data.get('node_id', 'unknown')}: {data.get('message', 'No message')[:80]}...")
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Error processing response: {e}")
                await asyncio.sleep(1)
        
        pubsub.close()
    
    async def run_smoke_tests(self):
        """Run comprehensive smoke tests."""
        
        print("🚀 Starting Node B Smoke Tests...")
        
        # Test 1: Basic coordination message
        await self.send_coordination_task(
            "basic_coordination_test",
            {
                "message": "Hello Node B! This is a smoke test for distributed coordination.",
                "test_type": "basic_coordination",
                "priority": "high"
            }
        )
        
        # Test 2: Complex task simulation
        await self.send_coordination_task(
            "complex_task_simulation",
            {
                "task_type": "code_analysis",
                "files_to_analyze": ["src/security/secure_credentials.py", "simple_working_node_b.py"],
                "analysis_depth": "comprehensive",
                "expected_output": "security_report"
            }
        )
        
        # Test 3: Workload processing (for Vonnegut container)
        await self.send_workload_task(
            "Distributed AI coordination workload - process Beast Mode network optimization"
        )
        
        # Test 4: Performance test
        await self.send_coordination_task(
            "performance_benchmark",
            {
                "benchmark_type": "message_processing",
                "iterations": 100,
                "payload_size": "medium",
                "measure_latency": True
            }
        )
        
        # Listen for all responses
        await self.listen_for_responses(timeout_seconds=20)
        
        # Generate test report
        self.generate_test_report()
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        
        print("\n" + "=" * 60)
        print("🧪 NODE B SMOKE TEST REPORT")
        print("=" * 60)
        
        test_duration = (datetime.now() - self.test_start).total_seconds()
        
        print(f"Test ID: {self.test_id}")
        print(f"Duration: {test_duration:.2f} seconds")
        print(f"Responses Received: {len(self.responses)}")
        
        # Analyze responses by node
        nodes_responded = set()
        response_types = {}
        
        for response in self.responses:
            node_id = response['node_id']
            nodes_responded.add(node_id)
            
            resp_type = response['response_type']
            if resp_type not in response_types:
                response_types[resp_type] = 0
            response_types[resp_type] += 1
        
        print(f"\n📊 Response Analysis:")
        print(f"   Nodes Responded: {len(nodes_responded)}")
        for node in sorted(nodes_responded):
            node_responses = [r for r in self.responses if r['node_id'] == node]
            print(f"   • {node}: {len(node_responses)} responses")
        
        print(f"\n📋 Response Types:")
        for resp_type, count in response_types.items():
            print(f"   • {resp_type}: {count}")
        
        # Test results
        print(f"\n✅ Test Results:")
        
        # Check if both nodes responded
        expected_nodes = {"simple-node-b", "node-b-vonnegut-container"}
        responding_nodes = nodes_responded & expected_nodes
        
        if len(responding_nodes) >= 2:
            print("   ✅ Multi-node coordination: PASS")
        elif len(responding_nodes) == 1:
            print("   ⚠️  Multi-node coordination: PARTIAL (1 node responding)")
        else:
            print("   ❌ Multi-node coordination: FAIL")
        
        if len(self.responses) >= 4:
            print("   ✅ Response volume: PASS")
        elif len(self.responses) >= 2:
            print("   ⚠️  Response volume: PARTIAL")
        else:
            print("   ❌ Response volume: FAIL")
        
        if test_duration < 25:
            print("   ✅ Response time: PASS")
        else:
            print("   ⚠️  Response time: SLOW")
        
        # Overall assessment
        if len(responding_nodes) >= 2 and len(self.responses) >= 4:
            print(f"\n🎉 SMOKE TEST: SUCCESS")
            print("   Distributed Node B network is operational!")
        elif len(responding_nodes) >= 1:
            print(f"\n⚠️  SMOKE TEST: PARTIAL SUCCESS")
            print("   Some Node B instances are operational")
        else:
            print(f"\n❌ SMOKE TEST: FAILURE")
            print("   Node B network needs investigation")
        
        # Detailed response log
        if self.responses:
            print(f"\n📝 Detailed Response Log:")
            for i, response in enumerate(self.responses, 1):
                print(f"   {i}. [{response['timestamp']}] {response['node_id']}")
                print(f"      Type: {response['response_type']}")
                print(f"      Message: {response['message'][:100]}...")


async def main():
    """Main smoke test function."""
    
    try:
        smoke_test = NodeBSmokeTest()
        await smoke_test.run_smoke_tests()
        
    except KeyboardInterrupt:
        print("\n🛑 Smoke test interrupted")
    except Exception as e:
        print(f"\n❌ Smoke test error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🧪 Starting Node B Distributed Smoke Test...")
    asyncio.run(main())