#!/usr/bin/env python3
"""
Query CMS Task Status - Find tasks with status information
"""

import requests
import json


def authenticate_with_directus() -> str:
    """Authenticate with Directus and get access token."""
    try:
        auth_data = {
            "email": "admin@example.com",
            "password": "d1r3ctu5"
        }
        
        response = requests.post(
            "http://localhost:8055/auth/login",
            json=auth_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('data', {}).get('access_token')
            return token
        return None
        
    except Exception as e:
        print(f"Authentication error: {e}")
        return None


def get_tasks_with_status(token: str):
    """Get all tasks and analyze their status fields."""
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            "http://localhost:8055/items/tasks",
            headers=headers,
            params={"limit": -1},  # Get all items
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            tasks = data.get('data', [])
            
            print(f"📊 Total tasks in CMS: {len(tasks)}")
            
            # Analyze status fields
            status_counts = {}
            tasks_with_status = 0
            tasks_without_status = 0
            
            status_field_names = ['status', 'task_status', 'completion_status', 'state']
            
            for task in tasks:
                has_status = False
                task_status_info = {}
                
                # Check for various status field names
                for field_name in status_field_names:
                    if field_name in task and task[field_name] is not None:
                        has_status = True
                        status_value = task[field_name]
                        task_status_info[field_name] = status_value
                        
                        # Count status values
                        key = f"{field_name}:{status_value}"
                        status_counts[key] = status_counts.get(key, 0) + 1
                
                if has_status:
                    tasks_with_status += 1
                else:
                    tasks_without_status += 1
            
            print(f"\n📈 Status Analysis:")
            print(f"Tasks WITH status: {tasks_with_status}")
            print(f"Tasks WITHOUT status: {tasks_without_status}")
            
            if status_counts:
                print(f"\n📋 Status Breakdown:")
                for status_key, count in sorted(status_counts.items()):
                    print(f"  - {status_key}: {count}")
            
            # Show sample tasks with status
            print(f"\n🔍 Sample tasks with status (first 5):")
            sample_count = 0
            for task in tasks:
                if sample_count >= 5:
                    break
                    
                task_has_status = False
                for field_name in status_field_names:
                    if field_name in task and task[field_name] is not None:
                        task_has_status = True
                        break
                
                if task_has_status:
                    task_id = task.get('id', 'unknown')
                    task_title = task.get('title', task.get('name', 'untitled'))[:50]
                    
                    status_info = []
                    for field_name in status_field_names:
                        if field_name in task and task[field_name] is not None:
                            status_info.append(f"{field_name}={task[field_name]}")
                    
                    print(f"  - Task {task_id}: {task_title} ({', '.join(status_info)})")
                    sample_count += 1
            
            return {
                "total_tasks": len(tasks),
                "tasks_with_status": tasks_with_status,
                "tasks_without_status": tasks_without_status,
                "status_breakdown": status_counts
            }
            
        else:
            print(f"❌ Failed to get tasks: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"💥 Error getting tasks: {e}")
        return None


if __name__ == "__main__":
    print("🔍 Querying CMS for task status information...")
    
    token = authenticate_with_directus()
    if not token:
        print("❌ Cannot proceed without authentication")
        exit(1)
    
    result = get_tasks_with_status(token)
    
    if result:
        print(f"\n🎯 ANSWER: {result['tasks_with_status']} tasks in the CMS have status information")
    else:
        print("❌ Failed to get task status information")