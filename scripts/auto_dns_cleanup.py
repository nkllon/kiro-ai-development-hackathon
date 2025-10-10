#!/usr/bin/env python3
"""
Automatic DNS Cleanup Script
Automatically removes old Squarespace DNS records and sets up tunnel records.
"""

import os
import sys
import json
import requests
from typing import List, Dict, Optional

class CloudflareDNSManager:
    def __init__(self, api_token: str, zone_id: str, domain: str, tunnel_id: str):
        self.api_token = api_token
        self.zone_id = zone_id
        self.domain = domain
        self.tunnel_hostname = f"{tunnel_id}.cfargotunnel.com"
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
        # Squarespace IPs to delete
        self.squarespace_ips = {
            '198.185.159.144', '198.185.159.145',
            '198.49.23.144', '198.49.23.145'
        }
    
    def get_dns_records(self) -> List[Dict]:
        """Get all DNS records for the zone."""
        url = f"{self.base_url}/zones/{self.zone_id}/dns_records"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            print(f"❌ Error getting DNS records: {response.text}")
            return []
        
        return response.json()['result']
    
    def delete_record(self, record_id: str, record_name: str, record_content: str) -> bool:
        """Delete a DNS record."""
        url = f"{self.base_url}/zones/{self.zone_id}/dns_records/{record_id}"
        response = requests.delete(url, headers=self.headers)
        
        if response.status_code == 200:
            print(f"✅ Deleted: {record_name} -> {record_content}")
            return True
        else:
            print(f"❌ Failed to delete {record_name} -> {record_content}: {response.text}")
            return False
    
    def create_record(self, record_type: str, name: str, content: str, proxied: bool = True) -> bool:
        """Create a DNS record."""
        url = f"{self.base_url}/zones/{self.zone_id}/dns_records"
        data = {
            "type": record_type,
            "name": name,
            "content": content,
            "proxied": proxied
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        
        if response.status_code == 200:
            print(f"✅ Created: {name} ({record_type}) -> {content}")
            return True
        else:
            print(f"❌ Failed to create {name} -> {content}: {response.text}")
            return False
    
    def update_record(self, record_id: str, record_type: str, name: str, content: str, proxied: bool = True) -> bool:
        """Update a DNS record."""
        url = f"{self.base_url}/zones/{self.zone_id}/dns_records/{record_id}"
        data = {
            "type": record_type,
            "name": name,
            "content": content,
            "proxied": proxied
        }
        
        response = requests.put(url, headers=self.headers, json=data)
        
        if response.status_code == 200:
            print(f"✅ Updated: {name} ({record_type}) -> {content}")
            return True
        else:
            print(f"❌ Failed to update {name} -> {content}: {response.text}")
            return False
    
    def cleanup_dns(self):
        """Main cleanup function."""
        print("🔍 Getting current DNS records...")
        records = self.get_dns_records()
        
        if not records:
            print("❌ Could not retrieve DNS records. Check your API token and zone ID.")
            return False
        
        print(f"📋 Found {len(records)} DNS records")
        
        # Track what we need to do
        records_to_delete = []
        records_to_update = []
        records_to_create = []
        
        # Analyze existing records
        has_root_a = False
        has_www_cname = False
        has_observatory_cname = False
        
        for record in records:
            record_name = record['name']
            record_type = record['type']
            record_content = record['content']
            record_id = record['id']
            
            # Check for Squarespace A records to delete
            if (record_type == 'A' and 
                record_name == self.domain and 
                record_content in self.squarespace_ips):
                records_to_delete.append((record_id, record_name, record_content))
            
            # Check for Squarespace CNAME records to update
            elif (record_type == 'CNAME' and 
                  record_name == f'www.{self.domain}' and 
                  'squarespace' in record_content.lower()):
                records_to_update.append((record_id, 'CNAME', 'www', self.tunnel_hostname))
                has_www_cname = True
            
            # Check existing tunnel records
            elif record_type == 'A' and record_name == self.domain:
                if record_content != self.tunnel_hostname:
                    records_to_update.append((record_id, 'A', self.domain, self.tunnel_hostname))
                has_root_a = True
            
            elif record_type == 'CNAME' and record_name == f'www.{self.domain}':
                if record_content != self.tunnel_hostname:
                    records_to_update.append((record_id, 'CNAME', 'www', self.tunnel_hostname))
                has_www_cname = True
            
            elif record_type == 'CNAME' and record_name == f'observatory.{self.domain}':
                if record_content != self.tunnel_hostname:
                    records_to_update.append((record_id, 'CNAME', 'observatory', self.tunnel_hostname))
                has_observatory_cname = True
        
        # Determine what records to create
        if not has_root_a:
            records_to_create.append(('A', self.domain, self.tunnel_hostname))
        
        if not has_www_cname:
            records_to_create.append(('CNAME', 'www', self.tunnel_hostname))
        
        if not has_observatory_cname:
            records_to_create.append(('CNAME', 'observatory', self.tunnel_hostname))
        
        # Execute the cleanup plan
        print("\n🧹 CLEANUP PLAN:")
        print(f"  • Delete {len(records_to_delete)} old Squarespace records")
        print(f"  • Update {len(records_to_update)} existing records")
        print(f"  • Create {len(records_to_create)} new records")
        
        if not records_to_delete and not records_to_update and not records_to_create:
            print("✅ DNS is already configured correctly!")
            return True
        
        print("\n🚀 Executing cleanup...")
        
        # Delete old records
        for record_id, name, content in records_to_delete:
            self.delete_record(record_id, name, content)
        
        # Update existing records
        for record_id, record_type, name, content in records_to_update:
            self.update_record(record_id, record_type, name, content)
        
        # Create new records
        for record_type, name, content in records_to_create:
            self.create_record(record_type, name, content)
        
        print("\n✅ DNS cleanup completed!")
        print("\n⏳ Wait 2-3 minutes for DNS propagation, then test:")
        print(f"   • https://{self.domain}")
        print(f"   • https://www.{self.domain}")
        print(f"   • https://observatory.{self.domain}")
        
        return True

def get_zone_id(api_token: str, domain: str) -> Optional[str]:
    """Get the zone ID for a domain."""
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    url = f"https://api.cloudflare.com/client/v4/zones?name={domain}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        zones = response.json()['result']
        if zones:
            return zones[0]['id']
    
    return None

def main():
    # Configuration
    domain = "nkllon.com"
    tunnel_id = "e567ba2b-df21-47d3-9275-7b8b197f18fc"
    
    # Get API token from environment or prompt
    api_token = os.getenv('CLOUDFLARE_API_TOKEN')
    
    if not api_token:
        print("🔑 Cloudflare API Token Required")
        print("=" * 40)
        print("1. Go to https://dash.cloudflare.com/profile/api-tokens")
        print("2. Click 'Create Token'")
        print("3. Use 'Edit zone DNS' template")
        print("4. Select your zone: nkllon.com")
        print("5. Copy the token")
        print()
        api_token = input("Enter your Cloudflare API token: ").strip()
        
        if not api_token:
            print("❌ API token is required")
            sys.exit(1)
    
    # Get zone ID
    print("🔍 Looking up zone ID...")
    zone_id = get_zone_id(api_token, domain)
    
    if not zone_id:
        print(f"❌ Could not find zone for {domain}. Check your API token permissions.")
        sys.exit(1)
    
    print(f"✅ Found zone ID: {zone_id}")
    
    # Create DNS manager and run cleanup
    dns_manager = CloudflareDNSManager(api_token, zone_id, domain, tunnel_id)
    success = dns_manager.cleanup_dns()
    
    if success:
        print("\n🎉 DNS cleanup completed successfully!")
        print("\nNext steps:")
        print("1. Start your tunnel: cloudflared tunnel run e567ba2b-df21-47d3-9275-7b8b197f18fc")
        print("2. Test your sites in a few minutes")
    else:
        print("\n❌ DNS cleanup failed. Check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()