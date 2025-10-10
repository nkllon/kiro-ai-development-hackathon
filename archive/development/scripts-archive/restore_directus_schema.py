#!/usr/bin/env python3
"""
Restore Directus schema through proper API calls
"""

import requests
import sys

def get_auth_token():
    """Get authentication token from Directus"""
    response = requests.post('http://localhost:8055/auth/login', json={
        'email': 'admin@example.com',
        'password': 'd1r3ctu5'
    })
    
    if response.status_code == 200:
        return response.json()['data']['access_token']
    else:
        print(f"❌ Failed to authenticate: {response.text}")
        return None

def create_collection(token, collection_name, fields):
    """Create a collection with fields through Directus API"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Create collection
    collection_data = {
        'collection': collection_name,
        'meta': {
            'collection': collection_name,
            'icon': 'folder',
            'note': f'{collection_name} data',
            'display_template': '{{name}}',
            'hidden': False,
            'singleton': False,
            'accountability': 'all'
        },
        'schema': {
            'name': collection_name
        }
    }
    
    response = requests.post('http://localhost:8055/collections', 
                           json=collection_data, headers=headers)
    
    if response.status_code not in [200, 409]:  # 409 = already exists
        print(f"⚠️ Collection {collection_name} creation: {response.status_code}")
        if response.status_code != 409:
            print(f"   Error: {response.text}")
            return False
    
    # Create fields
    for field in fields:
        field_data = {
            'field': field['name'],
            'type': field['type'],
            'meta': {
                'collection': collection_name,
                'field': field['name'],
                'special': field.get('special', []),
                'interface': field.get('interface', 'input'),
                'options': field.get('options', {}),
                'display': field.get('display', 'raw'),
                'display_options': field.get('display_options', {}),
                'readonly': field.get('readonly', False),
                'hidden': field.get('hidden', False),
                'sort': field.get('sort', None),
                'width': field.get('width', 'full'),
                'group': field.get('group', None),
                'note': field.get('note', ''),
                'required': field.get('required', False),
                'validation': field.get('validation', None),
                'validation_message': field.get('validation_message', None)
            },
            'schema': {
                'name': field['name'],
                'table': collection_name,
                'data_type': field['type'],
                'default_value': field.get('default', None),
                'is_nullable': not field.get('required', False),
                'is_unique': field.get('unique', False),
                'is_primary_key': field.get('primary_key', False),
                'has_auto_increment': field.get('auto_increment', False),
                'foreign_key_table': field.get('foreign_key_table', None),
                'foreign_key_column': field.get('foreign_key_column', None)
            }
        }
        
        response = requests.post(f'http://localhost:8055/fields/{collection_name}',
                               json=field_data, headers=headers)
        
        if response.status_code not in [200, 409]:
            print(f"⚠️ Field {field['name']} in {collection_name}: {response.status_code}")
            if response.status_code != 409:
                print(f"   Error: {response.text}")
        else:
            print(f"✅ Created field: {collection_name}.{field['name']}")
    
    return True

def main():
    print("🚀 Restoring Directus schema through API...")
    
    token = get_auth_token()
    if not token:
        return False
    
    print("✅ Authenticated with Directus")
    
    # Define collections and their fields based on the SQL schema
    collections = {
        'repository_items': [
            {'name': 'id', 'type': 'uuid', 'primary_key': True, 'required': True},
            {'name': 'item_type', 'type': 'string', 'required': True, 'width': 'half'},
            {'name': 'path', 'type': 'string', 'required': True, 'width': 'full'},
            {'name': 'name', 'type': 'string', 'required': True, 'width': 'half'},
            {'name': 'content_hash', 'type': 'string', 'width': 'half'},
            {'name': 'file_size', 'type': 'integer', 'width': 'half'},
            {'name': 'mime_type', 'type': 'string', 'width': 'half'},
            {'name': 'encoding', 'type': 'string', 'width': 'half'},
            {'name': 'is_binary', 'type': 'boolean', 'default': False, 'width': 'half'},
            {'name': 'line_count', 'type': 'integer', 'width': 'half'}
        ],
        'specifications': [
            {'name': 'id', 'type': 'uuid', 'primary_key': True, 'required': True},
            {'name': 'repository_item_id', 'type': 'uuid', 'required': True, 'width': 'half'},
            {'name': 'spec_name', 'type': 'string', 'required': True, 'width': 'half'},
            {'name': 'spec_type', 'type': 'string', 'required': True, 'width': 'half'},
            {'name': 'priority', 'type': 'integer', 'width': 'half'},
            {'name': 'status', 'type': 'string', 'width': 'half'},
            {'name': 'content', 'type': 'text', 'width': 'full'},
            {'name': 'metadata', 'type': 'json', 'width': 'full'}
        ],
        'requirements': [
            {'name': 'id', 'type': 'uuid', 'primary_key': True, 'required': True},
            {'name': 'specification_id', 'type': 'uuid', 'required': True, 'width': 'half'},
            {'name': 'req_id', 'type': 'string', 'required': True, 'width': 'half'},
            {'name': 'title', 'type': 'string', 'required': True, 'width': 'full'},
            {'name': 'description', 'type': 'text', 'width': 'full'},
            {'name': 'status', 'type': 'string', 'width': 'half'},
            {'name': 'priority', 'type': 'integer', 'width': 'half'},
            {'name': 'tags', 'type': 'json', 'width': 'full'}
        ],
        'tasks': [
            {'name': 'id', 'type': 'uuid', 'primary_key': True, 'required': True},
            {'name': 'title', 'type': 'string', 'required': True, 'width': 'full'},
            {'name': 'description', 'type': 'text', 'width': 'full'},
            {'name': 'status', 'type': 'string', 'width': 'half'},
            {'name': 'priority', 'type': 'integer', 'width': 'half'},
            {'name': 'assignee', 'type': 'string', 'width': 'half'},
            {'name': 'due_date', 'type': 'datetime', 'width': 'half'},
            {'name': 'tags', 'type': 'json', 'width': 'full'}
        ],
        'documents': [
            {'name': 'id', 'type': 'uuid', 'primary_key': True, 'required': True},
            {'name': 'title', 'type': 'string', 'required': True, 'width': 'full'},
            {'name': 'content', 'type': 'text', 'width': 'full'},
            {'name': 'document_type', 'type': 'string', 'width': 'half'},
            {'name': 'status', 'type': 'string', 'width': 'half'},
            {'name': 'tags', 'type': 'json', 'width': 'full'}
        ],
        'code_files': [
            {'name': 'id', 'type': 'uuid', 'primary_key': True, 'required': True},
            {'name': 'file_path', 'type': 'string', 'required': True, 'width': 'full'},
            {'name': 'file_name', 'type': 'string', 'required': True, 'width': 'half'},
            {'name': 'file_type', 'type': 'string', 'width': 'half'},
            {'name': 'line_count', 'type': 'integer', 'width': 'half'},
            {'name': 'size_bytes', 'type': 'integer', 'width': 'half'},
            {'name': 'last_modified', 'type': 'datetime', 'width': 'half'},
            {'name': 'metadata', 'type': 'json', 'width': 'full'}
        ]
    }
    
    # Create each collection
    for collection_name, fields in collections.items():
        print(f"\n🔄 Creating collection: {collection_name}")
        if create_collection(token, collection_name, fields):
            print(f"✅ Collection {collection_name} created successfully")
        else:
            print(f"❌ Failed to create collection {collection_name}")
    
    print("\n🎉 Schema restoration completed!")
    print("🌐 Check your collections at: http://localhost:8055/admin")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
