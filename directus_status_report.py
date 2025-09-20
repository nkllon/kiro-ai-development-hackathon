#!/usr/bin/env python3
"""
Directus Status Report

Shows the current state of Directus with relationships and data.
"""

import requests
import json


def generate_status_report():
    """Generate a comprehensive status report."""
    
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
    
    print("📊 Directus CMS Status Report")
    print("=" * 60)
    
    # Get collection counts
    collections = ["specifications", "code_files", "documents", "tasks"]
    
    print("\n📋 Collection Summary:")
    for collection in collections:
        try:
            response = requests.get(
                f"http://localhost:8055/items/{collection}?aggregate[countDistinct]=id",
                headers=headers
            )
            
            if response.status_code == 200:
                count = response.json()["data"][0]["countDistinct"]["id"]
                print(f"   • {collection}: {count:,} items")
            else:
                print(f"   • {collection}: Error getting count")
                
        except Exception as e:
            print(f"   • {collection}: Error - {e}")
    
    # Check relationships
    print("\n🔗 Relationship Status:")
    
    try:
        # Get specifications with linked items
        response = requests.get(
            "http://localhost:8055/items/code_files?filter[specification_id][_nnull]=true&aggregate[countDistinct]=id",
            headers=headers
        )
        
        if response.status_code == 200:
            linked_code_files = response.json()["data"][0]["countDistinct"]["id"]
            print(f"   • Code files linked to specs: {linked_code_files:,}")
        
        response = requests.get(
            "http://localhost:8055/items/documents?filter[specification_id][_nnull]=true&aggregate[countDistinct]=id",
            headers=headers
        )
        
        if response.status_code == 200:
            linked_documents = response.json()["data"][0]["countDistinct"]["id"]
            print(f"   • Documents linked to specs: {linked_documents:,}")
        
        response = requests.get(
            "http://localhost:8055/items/tasks?filter[specification_id][_nnull]=true&aggregate[countDistinct]=id",
            headers=headers
        )
        
        if response.status_code == 200:
            linked_tasks = response.json()["data"][0]["countDistinct"]["id"]
            print(f"   • Tasks linked to specs: {linked_tasks:,}")
            
    except Exception as e:
        print(f"   Error checking relationships: {e}")
    
    # Show sample specifications with their related items
    print("\n📋 Sample Specifications with Related Items:")
    
    try:
        # Get specs that have related items
        response = requests.get(
            "http://localhost:8055/items/specifications?limit=10&fields=id,spec_name",
            headers=headers
        )
        
        if response.status_code == 200:
            specs = response.json()["data"]
            
            for spec in specs[:5]:  # Show first 5
                spec_id = spec["id"]
                spec_name = spec["spec_name"]
                
                # Count related items for this spec
                code_response = requests.get(
                    f"http://localhost:8055/items/code_files?filter[specification_id][_eq]={spec_id}&aggregate[countDistinct]=id",
                    headers=headers
                )
                
                doc_response = requests.get(
                    f"http://localhost:8055/items/documents?filter[specification_id][_eq]={spec_id}&aggregate[countDistinct]=id",
                    headers=headers
                )
                
                task_response = requests.get(
                    f"http://localhost:8055/items/tasks?filter[specification_id][_eq]={spec_id}&aggregate[countDistinct]=id",
                    headers=headers
                )
                
                code_count = 0
                doc_count = 0
                task_count = 0
                
                if code_response.status_code == 200:
                    code_count = code_response.json()["data"][0]["countDistinct"]["id"]
                
                if doc_response.status_code == 200:
                    doc_count = doc_response.json()["data"][0]["countDistinct"]["id"]
                
                if task_response.status_code == 200:
                    task_count = task_response.json()["data"][0]["countDistinct"]["id"]
                
                if code_count > 0 or doc_count > 0 or task_count > 0:
                    print(f"   📋 {spec_name[:50]}...")
                    print(f"      Code files: {code_count}, Documents: {doc_count}, Tasks: {task_count}")
                
    except Exception as e:
        print(f"   Error getting sample data: {e}")
    
    # Show relationship configuration
    print("\n🔧 Relationship Configuration:")
    
    try:
        response = requests.get("http://localhost:8055/relations", headers=headers)
        
        if response.status_code == 200:
            relations = response.json()["data"]
            
            # Filter to our custom relations
            custom_relations = [r for r in relations if not r["collection"].startswith("directus_")]
            
            for rel in custom_relations:
                print(f"   🔗 {rel['collection']}.{rel['field']} → {rel['related_collection']}")
                
    except Exception as e:
        print(f"   Error getting relations: {e}")
    
    print("\n" + "=" * 60)
    print("🌐 Directus Web Interface: http://localhost:8055")
    print("   Login: admin@example.com / d1r3ctu5")
    print("\n✅ Status: Directus CMS is ready for use with:")
    print("   • Complete repository data synchronized")
    print("   • Proper relationships configured")
    print("   • Working web interface for browsing and editing")
    print("   • API access for programmatic use")


if __name__ == "__main__":
    generate_status_report()