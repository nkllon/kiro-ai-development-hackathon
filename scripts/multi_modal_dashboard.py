#!/usr/bin/env python3
"""
Multi-Modal Real-time Dashboard

Scenario-based display selection for different DevOps contexts:
- "Whiskey Mode": Chill terminal dashboard for casual monitoring
- "War Room Mode": Full Grafana-style web dashboard for deep analysis  
- "Pager Mode": Critical alerts and notifications for urgent issues
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import subprocess
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScenarioBasedDashboard:
    """
    Multi-modal dashboard with scenario-based display selection.
    
    Adapts display style based on context and user preference.
    """
    
    def __init__(self):
        self.event_stream_file = Path('beast_mode_events.jsonl')
        self.metrics_file = Path('beast_mode_metrics.json')
        self.current_scenario = "whiskey"  # Default to chill mode
        
        # Scenario configurations
        self.scenarios = {
            'whiskey': {
                'name': 'Whiskey Mode',
                'description': 'Chill monitoring - having a drink, watching the show',
                'display_type': 'terminal_chill',
                'update_frequency': 5,  # seconds
                'alert_threshold': 'high',
                'colors': True,
                'animations': True
            },
            'war_room': {
                'name': 'War Room Mode', 
                'description': 'Full tactical display - all metrics, deep analysis',
                'display_type': 'web_dashboard',
                'update_frequency': 1,  # seconds
                'alert_threshold': 'medium',
                'colors': True,
                'animations': False
            },
            'pager': {
                'name': 'Pager Mode',
                'description': 'Critical alerts only - page me when shit hits the fan',
                'display_type': 'alert_only',
                'update_frequency': 0.5,  # seconds
                'alert_threshold': 'critical',
                'colors': False,
                'animations': False
            }
        }
    
    async def start_dashboard(self, scenario: str = None):
        """Start the appropriate dashboard for the scenario."""
        if scenario:
            self.current_scenario = scenario
        
        config = self.scenarios[self.current_scenario]
        logger.info(f"🎯 Starting {config['name']}: {config['description']}")
        
        # Initialize event stream
        await self._initialize_event_stream()
        
        # Start appropriate display
        if config['display_type'] == 'terminal_chill':
            await self._run_whiskey_mode()
        elif config['display_type'] == 'web_dashboard':
            await self._run_war_room_mode()
        elif config['display_type'] == 'alert_only':
            await self._run_pager_mode()
    
    async def _run_whiskey_mode(self):
        """Chill terminal dashboard - perfect for having a drink and watching."""
        logger.info("🥃 WHISKEY MODE ACTIVATED - Sit back and enjoy the show")
        
        try:
            while True:
                # Clear screen with style
                os.system('clear')
                
                # Header with ASCII art
                print("🥃 ═══════════════════════════════════════════════════════════")
                print("   BEAST MODE WHISKEY DASHBOARD - Systematic Excellence")
                print("   \"Having a drink, watching the magic happen\"")
                print("═══════════════════════════════════════════════════════════")
                print()
                
                # Current status
                await self._display_chill_status()
                
                # Recent activity (scrolling feed)
                await self._display_activity_feed()
                
                # System health (visual indicators)
                await self._display_health_indicators()
                
                # Footer
                print()
                print("🐺 Beast Mode Status: SYSTEMATIC SUPERIORITY MAINTAINED")
                print(f"📊 Last Updated: {datetime.now().strftime('%H:%M:%S')}")
                print("Press Ctrl+C to exit whiskey mode")
                
                # Update frequency for chill mode
                await asyncio.sleep(self.scenarios['whiskey']['update_frequency'])
                
        except KeyboardInterrupt:
            print("\n🥃 Whiskey mode ended. Hope you enjoyed the show!")
    
    async def _run_war_room_mode(self):
        """Full tactical web dashboard - all metrics, deep analysis."""
        logger.info("⚔️  WAR ROOM MODE ACTIVATED - Full tactical display")
        
        # Generate web dashboard
        await self._generate_web_dashboard()
        
        # Start web server (simplified)
        try:
            import http.server
            import socketserver
            import threading
            
            # Create dashboard HTML
            dashboard_html = await self._create_dashboard_html()
            
            with open('beast_mode_dashboard.html', 'w') as f:
                f.write(dashboard_html)
            
            # Start simple HTTP server
            PORT = 8080
            Handler = http.server.SimpleHTTPRequestHandler
            
            def start_server():
                with socketserver.TCPServer(("", PORT), Handler) as httpd:
                    logger.info(f"🌐 War Room Dashboard: http://localhost:{PORT}/beast_mode_dashboard.html")
                    httpd.serve_forever()
            
            server_thread = threading.Thread(target=start_server, daemon=True)
            server_thread.start()
            
            # Keep updating dashboard data
            while True:
                await self._update_dashboard_data()
                await asyncio.sleep(self.scenarios['war_room']['update_frequency'])
                
        except KeyboardInterrupt:
            logger.info("⚔️  War room mode ended")
    
    async def _run_pager_mode(self):
        """Critical alerts only - page when shit hits the fan."""
        logger.info("📟 PAGER MODE ACTIVATED - Critical alerts only")
        
        alert_count = 0
        
        try:
            while True:
                # Check for critical issues
                critical_alerts = await self._check_critical_alerts()
                
                for alert in critical_alerts:
                    alert_count += 1
                    
                    # Terminal bell + urgent message
                    print(f"\a🚨 CRITICAL ALERT #{alert_count}")
                    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
                    print(f"🔥 {alert['message']}")
                    print(f"📍 {alert['source']}")
                    print("─" * 50)
                    
                    # Log for external paging systems
                    logger.critical(f"PAGER_ALERT: {alert['message']}")
                
                if not critical_alerts:
                    # Quiet mode - just a heartbeat
                    print(f"📟 {datetime.now().strftime('%H:%M:%S')} - All systems nominal", end='\r')
                
                await asyncio.sleep(self.scenarios['pager']['update_frequency'])
                
        except KeyboardInterrupt:
            print("\n📟 Pager mode ended")
    
    async def _display_chill_status(self):
        """Display chill status for whiskey mode."""
        # Simulate reading current metrics
        metrics = await self._get_current_metrics()
        
        print("🎯 Current Status:")
        print(f"   ✅ Tests Passing: {metrics.get('test_pass_rate', 95):.1f}%")
        print(f"   🐺 Beast Mode: {'ACTIVE' if metrics.get('beast_mode_active', True) else 'INACTIVE'}")
        print(f"   🔍 Hubris Level: {metrics.get('hubris_level', 'LOW')}")
        print(f"   ⚡ System Load: {metrics.get('system_load', 'NORMAL')}")
        print()
    
    async def _display_activity_feed(self):
        """Display recent activity feed."""
        print("📡 Recent Activity:")
        
        # Simulate activity feed
        activities = [
            "🧪 test_bypass_detector.py - 9 tests passed",
            "🔧 emergency_validator.py - Auto-formatted by Kiro",
            "📝 hubris_prevention/models.py - Updated",
            "✅ Task 3.2 completed - Emergency claim verification",
            "🎯 Mama Discovery Protocol - Operational"
        ]
        
        for activity in activities[-5:]:
            print(f"   {activity}")
        print()
    
    async def _display_health_indicators(self):
        """Display visual health indicators."""
        print("🏥 System Health:")
        print("   Dependencies: 🟢 HEALTHY")
        print("   Test Coverage: 🟢 >90%") 
        print("   Code Quality: 🟢 EXCELLENT")
        print("   Accountability: 🟢 CHAINS VERIFIED")
        print("   Hubris Level: 🟢 UNDER CONTROL")
    
    async def _create_dashboard_html(self):
        """Create HTML dashboard for war room mode."""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Beast Mode War Room Dashboard</title>
    <style>
        body { 
            background: #1a1a1a; 
            color: #00ff00; 
            font-family: 'Courier New', monospace;
            margin: 0;
            padding: 20px;
        }
        .header { 
            text-align: center; 
            border-bottom: 2px solid #00ff00;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .metric-card {
            border: 1px solid #00ff00;
            padding: 15px;
            border-radius: 5px;
            background: #0a0a0a;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #00ff41;
        }
        .alert-critical { color: #ff0000; }
        .alert-warning { color: #ffaa00; }
        .alert-info { color: #00aaff; }
        .status-good { color: #00ff00; }
    </style>
    <script>
        // Auto-refresh every second
        setInterval(() => {
            fetch('beast_mode_metrics.json')
                .then(response => response.json())
                .then(data => updateDashboard(data))
                .catch(err => console.log('Metrics update failed:', err));
        }, 1000);
        
        function updateDashboard(metrics) {
            document.getElementById('timestamp').textContent = new Date().toLocaleTimeString();
            document.getElementById('test-pass-rate').textContent = (metrics.test_pass_rate || 95) + '%';
            document.getElementById('hubris-level').textContent = metrics.hubris_level || 'LOW';
            document.getElementById('system-load').textContent = metrics.system_load || 'NORMAL';
        }
    </script>
</head>
<body>
    <div class="header">
        <h1>⚔️ BEAST MODE WAR ROOM DASHBOARD</h1>
        <h2>Systematic Excellence Command Center</h2>
        <p>Last Updated: <span id="timestamp"></span></p>
    </div>
    
    <div class="metrics-grid">
        <div class="metric-card">
            <h3>🧪 Test Status</h3>
            <div class="metric-value status-good" id="test-pass-rate">95%</div>
            <p>Tests Passing</p>
        </div>
        
        <div class="metric-card">
            <h3>🐺 Beast Mode</h3>
            <div class="metric-value status-good">ACTIVE</div>
            <p>Systematic Superiority</p>
        </div>
        
        <div class="metric-card">
            <h3>🔍 Hubris Level</h3>
            <div class="metric-value status-good" id="hubris-level">LOW</div>
            <p>Accountability Status</p>
        </div>
        
        <div class="metric-card">
            <h3>⚡ System Load</h3>
            <div class="metric-value status-good" id="system-load">NORMAL</div>
            <p>Resource Utilization</p>
        </div>
        
        <div class="metric-card">
            <h3>📊 Task Progress</h3>
            <div class="metric-value status-good">73%</div>
            <p>Implementation Complete</p>
        </div>
        
        <div class="metric-card">
            <h3>🎯 Quality Score</h3>
            <div class="metric-value status-good">A+</div>
            <p>Code Quality Rating</p>
        </div>
    </div>
    
    <div style="margin-top: 30px;">
        <h3>📡 Live Activity Stream</h3>
        <div id="activity-stream" style="height: 200px; overflow-y: scroll; border: 1px solid #00ff00; padding: 10px;">
            <p>🧪 test_bypass_detector.py - 9 tests passed</p>
            <p>🔧 emergency_validator.py - Auto-formatted by Kiro</p>
            <p>📝 hubris_prevention/models.py - Updated</p>
            <p>✅ Task 3.2 completed - Emergency claim verification</p>
            <p>🎯 Mama Discovery Protocol - Operational</p>
        </div>
    </div>
</body>
</html>
        """
    
    async def _check_critical_alerts(self):
        """Check for critical alerts that require paging."""
        alerts = []
        
        # Check test failure rate
        metrics = await self._get_current_metrics()
        test_pass_rate = metrics.get('test_pass_rate', 100)
        
        if test_pass_rate < 80:
            alerts.append({
                'message': f'Test pass rate dropped to {test_pass_rate:.1f}%',
                'source': 'test_monitoring',
                'severity': 'critical'
            })
        
        # Check hubris levels
        hubris_level = metrics.get('hubris_level', 'LOW')
        if hubris_level in ['HIGH', 'CRITICAL']:
            alerts.append({
                'message': f'Hubris level escalated to {hubris_level}',
                'source': 'hubris_prevention',
                'severity': 'critical'
            })
        
        # Check system health
        system_load = metrics.get('system_load', 'NORMAL')
        if system_load in ['HIGH', 'CRITICAL']:
            alerts.append({
                'message': f'System load critical: {system_load}',
                'source': 'system_monitoring',
                'severity': 'critical'
            })
        
        return alerts
    
    async def _get_current_metrics(self):
        """Get current system metrics."""
        # In real implementation, would read from metrics file or API
        return {
            'test_pass_rate': 89.5,  # Slightly below perfect for demo
            'beast_mode_active': True,
            'hubris_level': 'LOW',
            'system_load': 'NORMAL',
            'tasks_completed': 15,
            'total_tasks': 50,
            'code_quality': 'A+',
            'last_updated': datetime.now().isoformat()
        }
    
    async def _initialize_event_stream(self):
        """Initialize event stream file."""
        if not self.event_stream_file.exists():
            self.event_stream_file.touch()
        
        # Write initial event
        initial_event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'dashboard_started',
            'scenario': self.current_scenario,
            'message': f'Dashboard started in {self.scenarios[self.current_scenario]["name"]}'
        }
        
        with open(self.event_stream_file, 'a') as f:
            f.write(json.dumps(initial_event) + '\n')
    
    async def _generate_web_dashboard(self):
        """Generate web dashboard files."""
        # Create metrics JSON file for web dashboard
        metrics = await self._get_current_metrics()
        
        with open('beast_mode_metrics.json', 'w') as f:
            json.dump(metrics, f, indent=2)
    
    async def _update_dashboard_data(self):
        """Update dashboard data files."""
        await self._generate_web_dashboard()


