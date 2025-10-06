#!/usr/bin/env python3
"""
Observatory Container Cleanup Script
===================================

Systematically shuts down and removes all Observatory-related Docker containers,
volumes, and networks. Part of Observatory Vonnegut Deployment Recovery.
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

def run_command(cmd, description, timeout=60):
    """Run a command with proper error handling and logging."""
    print(f"🔧 {description}...")
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True, result.stdout
        else:
            print(f"⚠️  {description} - Warning: {result.stderr.strip()}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        print(f"❌ {description} - Timed out after {timeout} seconds")
        return False, "Command timed out"
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False, str(e)

def get_observatory_containers():
    """Get list of Observatory-related containers."""
    print("🔍 Identifying Observatory-related containers...")
    
    # Get all containers with observatory in the name or from observatory compose project
    cmd = 'docker ps -a --format "{{.Names}}\t{{.Image}}\t{{.Status}}" | grep -E "(observatory|beast-mode)"'
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        containers = []
        
        if result.returncode == 0 and result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        containers.append({
                            'name': parts[0],
                            'image': parts[1],
                            'status': parts[2]
                        })
        
        print(f"📋 Found {len(containers)} Observatory-related containers:")
        for container in containers:
            print(f"   • {container['name']} ({container['image']}) - {container['status']}")
        
        return containers
        
    except Exception as e:
        print(f"❌ Error getting container list: {e}")
        return []

def stop_containers(containers):
    """Stop all Observatory containers gracefully."""
    print(f"\n🛑 Stopping {len(containers)} Observatory containers...")
    
    stopped_containers = []
    failed_containers = []
    
    for container in containers:
        container_name = container['name']
        
        # Try graceful stop first
        success, output = run_command(
            f"docker stop {container_name}",
            f"Stopping container {container_name}",
            timeout=30
        )
        
        if success:
            stopped_containers.append(container_name)
        else:
            # Try force kill if graceful stop fails
            print(f"⚠️  Graceful stop failed for {container_name}, trying force kill...")
            success, output = run_command(
                f"docker kill {container_name}",
                f"Force killing container {container_name}",
                timeout=10
            )
            
            if success:
                stopped_containers.append(container_name)
            else:
                failed_containers.append(container_name)
    
    print(f"✅ Successfully stopped: {len(stopped_containers)} containers")
    print(f"❌ Failed to stop: {len(failed_containers)} containers")
    
    if failed_containers:
        print("Failed containers:")
        for name in failed_containers:
            print(f"   • {name}")
    
    return stopped_containers, failed_containers

def remove_containers(containers):
    """Remove all Observatory containers."""
    print(f"\n🗑️  Removing {len(containers)} Observatory containers...")
    
    removed_containers = []
    failed_containers = []
    
    for container in containers:
        container_name = container['name']
        
        success, output = run_command(
            f"docker rm -f {container_name}",
            f"Removing container {container_name}",
            timeout=30
        )
        
        if success:
            removed_containers.append(container_name)
        else:
            failed_containers.append(container_name)
    
    print(f"✅ Successfully removed: {len(removed_containers)} containers")
    print(f"❌ Failed to remove: {len(failed_containers)} containers")
    
    return removed_containers, failed_containers

def get_observatory_volumes():
    """Get list of Observatory-related volumes."""
    print("\n🔍 Identifying Observatory-related volumes...")
    
    cmd = 'docker volume ls --format "{{.Name}}" | grep -E "observatory"'
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        volumes = []
        
        if result.returncode == 0 and result.stdout.strip():
            volumes = [vol.strip() for vol in result.stdout.strip().split('\n') if vol.strip()]
        
        print(f"📋 Found {len(volumes)} Observatory-related volumes:")
        for volume in volumes:
            print(f"   • {volume}")
        
        return volumes
        
    except Exception as e:
        print(f"❌ Error getting volume list: {e}")
        return []

def remove_volumes(volumes):
    """Remove Observatory volumes."""
    print(f"\n🗑️  Removing {len(volumes)} Observatory volumes...")
    
    removed_volumes = []
    failed_volumes = []
    
    for volume in volumes:
        success, output = run_command(
            f"docker volume rm {volume}",
            f"Removing volume {volume}",
            timeout=30
        )
        
        if success:
            removed_volumes.append(volume)
        else:
            failed_volumes.append(volume)
    
    print(f"✅ Successfully removed: {len(removed_volumes)} volumes")
    print(f"❌ Failed to remove: {len(failed_volumes)} volumes")
    
    return removed_volumes, failed_volumes

def get_observatory_networks():
    """Get list of Observatory-related networks."""
    print("\n🔍 Identifying Observatory-related networks...")
    
    cmd = 'docker network ls --format "{{.Name}}" | grep -E "observatory"'
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        networks = []
        
        if result.returncode == 0 and result.stdout.strip():
            networks = [net.strip() for net in result.stdout.strip().split('\n') if net.strip()]
        
        print(f"📋 Found {len(networks)} Observatory-related networks:")
        for network in networks:
            print(f"   • {network}")
        
        return networks
        
    except Exception as e:
        print(f"❌ Error getting network list: {e}")
        return []

def remove_networks(networks):
    """Remove Observatory networks."""
    print(f"\n🗑️  Removing {len(networks)} Observatory networks...")
    
    removed_networks = []
    failed_networks = []
    
    for network in networks:
        success, output = run_command(
            f"docker network rm {network}",
            f"Removing network {network}",
            timeout=30
        )
        
        if success:
            removed_networks.append(network)
        else:
            failed_networks.append(network)
    
    print(f"✅ Successfully removed: {len(removed_networks)} networks")
    print(f"❌ Failed to remove: {len(failed_networks)} networks")
    
    return removed_networks, failed_networks

def verify_cleanup():
    """Verify that all Observatory resources have been cleaned up."""
    print("\n🔍 Verifying cleanup completion...")
    
    # Check for remaining containers
    cmd = 'docker ps -a --format "{{.Names}}" | grep -E "(observatory|beast-mode)" | wc -l'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    remaining_containers = int(result.stdout.strip()) if result.returncode == 0 else 0
    
    # Check for remaining volumes
    cmd = 'docker volume ls --format "{{.Name}}" | grep -E "observatory" | wc -l'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    remaining_volumes = int(result.stdout.strip()) if result.returncode == 0 else 0
    
    # Check for remaining networks
    cmd = 'docker network ls --format "{{.Name}}" | grep -E "observatory" | wc -l'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    remaining_networks = int(result.stdout.strip()) if result.returncode == 0 else 0
    
    print(f"📊 Cleanup Verification:")
    print(f"   • Remaining containers: {remaining_containers}")
    print(f"   • Remaining volumes: {remaining_volumes}")
    print(f"   • Remaining networks: {remaining_networks}")
    
    cleanup_complete = (remaining_containers == 0 and remaining_volumes == 0 and remaining_networks == 0)
    
    if cleanup_complete:
        print("✅ Cleanup verification passed - all Observatory resources removed")
    else:
        print("⚠️  Cleanup verification found remaining resources")
    
    return cleanup_complete, {
        'containers': remaining_containers,
        'volumes': remaining_volumes,
        'networks': remaining_networks
    }

def generate_cleanup_report(results):
    """Generate a detailed cleanup report."""
    timestamp = datetime.now().isoformat()
    
    report = {
        "timestamp": timestamp,
        "cleanup_results": results,
        "summary": {
            "total_containers_processed": len(results.get('containers_found', [])),
            "containers_removed": len(results.get('containers_removed', [])),
            "total_volumes_processed": len(results.get('volumes_found', [])),
            "volumes_removed": len(results.get('volumes_removed', [])),
            "total_networks_processed": len(results.get('networks_found', [])),
            "networks_removed": len(results.get('networks_removed', [])),
            "cleanup_successful": results.get('cleanup_complete', False)
        }
    }
    
    report_file = Path("observatory_cleanup_report.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📋 Detailed cleanup report saved to: {report_file}")
    return report_file

def main():
    """Main cleanup execution."""
    print("🚀 Observatory Container Cleanup Script")
    print("=" * 50)
    
    results = {}
    
    # Step 1: Get all Observatory containers
    containers = get_observatory_containers()
    results['containers_found'] = [c['name'] for c in containers]
    
    if not containers:
        print("ℹ️  No Observatory containers found to clean up")
    else:
        # Step 2: Stop containers
        stopped, failed_stop = stop_containers(containers)
        results['containers_stopped'] = stopped
        results['containers_failed_stop'] = failed_stop
        
        # Step 3: Remove containers
        removed_containers, failed_remove = remove_containers(containers)
        results['containers_removed'] = removed_containers
        results['containers_failed_remove'] = failed_remove
    
    # Step 4: Get and remove volumes
    volumes = get_observatory_volumes()
    results['volumes_found'] = volumes
    
    if volumes:
        removed_volumes, failed_volumes = remove_volumes(volumes)
        results['volumes_removed'] = removed_volumes
        results['volumes_failed_remove'] = failed_volumes
    else:
        print("ℹ️  No Observatory volumes found to clean up")
        results['volumes_removed'] = []
        results['volumes_failed_remove'] = []
    
    # Step 5: Get and remove networks
    networks = get_observatory_networks()
    results['networks_found'] = networks
    
    if networks:
        removed_networks, failed_networks = remove_networks(networks)
        results['networks_removed'] = removed_networks
        results['networks_failed_remove'] = failed_networks
    else:
        print("ℹ️  No Observatory networks found to clean up")
        results['networks_removed'] = []
        results['networks_failed_remove'] = []
    
    # Step 6: Verify cleanup
    cleanup_complete, remaining = verify_cleanup()
    results['cleanup_complete'] = cleanup_complete
    results['remaining_resources'] = remaining
    
    # Step 7: Generate report
    report_file = generate_cleanup_report(results)
    
    # Final summary
    print(f"\n🎯 Observatory Container Cleanup Summary")
    print("=" * 50)
    print(f"✅ Containers processed: {len(results.get('containers_found', []))}")
    print(f"✅ Containers removed: {len(results.get('containers_removed', []))}")
    print(f"✅ Volumes processed: {len(results.get('volumes_found', []))}")
    print(f"✅ Volumes removed: {len(results.get('volumes_removed', []))}")
    print(f"✅ Networks processed: {len(results.get('networks_found', []))}")
    print(f"✅ Networks removed: {len(results.get('networks_removed', []))}")
    print(f"📋 Cleanup report: {report_file}")
    
    if cleanup_complete:
        print("\n🎉 Observatory cleanup completed successfully!")
        print("🚀 Ready for monolithic deployment")
    else:
        print("\n⚠️  Cleanup completed with some remaining resources")
        print("   Manual intervention may be required")
    
    return cleanup_complete

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Cleanup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Cleanup failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)