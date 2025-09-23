#!/usr/bin/env python3
"""Create sample relationships to demonstrate functionality."""

import requests


def create_sample_relationships():
    """Create sample relationships between specs and files."""
    
    # Authenticate
    response = requests.post("http://localhost:8055/auth/login", json={
        "email": "admin@example.com",
        "password": "d1r3ctu5"
    })
    
    token = response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔗 Creating Sample Relationships")
    print("=" * 40)
    
    # Find Integration Orchestrator spec
    response = requests.get(
        "http://localhost:8055/items/specifications",
        headers=headers,
        params={"filter[spec_name][_eq]": "integration-orchestrator-framework"}
    )
    
    if response.status_code == 200 and response.json()["data"]:
        integration_spec = response.json()["data"][0]
        spec_id = integration_spec["id"]
        
        print(f"📋 Found Integration Orchestrator spec (ID: {spec_id})")
        
        # Find related code files
        response = requests.get(
            "http://localhost:8055/items/code_files",
            headers=headers,
            params={"filter[file_path][_contains]": "integration_orchestrator", "limit": 10}
        )
        
        if response.status_code == 200:
            code_files = response.json()["data"]
            print(f"💻 Found {len(code_files)} related code files")
            
            # Link them to the spec
            linked_count = 0
            for code_file in code_files:
                update_response = requests.patch(
                    f"http://localhost:8055/items/code_files/{code_file['id']}",
                    headers=headers,
                    json={"specification_id": spec_id}
                )
                
                if update_response.status_code == 200:
                    linked_count += 1
                    print(f"   ✅ Linked: {code_file['file_name']}")
            
            print(f"🔗 Successfully linked {linked_count} code files to Integration Orchestrator spec")
    
    # Find AI Cursor Sharing spec
    response = requests.get(
        "http://localhost:8055/items/specifications",
        headers=headers,
        params={"filter[spec_name][_eq]": "ai-driven-cursor-sharing"}
    )
    
    if response.status_code == 200 and response.json()["data"]:
        cursor_spec = response.json()["data"][0]
        spec_id = cursor_spec["id"]
        
        print(f"\n📋 Found AI Cursor Sharing spec (ID: {spec_id})")
        
        # Find related code files
        response = requests.get(
            "http://localhost:8055/items/code_files",
            headers=headers,
            params={"filter[file_path][_contains]": "cursor_sharing", "limit": 10}
        )
        
        if response.status_code == 200:
            code_files = response.json()["data"]
            print(f"💻 Found {len(code_files)} related code files")
            
            # Link them to the spec
            linked_count = 0
            for code_file in code_files:
                update_response = requests.patch(
                    f"http://localhost:8055/items/code_files/{code_file['id']}",
                    headers=headers,
                    json={"specification_id": spec_id}
                )
                
                if update_response.status_code == 200:
                    linked_count += 1
                    print(f"   ✅ Linked: {code_file['file_name']}")
            
            print(f"🔗 Successfully linked {linked_count} code files to AI Cursor Sharing spec")
    
    # Test the relationships
    print(f"\n🧪 Testing Relationships:")
    
    # Get Integration Orchestrator with related files
    response = requests.get(
        f"http://localhost:8055/items/specifications",
        headers=headers,
        params={
            "filter[spec_name][_eq]": "integration-orchestrator-framework",
            "fields": "id,spec_name,related_code_files.file_name"
        }
    )
    
    if response.status_code == 200 and response.json()["data"]:
        spec = response.json()["data"][0]
        related_files = spec.get("related_code_files", [])
        
        print(f"   📋 {spec['spec_name']}")
        print(f"   🔗 Related files: {len(related_files)}")
        
        for file in related_files[:5]:  # Show first 5
            print(f"      • {file['file_name']}")
        
        if len(related_files) > 5:
            print(f"      ... and {len(related_files) - 5} more")
    
    print(f"\n✅ Sample Relationships Created!")
    print(f"\n🌐 Now go to http://localhost:8055 and:")
    print(f"   1. Navigate to 'Specifications' collection")
    print(f"   2. Click on 'integration-orchestrator-framework'")
    print(f"   3. You should see a 'Related Code Files' section with actual files!")
    print(f"   4. Click on 'Code Files' collection")
    print(f"   5. Edit any integration_orchestrator file")
    print(f"   6. You should see it's linked to the Integration Orchestrator spec!")


if __name__ == "__main__":
    create_sample_relationships()