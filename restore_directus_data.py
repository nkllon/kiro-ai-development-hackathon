#!/usr/bin/env python3
"""
Restore Directus data from exports
"""

import json
import requests
import sys
from pathlib import Path

def get_auth_token():
    """Get authentication token from Directus"""
    # Try to get token using admin credentials
    response = requests.post('http://localhost:8055/auth/login', json={
        'email': 'admin@example.com',
        'password': 'd1r3ctu5'
    })
    
    if response.status_code == 200:
        return response.json()['data']['access_token']
    else:
        print(f"❌ Failed to authenticate: {response.text}")
        return None

def restore_interfaces(token):
    """Restore interface data"""
    print("🔄 Restoring interface data...")
    
    with open('directus_interface_export.json', 'r') as f:
        data = json.load(f)
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Create interfaces collection if it doesn't exist
    collection_data = {
        'collection': 'interfaces',
        'meta': {
            'collection': 'interfaces',
            'icon': 'code',
            'note': 'Interface registry data',
            'display_template': '{{name}}',
            'hidden': False,
            'singleton': False,
            'translations': None,
            'archive_field': None,
            'archive_app_filter': True,
            'archive_value': None,
            'unarchive_value': None,
            'sort_field': None,
            'accountability': 'all',
            'color': None,
            'item_duplication_fields': None,
            'sort': None,
            'group': None,
            'collapse': 'open',
            'preview_url': None,
            'versioning': False
        },
        'schema': {
            'name': 'interfaces'
        }
    }
    
    # Try to create collection
    response = requests.post('http://localhost:8055/collections', 
                           json=collection_data, headers=headers)
    
    if response.status_code not in [200, 409]:  # 409 = already exists
        print(f"⚠️ Collection creation response: {response.status_code}")
    
    # Insert interface data
    for interface in data['interfaces']:
        response = requests.post('http://localhost:8055/items/interfaces',
                               json=interface, headers=headers)
        if response.status_code == 200:
            print(f"✅ Restored interface: {interface['name']}")
        else:
            print(f"❌ Failed to restore {interface['name']}: {response.text}")

def restore_schema(token):
    """Restore schema from SQL file"""
    print("🔄 Restoring schema...")
    
    with open('directus_schema_migration.sql', 'r') as f:
        sql_content = f.read()
    
    # Split into individual statements
    statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    for statement in statements:
        if statement.startswith('CREATE TABLE') or statement.startswith('CREATE INDEX'):
            response = requests.post('http://localhost:8055/database/query', 
                                   json={'query': statement}, headers=headers)
            if response.status_code == 200:
                print(f"✅ Executed: {statement[:50]}...")
            else:
                print(f"⚠️ Failed: {statement[:50]}... - {response.text}")

def main():
    print("🚀 Restoring Directus data from exports...")
    
    # Check if export files exist
    if not Path('directus_interface_export.json').exists():
        print("❌ directus_interface_export.json not found")
        return False
    
    if not Path('directus_schema_migration.sql').exists():
        print("❌ directus_schema_migration.sql not found")
        return False
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        return False
    
    print("✅ Authenticated with Directus")
    
    # Restore data
    restore_schema(token)
    restore_interfaces(token)
    
    print("\n🎉 Data restoration completed!")
    print("🌐 Check your data at: http://localhost:8055/admin")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
