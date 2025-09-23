#!/usr/bin/env python3
"""
Register Collections in Directus

Properly registers custom collections in Directus so they appear in the admin interface.
"""

import requests
import json


def register_collections():
    """Register custom collections in Directus."""
    
    # Authenticate
    response = requests.post("http://localhost:8055/auth/login", json={
        "email": "admin@example.com",
        "password": "d1r3ctu5"
    })
    
    if response.status_code != 200:
        print("❌ Authentication failed")
        return
    
    token = response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print("📋 Registering Collections in Directus")
    print("=" * 40)
    
    # Collection configurations
    collections_config = [
        {
            "collection": "specifications",
            "meta": {
                "collection": "specifications",
                "icon": "description",
                "note": "Feature specifications and requirements",
                "display_template": "{{spec_name}}",
                "hidden": False,
                "singleton": False,
                "sort_field": "priority",
                "archive_field": "status",
                "archive_value": "archived",
                "unarchive_value": "active"
            },
            "fields": [
                {
                    "field": "spec_name",
                    "type": "string",
                    "meta": {
                        "interface": "input",
                        "display": "raw",
                        "readonly": False,
                        "hidden": False,
                        "width": "full",
                        "options": {},
                        "display_options": {},
                        "note": "Name of the specification"
                    }
                }
            ]
        },
        {
            "collection": "code_files", 
            "meta": {
                "collection": "code_files",
                "icon": "code",
                "note": "Source code files in the repository",
                "display_template": "{{file_name}}",
                "hidden": False,
                "singleton": False
            }
        },
        {
            "collection": "documents",
            "meta": {
                "collection": "documents", 
                "icon": "article",
                "note": "Documentation and markdown files",
                "display_template": "{{title}}",
                "hidden": False,
                "singleton": False
            }
        },
        {
            "collection": "tasks",
            "meta": {
                "collection": "tasks",
                "icon": "task_alt", 
                "note": "Implementation tasks and todos",
                "display_template": "{{title}}",
                "hidden": False,
                "singleton": False,
                "sort_field": "priority"
            }
        }
    ]
    
    # Register each collection
    for config in collections_config:
        collection_name = config["collection"]
        
        # Check if collection exists
        response = requests.get(
            f"http://localhost:8055/collections/{collection_name}",
            headers=headers
        )
        
        if response.status_code == 200:
            # Update existing collection
            response = requests.patch(
                f"http://localhost:8055/collections/{collection_name}",
                headers=headers,
                json={"meta": config["meta"]}
            )
            
            if response.status_code == 200:
                print(f"   ✅ Updated collection: {collection_name}")
            else:
                print(f"   ⚠️  Failed to update {collection_name}: {response.status_code}")
        else:
            # Create new collection
            response = requests.post(
                "http://localhost:8055/collections",
                headers=headers,
                json=config
            )
            
            if response.status_code in [200, 201]:
                print(f"   ✅ Created collection: {collection_name}")
            else:
                print(f"   ❌ Failed to create {collection_name}: {response.status_code}")
    
    # Test access after registration
    print("\n🧪 Testing collection access...")
    
    response = requests.get(
        "http://localhost:8055/items/specifications?limit=1",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"✅ Specifications accessible: {len(data)} items returned")
        
        if data:
            spec = data[0]
            print(f"   Sample: {spec.get('spec_name', 'No name')}")
            
            # Test with relationships
            spec_id = spec["id"]
            response = requests.get(
                f"http://localhost:8055/items/specifications/{spec_id}?fields=*,code_files.file_name",
                headers=headers
            )
            
            if response.status_code == 200:
                spec_with_relations = response.json()["data"]
                code_files = spec_with_relations.get("code_files", [])
                print(f"   Related code files: {len(code_files)}")
                
                if code_files:
                    print(f"   Sample file: {code_files[0].get('file_name', 'No name')}")
    else:
        print(f"❌ Specifications not accessible: {response.status_code}")
        print(response.text)
    
    print("\n🎉 Collection registration complete!")
    print("\n🌐 Try accessing: http://localhost:8055/admin/content/specifications")
    print("   Login: admin@example.com / d1r3ctu5")


if __name__ == "__main__":
    register_collections()