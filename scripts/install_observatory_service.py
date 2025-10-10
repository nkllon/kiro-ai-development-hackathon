#!/usr/bin/env python3
"""
Observatory Service Installer
Creates system services for Observatory to run on boot.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

class ServiceInstaller:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.system = platform.system().lower()
        
    def create_macos_service(self):
        """Create macOS LaunchAgent for Observatory."""
        # Get full paths to avoid macOS security issues
        cloudflared_path = subprocess.run(['which', 'cloudflared'], capture_output=True, text=True).stdout.strip()
        if not cloudflared_path:
            cloudflared_path = '/opt/homebrew/bin/cloudflared'
        
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.nkllon.observatory</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>{self.project_root}/scripts/observatory_launcher.sh</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>{self.project_root}</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>{self.project_root}/logs/service.out.log</string>
    
    <key>StandardErrorPath</key>
    <string>{self.project_root}/logs/service.err.log</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PYTHONPATH</key>
        <string>{self.project_root}</string>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
        <key>HOME</key>
        <string>{Path.home()}</string>
    </dict>
</dict>
</plist>'''
        
        # Create LaunchAgents directory if it doesn't exist
        launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
        launch_agents_dir.mkdir(exist_ok=True)
        
        plist_file = launch_agents_dir / "com.nkllon.observatory.plist"
        
        with open(plist_file, 'w') as f:
            f.write(plist_content)
        
        print(f"✅ Created macOS service: {plist_file}")
        
        # Load the service
        try:
            subprocess.run(['launchctl', 'load', str(plist_file)], check=True)
            print("✅ Service loaded and will start on boot")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Could not load service: {e}")
            print("You can manually load it with:")
            print(f"   launchctl load {plist_file}")
        
        return plist_file
    
    def create_linux_service(self):
        """Create systemd service for Observatory."""
        service_content = f'''[Unit]
Description=Observatory Monitoring Platform
After=network.target
Wants=network.target

[Service]
Type=forking
User={os.getenv('USER')}
WorkingDirectory={self.project_root}
Environment=PYTHONPATH={self.project_root}
ExecStart={sys.executable} {self.project_root}/scripts/start_observatory_production.py
ExecStop={sys.executable} {self.project_root}/scripts/start_observatory_production.py --stop
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target'''
        
        service_file = Path("/etc/systemd/system/observatory.service")
        
        try:
            # Write service file (requires sudo)
            subprocess.run(['sudo', 'tee', str(service_file)], 
                         input=service_content.encode(), check=True)
            
            # Reload systemd and enable service
            subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
            subprocess.run(['sudo', 'systemctl', 'enable', 'observatory'], check=True)
            
            print(f"✅ Created Linux service: {service_file}")
            print("✅ Service enabled and will start on boot")
            
            # Start the service
            subprocess.run(['sudo', 'systemctl', 'start', 'observatory'], check=True)
            print("✅ Service started")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create Linux service: {e}")
            print("You may need to run this script with sudo")
        
        return service_file
    
    def install_service(self):
        """Install Observatory as a system service."""
        print(f"🔧 Installing Observatory service for {self.system}...")
        
        # Create logs directory
        (self.project_root / "logs").mkdir(exist_ok=True)
        
        if self.system == "darwin":
            return self.create_macos_service()
        elif self.system == "linux":
            return self.create_linux_service()
        else:
            print(f"❌ Unsupported system: {self.system}")
            print("Supported systems: macOS (darwin), Linux")
            return None
    
    def uninstall_service(self):
        """Uninstall Observatory system service."""
        print(f"🗑️  Uninstalling Observatory service for {self.system}...")
        
        if self.system == "darwin":
            plist_file = Path.home() / "Library" / "LaunchAgents" / "com.nkllon.observatory.plist"
            if plist_file.exists():
                try:
                    subprocess.run(['launchctl', 'unload', str(plist_file)], check=True)
                    plist_file.unlink()
                    print("✅ macOS service uninstalled")
                except subprocess.CalledProcessError as e:
                    print(f"⚠️  Error uninstalling: {e}")
            else:
                print("No macOS service found")
                
        elif self.system == "linux":
            try:
                subprocess.run(['sudo', 'systemctl', 'stop', 'observatory'], check=True)
                subprocess.run(['sudo', 'systemctl', 'disable', 'observatory'], check=True)
                subprocess.run(['sudo', 'rm', '/etc/systemd/system/observatory.service'], check=True)
                subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
                print("✅ Linux service uninstalled")
            except subprocess.CalledProcessError as e:
                print(f"⚠️  Error uninstalling: {e}")
    
    def show_status(self):
        """Show service status."""
        if self.system == "darwin":
            try:
                result = subprocess.run(['launchctl', 'list', 'com.nkllon.observatory'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ macOS service is loaded")
                    print(result.stdout)
                else:
                    print("❌ macOS service is not loaded")
            except subprocess.CalledProcessError:
                print("❌ macOS service is not loaded")
                
        elif self.system == "linux":
            try:
                subprocess.run(['systemctl', 'status', 'observatory'], check=True)
            except subprocess.CalledProcessError:
                print("❌ Linux service is not running")

def main():
    installer = ServiceInstaller()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "--install":
            installer.install_service()
        elif command == "--uninstall":
            installer.uninstall_service()
        elif command == "--status":
            installer.show_status()
        else:
            print("Usage: python install_observatory_service.py [--install|--uninstall|--status]")
    else:
        print("Observatory Service Installer")
        print("=" * 40)
        print("Options:")
        print("  --install    Install Observatory as system service")
        print("  --uninstall  Remove Observatory system service")
        print("  --status     Show service status")
        print()
        print("After installation, Observatory will:")
        print("  • Start automatically on boot")
        print("  • Restart if it crashes")
        print("  • Run in the background")
        print("  • Be accessible at https://observatory.nkllon.com/")

if __name__ == "__main__":
    main()