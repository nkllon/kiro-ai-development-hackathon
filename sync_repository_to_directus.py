#!/usr/bin/env python3
"""
Repository to Directus Sync Script

Syncs current repository content to Directus for smoke testing.
This ensures the Directus web interface shows actual repository data.
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime


class DirectusSync:
    """Sync repository content to Directus."""
    
    def __init__(self):
        self.directus_url = "http://localhost:8055"
        self.admin_email = "admin@example.com"
        self.admin_password = "d1r3ctu5"
        self.token = None
        
    def authenticate(self):
        """Authenticate with Directus and get access token."""
        try:
            response = requests.post(f"{self.directus_url}/auth/login", json={
                "email": self.admin_email,
                "password": self.admin_password
            })
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["data"]["access_token"]
                print("✅ Authenticated with Directus")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def get_headers(self):
        """Get headers with authentication token."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def sync_specifications(self):
        """Sync .kiro/specs to Directus specifications table."""
        print("\n📋 Syncing specifications...")
        
        specs_dir = Path(".kiro/specs")
        synced_count = 0
        
        for spec_path in specs_dir.iterdir():
            if spec_path.is_dir():
                try:
                    # Check if requirements.md exists
                    requirements_file = spec_path / "requirements.md"
                    design_file = spec_path / "design.md"
                    tasks_file = spec_path / "tasks.md"
                    
                    spec_data = {
                        "spec_name": spec_path.name,
                        "spec_type": "requirements",
                        "status": "active",
                        "priority": 1,
                        "metadata": {
                            "has_requirements": requirements_file.exists(),
                            "has_design": design_file.exists(),
                            "has_tasks": tasks_file.exists(),
                            "synced_at": datetime.now().isoformat()
                        }
                    }
                    
                    # Add content if requirements file exists
                    if requirements_file.exists():
                        with open(requirements_file, 'r', encoding='utf-8') as f:
                            spec_data["content"] = f.read()[:10000]  # Limit content size
                    
                    # Check if spec already exists
                    existing = self.get_existing_spec(spec_path.name)
                    
                    if existing:
                        # Update existing
                        response = requests.patch(
                            f"{self.directus_url}/items/specifications/{existing['id']}",
                            headers=self.get_headers(),
                            json=spec_data
                        )
                    else:
                        # Create new
                        response = requests.post(
                            f"{self.directus_url}/items/specifications",
                            headers=self.get_headers(),
                            json=spec_data
                        )
                    
                    if response.status_code in [200, 201]:
                        synced_count += 1
                        print(f"   ✅ {spec_path.name}")
                    else:
                        print(f"   ❌ {spec_path.name}: {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ {spec_path.name}: {e}")
        
        print(f"📊 Synced {synced_count} specifications")
    
    def sync_code_files(self):
        """Sync key code files to Directus."""
        print("\n💻 Syncing code files...")
        
        code_patterns = [
            "src/**/*.py",
            "scripts/*.py",
            "*.py"
        ]
        
        synced_count = 0
        
        for pattern in code_patterns:
            for file_path in Path(".").glob(pattern):
                if file_path.is_file() and file_path.stat().st_size < 100000:  # Skip large files
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        file_data = {
                            "file_name": file_path.name,
                            "file_path": str(file_path),
                            "file_type": file_path.suffix.lstrip('.') or 'text',
                            "line_count": len(content.splitlines()),
                            "content": content[:50000],  # Limit content size
                            "metadata": {
                                "size_bytes": file_path.stat().st_size,
                                "synced_at": datetime.now().isoformat()
                            }
                        }
                        
                        # Check if file already exists
                        existing = self.get_existing_code_file(str(file_path))
                        
                        if existing:
                            # Update existing
                            response = requests.patch(
                                f"{self.directus_url}/items/code_files/{existing['id']}",
                                headers=self.get_headers(),
                                json=file_data
                            )
                        else:
                            # Create new
                            response = requests.post(
                                f"{self.directus_url}/items/code_files",
                                headers=self.get_headers(),
                                json=file_data
                            )
                        
                        if response.status_code in [200, 201]:
                            synced_count += 1
                            if synced_count <= 10:  # Only show first 10
                                print(f"   ✅ {file_path}")
                        
                    except Exception as e:
                        if synced_count <= 5:  # Only show first few errors
                            print(f"   ❌ {file_path}: {e}")
        
        print(f"📊 Synced {synced_count} code files")
    
    def sync_documents(self):
        """Sync key documents to Directus."""
        print("\n📄 Syncing documents...")
        
        doc_patterns = [
            "*.md",
            "docs/*.md",
            ".kiro/**/*.md"
        ]
        
        synced_count = 0
        
        for pattern in doc_patterns:
            for file_path in Path(".").glob(pattern):
                if file_path.is_file() and file_path.stat().st_size < 200000:  # Skip very large files
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        doc_data = {
                            "title": file_path.name,
                            "document_type": "markdown",
                            "content": content[:100000],  # Limit content size
                            "metadata": {
                                "file_path": str(file_path),
                                "size_bytes": file_path.stat().st_size,
                                "synced_at": datetime.now().isoformat()
                            }
                        }
                        
                        # Check if document already exists
                        existing = self.get_existing_document(file_path.name)
                        
                        if existing:
                            # Update existing
                            response = requests.patch(
                                f"{self.directus_url}/items/documents/{existing['id']}",
                                headers=self.get_headers(),
                                json=doc_data
                            )
                        else:
                            # Create new
                            response = requests.post(
                                f"{self.directus_url}/items/documents",
                                headers=self.get_headers(),
                                json=doc_data
                            )
                        
                        if response.status_code in [200, 201]:
                            synced_count += 1
                            if synced_count <= 10:  # Only show first 10
                                print(f"   ✅ {file_path.name}")
                        
                    except Exception as e:
                        if synced_count <= 5:  # Only show first few errors
                            print(f"   ❌ {file_path.name}: {e}")
        
        print(f"📊 Synced {synced_count} documents")
    
    def get_existing_spec(self, spec_name):
        """Check if specification already exists."""
        try:
            response = requests.get(
                f"{self.directus_url}/items/specifications",
                headers=self.get_headers(),
                params={"filter[spec_name][_eq]": spec_name}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data["data"]:
                    return data["data"][0]
            return None
            
        except Exception:
            return None
    
    def get_existing_code_file(self, file_path):
        """Check if code file already exists."""
        try:
            response = requests.get(
                f"{self.directus_url}/items/code_files",
                headers=self.get_headers(),
                params={"filter[file_path][_eq]": file_path}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data["data"]:
                    return data["data"][0]
            return None
            
        except Exception:
            return None
    
    def get_existing_document(self, title):
        """Check if document already exists."""
        try:
            response = requests.get(
                f"{self.directus_url}/items/documents",
                headers=self.get_headers(),
                params={"filter[title][_eq]": title}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data["data"]:
                    return data["data"][0]
            return None
            
        except Exception:
            return None
    
    def get_stats(self):
        """Get current Directus statistics."""
        try:
            stats = {}
            
            for collection in ["specifications", "code_files", "documents"]:
                response = requests.get(
                    f"{self.directus_url}/items/{collection}",
                    headers=self.get_headers(),
                    params={"aggregate[countDistinct]": "id"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    stats[collection] = data["data"][0]["countDistinct"]["id"]
                else:
                    stats[collection] = 0
            
            return stats
            
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}
    
    def run_sync(self):
        """Run complete sync process."""
        print("🚀 Repository to Directus Sync")
        print("=" * 50)
        
        # Check Directus health
        try:
            response = requests.get(f"{self.directus_url}/server/health")
            if response.status_code != 200:
                print("❌ Directus is not healthy")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to Directus: {e}")
            return False
        
        print("✅ Directus is healthy")
        
        # Authenticate
        if not self.authenticate():
            return False
        
        # Get initial stats
        print("\n📊 Current Directus Statistics:")
        initial_stats = self.get_stats()
        for collection, count in initial_stats.items():
            print(f"   {collection}: {count} items")
        
        # Sync content
        self.sync_specifications()
        self.sync_code_files()
        self.sync_documents()
        
        # Get final stats
        print("\n📊 Final Directus Statistics:")
        final_stats = self.get_stats()
        for collection, count in final_stats.items():
            initial = initial_stats.get(collection, 0)
            change = count - initial
            change_str = f" (+{change})" if change > 0 else ""
            print(f"   {collection}: {count} items{change_str}")
        
        print("\n✅ Sync Complete!")
        print(f"🌐 Directus Web Interface: {self.directus_url}")
        print("   Login: admin@kiro.dev / KiroAdmin2024!")
        
        return True


if __name__ == "__main__":
    sync = DirectusSync()
    sync.run_sync()