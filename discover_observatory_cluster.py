#!/usr/bin/env python3
"""
Discover Observatory Cluster - Find the network Redis
Helps locate and connect to the lab Redis cluster
"""

import redis
import sys
import socket

# Common Redis cluster locations to try
COMMON_LOCATIONS = [
    ('localhost', 6379),
    ('127.0.0.1', 6379),
    ('192.168.1.119', 6379),  # From vonnegut_deployment
    ('redis', 6379),           # Docker network name
    ('host.docker.internal', 6379),  # Docker host
]

COMMON_PASSWORDS = [
    'beastmode2025',  # From vonnegut_deployment
    '',               # No password
]


def test_connection(host, port, password):
    """Test Redis connection"""
    try:
        r = redis.Redis(
            host=host,
            port=port,
            password=password if password else None,
            decode_responses=True,
            socket_connect_timeout=2
        )
        result = r.ping()
        return True if result else False
    except:
        return False


def discover_cluster():
    """Try to discover the observatory cluster"""
    print("🔍 Discovering Observatory Cluster...")
    print("=" * 70)
    print()
    
    found = []
    
    # Try common locations
    for host, port in COMMON_LOCATIONS:
        # Check if host is reachable first
        try:
            socket.gethostbyname(host)
        except socket.gaierror:
            print(f"⏭️  Skipping {host}:{port} (hostname not found)")
            continue
        
        for password in COMMON_PASSWORDS:
            pwd_display = f"password: {'*' * len(password)}" if password else "no auth"
            
            if test_connection(host, port, password):
                print(f"✅ Found: {host}:{port} ({pwd_display})")
                found.append((host, port, password))
                
                # Get some info
                try:
                    r = redis.Redis(
                        host=host,
                        port=port,
                        password=password if password else None,
                        decode_responses=True
                    )
                    
                    # Check for mailboxes
                    mailboxes = r.keys('beast:mailbox:*:in')
                    if mailboxes:
                        agents = sorted([k.split(':')[2] for k in mailboxes])
                        print(f"   Agents: {', '.join(agents)}")
                    
                    dbsize = r.dbsize()
                    print(f"   Keys: {dbsize}")
                    print()
                except:
                    print()
                
                break  # Found with this password, no need to try others
            else:
                print(f"⏭️  Not found: {host}:{port} ({pwd_display})")
    
    print("=" * 70)
    
    if found:
        print(f"\n✅ Found {len(found)} Redis instance(s)")
        print()
        print("To use the observatory cluster:")
        host, port, password = found[0]
        print(f"  export LAB_REDIS_HOST={host}")
        print(f"  export LAB_REDIS_PORT={port}")
        if password:
            print(f"  export LAB_REDIS_PASSWORD={password}")
        print()
        return found
    else:
        print("\n❌ Could not find observatory cluster")
        print()
        print("Please provide:")
        print("  - Cluster IP/hostname")
        print("  - Port (if not 6379)")
        print("  - Password")
        print()
        print("Then set environment variables:")
        print("  export LAB_REDIS_HOST=<cluster_ip>")
        print("  export LAB_REDIS_PORT=6379")
        print("  export LAB_REDIS_PASSWORD=<password>")
        return []


if __name__ == '__main__':
    found = discover_cluster()
    sys.exit(0 if found else 1)



