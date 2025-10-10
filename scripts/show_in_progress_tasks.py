#!/usr/bin/env python3
"""
Show In-Progress Tasks from CMS
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


def show_in_progress_tasks(token: str):
    """Show all tasks with in_progress status."""
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Query for tasks with in_progress status
        response = requests.get(
            "http://localhost:8055/items/tasks",
            headers=headers,
            params={
                "filter[status][_eq]": "in_progress",
                "limit": -1
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            tasks = data.get('data', [])
            
            print(f"📊 Found {len(tasks)} tasks with 'in_progress' status:")
            
            if not tasks:
                print("No tasks currently in progress.")
                return
            
            for i, task in enumerate(tasks, 1):
                print(f"\n🔄 Task {i}:")
                print(f"  ID: {task.get('id', 'N/A')}")
                print(f"  Title: {task.get('title', task.get('name', 'Untitled'))}")
                print(f"  Status: {task.get('status', 'N/A')}")
                
                # Show additional relevant fields
                if 'description' in task and task['description']:
                    desc = task['description'][:200] + "..." if len(task['description']) > 200 else task['description']
                    print(f"  Description: {desc}")
                
                if 'priority' in task and task['priority']:
                    print(f"  Priority: {task['priority']}")
                
                if 'assigned_to' in task and task['assigned_to']:
                    print(f"  Assigned To: {task['assigned_to']}")
                
                if 'due_date' in task and task['due_date']:
                    print(f"  Due Date: {task['due_date']}")
                
                if 'created_at' in task and task['created_at']:
                    print(f"  Created: {task['created_at']}")
                
                if 'updated_at' in task and task['updated_at']:
                    print(f"  Updated: {task['updated_at']}")
                
                # Show any progress-related fields
                progress_fields = ['progress', 'completion_percentage', 'progress_notes']
                for field in progress_fields:
                    if field in task and task[field] is not None:
                        print(f"  {field.replace('_', ' ').title()}: {task[field]}")
            
            return tasks
            
        else:
            print(f"❌ Failed to get in-progress tasks: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"💥 Error getting in-progress tasks: {e}")
        return None


if __name__ == "__main__":
    print("🔍 Showing tasks with 'in_progress' status from CMS...")
    
    token = authenticate_with_directus()
    if not token:
        print("❌ Cannot proceed without authentication")
        exit(1)
    
    tasks = show_in_progress_tasks(token)