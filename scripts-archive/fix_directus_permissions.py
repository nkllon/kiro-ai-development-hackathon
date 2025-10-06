#!/usr/bin/env python3
"""
Fix Directus Permissions

Ensures all collections have proper permissions for the admin user.
"""

import requests
import json


def fix_directus_permissions():
    """Fix permissions for all collections."""
    
    # Authenticate
    response = requests.post("http://localhost:8055/auth/login", json={
        "email": "admin@example.com",
        "password": "d1r3ctu5"
    })
    
    if response.status_code != 200:
        print("❌ Authentication failed")
        return
    
    token = response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔧 Fixing Directus Permissions")
    print("=" * 40)
    
    # Get all collections
    response = requests.get("http://localhost:8055/collections", headers=headers)
    
    if response.status_code != 200:
        print("❌ Failed to get collections")
        return
    
    collections = response.json()["data"]
    custom_collections = [c for c in collections if not c["collection"].startswith("directus_")]
    
    print(f"📋 Found {len(custom_collections)} custom collections")
    
    # Get admin role ID
    response = requests.get("http://localhost:8055/roles", headers=headers)
    admin_role_id = None
    
    if response.status_code == 200:
        roles = response.json()["data"]
        for role in roles:
            if role.get("admin_access", False):
                admin_role_id = role["id"]
                break
    
    if not admin_role_id:
        print("❌ Could not find admin role")
        return
    
    print(f"👤 Admin role ID: {admin_role_id}")
    
    # Create permissions for each collection
    for collection in custom_collections:
        collection_name = collection["collection"]
        
        # Check if permissions already exist
        response = requests.get(
            f"http://localhost:8055/permissions?filter[role][_eq]={admin_role_id}&filter[collection][_eq]={collection_name}",
            headers=headers
        )
        
        if response.status_code == 200:
            existing_permissions = response.json()["data"]
            
            if existing_permissions:
                print(f"   ✅ {collection_name} (permissions exist)")
                continue
        
        # Create full permissions for admin
        permission_data = {
            "role": admin_role_id,
            "collection": collection_name,
            "action": "read",
            "permissions": {},
            "validation": {},
            "presets": {},
            "fields": ["*"]
        }
        
        # Create read permission
        response = requests.post(
            "http://localhost:8055/permissions",
            headers=headers,
            json=permission_data
        )
        
        if response.status_code in [200, 201]:
            print(f"   ✅ {collection_name} (read permission created)")
        else:
            print(f"   ❌ {collection_name} (failed to create read permission)")
        
        # Create other permissions (create, update, delete)
        for action in ["create", "update", "delete"]:
            permission_data["action"] = action
            
            response = requests.post(
                "http://localhost:8055/permissions",
                headers=headers,
                json=permission_data
            )
    
    print("\n🔄 Refreshing Directus schema...")
    
    # Refresh schema
    response = requests.post(
        "http://localhost:8055/schema/snapshot",
        headers=headers
    )
    
    if response.status_code in [200, 201]:
        print("✅ Schema refreshed")
    
    # Test access to specifications
    print("\n🧪 Testing collection access...")
    
    response = requests.get(
        "http://localhost:8055/items/specifications?limit=3",
        headers=headers
    )
    
    if response.status_code == 200:
        specs = response.json()["data"]
        print(f"✅ Specifications accessible: {len(specs)} items")
        
        if specs:
            # Test with relationships
            spec_id = specs[0]["id"]
            response = requests.get(
                f"http://localhost:8055/items/specifications/{spec_id}?fields=*,code_files.file_name",
                headers=headers
            )
            
            if response.status_code == 200:
                spec_data = response.json()["data"]
                code_files_count = len(spec_data.get("code_files", []))
                print(f"✅ Relationships working: {code_files_count} related code files")
            else:
                print("⚠️  Relationships may need configuration")
    else:
        print(f"❌ Specifications not accessible: {response.status_code}")
        print(response.text)
    
    print("\n🎉 Permission fix complete!")
    print("🌐 Try accessing Directus at: http://localhost:8055")


if __name__ == "__main__":
    fix_directus_permissions()