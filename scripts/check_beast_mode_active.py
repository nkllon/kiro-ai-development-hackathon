#!/usr/bin/env python3
"""
Check Beast Mode Active Modules and Agents in Redis
"""

import redis
import json
import os
from datetime import datetime


def connect_to_redis():
    """Connect to Redis using environment configuration."""
    try:
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', '6379'))
        redis_password = os.getenv('REDIS_PASSWORD', os.getenv('BEAST_MODE_REDIS_PASSWORD', ''))
        
        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password if redis_password else None,
            decode_responses=True
        )
        
        r.ping()
        return r
        
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return None


def check_beast_mode_active(r):
    """Check Beast Mode active modules and agents."""
    print("🔍 Checking Beast Mode active components...")
    
    # Check active modules
    try:
        active_modules = r.hgetall("beast_mode:active_modules")
        if active_modules:
            print(f"\n📋 Active Modules ({len(active_modules)}):")
            for module_id, data in active_modules.items():
                try:
                    module_info = json.loads(data)
                    status = module_info.get('status', 'unknown')
                    last_seen = module_info.get('last_heartbeat', module_info.get('last_seen', 'unknown'))
                    print(f"  - {module_id}: {status} (last_seen: {last_seen})")
                except json.JSONDecodeError:
                    print(f"  - {module_id}: {data}")
        else:
            print("\n📋 No active modules found")
            
    except Exception as e:
        print(f"❌ Error checking active modules: {e}")
    
    # Check active agents
    try:
        active_agents = r.hgetall("beast_mode:active_agents")
        if active_agents:
            print(f"\n🤖 Active Agents ({len(active_agents)}):")
            for agent_id, data in active_agents.items():
                try:
                    agent_info = json.loads(data)
                    status = agent_info.get('status', 'unknown')
                    task = agent_info.get('current_task', 'none')
                    last_seen = agent_info.get('last_heartbeat', agent_info.get('last_seen', 'unknown'))
                    print(f"  - {agent_id}: {status} | Task: {task} | Last seen: {last_seen}")
                except json.JSONDecodeError:
                    print(f"  - {agent_id}: {data}")
        else:
            print("\n🤖 No active agents found")
            
    except Exception as e:
        print(f"❌ Error checking active agents: {e}")
    
    # Check for any execution tracking
    try:
        execution_keys = r.keys("execution:*")
        if execution_keys:
            print(f"\n⚡ Execution Tracking ({len(execution_keys)} keys):")
            for key in execution_keys[:10]:  # Show first 10
                try:
                    key_type = r.type(key)
                    if key_type == 'string':
                        value = r.get(key)
                        try:
                            data = json.loads(value)
                            status = data.get('status', 'unknown')
                            task_id = data.get('task_id', 'unknown')
                            print(f"  - {key}: {status} (task: {task_id})")
                        except:
                            print(f"  - {key}: {value[:100]}...")
                    elif key_type == 'hash':
                        hash_data = r.hgetall(key)
                        status = hash_data.get('status', 'unknown')
                        print(f"  - {key}: {status}")
                except Exception as e:
                    print(f"  - {key}: Error - {e}")
        else:
            print("\n⚡ No execution tracking found")
            
    except Exception as e:
        print(f"❌ Error checking execution tracking: {e}")
    
    # Check DAG execution status
    try:
        dag_keys = r.keys("dag:*")
        if dag_keys:
            print(f"\n📊 DAG Execution ({len(dag_keys)} keys):")
            for key in dag_keys[:10]:
                try:
                    key_type = r.type(key)
                    if key_type == 'string':
                        value = r.get(key)
                        try:
                            data = json.loads(value)
                            status = data.get('status', 'unknown')
                            print(f"  - {key}: {status}")
                        except:
                            print(f"  - {key}: {value[:100]}...")
                    elif key_type == 'hash':
                        hash_data = r.hgetall(key)
                        status = hash_data.get('status', 'unknown')
                        print(f"  - {key}: {status}")
                except Exception as e:
                    print(f"  - {key}: Error - {e}")
        else:
            print("\n📊 No DAG execution found")
            
    except Exception as e:
        print(f"❌ Error checking DAG execution: {e}")


if __name__ == "__main__":
    print("🔍 Checking Beast Mode active components in Redis...")
    
    r = connect_to_redis()
    if not r:
        exit(1)
    
    check_beast_mode_active(r)