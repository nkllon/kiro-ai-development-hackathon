#!/usr/bin/env python3
"""
Check Redis for Running Tasks
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
        
        print(f"🔗 Connecting to Redis at {redis_host}:{redis_port}")
        
        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password if redis_password else None,
            decode_responses=True
        )
        
        # Test connection
        r.ping()
        print("✅ Redis connection successful")
        return r
        
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return None


def check_running_tasks(r):
    """Check Redis for running tasks and execution tracking."""
    print("\n🔍 Scanning Redis for running tasks...")
    
    # Check various Redis patterns for task execution
    patterns_to_check = [
        "task:*",
        "execution:*", 
        "dag:*",
        "celery:*",
        "beast_mode:*",
        "running:*",
        "active:*",
        "job:*"
    ]
    
    all_running_tasks = []
    
    for pattern in patterns_to_check:
        try:
            keys = r.keys(pattern)
            if keys:
                print(f"\n📋 Pattern '{pattern}' found {len(keys)} keys:")
                
                for key in keys[:10]:  # Show first 10 keys
                    try:
                        key_type = r.type(key)
                        
                        if key_type == 'string':
                            value = r.get(key)
                            try:
                                # Try to parse as JSON
                                data = json.loads(value)
                                if isinstance(data, dict):
                                    status = data.get('status', 'unknown')
                                    task_id = data.get('task_id', data.get('id', 'unknown'))
                                    
                                    print(f"  - {key}: {status} (task_id: {task_id})")
                                    
                                    if status in ['running', 'in_progress', 'executing', 'active']:
                                        all_running_tasks.append({
                                            'key': key,
                                            'status': status,
                                            'task_id': task_id,
                                            'data': data
                                        })
                                else:
                                    print(f"  - {key}: {value[:100]}...")
                            except json.JSONDecodeError:
                                print(f"  - {key}: {value[:100]}...")
                                
                        elif key_type == 'hash':
                            hash_data = r.hgetall(key)
                            status = hash_data.get('status', 'unknown')
                            print(f"  - {key} (hash): status={status}")
                            
                            if status in ['running', 'in_progress', 'executing', 'active']:
                                all_running_tasks.append({
                                    'key': key,
                                    'status': status,
                                    'data': hash_data
                                })
                                
                        elif key_type == 'list':
                            list_len = r.llen(key)
                            print(f"  - {key} (list): {list_len} items")
                            
                        elif key_type == 'set':
                            set_size = r.scard(key)
                            print(f"  - {key} (set): {set_size} members")
                            
                    except Exception as e:
                        print(f"  - {key}: Error reading - {e}")
                        
        except Exception as e:
            print(f"❌ Error checking pattern {pattern}: {e}")
    
    return all_running_tasks


def check_celery_tasks(r):
    """Check specifically for Celery task queues."""
    print("\n🔍 Checking Celery task queues...")
    
    celery_patterns = [
        "celery-task-meta-*",
        "_kombu.binding.*",
        "unacked_mutex",
        "unacked"
    ]
    
    for pattern in celery_patterns:
        try:
            keys = r.keys(pattern)
            if keys:
                print(f"📋 Celery pattern '{pattern}': {len(keys)} keys")
                
                for key in keys[:5]:  # Show first 5
                    try:
                        key_type = r.type(key)
                        if key_type == 'string':
                            value = r.get(key)
                            try:
                                data = json.loads(value)
                                if 'status' in data:
                                    print(f"  - {key}: {data['status']}")
                                else:
                                    print(f"  - {key}: {str(data)[:100]}...")
                            except:
                                print(f"  - {key}: {value[:100]}...")
                    except Exception as e:
                        print(f"  - {key}: Error - {e}")
                        
        except Exception as e:
            print(f"❌ Error checking Celery pattern {pattern}: {e}")


def check_beast_mode_registry(r):
    """Check Beast Mode service registry."""
    print("\n🔍 Checking Beast Mode service registry...")
    
    try:
        # Check for ReflectiveModule registrations
        registry_keys = r.keys("reflective_module:*")
        if registry_keys:
            print(f"📋 Found {len(registry_keys)} ReflectiveModule registrations:")
            
            for key in registry_keys:
                try:
                    data = r.hgetall(key)
                    module_id = data.get('module_id', 'unknown')
                    status = data.get('status', 'unknown')
                    last_heartbeat = data.get('last_heartbeat', 'unknown')
                    
                    print(f"  - {module_id}: {status} (heartbeat: {last_heartbeat})")
                    
                except Exception as e:
                    print(f"  - {key}: Error reading - {e}")
        else:
            print("No ReflectiveModule registrations found")
            
    except Exception as e:
        print(f"❌ Error checking Beast Mode registry: {e}")


if __name__ == "__main__":
    print("🔍 Checking Redis for running tasks...")
    
    r = connect_to_redis()
    if not r:
        exit(1)
    
    # Check for running tasks
    running_tasks = check_running_tasks(r)
    
    # Check Celery specifically
    check_celery_tasks(r)
    
    # Check Beast Mode registry
    check_beast_mode_registry(r)
    
    # Summary
    print(f"\n🎯 SUMMARY:")
    print(f"Found {len(running_tasks)} potentially running tasks in Redis")
    
    if running_tasks:
        print("\n🔄 Running Tasks Details:")
        for task in running_tasks:
            print(f"  - Key: {task['key']}")
            print(f"    Status: {task['status']}")
            if 'task_id' in task:
                print(f"    Task ID: {task['task_id']}")
            print()
    else:
        print("No actively running tasks found in Redis")