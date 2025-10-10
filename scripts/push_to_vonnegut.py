#!/usr/bin/env python3
"""
Push Observatory Code to Vonnegut
=================================

Creates a deployment package and uploads it to Vonnegut server.
"""

import os
import sys
import subprocess
import tarfile
from pathlib import Path

def create_deployment_package():
    """Create a deployment package with essential Observatory files."""
    print("📦 Creating deployment package...")
    
    # Files and directories to include
    include_patterns = [
        "src/",
        "start_observatory.py",
        "start_observatory_minimal.py", 
        "requirements.txt",
        "cloudflared-config.yml",
        ".kiro/",
        "scripts/",
        "docs/"
    ]
    
    # Create tar package
    package_path = Path("observatory_deployment.tar.gz")
    
    with tarfile.open(package_path, "w:gz") as tar:
        for pattern in include_patterns:
            path = Path(pattern)
            if path.exists():
                print(f"  Adding: {pattern}")
                tar.add(pattern, arcname=pattern)
    
    print(f"✅ Package created: {package_path} ({package_path.stat().st_size / 1024 / 1024:.1f} MB)")
    return package_path

def upload_to_vonnegut(package_path: Path):
    """Upload package to Vonnegut server."""
    vonnegut_ip = "192.168.1.119"
    ssh_user = "lou"
    remote_path = "/home/lou/observatory"
    
    print(f"📤 Uploading to {ssh_user}@{vonnegut_ip}:{remote_path}")
    
    try:
        # Create remote directory
        subprocess.run([
            "ssh", f"{ssh_user}@{vonnegut_ip}",
            f"mkdir -p {remote_path}"
        ], check=True)
        
        # Upload package
        subprocess.run([
            "scp", str(package_path),
            f"{ssh_user}@{vonnegut_ip}:{remote_path}/"
        ], check=True)
        
        # Extract on remote
        subprocess.run([
            "ssh", f"{ssh_user}@{vonnegut_ip}",
            f"cd {remote_path} && tar -xzf {package_path.name} && rm {package_path.name}"
        ], check=True)
        
        print("✅ Upload and extraction complete")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Upload failed: {e}")
        return False

def copy_tunnel_credentials():
    """Copy tunnel credentials to Vonnegut."""
    vonnegut_ip = "192.168.1.119"
    ssh_user = "lou"
    remote_path = "/home/lou/observatory"
    
    credentials_file = Path.home() / ".cloudflared" / "d1e53e43-033f-4994-8f46-c83962ae3785.json"
    
    if credentials_file.exists():
        print("🔑 Copying tunnel credentials...")
        try:
            subprocess.run([
                "scp", str(credentials_file),
                f"{ssh_user}@{vonnegut_ip}:{remote_path}/tunnel-credentials.json"
            ], check=True)
            print("✅ Credentials copied")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Credentials copy failed: {e}")
            return False
    else:
        print(f"⚠️ Credentials file not found: {credentials_file}")
        return False

def main():
    """Main push execution."""
    print("🎯 Push Observatory to Vonnegut")
    print("=" * 40)
    
    # Create package
    package_path = create_deployment_package()
    
    # Upload to Vonnegut
    if not upload_to_vonnegut(package_path):
        return False
    
    # Copy credentials
    copy_tunnel_credentials()
    
    # Cleanup local package
    package_path.unlink()
    print("🧹 Cleaned up local package")
    
    print("\n🎉 Observatory code successfully pushed to Vonnegut!")
    print("📁 Location: /home/lou/observatory/")
    print("🚀 Ready for deployment")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)