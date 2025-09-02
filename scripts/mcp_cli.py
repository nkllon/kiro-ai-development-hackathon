#!/usr/bin/env python3
"""
MCP CLI - Model Context Protocol Management Tool
Manages MCP servers, configuration, and integration
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict


class MCPManager:
    """Manages MCP servers and configuration"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.mcp_config_dir = self.project_path / ".mcp"
        self.mcp_config_file = self.project_path / "mcp.json"

    def check_mcp_servers(self) -> dict[str, bool]:
        """Check which MCP servers are available"""
        servers = {
            "@modelcontextprotocol/server-filesystem": False,
            "mcp-server-code-runner": False,
            "@sentry/mcp-server": False,
            "@heroku/mcp-server": False,
            "@notionhq/notion-mcp-server": False,
        }

        for server in servers:
            try:
                result = subprocess.run([server, "--version"], capture_output=True, text=True, timeout=5)
                servers[server] = result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError):
                servers[server] = False

        return servers

    def install_mcp_servers(self) -> dict[str, bool]:
        """Install MCP servers using npm"""
        print("🔧 Installing MCP servers...")

        servers_to_install = [
            "mcp-server-filesystem",
            "mcp-server-github",
            "mcp-server-stack",
            "mcp-server-http",
            "mcp-server-json",
        ]

        results = {}

        for server in servers_to_install:
            print(f"📋 Installing {server}...")
            try:
                # Use npm install with --prefix to avoid global permission issues
                result = subprocess.run(
                    ["npm", "install", "--prefix", str(self.project_path), server],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                results[server] = result.returncode == 0

                if results[server]:
                    print(f"✅ {server} installed successfully")
                else:
                    print(f"❌ {server} installation failed: {result.stderr}")

            except subprocess.TimeoutExpired:
                print(f"⏰ {server} installation timed out")
                results[server] = False
            except Exception as e:
                print(f"❌ {server} installation error: {e}")
                results[server] = False

        return results

    def create_mcp_config(self) -> bool:
        """Create basic MCP configuration file"""
        config = {
            "mcpServers": {
                "filesystem": {
                    "command": "npx",
                    "args": ["mcp-server-filesystem"],
                    "env": {},
                },
                "github": {
                    "command": "npx",
                    "args": ["mcp-server-github"],
                    "env": {"GITHUB_TOKEN": "${GITHUB_TOKEN}"},
                },
                "stack": {"command": "npx", "args": ["mcp-server-stack"], "env": {}},
                "http": {"command": "npx", "args": ["mcp-server-http"], "env": {}},
                "json": {"command": "npx", "args": ["mcp-server-json"], "env": {}},
            }
        }

        try:
            with open(self.mcp_config_file, "w") as f:
                json.dump(config, f, indent=2)
            print(f"✅ MCP configuration created: {self.mcp_config_file}")
            return True
        except Exception as e:
            print(f"❌ Failed to create MCP config: {e}")
            return False

    def create_mcp_directory(self) -> bool:
        """Create .mcp directory for MCP-specific files"""
        try:
            self.mcp_config_dir.mkdir(exist_ok=True)
            print(f"✅ MCP directory created: {self.mcp_config_dir}")
            return True
        except Exception as e:
            print(f"❌ Failed to create MCP directory: {e}")
            return False

    def validate_mcp_setup(self) -> dict[str, any]:
        """Validate MCP setup and return status"""
        status = {
            "mcp_config_exists": self.mcp_config_file.exists(),
            "mcp_directory_exists": self.mcp_config_dir.exists(),
            "servers_available": self.check_mcp_servers(),
            "total_servers": 0,
            "available_servers": 0,
        }

        status["total_servers"] = len(status["servers_available"])
        status["available_servers"] = sum(1 for available in status["servers_available"].values() if available)

        return status

    def setup_mcp_integration(self) -> bool:
        """Complete MCP setup process"""
        print("🚀 Setting up MCP integration...")

        # Create directory
        if not self.create_mcp_directory():
            return False

        # Install servers
        install_results = self.install_mcp_servers()
        successful_installs = sum(1 for success in install_results.values() if success)

        if successful_installs == 0:
            print("⚠️ No MCP servers were installed successfully")
            return False

        # Create configuration
        if not self.create_mcp_config():
            return False

        # Validate setup
        status = self.validate_mcp_setup()

        print("\n📊 MCP Setup Summary:")
        print(f"  📁 Config file: {'✅' if status['mcp_config_exists'] else '❌'}")
        print(f"  📁 MCP directory: {'✅' if status['mcp_directory_exists'] else '❌'}")
        print(f"  🔧 Servers available: {status['available_servers']}/{status['total_servers']}")

        for server, available in status["servers_available"].items():
            status_icon = "✅" if available else "❌"
            print(f"    {status_icon} {server}")

        return status["mcp_config_exists"] and status["available_servers"] > 0


def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python mcp_cli.py [check|install|setup|validate]")
        print("  check   - Check MCP server availability")
        print("  install - Install MCP servers")
        print("  setup   - Complete MCP setup")
        print("  validate- Validate MCP configuration")
        sys.exit(1)

    command = sys.argv[1].lower()
    manager = MCPManager()

    if command == "check":
        print("🔍 Checking MCP server availability...")
        servers = manager.check_mcp_servers()

        print("\n📊 MCP Server Status:")
        for server, available in servers.items():
            status = "✅ Available" if available else "❌ Not available"
            print(f"  {server}: {status}")

    elif command == "install":
        print("📦 Installing MCP servers...")
        results = manager.install_mcp_servers()

        print("\n📊 Installation Results:")
        for server, success in results.items():
            status = "✅ Success" if success else "❌ Failed"
            print(f"  {server}: {status}")

    elif command == "setup":
        print("🚀 Running complete MCP setup...")
        success = manager.setup_mcp_integration()

        if success:
            print("\n🎉 MCP setup completed successfully!")
        else:
            print("\n❌ MCP setup failed!")
            sys.exit(1)

    elif command == "validate":
        print("🔍 Validating MCP configuration...")
        status = manager.validate_mcp_setup()

        print("\n📊 MCP Configuration Status:")
        print(f"  📁 Config file: {'✅' if status['mcp_config_exists'] else '❌'}")
        print(f"  📁 MCP directory: {'✅' if status['mcp_directory_exists'] else '❌'}")
        print(f"  🔧 Servers: {status['available_servers']}/{status['total_servers']} available")

        if status["available_servers"] == 0:
            print("\n⚠️ No MCP servers are available. Run 'install' or 'setup' first.")

    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: check, install, setup, validate")
        sys.exit(1)


if __name__ == "__main__":
    main()
