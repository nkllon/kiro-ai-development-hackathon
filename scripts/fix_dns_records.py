#!/usr/bin/env python3
"""
DNS Records Fix Script
Provides step-by-step instructions to clean up DNS after nameserver migration.
"""

import subprocess
import sys

class DNSFixer:
    def __init__(self, domain: str, tunnel_id: str):
        self.domain = domain
        self.tunnel_id = tunnel_id
        self.tunnel_hostname = f"{tunnel_id}.cfargotunnel.com"
    
    def check_current_dns(self):
        """Check current DNS configuration."""
        print("🔍 CURRENT DNS STATUS:")
        print("-" * 40)
        
        # Check A records
        try:
            result = subprocess.run(['dig', self.domain, 'A', '+short'], 
                                  capture_output=True, text=True)
            ips = [ip.strip() for ip in result.stdout.strip().split('\n') if ip.strip()]
            if ips:
                print(f"A records for {self.domain}:")
                for ip in ips:
                    if ip in ['198.185.159.144', '198.185.159.145', '198.49.23.144', '198.49.23.145']:
                        print(f"  ❌ {ip} (Squarespace - DELETE THIS)")
                    else:
                        print(f"  ✅ {ip}")
            else:
                print(f"No A records found for {self.domain}")
        except Exception as e:
            print(f"Error checking A records: {e}")
        
        # Check CNAME records
        subdomains = ['www', 'observatory']
        for subdomain in subdomains:
            try:
                result = subprocess.run(['dig', f'{subdomain}.{self.domain}', 'CNAME', '+short'], 
                                      capture_output=True, text=True)
                cnames = [c.strip() for c in result.stdout.strip().split('\n') if c.strip()]
                if cnames:
                    print(f"CNAME records for {subdomain}.{self.domain}:")
                    for cname in cnames:
                        if 'squarespace' in cname.lower():
                            print(f"  ❌ {cname} (Squarespace - REPLACE THIS)")
                        elif 'cfargotunnel.com' in cname:
                            print(f"  ✅ {cname} (Tunnel - GOOD)")
                        else:
                            print(f"  ⚠️  {cname} (Unknown)")
                else:
                    print(f"No CNAME records found for {subdomain}.{self.domain}")
            except Exception as e:
                print(f"Error checking CNAME for {subdomain}: {e}")
    
    def print_cleanup_instructions(self):
        """Print step-by-step cleanup instructions."""
        print("\n" + "="*60)
        print("🧹 DNS CLEANUP INSTRUCTIONS")
        print("="*60)
        
        print("\n1. 🌐 GO TO CLOUDFLARE DASHBOARD:")
        print("   https://dash.cloudflare.com/")
        print(f"   → Select your domain: {self.domain}")
        print("   → Go to DNS > Records")
        
        print("\n2. ❌ DELETE THESE OLD SQUARESPACE RECORDS:")
        print("   Look for A records pointing to:")
        print("   • 198.185.159.144")
        print("   • 198.185.159.145") 
        print("   • 198.49.23.144")
        print("   • 198.49.23.145")
        print("   → Click the trash icon next to each one")
        
        print("\n3. ➕ ADD/UPDATE THESE TUNNEL RECORDS:")
        print(f"   A record: {self.domain}")
        print(f"   → Name: {self.domain}")
        print("   → Type: A")
        print(f"   → Content: {self.tunnel_hostname}")
        print("   → Proxy status: Proxied (orange cloud)")
        print()
        print(f"   CNAME record: www.{self.domain}")
        print("   → Name: www")
        print("   → Type: CNAME")
        print(f"   → Content: {self.tunnel_hostname}")
        print("   → Proxy status: Proxied (orange cloud)")
        print()
        print(f"   CNAME record: observatory.{self.domain}")
        print("   → Name: observatory")
        print("   → Type: CNAME")
        print(f"   → Content: {self.tunnel_hostname}")
        print("   → Proxy status: Proxied (orange cloud)")
        
        print("\n4. ✅ VERIFY THE CHANGES:")
        print("   Wait 2-3 minutes, then run:")
        print(f"   dig {self.domain} A")
        print(f"   dig www.{self.domain} CNAME")
        print(f"   dig observatory.{self.domain} CNAME")
        
        print("\n5. 🚀 START YOUR TUNNEL:")
        print("   Run this command to start the tunnel:")
        print(f"   cloudflared tunnel run {self.tunnel_id}")
        
        print("\n💡 WHY THIS HAPPENED:")
        print("When you transferred nameservers from Squarespace to Cloudflare,")
        print("Cloudflare imported ALL existing DNS records to avoid breaking")
        print("your site. This is normal behavior - you just need to clean up")
        print("the old records and point everything to your tunnel.")
    
    def create_verification_script(self):
        """Create a script to verify DNS changes."""
        script_content = f'''#!/bin/bash
echo "🔍 Verifying DNS changes for {self.domain}..."
echo

echo "A record for {self.domain}:"
dig {self.domain} A +short

echo
echo "CNAME for www.{self.domain}:"
dig www.{self.domain} CNAME +short

echo
echo "CNAME for observatory.{self.domain}:"
dig observatory.{self.domain} CNAME +short

echo
echo "✅ If you see {self.tunnel_hostname} in the results above,"
echo "   your DNS is configured correctly!"
'''
        
        with open('scripts/verify_dns.sh', 'w') as f:
            f.write(script_content)
        
        subprocess.run(['chmod', '+x', 'scripts/verify_dns.sh'])
        print(f"\n📝 Created verification script: scripts/verify_dns.sh")
        print("   Run it after making DNS changes to verify everything works.")

def main():
    domain = "nkllon.com"
    tunnel_id = "e567ba2b-df21-47d3-9275-7b8b197f18fc"
    
    fixer = DNSFixer(domain, tunnel_id)
    fixer.check_current_dns()
    fixer.print_cleanup_instructions()
    fixer.create_verification_script()

if __name__ == "__main__":
    main()