#!/usr/bin/env python3
"""
Populate Directus Relationships with Real Data

Links specifications to their actual code files, documents, and tasks
based on the repository structure and content.
"""

import os
import requests
import json
from pathlib import Path


class DirectusRelationshipPopulator:
    """Populate relationships in Directus with real repository data."""
    
    def __init__(self):
        self.directus_url = "http://localhost:8055"
        self.admin_email = "admin@example.com"
        self.admin_password = "d1r3ctu5"
        self.token = None
        
    def authenticate(self):
        """Authenticate with Directus."""
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
    
    def get_all_specifications(self):
        """Get all specifications from Directus."""
        try:
            response = requests.get(
                f"{self.directus_url}/items/specifications",
                headers=self.get_headers(),
                params={"limit": -1}  # Get all items
            )
            
            if response.status_code == 200:
                return response.json()["data"]
            else:
                print(f"Failed to get specifications: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error getting specifications: {e}")
            return []
    
    def get_all_code_files(self):
        """Get all code files from Directus."""
        try:
            response = requests.get(
                f"{self.directus_url}/items/code_files",
                headers=self.get_headers(),
                params={"limit": -1}  # Get all items
            )
            
            if response.status_code == 200:
                return response.json()["data"]
            else:
                print(f"Failed to get code files: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error getting code files: {e}")
            return []
    
    def get_all_documents(self):
        """Get all documents from Directus."""
        try:
            response = requests.get(
                f"{self.directus_url}/items/documents",
                headers=self.get_headers(),
                params={"limit": -1}  # Get all items
            )
            
            if response.status_code == 200:
                return response.json()["data"]
            else:
                print(f"Failed to get documents: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error getting documents: {e}")
            return []
    
    def link_code_files_to_specs(self):
        """Link code files to their corresponding specifications."""
        print("\n💻 Linking code files to specifications...")
        
        specifications = self.get_all_specifications()
        code_files = self.get_all_code_files()
        
        linked_count = 0
        
        for spec in specifications:
            spec_name = spec["spec_name"]
            spec_id = spec["id"]
            
            # Find code files that belong to this spec
            matching_files = []
            
            # Strategy 1: Direct path matching
            for code_file in code_files:
                file_path = code_file.get("file_path", "")
                
                # Check if file path contains spec name or related keywords
                if (spec_name in file_path or 
                    spec_name.replace("-", "_") in file_path or
                    spec_name.replace("_", "-") in file_path):
                    matching_files.append(code_file)
                
                # Special cases for our recent work
                elif "integration_orchestrator" in file_path and "integration-orchestrator" in spec_name:
                    matching_files.append(code_file)
                elif "cursor_sharing" in file_path and "cursor-sharing" in spec_name:
                    matching_files.append(code_file)
                elif "gpt5" in file_path and "gpt5" in spec_name:
                    matching_files.append(code_file)
            
            # Link the matching files
            for code_file in matching_files:
                try:
                    response = requests.patch(
                        f"{self.directus_url}/items/code_files/{code_file['id']}",
                        headers=self.get_headers(),
                        json={"specification_id": spec_id}
                    )
                    
                    if response.status_code == 200:
                        linked_count += 1
                        if linked_count <= 10:  # Show first 10
                            print(f"   ✅ {code_file['file_name']} → {spec_name}")
                    
                except Exception as e:
                    print(f"   ❌ Error linking {code_file['file_name']}: {e}")
        
        print(f"📊 Linked {linked_count} code files to specifications")
    
    def link_documents_to_specs(self):
        """Link documents to their corresponding specifications."""
        print("\n📄 Linking documents to specifications...")
        
        specifications = self.get_all_specifications()
        documents = self.get_all_documents()
        
        linked_count = 0
        
        for spec in specifications:
            spec_name = spec["spec_name"]
            spec_id = spec["id"]
            
            # Find documents that belong to this spec
            matching_docs = []
            
            for document in documents:
                doc_title = document.get("title", "")
                doc_metadata = document.get("metadata", {})
                doc_file_path = doc_metadata.get("file_path", "") if isinstance(doc_metadata, dict) else ""
                
                # Check if document is related to this spec
                if (spec_name in doc_title or 
                    spec_name in doc_file_path or
                    spec_name.replace("-", "_") in doc_file_path or
                    spec_name.replace("_", "-") in doc_file_path):
                    matching_docs.append(document)
                
                # Special matching for spec files themselves
                elif (doc_title in ["requirements.md", "design.md", "tasks.md"] and 
                      spec_name in doc_file_path):
                    matching_docs.append(document)
            
            # Link the matching documents
            for document in matching_docs:
                try:
                    response = requests.patch(
                        f"{self.directus_url}/items/documents/{document['id']}",
                        headers=self.get_headers(),
                        json={"specification_id": spec_id}
                    )
                    
                    if response.status_code == 200:
                        linked_count += 1
                        if linked_count <= 10:  # Show first 10
                            print(f"   ✅ {document['title']} → {spec_name}")
                    
                except Exception as e:
                    print(f"   ❌ Error linking {document['title']}: {e}")
        
        print(f"📊 Linked {linked_count} documents to specifications")
    
    def create_tasks_from_specs(self):
        """Create tasks based on the tasks.md files in specifications."""
        print("\n📋 Creating tasks from specification task files...")
        
        specifications = self.get_all_specifications()
        created_count = 0
        
        for spec in specifications:
            spec_name = spec["spec_name"]
            spec_id = spec["id"]
            
            # Check if this spec has a tasks.md file
            tasks_file = Path(f".kiro/specs/{spec_name}/tasks.md")
            
            if tasks_file.exists():
                try:
                    with open(tasks_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Parse tasks from the markdown content
                    tasks = self.parse_tasks_from_markdown(content)
                    
                    # Create tasks in Directus
                    for task_data in tasks[:5]:  # Limit to first 5 tasks per spec
                        task_payload = {
                            "title": task_data["title"],
                            "description": task_data.get("description", ""),
                            "status": "not_started",
                            "priority": task_data.get("priority", 3),
                            "specification_id": spec_id,
                            "tags": [spec_name]
                        }
                        
                        response = requests.post(
                            f"{self.directus_url}/items/tasks",
                            headers=self.get_headers(),
                            json=task_payload
                        )
                        
                        if response.status_code in [200, 201]:
                            created_count += 1
                            if created_count <= 10:  # Show first 10
                                print(f"   ✅ Created task: {task_data['title'][:50]}... → {spec_name}")
                
                except Exception as e:
                    print(f"   ❌ Error processing tasks for {spec_name}: {e}")
        
        print(f"📊 Created {created_count} tasks from specifications")
    
    def parse_tasks_from_markdown(self, content):
        """Parse tasks from markdown content."""
        tasks = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Look for task items (- [ ] or - [x])
            if line.startswith('- [ ]') or line.startswith('- [x]'):
                # Extract task title
                task_text = line[5:].strip()  # Remove '- [ ] '
                
                # Split on first period or colon to get title
                if '.' in task_text:
                    title = task_text.split('.', 1)[0].strip()
                    description = task_text.split('.', 1)[1].strip() if '.' in task_text else ""
                elif ':' in task_text:
                    title = task_text.split(':', 1)[0].strip()
                    description = task_text.split(':', 1)[1].strip() if ':' in task_text else ""
                else:
                    title = task_text[:100]  # Limit title length
                    description = task_text
                
                tasks.append({
                    "title": title,
                    "description": description,
                    "priority": 3
                })
        
        return tasks
    
    def verify_relationships(self):
        """Verify that relationships are working."""
        print("\n🔍 Verifying relationships...")
        
        try:
            # Get a few specifications with their related items
            response = requests.get(
                f"{self.directus_url}/items/specifications",
                headers=self.get_headers(),
                params={
                    "limit": 5,
                    "fields": "id,spec_name,code_files.id,documents.id,tasks.id"
                }
            )
            
            if response.status_code == 200:
                specs = response.json()["data"]
                
                total_code_files = 0
                total_documents = 0
                total_tasks = 0
                
                for spec in specs:
                    code_count = len(spec.get("code_files", []))
                    doc_count = len(spec.get("documents", []))
                    task_count = len(spec.get("tasks", []))
                    
                    total_code_files += code_count
                    total_documents += doc_count
                    total_tasks += task_count
                    
                    if code_count > 0 or doc_count > 0 or task_count > 0:
                        print(f"   📋 {spec['spec_name'][:40]}...")
                        print(f"      Code: {code_count}, Docs: {doc_count}, Tasks: {task_count}")
                
                print(f"\n📊 Total relationships found:")
                print(f"   Code files linked: {total_code_files}")
                print(f"   Documents linked: {total_documents}")
                print(f"   Tasks linked: {total_tasks}")
                
                if total_code_files > 0 or total_documents > 0 or total_tasks > 0:
                    print("✅ Relationships are working and populated!")
                else:
                    print("⚠️  No relationships found - may need more specific linking logic")
            
        except Exception as e:
            print(f"Error verifying relationships: {e}")
    
    def run_population(self):
        """Run the complete relationship population process."""
        print("🚀 Directus Relationship Population")
        print("=" * 50)
        
        if not self.authenticate():
            return False
        
        # Link existing data
        self.link_code_files_to_specs()
        self.link_documents_to_specs()
        self.create_tasks_from_specs()
        
        # Verify results
        self.verify_relationships()
        
        print("\n" + "=" * 50)
        print("🎉 Relationship Population Complete!")
        print("\n🌐 Directus Admin Interface: http://localhost:8055")
        print("   Login: admin@example.com / d1r3ctu5")
        print("\n📋 You should now see:")
        print("   • Specifications with related code files")
        print("   • Documents linked to their specifications")
        print("   • Tasks created from specification task files")
        print("   • Proper navigation between related items")
        
        return True


if __name__ == "__main__":
    populator = DirectusRelationshipPopulator()
    populator.run_population()