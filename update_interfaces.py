#!/usr/bin/env python3
"""
Update Interfaces with Proper Data
"""

import sys
import requests
import re
from pathlib import Path

DIRECTUS_URL = "http://localhost:8055"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "d1r3ctu5"

def get_auth_token():
    """Get authentication token from Directus"""
    response = requests.post(f"{DIRECTUS_URL}/auth/login", json={
        'email': ADMIN_EMAIL,
        'password': ADMIN_PASSWORD
    })
    
    if response.status_code == 200:
        return response.json()['data']['access_token']
    else:
        print(f"❌ Authentication failed: {response.text}")
        return None

def update_interfaces(token):
    """Update all interfaces with proper data"""
    print("🔌 Updating interfaces with proper data...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Get all interfaces
    response = requests.get(f"{DIRECTUS_URL}/items/interfaces", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get interfaces: {response.text}")
        return 0
    
    interfaces = response.json()['data']
    print(f"Found {len(interfaces)} interfaces to update")
    
    # Define interface data based on ID
    interface_data = {
        6: {"name": "BeastModeError", "file_path": "src/beast_mode/core/exceptions.py", "interface_type": "exception"},
        7: {"name": "BeastModeConfigurationError", "file_path": "src/beast_mode/core/exceptions.py", "interface_type": "exception"},
        8: {"name": "BeastModeRuntimeError", "file_path": "src/beast_mode/core/exceptions.py", "interface_type": "exception"},
        9: {"name": "BeastModeValidationError", "file_path": "src/beast_mode/core/exceptions.py", "interface_type": "exception"},
        10: {"name": "Exceptions", "file_path": "src/beast_mode/core/exceptions.py", "interface_type": "module"},
        11: {"name": "ModuleStatus", "file_path": "src/rm_ddd/core/unified_reflective_module.py", "interface_type": "enum"},
        12: {"name": "ModuleCapability", "file_path": "src/rm_ddd/core/unified_reflective_module.py", "interface_type": "enum"},
        13: {"name": "OperationTrace", "file_path": "src/rm_ddd/core/unified_reflective_module.py", "interface_type": "dataclass"},
        14: {"name": "ModuleHealth", "file_path": "src/rm_ddd/core/unified_reflective_module.py", "interface_type": "dataclass"},
        15: {"name": "GracefulDegradationResult", "file_path": "src/rm_ddd/core/unified_reflective_module.py", "interface_type": "dataclass"},
        16: {"name": "ReflectiveModule", "file_path": "src/rm_ddd/core/unified_reflective_module.py", "interface_type": "abstract_class"},
        17: {"name": "TestBeastMode", "file_path": "tests/beast_mode/test_unit.py", "interface_type": "test_class"}
    }
    
    updated = 0
    for interface in interfaces:
        interface_id = interface['id']
        if interface_id in interface_data:
            data = interface_data[interface_id]
            
            update_response = requests.patch(
                f"{DIRECTUS_URL}/items/interfaces/{interface_id}",
                json=data,
                headers=headers
            )
            
            if update_response.status_code == 200:
                print(f"   ✅ Updated interface {interface_id}: {data['name']} -> {data['file_path']}")
                updated += 1
            else:
                print(f"   ❌ Failed to update interface {interface_id}: {update_response.text}")
    
    print(f"🔌 Interfaces updated: {updated}")
    return updated

def main():
    """Main function"""
    print("🔧 Updating Interfaces")
    print("=" * 30)
    
    token = get_auth_token()
    if not token:
        return 1
    
    updated = update_interfaces(token)
    
    print(f"\n🎉 Update complete!")
    print(f"📊 Interfaces updated: {updated}")
    print(f"\n🌐 Check in Directus: http://localhost:8055/admin")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
