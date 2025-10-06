#!/usr/bin/env python3
"""
Fix All Directus Collections with Proper File Path References
"""

import sys
import requests
import hashlib
from pathlib import Path

# Add project root to path
sys.path.append('.')

DIRECTUS_URL = "http://localhost:8055"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = get_directus_password()

def get_auth_token():
    """Get authentication token from Directus"""
    print("🔐 Authenticating with Directus...")
    
    response = requests.post(f"{DIRECTUS_URL}/auth/login", json={
        'email': ADMIN_EMAIL,
        'password': ADMIN_PASSWORD
    })
    
    if response.status_code == 200:
        token = response.json()['data']['access_token']
        print("✅ Authentication successful")
        return token
    else:
        print(f"❌ Authentication failed: {response.text}")
        return None

def get_file_content(file_path, max_size=50000):
    """Get file content safely"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(max_size)  # Limit size
            return content
    except Exception:
        return ""

def clear_empty_interfaces(token):
    """Clear the empty interfaces"""
    print("🧹 Clearing empty interfaces...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Get all interfaces
    response = requests.get(f"{DIRECTUS_URL}/items/interfaces", headers=headers)
    if response.status_code == 200:
        interfaces = response.json()['data']
        for interface in interfaces:
            if not interface.get('name') or interface.get('name') == 'NO_NAME':
                # Delete empty interface
                delete_response = requests.delete(f"{DIRECTUS_URL}/items/interfaces/{interface['id']}", headers=headers)
                if delete_response.status_code == 204:
                    print(f"   🗑️ Deleted empty interface ID {interface['id']}")
    
    print("✅ Empty interfaces cleared")

def update_documents_with_paths(token, files):
    """Update documents with proper file paths"""
    print("📄 Updating documents with file paths...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    updated = 0
    for file_path in files:
        if not file_path.endswith('.md'):
            continue
            
        path_obj = Path(file_path)
        if not path_obj.exists():
            continue
        
        # Find existing document
        response = requests.get(f"{DIRECTUS_URL}/items/documents?filter[title][_eq]={path_obj.name}", headers=headers)
        if response.status_code == 200 and response.json()['data']:
            doc = response.json()['data'][0]
            
            # Update with file path
            update_data = {
                'metadata': {
                    'file_path': file_path,
                    'absolute_path': str(path_obj.absolute()),
                    'discovered_at': '2025-09-20T08:00:00Z'
                }
            }
            
            update_response = requests.patch(f"{DIRECTUS_URL}/items/documents/{doc['id']}", json=update_data, headers=headers)
            if update_response.status_code == 200:
                print(f"   ✅ Updated document: {path_obj.name} -> {file_path}")
                updated += 1
    
    print(f"📄 Documents updated: {updated}")
    return updated

def update_code_files_with_paths(token, files):
    """Update code files with proper file paths"""
    print("💻 Updating code files with file paths...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    updated = 0
    for file_path in files:
        if not file_path.endswith('.py'):
            continue
            
        path_obj = Path(file_path)
        if not path_obj.exists():
            continue
        
        # Find existing code file
        response = requests.get(f"{DIRECTUS_URL}/items/code_files?filter[file_name][_eq]={path_obj.name}", headers=headers)
        if response.status_code == 200 and response.json()['data']:
            code_file = response.json()['data'][0]
            
            # Update with file path
            update_data = {
                'file_path': file_path,
                'metadata': {
                    'absolute_path': str(path_obj.absolute()),
                    'relative_path': file_path,
                    'discovered_at': '2025-09-20T08:00:00Z',
                    'extension': path_obj.suffix
                }
            }
            
            update_response = requests.patch(f"{DIRECTUS_URL}/items/code_files/{code_file['id']}", json=update_data, headers=headers)
            if update_response.status_code == 200:
                print(f"   ✅ Updated code file: {path_obj.name} -> {file_path}")
                updated += 1
    
    print(f"💻 Code files updated: {updated}")
    return updated

def create_proper_interfaces(token, files):
    """Create proper interfaces from Python files"""
    print("🔌 Creating proper interfaces...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    created = 0
    for file_path in files:
        if not file_path.endswith('.py'):
            continue
            
        path_obj = Path(file_path)
        if not path_obj.exists():
            continue
        
        # Extract class names from Python files
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find class definitions
            import re
            class_matches = re.findall(r'class\s+(\w+)(?:\([^)]*\))?:', content)
            
            for class_name in class_matches:
                # Check if interface already exists
                response = requests.get(f"{DIRECTUS_URL}/items/interfaces?filter[name][_eq]={class_name}", headers=headers)
                if response.status_code == 200 and response.json()['data']:
                    continue  # Already exists
                
                # Create interface
                interface_data = {
                    'name': class_name,
                    'interface_type': 'class',
                    'module_path': file_path.replace('/', '.').replace('.py', ''),
                    'file_path': file_path,
                    'line_number': content.find(f'class {class_name}') + 1,
                    'version': '1.0.0',
                    'status': 'active',
                    'description': f'Interface {class_name} from {path_obj.name}',
                    'docstring': f'Interface {class_name} extracted from {file_path}',
                    'rdi_compliant': True,
                    'health_score': 1.0,
                    'metadata': {
                        'absolute_path': str(path_obj.absolute()),
                        'discovered_at': '2025-09-20T08:00:00Z',
                        'source_file': path_obj.name
                    }
                }
                
                response = requests.post(f"{DIRECTUS_URL}/items/interfaces", json=interface_data, headers=headers)
                if response.status_code == 200:
                    print(f"   ✅ Created interface: {class_name} from {path_obj.name}")
                    created += 1
                else:
                    print(f"   ❌ Failed to create {class_name}: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Error processing {file_path}: {e}")
    
    print(f"🔌 Interfaces created: {created}")
    return created

def main():
    """Main fixing function"""
    print("🔧 Fixing All Directus Collections")
    print("=" * 50)
    
    # Get auth token
    token = get_auth_token()
    if not token:
        return 1
    
    # Get test files
    test_files = [
        'README.md',
        'Makefile',
        'requirements.txt',
        '.kiro/specs/reflective-module-architecture-consolidation/requirements.md',
        'src/beast_mode/core/reflective_module.py',
        'src/beast_mode/core/exceptions.py',
        'src/rm_ddd/core/unified_reflective_module.py',
        'tests/beast_mode/test_unit.py'
    ]
    
    # Filter existing files
    existing_files = [f for f in test_files if Path(f).exists()]
    print(f"📁 Found {len(existing_files)} files to process")
    
    # Clear empty interfaces
    clear_empty_interfaces(token)
    
    # Update documents with paths
    docs_updated = update_documents_with_paths(token, existing_files)
    
    # Update code files with paths
    code_updated = update_code_files_with_paths(token, existing_files)
    
    # Create proper interfaces
    interfaces_created = create_proper_interfaces(token, existing_files)
    
    print(f"\n🎉 Fixing complete!")
    print(f"📊 Summary:")
    print(f"   - Documents updated: {docs_updated}")
    print(f"   - Code files updated: {code_updated}")
    print(f"   - Interfaces created: {interfaces_created}")
    print(f"\n🌐 Check in Directus: http://localhost:8055/admin")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
