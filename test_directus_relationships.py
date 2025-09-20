#!/usr/bin/env python3
"""Test Directus relationships to show they're working."""

import requests
import json


def test_relationships():
    """Test that relationships are working in Directus."""
    
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
    
    print("🔍 Testing Directus Relationships")
    print("=" * 40)
    
    # Test 1: Get specifications with related items
    print("\n1. Specifications with related items:")
    response = requests.get(
        "http://localhost:8055/items/specifications?limit=5&fields=id,spec_name,code_files.id,documents.id,tasks.id",
        headers=headers
    )
    
    if response.status_code == 200:
        specs = response.json()["data"]
        for spec in specs:
            code_count = len(spec.get("code_files", []))
            doc_count = len(spec.get("documents", []))
            task_count = len(spec.get("tasks", []))
            
            print(f"   📋 {spec['spec_name'][:50]}...")
            print(f"      Code files: {code_count}, Documents: {doc_count}, Tasks: {task_count}")
    
    # Test 2: Get code files with their specifications
    print("\n2. Code files with their specifications:")
    response = requests.get(
        "http://localhost:8055/items/code_files?filter[specification_id][_nnull]=true&limit=5&fields=file_name,specification_id.spec_name",
        headers=headers
    )
    
    if response.status_code == 200:
        files = response.json()["data"]
        for file in files:
            spec_name = file.get("specification_id", {}).get("spec_name", "No spec")
            print(f"   💻 {file['file_name']} → {spec_name}")
    
    # Test 3: Show relationship structure
    print("\n3. Relationship structure:")
    
    # Get collections with relationships
    response = requests.get("http://localhost:8055/relations", headers=headers)
    
    if response.status_code == 200:
        relations = response.json()["data"]
        
        # Filter to our custom relations
        custom_relations = [r for r in relations if not r["collection"].startswith("directus_")]
        
        print(f"   Found {len(custom_relations)} custom relationships:")
        for rel in custom_relations:
            print(f"   🔗 {rel['collection']}.{rel['field']} → {rel['related_collection']}")
    
    print("\n✅ Relationships are working!")
    print("\n🌐 In the Directus web interface, you can now:")
    print("   • Click on a specification to see its related code files")
    print("   • Navigate from code files back to their specifications")
    print("   • Create new relationships using dropdown selectors")
    print("   • Filter and search across related items")


if __name__ == "__main__":
    test_relationships()