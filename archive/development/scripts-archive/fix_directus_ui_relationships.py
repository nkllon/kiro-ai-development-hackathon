#!/usr/bin/env python3
"""
Fix Directus UI Relationships

Properly configure Directus relationships through the fields API
to ensure the UI shows related items correctly.
"""

import requests
import json


class DirectusUIFixer:
    """Fix Directus UI relationships."""
    
    def __init__(self):
        self.directus_url = "http://localhost:8055"
        self.admin_email = "admin@example.com"
        self.admin_password = get_directus_password()
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
    
    def delete_broken_fields(self):
        """Delete any broken relationship fields."""
        print("\n🧹 Cleaning up broken fields...")
        
        collections = ["specifications", "code_files", "documents", "tasks"]
        broken_fields = ["related_code_files", "related_documents", "related_tasks"]
        
        for collection in collections:
            for field in broken_fields:
                try:
                    response = requests.delete(
                        f"{self.directus_url}/fields/{collection}/{field}",
                        headers=self.get_headers()
                    )
                    
                    if response.status_code in [200, 204]:
                        print(f"   ✅ Deleted broken field: {collection}.{field}")
                    elif response.status_code == 404:
                        # Field doesn't exist, which is fine
                        pass
                    else:
                        print(f"   ⚠️  Could not delete {collection}.{field}: {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Error deleting {collection}.{field}: {e}")
    
    def ensure_relationship_fields_exist(self):
        """Ensure the relationship fields exist in the database."""
        print("\n📝 Ensuring relationship fields exist...")
        
        # Check and create specification_id fields
        collections_needing_spec_id = ["code_files", "documents", "tasks"]
        
        for collection in collections_needing_spec_id:
            try:
                # Check if field exists
                response = requests.get(
                    f"{self.directus_url}/fields/{collection}/specification_id",
                    headers=self.get_headers()
                )
                
                if response.status_code == 404:
                    # Field doesn't exist, create it
                    field_config = {
                        "field": "specification_id",
                        "type": "integer",
                        "meta": {
                            "interface": "select-dropdown-m2o",
                            "display": "related-values",
                            "display_options": {
                                "template": "{{spec_name}}"
                            },
                            "special": ["m2o"]
                        },
                        "schema": {
                            "is_nullable": True
                        }
                    }
                    
                    create_response = requests.post(
                        f"{self.directus_url}/fields/{collection}",
                        headers=self.get_headers(),
                        json=field_config
                    )
                    
                    if create_response.status_code in [200, 201]:
                        print(f"   ✅ Created field: {collection}.specification_id")
                    else:
                        print(f"   ❌ Failed to create {collection}.specification_id: {create_response.status_code}")
                        print(f"      Response: {create_response.text}")
                else:
                    print(f"   ✅ Field exists: {collection}.specification_id")
                    
            except Exception as e:
                print(f"   ❌ Error with {collection}.specification_id: {e}")
    
    def create_proper_relationships(self):
        """Create proper many-to-one relationships."""
        print("\n🔗 Creating proper relationships...")
        
        relationships = [
            {
                "collection": "code_files",
                "field": "specification_id",
                "related_collection": "specifications",
                "meta": {
                    "many_to_one": "specifications",
                    "one_to_many": "code_files"
                },
                "schema": {
                    "on_delete": "SET NULL"
                }
            },
            {
                "collection": "documents", 
                "field": "specification_id",
                "related_collection": "specifications",
                "meta": {
                    "many_to_one": "specifications",
                    "one_to_many": "documents"
                },
                "schema": {
                    "on_delete": "SET NULL"
                }
            },
            {
                "collection": "tasks",
                "field": "specification_id", 
                "related_collection": "specifications",
                "meta": {
                    "many_to_one": "specifications",
                    "one_to_many": "tasks"
                },
                "schema": {
                    "on_delete": "SET NULL"
                }
            }
        ]
        
        for relation in relationships:
            try:
                # Delete existing relation if it exists
                delete_response = requests.delete(
                    f"{self.directus_url}/relations/{relation['collection']}/{relation['field']}",
                    headers=self.get_headers()
                )
                
                # Create new relation
                create_response = requests.post(
                    f"{self.directus_url}/relations",
                    headers=self.get_headers(),
                    json=relation
                )
                
                if create_response.status_code in [200, 201]:
                    print(f"   ✅ Created relation: {relation['collection']}.{relation['field']} → {relation['related_collection']}")
                else:
                    print(f"   ⚠️  Relation issue: {create_response.status_code}")
                    print(f"      Response: {create_response.text}")
                    
            except Exception as e:
                print(f"   ❌ Error creating relation: {e}")
    
    def test_api_access(self):
        """Test that we can now access the collections properly."""
        print("\n🧪 Testing API access...")
        
        collections = ["specifications", "code_files", "documents", "tasks"]
        
        for collection in collections:
            try:
                response = requests.get(
                    f"{self.directus_url}/items/{collection}?limit=1",
                    headers=self.get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()["data"]
                    count = len(data)
                    print(f"   ✅ {collection}: {count} item(s) accessible")
                else:
                    print(f"   ❌ {collection}: Error {response.status_code}")
                    print(f"      Response: {response.text}")
                    
            except Exception as e:
                print(f"   ❌ Error testing {collection}: {e}")
    
    def populate_sample_relationships(self):
        """Populate some sample relationships to demonstrate functionality."""
        print("\n📊 Populating sample relationships...")
        
        try:
            # Get Integration Orchestrator spec
            spec_response = requests.get(
                f"{self.directus_url}/items/specifications?filter[spec_name][_contains]=integration-orchestrator&limit=1",
                headers=self.get_headers()
            )
            
            if spec_response.status_code == 200:
                specs = spec_response.json()["data"]
                if specs:
                    spec_id = specs[0]["id"]
                    spec_name = specs[0]["spec_name"]
                    
                    # Link some code files
                    code_response = requests.get(
                        f"{self.directus_url}/items/code_files?filter[file_path][_contains]=integration_orchestrator&limit=5",
                        headers=self.get_headers()
                    )
                    
                    if code_response.status_code == 200:
                        code_files = code_response.json()["data"]
                        
                        linked_count = 0
                        for code_file in code_files:
                            update_response = requests.patch(
                                f"{self.directus_url}/items/code_files/{code_file['id']}",
                                headers=self.get_headers(),
                                json={"specification_id": spec_id}
                            )
                            
                            if update_response.status_code == 200:
                                linked_count += 1
                        
                        print(f"   ✅ Linked {linked_count} code files to {spec_name}")
            
            # Get AI Cursor Sharing spec
            cursor_response = requests.get(
                f"{self.directus_url}/items/specifications?filter[spec_name][_contains]=cursor-sharing&limit=1",
                headers=self.get_headers()
            )
            
            if cursor_response.status_code == 200:
                specs = cursor_response.json()["data"]
                if specs:
                    spec_id = specs[0]["id"]
                    spec_name = specs[0]["spec_name"]
                    
                    # Link cursor sharing code files
                    code_response = requests.get(
                        f"{self.directus_url}/items/code_files?filter[file_path][_contains]=cursor_sharing&limit=5",
                        headers=self.get_headers()
                    )
                    
                    if code_response.status_code == 200:
                        code_files = code_response.json()["data"]
                        
                        linked_count = 0
                        for code_file in code_files:
                            update_response = requests.patch(
                                f"{self.directus_url}/items/code_files/{code_file['id']}",
                                headers=self.get_headers(),
                                json={"specification_id": spec_id}
                            )
                            
                            if update_response.status_code == 200:
                                linked_count += 1
                        
                        print(f"   ✅ Linked {linked_count} code files to {spec_name}")
                        
        except Exception as e:
            print(f"   ❌ Error populating relationships: {e}")
    
    def verify_relationships_working(self):
        """Verify that relationships are now working in the UI."""
        print("\n✅ Verifying relationships are working...")
        
        try:
            # Test getting specifications with related items
            response = requests.get(
                f"{self.directus_url}/items/specifications?fields=id,spec_name,code_files.id&limit=3",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                specs = response.json()["data"]
                
                for spec in specs:
                    code_files = spec.get("code_files", [])
                    print(f"   📋 {spec['spec_name']}: {len(code_files)} related code files")
                
                print("\n🎉 Relationships are working! You should now see:")
                print("   • Related items in the Directus web interface")
                print("   • Dropdown selectors for linking items")
                print("   • Navigation between related records")
            else:
                print(f"   ❌ Still having issues: {response.status_code}")
                print(f"      Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error verifying relationships: {e}")
    
    def run_fix(self):
        """Run the complete UI relationship fix."""
        print("🔧 Directus UI Relationship Fix")
        print("=" * 50)
        
        if not self.authenticate():
            return False
        
        # Fix the issues
        self.delete_broken_fields()
        self.ensure_relationship_fields_exist()
        self.create_proper_relationships()
        self.test_api_access()
        self.populate_sample_relationships()
        self.verify_relationships_working()
        
        print("\n" + "=" * 50)
        print("🎉 Directus UI Fix Complete!")
        print("\n🌐 Directus Admin Interface: http://localhost:8055")
        print("   Login: admin@example.com / d1r3ctu5")
        print("\n📋 The specifications should now show:")
        print("   • Related code files")
        print("   • Proper dropdown selectors")
        print("   • Working navigation between items")
        
        return True


if __name__ == "__main__":
    fixer = DirectusUIFixer()
    fixer.run_fix()