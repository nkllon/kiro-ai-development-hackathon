#!/usr/bin/env python3
"""
Cloudflare Tunnel Diagnostic Script

Uses the newly implemented CloudflareTunnelDiscoverer to diagnose and help restore tunnel connectivity.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.system_architecture.discovery.cloudflare_tunnel_discoverer import CloudflareTunnelDiscoverer


async def main():
    print("🔍 Cloudflare Tunnel Diagnostic Tool")
    print("=====================================")
    print()
    
    # Initialize the discoverer
    discoverer = CloudflareTunnelDiscoverer()
    
    print("📋 Expected Configuration:")
    print(f"  - Tunnel ID: {discoverer.expected_tunnel_id}")
    print(f"  - Subdomains: {', '.join(discoverer.expected_subdomains)}")
    print()
    
    # Discover current tunnel configuration
    print("🔍 Discovering tunnel configuration...")
    try:
        config = await discoverer.discover_tunnel_configuration()
        
        if config:
            print("✅ Tunnel configuration found!")
            print(f"  - Tunnel ID: {config.tunnel_id}")
            print(f"  - Status: {config.status}")
            print(f"  - Config file: {config.config_file}")
            print(f"  - Credentials: {config.credentials_file}")
            print(f"  - Ingress rules: {len(config.ingress_rules)}")
            print()
            
            # Test connectivity
            print("🌐 Testing connectivity...")
            connectivity_results = await discoverer.test_websocket_connectivity()
            
            for result in connectivity_results:
                status = "✅" if result.accessible else "❌"
                print(f"  {status} {result.endpoint}: {result.response_time_ms:.1f}ms")
                if result.error_message:
                    print(f"      Error: {result.error_message}")
            
            print()
            
            # Get health status
            health = discoverer.get_health_status()
            print(f"🏥 Health Status: {health.status.value}")
            print(f"   Health Score: {health.health_score:.1f}")
            if health.issues:
                print("   Issues:")
                for issue in health.issues:
                    print(f"     - {issue}")
            
        else:
            print("❌ No tunnel configuration found!")
            print()
            print("🔧 Suggested actions:")
            print("  1. Check if cloudflared is installed: cloudflared --version")
            print("  2. Check if tunnel config exists: ls -la cloudflare-tunnel-config-websocket.yml")
            print("  3. Check tunnel status: cloudflared tunnel list")
            print("  4. Start tunnel: cloudflared tunnel run d1e53e43-033f-4994-8f46-c83962ae3785")
            
    except Exception as e:
        print(f"❌ Error during discovery: {e}")
        print()
        print("🔧 Basic troubleshooting:")
        print("  1. Check if cloudflared is running: ps aux | grep cloudflared")
        print("  2. Check tunnel logs: cloudflared tunnel logs")
        print("  3. Restart tunnel service")


if __name__ == "__main__":
    asyncio.run(main())