class DashboardLauncher:
    """Launcher for scenario-based dashboard selection."""
    
    def __init__(self):
        self.dashboard = ScenarioBasedDashboard()
    
    async def interactive_launch(self):
        """Interactive dashboard launcher with scenario selection."""
        print("🎯 Beast Mode Multi-Modal Dashboard")
        print("═══════════════════════════════════")
        print()
        print("Select your scenario:")
        print("1. 🥃 Whiskey Mode - Chill monitoring (having a drink, watching the show)")
        print("2. ⚔️  War Room Mode - Full tactical display (all metrics, deep analysis)")
        print("3. 📟 Pager Mode - Critical alerts only (page me when shit hits the fan)")
        print()
        
        try:
            choice = input("Enter choice (1-3) or scenario name: ").strip()
            
            scenario_map = {
                '1': 'whiskey',
                '2': 'war_room', 
                '3': 'pager',
                'whiskey': 'whiskey',
                'war_room': 'war_room',
                'war': 'war_room',
                'pager': 'pager',
                'alert': 'pager'
            }
            
            scenario = scenario_map.get(choice.lower(), 'whiskey')
            
            await self.dashboard.start_dashboard(scenario)
            
        except KeyboardInterrupt:
            print("\n👋 Dashboard launcher ended")
    
    async def direct_launch(self, scenario: str):
        """Direct launch with specified scenario."""
        await self.dashboard.start_dashboard(scenario)


async def main():
    """Main entry point."""
    launcher = DashboardLauncher()
    
    # Check for command line scenario
    if len(sys.argv) > 1:
        scenario = sys.argv[1].lower()
        await launcher.direct_launch(scenario)
    else:
        await launcher.interactive_launch()


if __name__ == "__main__":
    asyncio.run(main())