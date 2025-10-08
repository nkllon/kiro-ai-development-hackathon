#!/usr/bin/env python3
"""Verify that UI relationships are working."""

import requests


def verify_relationships():
    """Verify relationships are visible in the UI."""
    
    # Authenticate
    response = requests.post("http://localhost:8055/auth/login", json={
        "email": "admin@example.com",
        "password": "d1r3ctu5"
    })
    
    token = response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔍 Verifying Directus UI Relationships")
    print("=" * 50)
    
    # Check specifications collection fields
    response = requests.get("http://localhost:8055/fields/specifications", headers=headers)
    if response.status_code == 200:
        fields = response.json()["data"]
        
        print("\n📋 Specifications Collection Fields:")
        for field in fields:
            if field and field.get("field"):
                field_name = field["field"]
                interface = field.get("meta", {}).get("interface") if field.get("meta") else None
                
                if interface:
                    print(f"   • {field_name}: {interface}")
                elif "related" in field_name or "specification" in field_name:
                    print(f"   • {field_name}: (relationship field)")
    
    # Check code_files collection fields  
    response = requests.get("http://localhost:8055/fields/code_files", headers=headers)
    if response.status_code == 200:
        fields = response.json()["data"]
        
        print("\n💻 Code Files Collection Fields:")
        for field in fields:
            if field and field.get("field"):
                field_name = field["field"]
                interface = field.get("meta", {}).get("interface") if field.get("meta") else None
                
                if interface:
                    print(f"   • {field_name}: {interface}")
                elif "specification" in field_name:
                    print(f"   • {field_name}: (relationship field)")
    
    # Test actual relationship data
    print("\n🔗 Testing Relationship Data:")
    
    # Get a specification with related items
    response = requests.get(
        "http://localhost:8055/items/specifications/1?fields=*,related_code_files.*,related_documents.*,related_tasks.*",
        headers=headers
    )
    
    if response.status_code == 200:
        spec = response.json()["data"]
        print(f"   📋 Specification: {spec.get('spec_name', 'Unknown')}")
        
        code_files = spec.get("related_code_files", [])
        documents = spec.get("related_documents", [])
        tasks = spec.get("related_tasks", [])
        
        print(f"      Related code files: {len(code_files)}")
        print(f"      Related documents: {len(documents)}")
        print(f"      Related tasks: {len(tasks)}")
        
        if code_files:
            print("      Sample code files:")
            for file in code_files[:3]:
                print(f"        • {file.get('file_name', 'Unknown')}")
    
    print("\n✅ Verification Complete!")
    print("\n🌐 In the Directus web interface (http://localhost:8055):")
    print("   1. Go to 'Specifications' collection")
    print("   2. Click on any specification")
    print("   3. You should see 'Related Code Files', 'Related Documents', 'Related Tasks' sections")
    print("   4. Go to 'Code Files' collection")
    print("   5. Edit any code file")
    print("   6. You should see a 'Specification' dropdown selector")


if __name__ == "__main__":
    verify_relationships()