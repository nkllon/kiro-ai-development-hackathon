#!/usr/bin/env python3
"""
DNS Cleanup Audit Tool
Helps identify and clean up old DNS records after nameserver migration.
"""

import json
import subprocess
import sys
from typing import Dict, List, Set
from dataclasses import dataclass

@dataclass
class DNSRecord:
    name: str
    type: str
    content: str
    ttl: int
    proxied: bool = False

class DNSCleanupAuditor:
    def __init__(self, domain: str):
        self.domain = domain
        self.squarespace_ips = {
            '198.185.159.144', '198.185.159.145',
            '198.49.23.144', '198.49.23.145'
        }
        self.squarespace_cnames = {
            'ext-cust.squarespace.com',
            'hosted-by-squarespace.com'
        }
    
    def get_cloudflare_records(self) -> List[DNSRecord]:
        """Get all DNS records from Cloudflare zone."""
        try:
            # This would use Cloudflare API - for now we'll simulate
            print(f"🔍 Checking DNS records for {self.domain}...")
            
            # Use dig to check current records
            result = subprocess.run(['dig', self.domain, 'ANY', '+short'], 
                                  capture_output=True, text=True)
            
            records = []
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        print(f"Found: {line}")
            
            return records
            
        except Exception as e:
            print(f"❌ Error getting DNS records: {e}")
            return []
    
    def identify_squarespace_records(self) -> Dict[str, List[str]]:
        """Identify records that are likely from Squarespace."""
        suspicious_records = {
            'squarespace_ips': [],
            'squarespace_cnames': [],
            'old_mx_records': [],
            'unnecessary_records': []
        }
        
        # Check A records pointing to Squarespace IPs
        try:
            result = subprocess.run(['dig', self.domain, 'A', '+short'], 
                                  capture_output=True, text=True)
            for ip in result.stdout.strip().split('\n'):
                if ip.strip() in self.squarespace_ips:
                    suspicious_records['squarespace_ips'].append(ip.strip())
        except:
            pass
        
        # Check CNAME records
        try:
            result = subprocess.run(['dig', f'www.{self.domain}', 'CNAME', '+short'], 
                                  capture_output=True, text=True)
            for cname in result.stdout.strip().split('\n'):
                if any(sq in cname for sq in self.squarespace_cnames):
                    suspicious_records['squarespace_cnames'].append(cname.strip())
        except:
            pass
        
        return suspicious_records
    
    def generate_cleanup_plan(self) -> Dict[str, List[str]]:
        """Generate a plan for cleaning up DNS records."""
        suspicious = self.identify_squarespace_records()
        
        cleanup_plan = {
            'safe_to_delete': [],
            'needs_replacement': [],
            'keep_but_verify': []
        }
        
        # Squarespace A records - safe to delete if we have tunnel
        if suspicious['squarespace_ips']:
            cleanup_plan['safe_to_delete'].extend([
                f"A record: {self.domain} -> {ip}" 
                for ip in suspicious['squarespace_ips']
            ])
        
        # CNAME records pointing to Squarespace
        if suspicious['squarespace_cnames']:
            cleanup_plan['needs_replacement'].extend([
                f"CNAME record: www.{self.domain} -> {cname}"
                for cname in suspicious['squarespace_cnames']
            ])
        
        return cleanup_plan
    
    def print_audit_report(self):
        """Print a comprehensive audit report."""
        print("\n" + "="*60)
        print(f"🔍 DNS CLEANUP AUDIT REPORT for {self.domain}")
        print("="*60)
        
        suspicious = self.identify_squarespace_records()
        cleanup_plan = self.generate_cleanup_plan()
        
        print("\n📋 CURRENT SITUATION:")
        if suspicious['squarespace_ips']:
            print(f"❌ Found {len(suspicious['squarespace_ips'])} Squarespace A records")
            for ip in suspicious['squarespace_ips']:
                print(f"   • {self.domain} -> {ip}")
        
        if suspicious['squarespace_cnames']:
            print(f"❌ Found {len(suspicious['squarespace_cnames'])} Squarespace CNAME records")
            for cname in suspicious['squarespace_cnames']:
                print(f"   • www.{self.domain} -> {cname}")
        
        print("\n🧹 CLEANUP RECOMMENDATIONS:")
        
        if cleanup_plan['safe_to_delete']:
            print("\n✅ SAFE TO DELETE (old Squarespace records):")
            for record in cleanup_plan['safe_to_delete']:
                print(f"   • {record}")
        
        if cleanup_plan['needs_replacement']:
            print("\n⚠️  NEEDS REPLACEMENT (update these):")
            for record in cleanup_plan['needs_replacement']:
                print(f"   • {record}")
            print("   → Replace with: CNAME www -> your-tunnel.cfargotunnel.com")
        
        print("\n🎯 WHAT YOU NEED:")
        print("1. Root domain A record: nkllon.com -> your-tunnel.cfargotunnel.com")
        print("2. WWW CNAME record: www.nkllon.com -> your-tunnel.cfargotunnel.com") 
        print("3. Observatory CNAME: observatory.nkllon.com -> your-tunnel.cfargotunnel.com")
        print("4. Delete all Squarespace A records")
        
        print("\n💡 NEXT STEPS:")
        print("1. Go to Cloudflare DNS dashboard")
        print("2. Delete the old Squarespace A records")
        print("3. Update/add the tunnel CNAME records")
        print("4. Test with: dig nkllon.com A")

def main():
    if len(sys.argv) != 2:
        print("Usage: python dns_cleanup_audit.py <domain>")
        sys.exit(1)
    
    domain = sys.argv[1]
    auditor = DNSCleanupAuditor(domain)
    auditor.print_audit_report()

if __name__ == "__main__":
    main()