#!/usr/bin/env python3
"""
Beast Mode Dashboard Launcher

Choose your monitoring experience:
1. Resource Monitor - Track tokens, money, network, resources
2. Multi-Modal Dashboard - Whiskey/War Room/Pager modes  
3. Integrated Monitor - Resource tracking + system integration
4. War Room Server - Full web dashboard with collaboration
"""

import asyncio
import sys
import subprocess
from pathlib import Path


class DashboardLauncher:
    """Launch different Beast Mode monitoring interfaces"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
    
    async def show_menu(self):
        """Show the dashboard selection menu"""
        print("💰 ═══════════════════════════════════════════════════════════")
        print("   BEAST MODE DASHBOARD LAUNCHER")
        print("   \"Choose your monitoring experience\"")
        print("═══════════════════════════════════════════════════════════")
        print()
        print("Available Dashboards:")
        print()
        print("1. 💰 Resource Monitor")
        print("   Track tokens, costs, network, CPU, memory, GPU")
        print("   Perfect for: Watching the money burn in real-time")
        print()
        print("2. 🎯 Multi-Modal Dashboard") 
        print("   Whiskey Mode (chill) / War Room (tactical) / Pager (alerts)")
        print("   Perfect for: Different monitoring contexts")
        print()
        print("3. 🔗 Integrated Monitor")
        print("   Resource tracking + automatic system integration")
        print("   Perfect for: Hands-off monitoring during development")
        print()
        print("4. ⚔️  War Room Server")
        print("   Full web dashboard with real-time collaboration")
        print("   Perfect for: Team coordination and incident response")
        print()
        print("5. 🚀 All Systems (Resource + War Room)")
        print("   Run resource monitor + web dashboard simultaneously")
        print("   Perfect for: Maximum visibility")
        print()
        
        choice = input("Enter your choice (1-5): ").strip()
        await self.launch_dashboard(choice)
    
    async def launch_dashboard(self, choice: str):
        """Launch the selected dashboard"""
        try:
            if choice == "1":
                await self._launch_resource_monitor()
            elif choice == "2":
                await self._launch_multi_modal()
            elif choice == "3":
                await self._launch_integrated_monitor()
            elif choice == "4":
                await self._launch_war_room_server()
            elif choice == "5":
                await self._launch_all_systems()
            else:
                print("❌ Invalid choice. Please select 1-5.")
                await self.show_menu()
        except KeyboardInterrupt:
            print("\n👋 Dashboard launcher ended")
    
    async def _launch_resource_monitor(self):
        """Launch the resource monitor"""
        print("🚀 Launching Resource Monitor...")
        print("💰 This will track tokens, costs, network, and system resources")
        print("Press Ctrl+C to stop")
        print("─" * 60)
        
        # Import and run the resource monitor
        from beast_mode_resource_monitor import main as resource_main
        await resource_main()
    
    async def _launch_multi_modal(self):
        """Launch the multi-modal dashboard"""
        print("🚀 Launching Multi-Modal Dashboard...")
        
        # Import and run the multi-modal dashboard
        from multi_modal_dashboard import main as modal_main
        await modal_main()
    
    async def _launch_integrated_monitor(self):
        """Launch the integrated monitor"""
        print("🚀 Launching Integrated Monitor...")
        print("🔗 This combines resource tracking with system integration")
        print("Press Ctrl+C to stop")
        print("─" * 60)
        
        # Import and run the integrated monitor
        from monitor_integration import main as integration_main
        await integration_main()
    
    async def _launch_war_room_server(self):
        """Launch the war room server"""
        print("🚀 Launching War Room Server...")
        print("⚔️  Starting web dashboard at http://localhost:8080")
        print("Press Ctrl+C to stop")
        print("─" * 60)
        
        try:
            # Import and run the war room server
            sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
            from beast_mode.monitoring.war_room_server import WarRoomServer
            
            server = WarRoomServer()
            await server.start_server()
        except ImportError as e:
            print(f"❌ Could not import war room server: {e}")
            print("Make sure FastAPI and uvicorn are installed:")
            print("pip install fastapi uvicorn websockets")
    
    async def _launch_all_systems(self):
        """Launch resource monitor + war room server simultaneously"""
        print("🚀 Launching All Systems...")
        print("💰 Resource Monitor + ⚔️  War Room Server")
        print("🌐 Web dashboard: http://localhost:8080")
        print("Press Ctrl+C to stop all systems")
        print("─" * 60)
        
        try:
            # Start both systems concurrently
            resource_task = asyncio.create_task(self._run_resource_monitor())
            war_room_task = asyncio.create_task(self._run_war_room_server())
            
            await asyncio.gather(resource_task, war_room_task)
        except Exception as e:
            print(f"❌ Error running all systems: {e}")
    
    async def _run_resource_monitor(self):
        """Run resource monitor as a task"""
        from beast_mode_resource_monitor import BeastModeResourceMonitor
        
        monitor = BeastModeResourceMonitor()
        
        # Add some demo data
        monitor.log_token_usage("openai", "gpt-4", 1500, 800, "demo_1")
        monitor.log_token_usage("anthropic", "claude-3", 2000, 1200, "demo_2")
        monitor.log_api_call()
        monitor.log_api_call()
        
        await monitor.start_monitoring()
    
    async def _run_war_room_server(self):
        """Run war room server as a task"""
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
            from beast_mode.monitoring.war_room_server import WarRoomServer
            
            server = WarRoomServer()
            await server.start_server()
        except ImportError:
            print("⚠️  War Room Server not available (missing dependencies)")
            # Keep running so resource monitor continues
            while True:
                await asyncio.sleep(60)


async def main():
    """Main entry point"""
    launcher = DashboardLauncher()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        choice = sys.argv[1]
        await launcher.launch_dashboard(choice)
    else:
        await launcher.show_menu()


if __name__ == "__main__":
    asyncio.run(main())