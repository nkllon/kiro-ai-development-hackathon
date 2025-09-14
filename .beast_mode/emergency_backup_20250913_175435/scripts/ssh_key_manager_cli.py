#!/usr/bin/env python3
"""
SSH Key Management CLI

Command-line interface for SSH key management domain.
"""

import sys
import asyncio
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ssh_key_management import SSHKeyManager


def main():
    """Main function for SSH key management CLI"""
    import argparse

    parser = argparse.ArgumentParser(description="SSH Key Manager for OpenFlow Playground")
    parser.add_argument("--host", default="vonnegut", help="Host name to configure")
    parser.add_argument("--user", help="Username for SSH connection (defaults to current user)")
    parser.add_argument("--key-name", default="id_rsa", help="SSH key name")
    parser.add_argument("--generate-key", action="store_true", help="Generate new SSH key")
    parser.add_argument("--install-key", action="store_true", help="Install key on remote host")
    parser.add_argument("--test-connection", action="store_true", help="Test SSH connection")
    parser.add_argument("--setup-host", action="store_true", help="Complete host setup")
    parser.add_argument("--setup-vonnegut", action="store_true", help="Complete vonnegut setup (legacy)")
    parser.add_argument("--rm-status", action="store_true", help="Show RM status")

    args = parser.parse_args()

    # Initialize SSH key manager
    ssh_manager = SSHKeyManager()

    # RM status check
    if args.rm_status:

        async def show_rm_status():
            status = await ssh_manager.get_module_status()
            capabilities = await ssh_manager.get_module_capabilities()
            health = await ssh_manager.is_healthy()
            indicators = await ssh_manager.get_health_indicators()

            print("🔍 SSH Key Manager RM Status:")
            print(f"  Health: {'✅ Healthy' if health else '❌ Unhealthy'}")
            print(f"  Status: {status.status if hasattr(status, 'status') else status.get('status')}")
            print(f"  Capabilities: {len(capabilities)}")
            print(f"  Success Rate: {indicators.get('success_rate', 0):.2%}")
            print(f"  Operations: {indicators.get('operation_count', 0)}")
            print(f"  Uptime: {indicators.get('uptime', 0):.1f}s")

        asyncio.run(show_rm_status())
        return

    if args.generate_key:
        success, message = ssh_manager.generate_ssh_key(args.key_name)
        if success:
            print(f"✅ SSH key generated: {message}")
        else:
            print(f"❌ Failed to generate SSH key: {message}")
            sys.exit(1)

    if args.install_key:
        success = ssh_manager.install_key_on_host(args.host, args.user or ssh_manager.current_user, args.key_name)
        if success:
            print(f"✅ SSH key installed on {args.host}")
        else:
            print(f"❌ Failed to install SSH key on {args.host}")
            sys.exit(1)

    if args.test_connection:
        success = ssh_manager.test_connection(args.host)
        if success:
            print(f"✅ SSH connection to {args.host} successful")
        else:
            print(f"❌ SSH connection to {args.host} failed")
            sys.exit(1)

    if args.setup_host:
        success = ssh_manager.setup_host_connection(args.host, args.user, args.key_name)
        if success:
            print(f"✅ SSH setup for {args.host} completed successfully!")
        else:
            print(f"❌ SSH setup for {args.host} failed")
            sys.exit(1)

    if args.setup_vonnegut:
        # Legacy support for vonnegut
        success = ssh_manager.setup_host_connection("vonnegut", args.user or "lou", args.key_name)
        if success:
            print("✅ vonnegut SSH setup completed successfully!")
        else:
            print("❌ vonnegut SSH setup failed")
            sys.exit(1)

    # Default: complete setup for specified host
    if not any([args.generate_key, args.install_key, args.test_connection, args.setup_host, args.setup_vonnegut]):
        success = ssh_manager.setup_host_connection(args.host, args.user, args.key_name)
        if success:
            print(f"✅ SSH setup for {args.host} completed successfully!")
        else:
            print(f"❌ SSH setup for {args.host} failed")
            sys.exit(1)


if __name__ == "__main__":
    main()
