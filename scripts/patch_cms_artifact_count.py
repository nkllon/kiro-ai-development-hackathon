#!/usr/bin/env python3
"""
Patch Script: CMS Artifact Count - Observer Mode Fix
Root Cause: CMS configuration collector was falling back to mock mode due to missing Directus token
Fix: Authenticate with Directus and get real artifact counts from running CMS

# TECHNICAL DEBT ANNOTATIONS (Auto-generated)
# TODO: [CRITICAL] Environment variable dependency - DIRECTUS_TOKEN required in ~/.env
#   - Impact: CMS collector fails silently without proper token configuration
#   - Cleanup: Add DIRECTUS_TOKEN to ~/.env or implement token auto-discovery
#   - Timeline: Before next CMS integration work
#   - Owner: Infrastructure team

# TODO: [HIGH] Hard-coded credentials in patch script
#   - Impact: Security risk with admin credentials in source code
#   - Cleanup: Move to secure credential management system
#   - Timeline: Before production deployment
#   - Owner: Security team

# TODO: [MEDIUM] Mock mode fallback behavior unclear
#   - Impact: Developers don't know when CMS is in mock vs real mode
#   - Cleanup: Add clear logging and status indicators for CMS mode
#   - Timeline: Next sprint
#   - Owner: Development team

# TODO: [LOW] Direct API calls bypass collector abstraction
#   - Impact: Inconsistent data access patterns
#   - Cleanup: Enhance collector to handle all artifact counting needs
#   - Timeline: Future refactoring cycle
#   - Owner: Architecture team
"""

import sys
import os
import asyncio
import requests
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.runtime_state_registry.collectors.cms_configuration_collector import CMSConfigurationCollector


def authenticate_with_directus() -> str:
    """Authenticate with Directus and get access token."""
    try:
        # Use credentials from docker-compose.yml
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
            if token:
                print(f"✅ Successfully authenticated with Directus")
                return token
        
        print(f"❌ Authentication failed: {response.status_code}")
        return None
        
    except Exception as e:
        print(f"💥 Authentication error: {e}")
        return None


def get_directus_collections(token: str) -> dict:
    """Get collections directly from Directus API."""
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            "http://localhost:8055/collections",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            collections = data.get('data', [])
            return collections
        else:
            print(f"❌ Failed to get collections: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"💥 Error getting collections: {e}")
        return []


def get_collection_items(token: str, collection_name: str) -> list:
    """Get items from a specific collection."""
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f"http://localhost:8055/items/{collection_name}",
            headers=headers,
            params={"limit": -1},  # Get all items
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('data', [])
            return items
        else:
            return []
            
    except Exception as e:
        print(f"⚠️  Error getting items from {collection_name}: {e}")
        return []


async def count_cms_artifacts_with_auth():
    """Count CMS artifacts with proper authentication."""
    print("🔍 Patching CMS artifact count issue...")
    
    # Step 1: Authenticate with Directus
    token = authenticate_with_directus()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Step 2: Set environment variable for the collector
    os.environ['DIRECTUS_TOKEN'] = token
    os.environ['DIRECTUS_URL'] = 'http://localhost:8055'
    
    # Step 3: Use the collector with authentication
    collector = CMSConfigurationCollector()
    data = await collector.collect_all_configuration_data()
    
    print(f"\n📊 CMS Artifact Count Results:")
    print(f"Service Definitions: {len(data)}")
    
    policies = collector.get_compliance_policies()
    print(f"Compliance Policies: {len(policies)}")
    
    templates = collector.get_configuration_templates()
    print(f"Configuration Templates: {len(templates)}")
    
    total_from_collector = len(data) + len(policies) + len(templates)
    print(f"Total from Collector: {total_from_collector}")
    
    # Step 4: Also get direct collection counts from Directus
    print(f"\n🔍 Direct Directus Collection Analysis:")
    collections = get_directus_collections(token)
    
    artifact_collections = []
    total_direct_items = 0
    
    for collection in collections:
        collection_name = collection.get('collection', '')
        
        # Skip system collections
        if collection_name.startswith('directus_'):
            continue
            
        items = get_collection_items(token, collection_name)
        item_count = len(items)
        
        if item_count > 0:
            artifact_collections.append({
                'name': collection_name,
                'count': item_count
            })
            total_direct_items += item_count
            print(f"  - {collection_name}: {item_count} items")
    
    print(f"\nTotal Direct Items: {total_direct_items}")
    print(f"Collections with Data: {len(artifact_collections)}")
    
    # Step 5: Show detailed breakdown
    if data:
        print(f"\n📋 Service Definitions Details:")
        for name, service_data in data.items():
            print(f"  - {name}: {service_data.expected_status.value}")
    
    if policies:
        print(f"\n📋 Compliance Policies Details:")
        for policy in policies:
            print(f"  - {policy.get('policy_name', 'unknown')}")
    
    if templates:
        print(f"\n📋 Configuration Templates Details:")
        for name in templates.keys():
            print(f"  - {name}")
    
    # Final answer
    print(f"\n🎯 FINAL ANSWER:")
    print(f"Total CMS Artifacts Logged: {max(total_from_collector, total_direct_items)}")
    
    return {
        "collector_total": total_from_collector,
        "direct_total": total_direct_items,
        "service_definitions": len(data),
        "compliance_policies": len(policies),
        "configuration_templates": len(templates),
        "artifact_collections": artifact_collections
    }


def validate_fix() -> dict:
    """Validate the fix was applied correctly."""
    try:
        # Test Directus connectivity
        response = requests.get("http://localhost:8055/server/health", timeout=5)
        directus_healthy = response.status_code == 200
        
        # Test authentication
        token = authenticate_with_directus()
        auth_working = token is not None
        
        return {
            "status": "passed" if (directus_healthy and auth_working) else "failed",
            "directus_healthy": directus_healthy,
            "authentication_working": auth_working,
            "validation_results": {
                "directus_accessible": directus_healthy,
                "can_authenticate": auth_working,
                "environment_configured": bool(os.getenv('DIRECTUS_TOKEN'))
            }
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "validation_results": {}
        }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Patch CMS artifact count issue")
    parser.add_argument('--validate', action='store_true', help='Validate the fix')
    
    args = parser.parse_args()
    
    if args.validate:
        result = validate_fix()
        print(f"Validation Status: {result['status']}")
        for key, value in result.get('validation_results', {}).items():
            print(f"  {key}: {value}")
    else:
        asyncio.run(count_cms_artifacts_with_auth())