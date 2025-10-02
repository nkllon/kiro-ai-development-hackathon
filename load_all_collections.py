#!/usr/bin/env python3
"""
Load Data into All Directus Collections
"""

import sys
import requests
import hashlib
from pathlib import Path

# Add project root to path
sys.path.append('.')

from src.security.secure_credentials import get_directus_password

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

def get_file_content(file_path, max_size=10000):
    """Get file content safely"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(max_size)  # Limit size
            return content
    except Exception:
        return ""

def get_file_hash(file_path):
    """Get content hash for duplicate detection"""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            return hashlib.sha256(content).hexdigest()
    except Exception:
        return None

def load_documents(token, files):
    """Load documents into documents collection"""
    print("📄 Loading documents...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    loaded = 0
    for file_path in files:
        if not file_path.endswith('.md'):
            continue
            
        path_obj = Path(file_path)
        if not path_obj.exists():
            continue
        
        # Check if already exists
        response = requests.get(f"{DIRECTUS_URL}/items/documents?filter[title][_eq]={path_obj.name}", headers=headers)
        if response.status_code == 200 and response.json()['data']:
            print(f"   ⏭️ Skipping {path_obj.name} (already exists)")
            continue
        
        # Get content
        content = get_file_content(file_path)
        
        # Create document
        doc = {
            'title': path_obj.name,
            'content': content,
            'document_type': 'markdown',
            'status': 'active',
            'tags': ['repository', 'markdown']
        }
        
        response = requests.post(f"{DIRECTUS_URL}/items/documents", json=doc, headers=headers)
        if response.status_code == 200:
            print(f"   ✅ Loaded document: {path_obj.name}")
            loaded += 1
        else:
            print(f"   ❌ Failed to load {path_obj.name}: {response.text}")
    
    print(f"📄 Documents loaded: {loaded}")
    return loaded

def load_code_files(token, files):
    """Load code files into code_files collection"""
    print("💻 Loading code files...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    loaded = 0
    for file_path in files:
        if not file_path.endswith('.py'):
            continue
            
        path_obj = Path(file_path)
        if not path_obj.exists():
            continue
        
        # Check if already exists
        response = requests.get(f"{DIRECTUS_URL}/items/code_files?filter[file_name][_eq]={path_obj.name}", headers=headers)
        if response.status_code == 200 and response.json()['data']:
            print(f"   ⏭️ Skipping {path_obj.name} (already exists)")
            continue
        
        # Get file stats
        stat = path_obj.stat()
        
        # Count lines
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f)
        except Exception:
            line_count = 0
        
        # Create code file
        code_file = {
            'file_path': file_path,
            'file_name': path_obj.name,
            'file_type': 'python',
            'line_count': line_count,
            'size_bytes': stat.st_size,
            'metadata': {
                'extension': path_obj.suffix,
                'discovered_at': '2025-09-20T08:00:00Z'
            }
        }
        
        response = requests.post(f"{DIRECTUS_URL}/items/code_files", json=code_file, headers=headers)
        if response.status_code == 200:
            print(f"   ✅ Loaded code file: {path_obj.name} ({line_count} lines)")
            loaded += 1
        else:
            print(f"   ❌ Failed to load {path_obj.name}: {response.text}")
    
    print(f"💻 Code files loaded: {loaded}")
    return loaded

def load_specifications(token, files):
    """Load specifications into specifications collection"""
    print("📋 Loading specifications...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    loaded = 0
    for file_path in files:
        if 'spec' not in file_path.lower() or not file_path.endswith('.md'):
            continue
            
        path_obj = Path(file_path)
        if not path_obj.exists():
            continue
        
        # Check if already exists
        response = requests.get(f"{DIRECTUS_URL}/items/specifications?filter[spec_name][_eq]={path_obj.stem}", headers=headers)
        if response.status_code == 200 and response.json()['data']:
            print(f"   ⏭️ Skipping {path_obj.name} (already exists)")
            continue
        
        # Get content
        content = get_file_content(file_path)
        
        # Create specification
        spec = {
            'spec_name': path_obj.stem,
            'spec_type': 'requirements',
            'priority': 1,
            'status': 'active',
            'content': content,
            'metadata': {
                'file_path': file_path,
                'discovered_at': '2025-09-20T08:00:00Z'
            }
        }
        
        response = requests.post(f"{DIRECTUS_URL}/items/specifications", json=spec, headers=headers)
        if response.status_code == 200:
            print(f"   ✅ Loaded specification: {path_obj.name}")
            loaded += 1
        else:
            print(f"   ❌ Failed to load {path_obj.name}: {response.text}")
    
    print(f"📋 Specifications loaded: {loaded}")
    return loaded

def load_tasks(token):
    """Load some sample tasks"""
    print("📝 Loading sample tasks...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    sample_tasks = [
        {
            'title': 'Repository Discovery Setup',
            'description': 'Set up repository discovery system and load data into Directus',
            'status': 'completed',
            'priority': 1,
            'assignee': 'admin',
            'tags': ['setup', 'discovery', 'directus']
        },
        {
            'title': 'Data Loading Test',
            'description': 'Test loading repository data into Directus collections',
            'status': 'in_progress',
            'priority': 2,
            'assignee': 'admin',
            'tags': ['testing', 'data', 'directus']
        },
        {
            'title': 'Collection Population',
            'description': 'Populate all Directus collections with repository data',
            'status': 'pending',
            'priority': 3,
            'assignee': 'admin',
            'tags': ['data', 'populate', 'collections']
        }
    ]
    
    loaded = 0
    for task in sample_tasks:
        # Check if already exists
        response = requests.get(f"{DIRECTUS_URL}/items/tasks?filter[title][_eq]={task['title']}", headers=headers)
        if response.status_code == 200 and response.json()['data']:
            print(f"   ⏭️ Skipping {task['title']} (already exists)")
            continue
        
        response = requests.post(f"{DIRECTUS_URL}/items/tasks", json=task, headers=headers)
        if response.status_code == 200:
            print(f"   ✅ Loaded task: {task['title']}")
            loaded += 1
        else:
            print(f"   ❌ Failed to load {task['title']}: {response.text}")
    
    print(f"📝 Tasks loaded: {loaded}")
    return loaded

def main():
    """Main loading function"""
    print("🚀 Loading Data into All Directus Collections")
    print("=" * 50)
    
    # Get auth token
    token = get_auth_token()
    if not token:
        return 1
    
    # Get some test files
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
    
    # Load into all collections
    total_loaded = 0
    
    # Load documents
    docs_loaded = load_documents(token, existing_files)
    total_loaded += docs_loaded
    
    # Load code files
    code_loaded = load_code_files(token, existing_files)
    total_loaded += code_loaded
    
    # Load specifications
    specs_loaded = load_specifications(token, existing_files)
    total_loaded += specs_loaded
    
    # Load tasks
    tasks_loaded = load_tasks(token)
    total_loaded += tasks_loaded
    
    print(f"\n🎉 Loading complete!")
    print(f"📊 Total items loaded: {total_loaded}")
    print(f"   - Documents: {docs_loaded}")
    print(f"   - Code files: {code_loaded}")
    print(f"   - Specifications: {specs_loaded}")
    print(f"   - Tasks: {tasks_loaded}")
    print(f"\n🌐 Check in Directus: http://localhost:8055/admin")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
