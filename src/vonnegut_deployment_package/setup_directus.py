#!/usr/bin/env python3
"""
Directus Setup Script
====================

Sets up Directus CMS with repository discovery schema and initial data.

Author: Beast Mode Framework
Date: 2025-09-18
Version: 1.0
"""

import requests
import json
import time
import sys
from pathlib import Path

# Add project root to path
sys.path.append('.')

from src.security.secure_credentials import get_directus_password, get_secure_credentials

# Get Directus configuration from environment variables
creds = get_secure_credentials()
directus_config = creds.get_directus_config()

DIRECTUS_URL = directus_config['url']
ADMIN_EMAIL = directus_config['admin_email']
ADMIN_PASSWORD = directus_config['admin_password']


def wait_for_directus():
    """Wait for Directus to be ready"""
    print("⏳ Waiting for Directus to start...")
    
    for attempt in range(30):  # Wait up to 5 minutes
        try:
            response = requests.get(f"{DIRECTUS_URL}/server/health", timeout=5)
            if response.status_code == 200:
                print("✅ Directus is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(10)
        print(f"   Attempt {attempt + 1}/30...")
    
    print("❌ Directus failed to start within timeout")
    return False


def get_auth_token():
    """Get authentication token from Directus"""
    print("🔐 Authenticating with Directus...")
    
    try:
        response = requests.post(f"{DIRECTUS_URL}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if response.status_code == 200:
            token = response.json()["data"]["access_token"]
            print("✅ Authentication successful")
            return token
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None


def create_collection(token, collection_config):
    """Create a collection in Directus"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(
            f"{DIRECTUS_URL}/collections",
            headers=headers,
            json=collection_config
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Created collection: {collection_config['collection']}")
            return True
        else:
            print(f"❌ Failed to create collection {collection_config['collection']}: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error creating collection: {e}")
        return False


def create_repository_discovery_schema(token):
    """Create the repository discovery schema in Directus"""
    print("📋 Creating repository discovery schema...")
    
    # Repository Items collection
    repository_items_config = {
        "collection": "repository_items",
        "meta": {
            "collection": "repository_items",
            "icon": "folder",
            "note": "Repository content items discovered by the content scanner",
            "display_template": "{{name}} ({{item_type}})",
            "hidden": False,
            "singleton": False,
            "translations": None,
            "archive_field": None,
            "archive_app_filter": True,
            "archive_value": None,
            "unarchive_value": None,
            "sort_field": None,
            "accountability": "all",
            "color": None,
            "item_duplication_fields": None,
            "sort": 1,
            "group": None,
            "collapse": "open"
        },
        "schema": {
            "name": "repository_items",
            "comment": "Repository content items"
        },
        "fields": [
            {
                "field": "id",
                "type": "uuid",
                "meta": {
                    "hidden": True,
                    "readonly": True,
                    "interface": "input",
                    "special": ["uuid"]
                },
                "schema": {
                    "name": "id",
                    "table": "repository_items",
                    "data_type": "uuid",
                    "default_value": "gen_random_uuid()",
                    "max_length": None,
                    "numeric_precision": None,
                    "numeric_scale": None,
                    "is_nullable": False,
                    "is_unique": True,
                    "is_primary_key": True,
                    "has_auto_increment": False,
                    "foreign_key_column": None,
                    "foreign_key_table": None,
                    "comment": ""
                }
            },
            {
                "field": "item_type",
                "type": "string",
                "meta": {
                    "interface": "select-dropdown",
                    "options": {
                        "choices": [
                            {"text": "Source Code", "value": "source_code"},
                            {"text": "Configuration", "value": "configuration"},
                            {"text": "Documentation", "value": "documentation"},
                            {"text": "Test", "value": "test"},
                            {"text": "Script", "value": "script"},
                            {"text": "Specification", "value": "specification"},
                            {"text": "Analysis", "value": "analysis"},
                            {"text": "Data", "value": "data"},
                            {"text": "Unknown", "value": "unknown"}
                        ]
                    }
                },
                "schema": {
                    "name": "item_type",
                    "table": "repository_items",
                    "data_type": "character varying",
                    "max_length": 50,
                    "is_nullable": False
                }
            },
            {
                "field": "path",
                "type": "string",
                "meta": {
                    "interface": "input",
                    "width": "full"
                },
                "schema": {
                    "name": "path",
                    "table": "repository_items",
                    "data_type": "character varying",
                    "max_length": 1000,
                    "is_nullable": False
                }
            },
            {
                "field": "name",
                "type": "string",
                "meta": {
                    "interface": "input"
                },
                "schema": {
                    "name": "name",
                    "table": "repository_items",
                    "data_type": "character varying",
                    "max_length": 255,
                    "is_nullable": False
                }
            }
        ]
    }
    
    success = create_collection(token, repository_items_config)
    return success


def main():
    """Main setup function"""
    print("🚀 Directus CMS Setup for Repository Discovery")
    print("=" * 50)
    
    # Check if Directus is running
    if not wait_for_directus():
        print("❌ Please start Directus first:")
        print("   cd deployment/local && docker-compose up directus directus-db")
        return 1
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        return 1
    
    # Create repository discovery schema
    if create_repository_discovery_schema(token):
        print("✅ Repository discovery schema created successfully!")
        print(f"🌐 Access Directus at: {DIRECTUS_URL}")
        print(f"📧 Login: {ADMIN_EMAIL}")
        print(f"🔑 Password: {ADMIN_PASSWORD}")
        return 0
    else:
        print("❌ Failed to create repository discovery schema")
        return 1


if __name__ == "__main__":
    sys.exit(main())