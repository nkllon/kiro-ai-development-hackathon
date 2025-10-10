#!/usr/bin/env python3
"""
Configure Directus Relationships

Sets up proper relationships between collections in Directus CMS
to make the data truly useful and interconnected.
"""

import requests
import json


class DirectusRelationshipConfigurator:
    """Configure relationships in Directus CMS."""
    
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
    
    def create_field(self, collection, field_config):
        """Create a field in a collection."""
        try:
            response = requests.post(
                f"{self.directus_url}/fields/{collection}",
                headers=self.get_headers(),
                json=field_config
            )
            
            if response.status_code in [200, 201]:
                print(f"   ✅ Created field: {field_config['field']}")
                return True
            else:
                print(f"   ⚠️  Field {field_config['field']}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error creating field {field_config['field']}: {e}")
            return False
    
    def create_relation(self, relation_config):
        """Create a relationship between collections."""
        try:
            response = requests.post(
                f"{self.directus_url}/relations",
                headers=self.get_headers(),
                json=relation_config
            )
            
            if response.status_code in [200, 201]:
                print(f"   ✅ Created relation: {relation_config['collection']} → {relation_config['related_collection']}")
                return True
            else:
                print(f"   ⚠️  Relation failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error creating relation: {e}")
            return False
    
    def setup_relationships(self):
        """Set up all the relationships between collections."""
        print("\n🔗 Setting up Directus relationships...")
        
        relationships = [
            # Tasks belong to Specifications
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
            },
            
            # Documents belong to Specifications  
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
            
            # Code Files belong to Specifications
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
            }
        ]
        
        # First, add the relationship fields if they don't exist
        fields_to_add = [
            {
                "collection": "tasks",
                "field": "specification_id",
                "type": "integer",
                "meta": {
                    "interface": "select-dropdown-m2o",
                    "display": "related-values",
                    "display_options": {
                        "template": "{{spec_name}}"
                    }
                }
            },
            {
                "collection": "documents", 
                "field": "specification_id",
                "type": "integer",
                "meta": {
                    "interface": "select-dropdown-m2o",
                    "display": "related-values",
                    "display_options": {
                        "template": "{{spec_name}}"
                    }
                }
            },
            {
                "collection": "code_files",
                "field": "specification_id", 
                "type": "integer",
                "meta": {
                    "interface": "select-dropdown-m2o",
                    "display": "related-values",
                    "display_options": {
                        "template": "{{spec_name}}"
                    }
                }
            }
        ]
        
        print("\n📝 Adding relationship fields...")
        for field_config in fields_to_add:
            self.create_field(field_config["collection"], field_config)
        
        print("\n🔗 Creating relationships...")
        for relation in relationships:
            self.create_relation(relation)
    
    def update_sample_data(self):
        """Update some sample data to demonstrate relationships."""
        print("\n📊 Updating sample data with relationships...")
        
        try:
            # Get Integration Orchestrator spec ID
            response = requests.get(
                f"{self.directus_url}/items/specifications",
                headers=self.get_headers(),
                params={"filter[spec_name][_eq]": "integration-orchestrator-framework"}
            )
            
            if response.status_code == 200:
                specs = response.json()["data"]
                if specs:
                    integration_spec_id = specs[0]["id"]
                    
                    # Link some code files to this spec
                    code_files_response = requests.get(
                        f"{self.directus_url}/items/code_files",
                        headers=self.get_headers(),
                        params={"filter[file_path][_contains]": "integration_orchestrator"}
                    )
                    
                    if code_files_response.status_code == 200:
                        code_files = code_files_response.json()["data"]
                        
                        for code_file in code_files[:5]:  # Link first 5 files
                            update_response = requests.patch(
                                f"{self.directus_url}/items/code_files/{code_file['id']}",
                                headers=self.get_headers(),
                                json={"specification_id": integration_spec_id}
                            )
                            
                            if update_response.status_code == 200:
                                print(f"   ✅ Linked {code_file['file_name']} to Integration Orchestrator spec")
            
            # Get AI Cursor Sharing spec ID
            response = requests.get(
                f"{self.directus_url}/items/specifications",
                headers=self.get_headers(),
                params={"filter[spec_name][_eq]": "ai-driven-cursor-sharing"}
            )
            
            if response.status_code == 200:
                specs = response.json()["data"]
                if specs:
                    cursor_spec_id = specs[0]["id"]
                    
                    # Link cursor sharing code files
                    code_files_response = requests.get(
                        f"{self.directus_url}/items/code_files",
                        headers=self.get_headers(),
                        params={"filter[file_path][_contains]": "cursor_sharing"}
                    )
                    
                    if code_files_response.status_code == 200:
                        code_files = code_files_response.json()["data"]
                        
                        for code_file in code_files[:5]:  # Link first 5 files
                            update_response = requests.patch(
                                f"{self.directus_url}/items/code_files/{code_file['id']}",
                                headers=self.get_headers(),
                                json={"specification_id": cursor_spec_id}
                            )
                            
                            if update_response.status_code == 200:
                                print(f"   ✅ Linked {code_file['file_name']} to AI Cursor Sharing spec")
                                
        except Exception as e:
            print(f"   ❌ Error updating sample data: {e}")
    
    def get_collections_info(self):
        """Get information about current collections."""
        try:
            response = requests.get(
                f"{self.directus_url}/collections",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                collections = response.json()["data"]
                print(f"\n📋 Current Collections ({len(collections)} total):")
                
                for collection in collections:
                    if not collection["collection"].startswith("directus_"):
                        print(f"   • {collection['collection']}")
                        
                        # Get field count
                        fields_response = requests.get(
                            f"{self.directus_url}/fields/{collection['collection']}",
                            headers=self.get_headers()
                        )
                        
                        if fields_response.status_code == 200:
                            fields = fields_response.json()["data"]
                            print(f"     Fields: {len(fields)}")
                            
                            # Show relationship fields
                            rel_fields = [f for f in fields if f.get("schema", {}).get("foreign_key_table")]
                            if rel_fields:
                                print(f"     Relationships: {len(rel_fields)}")
                                for rel_field in rel_fields:
                                    target = rel_field["schema"]["foreign_key_table"]
                                    print(f"       → {rel_field['field']} → {target}")
                            
        except Exception as e:
            print(f"Error getting collections info: {e}")
    
    def run_configuration(self):
        """Run the complete relationship configuration."""
        print("🚀 Directus Relationship Configuration")
        print("=" * 50)
        
        if not self.authenticate():
            return False
        
        # Show current state
        self.get_collections_info()
        
        # Set up relationships
        self.setup_relationships()
        
        # Update sample data
        self.update_sample_data()
        
        # Show final state
        print("\n" + "=" * 50)
        print("🎉 Relationship Configuration Complete!")
        print("\n🌐 Directus Admin Interface: http://localhost:8055")
        print("   Login: admin@example.com / d1r3ctu5")
        print("\n📋 You can now:")
        print("   • See related code files when viewing specifications")
        print("   • Navigate from specifications to their tasks")
        print("   • View documents linked to specifications")
        print("   • Create new relationships through the UI")
        
        return True


if __name__ == "__main__":
    configurator = DirectusRelationshipConfigurator()
    configurator.run_configuration()