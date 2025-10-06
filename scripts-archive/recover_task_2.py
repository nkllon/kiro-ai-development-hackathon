#!/usr/bin/env python3
"""
Task ID 2 Recovery Script
Generated: 2025-10-05T21:33:14.132305+00:00
Root Cause: STATUS_SYNC_FAILURE: Task completed but status not synchronized
"""

import requests
import json
from datetime import datetime, timezone

def authenticate_with_directus():
    """Authenticate with Directus CMS"""
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
            return data.get('data', {}).get('access_token')
        return None
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return None

def update_task_status():
    """Update Task ID 2 status to failed"""
    token = authenticate_with_directus()
    if not token:
        print("❌ Cannot proceed without authentication")
        return False
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    update_data = {
        "status": "failed",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "notes": "Status corrected by recovery script - task execution failed"
    }
    
    try:
        response = requests.patch(
            f"http://localhost:8055/items/tasks/2",
            headers=headers,
            json=update_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"✅ Task 2 status updated to 'failed'")
            return True
        else:
            print(f"❌ Failed to update task status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating task status: {e}")
        return False

def validate_recovery():
    """Validate that recovery was successful"""
    token = authenticate_with_directus()
    if not token:
        return False
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            f"http://localhost:8055/items/tasks/2",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            task_data = response.json().get('data', {})
            current_status = task_data.get('status')
            print(f"📊 Current task status: {current_status}")
            return current_status == 'failed'
        else:
            print(f"❌ Failed to validate recovery: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error validating recovery: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Starting Task ID 2 recovery...")
    
    if update_task_status():
        if validate_recovery():
            print("✅ Recovery completed successfully")
        else:
            print("❌ Recovery validation failed")
    else:
        print("❌ Recovery failed")
