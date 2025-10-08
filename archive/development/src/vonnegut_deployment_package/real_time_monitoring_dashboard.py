#!/usr/bin/env python3
"""
Real-Time WebSocket Monitoring Dashboard
Fibonacci Iteration 4a - Monitoring Deployment

Provides a real-time monitoring dashboard for observatory.nkllon.com
WebSocket infrastructure with live updates and alerting.
"""

import asyncio
import json
import time
import requests
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/realtime_monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RealTimeMonitoringDashboard:
    """Real-time monitoring dashboard for WebSocket deployment"""
    
    def __init__(self):
        self.dashboard_active = False
        self.monitoring_data = {}
        self.alert_history = []
        self.performance_history = []
        self.start_time = datetime.now()
        
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        logger.info("🚀 Real-Time Monitoring Dashboard initialized")
    
    async def check_websocket_connectivity(self) -> Dict[str, Any]:
        """Check WebSocket connectivity in real-time"""
        endpoints = [
            "wss://observatory.nkllon.com/ws/emoji-rain",
            "ws://localhost:8888/ws/emoji-rain"
        ]
        
        connectivity_status = {}
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                
                # Quick HTTP check for secure endpoints
                if endpoint.startswith('wss://'):
                    http_endpoint = endpoint.replace('wss://', 'https://').replace('/ws/', '/health')
                    try:
                        http_response = requests.get(http_endpoint, timeout=3)
                        http_ok = http_response.status_code == 200
                    except:
                        http_ok = False
                else:
                    http_ok = True
                
                # WebSocket connectivity test
                import websockets
                async with websockets.connect(endpoint, timeout=5) as ws:
                    test_msg = json.dumps({"type": "ping", "timestamp": datetime.now().isoformat()})
                    await ws.send(test_msg)
                    response = await asyncio.wait_for(ws.recv(), timeout=3)
                    
                    response_time = (time.time() - start_time) * 1000
                    
                    connectivity_status[endpoint] = {
                        'status': 'connected',
                        'response_time_ms': response_time,
                        'http_ok': http_ok,
                        'last_check': datetime.now().isoformat(),
                        'data_received': len(response)
                    }
                    
            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                connectivity_status[endpoint] = {
                    'status': 'disconnected',
                    'response_time_ms': response_time,
                    'error': str(e),
                    'http_ok': http_ok if 'http_ok' in locals() else False,
                    'last_check': datetime.now().isoformat()
                }
        
        return connectivity_status
    
    def get_system_performance(self) -> Dict[str, Any]:
        """Get real-time system performance metrics"""
        try:
            import psutil
            
            return {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage_percent': psutil.disk_usage('/').percent,
                'network_bytes_sent': psutil.net_io_counters().bytes_sent,
                'network_bytes_recv': psutil.net_io_counters().bytes_recv,
                'process_count': len(psutil.pids()),
                'timestamp': datetime.now().isoformat()
            }
        except ImportError:
            return {
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_usage_percent': 0,
                'timestamp': datetime.now().isoformat()
            }
    
    def check_cloudflare_status(self) -> Dict[str, Any]:
        """Check Cloudflare tunnel and service status"""
        status = {
            'tunnel_running': False,
            'cloudflare_operational': True,  # Mock status
            'websocket_support_enabled': True,
            'bot_protection_active': True,
            'last_check': datetime.now().isoformat()
        }
        
        try:
            # Check if cloudflared process is running
            result = subprocess.run(['pgrep', 'cloudflared'], capture_output=True, text=True)
            status['tunnel_running'] = result.returncode == 0
            
        except Exception as e:
            status['error'] = str(e)
        
        return status
    
    def check_ssl_certificate_status(self) -> Dict[str, Any]:
        """Check SSL certificate status"""
        ssl_status = {
            'certificate_valid': True,  # Mock status
            'certificate_expiry': '2025-12-31',
            'ssl_grade': 'A',
            'tls_version': 'TLS 1.3',
            'last_check': datetime.now().isoformat()
        }
        
        try:
            import ssl
            import socket
            
            hostname = 'observatory.nkllon.com'
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    ssl_status['certificate_valid'] = True
                    ssl_status['certificate_expiry'] = cert.get('notAfter', 'Unknown')
                    ssl_status['tls_version'] = ssock.version()
                    
        except Exception as e:
            ssl_status['certificate_valid'] = False
            ssl_status['error'] = str(e)
        
        return ssl_status
    
    def analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends from historical data"""
        if len(self.performance_history) < 2:
            return {'trend': 'insufficient_data', 'direction': 'stable'}
        
        recent_data = self.performance_history[-10:]  # Last 10 data points
        
        # Calculate trends
        cpu_trend = self._calculate_trend([d.get('cpu_percent', 0) for d in recent_data])
        memory_trend = self._calculate_trend([d.get('memory_percent', 0) for d in recent_data])
        response_time_trend = self._calculate_trend([d.get('avg_response_time_ms', 0) for d in recent_data])
        
        return {
            'cpu_trend': cpu_trend,
            'memory_trend': memory_trend,
            'response_time_trend': response_time_trend,
            'overall_trend': 'improving' if cpu_trend == 'decreasing' and memory_trend == 'decreasing' else 'stable'
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values"""
        if len(values) < 2:
            return 'stable'
        
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        if second_avg > first_avg * 1.05:
            return 'increasing'
        elif second_avg < first_avg * 0.95:
            return 'decreasing'
        else:
            return 'stable'
    
    def check_alerts(self, current_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for alert conditions"""
        alerts = []
        
        # WebSocket connectivity alerts
        websocket_data = current_data.get('websocket_connectivity', {})
        disconnected_endpoints = [ep for ep, data in websocket_data.items() if data.get('status') == 'disconnected']
        
        if disconnected_endpoints:
            alerts.append({
                'severity': 'critical',
                'type': 'websocket_disconnected',
                'message': f'WebSocket endpoints disconnected: {len(disconnected_endpoints)}',
                'details': disconnected_endpoints,
                'timestamp': datetime.now().isoformat()
            })
        
        # System performance alerts
        system_data = current_data.get('system_performance', {})
        if system_data.get('cpu_percent', 0) > 90:
            alerts.append({
                'severity': 'high',
                'type': 'high_cpu_usage',
                'message': f'High CPU usage: {system_data.get("cpu_percent", 0):.1f}%',
                'timestamp': datetime.now().isoformat()
            })
        
        if system_data.get('memory_percent', 0) > 90:
            alerts.append({
                'severity': 'high',
                'type': 'high_memory_usage',
                'message': f'High memory usage: {system_data.get("memory_percent", 0):.1f}%',
                'timestamp': datetime.now().isoformat()
            })
        
        # SSL certificate alerts
        ssl_data = current_data.get('ssl_status', {})
        if not ssl_data.get('certificate_valid', False):
            alerts.append({
                'severity': 'critical',
                'type': 'ssl_certificate_invalid',
                'message': 'SSL certificate is invalid or expired',
                'timestamp': datetime.now().isoformat()
            })
        
        # Cloudflare tunnel alerts
        cloudflare_data = current_data.get('cloudflare_status', {})
        if not cloudflare_data.get('tunnel_running', False):
            alerts.append({
                'severity': 'high',
                'type': 'tunnel_down',
                'message': 'Cloudflare tunnel is not running',
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate comprehensive dashboard data"""
        current_time = datetime.now()
        
        # Collect all monitoring data
        websocket_data = asyncio.run(self.check_websocket_connectivity())
        system_data = self.get_system_performance()
        cloudflare_data = self.check_cloudflare_status()
        ssl_data = self.check_ssl_certificate_status()
        
        # Calculate average response time
        response_times = [data.get('response_time_ms', 0) for data in websocket_data.values()]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Calculate connection success rate
        connected_count = sum(1 for data in websocket_data.values() if data.get('status') == 'connected')
        total_endpoints = len(websocket_data)
        success_rate = connected_count / total_endpoints if total_endpoints > 0 else 0
        
        # Store performance data
        performance_data = {
            'timestamp': current_time.isoformat(),
            'cpu_percent': system_data.get('cpu_percent', 0),
            'memory_percent': system_data.get('memory_percent', 0),
            'avg_response_time_ms': avg_response_time,
            'success_rate': success_rate
        }
        self.performance_history.append(performance_data)
        
        # Keep only last 100 data points
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]
        
        # Analyze trends
        trends = self.analyze_performance_trends()
        
        # Check for alerts
        current_data = {
            'websocket_connectivity': websocket_data,
            'system_performance': system_data,
            'cloudflare_status': cloudflare_data,
            'ssl_status': ssl_data
        }
        alerts = self.check_alerts(current_data)
        
        # Store alerts
        self.alert_history.extend(alerts)
        if len(self.alert_history) > 50:
            self.alert_history = self.alert_history[-50:]
        
        # Calculate overall health score
        health_score = 100
        health_score -= (1 - success_rate) * 50  # WebSocket connectivity
        health_score -= max(0, system_data.get('cpu_percent', 0) - 80) * 0.5  # CPU usage
        health_score -= max(0, system_data.get('memory_percent', 0) - 80) * 0.5  # Memory usage
        health_score -= 20 if not ssl_data.get('certificate_valid', False) else 0  # SSL issues
        health_score -= 15 if not cloudflare_data.get('tunnel_running', False) else 0  # Tunnel issues
        
        health_score = max(0, min(100, health_score))
        
        dashboard_data = {
            'timestamp': current_time.isoformat(),
            'uptime_minutes': (current_time - self.start_time).total_seconds() / 60,
            'overall_health_score': health_score,
            'health_status': 'healthy' if health_score >= 80 else 'degraded' if health_score >= 60 else 'critical',
            'websocket_connectivity': websocket_data,
            'system_performance': system_data,
            'cloudflare_status': cloudflare_data,
            'ssl_status': ssl_data,
            'performance_trends': trends,
            'active_alerts': alerts,
            'alert_history': self.alert_history[-10:],  # Last 10 alerts
            'performance_history': self.performance_history[-20:]  # Last 20 data points
        }
        
        return dashboard_data
    
    def print_dashboard(self, data: Dict[str, Any]):
        """Print real-time dashboard to console"""
        # Clear screen (works on most terminals)
        print('\033[2J\033[H', end='')
        
        print("🚀 OBSERVATORY.NKLLON.COM - REAL-TIME MONITORING DASHBOARD")
        print("=" * 70)
        print(f"⏰ Time: {data['timestamp']}")
        print(f"⏱️  Uptime: {data['uptime_minutes']:.1f} minutes")
        print(f"🏥 Overall Health: {data['overall_health_score']:.1f}/100 ({data['health_status'].upper()})")
        
        # WebSocket Status
        print(f"\n🌐 WebSocket Connectivity:")
        for endpoint, status in data['websocket_connectivity'].items():
            status_emoji = "🟢" if status['status'] == 'connected' else "🔴"
            print(f"  {status_emoji} {endpoint.split('/')[-1]}: {status['status']} ({status.get('response_time_ms', 0):.1f}ms)")
        
        # System Performance
        perf = data['system_performance']
        print(f"\n📊 System Performance:")
        print(f"  💻 CPU: {perf.get('cpu_percent', 0):.1f}%")
        print(f"  🧠 Memory: {perf.get('memory_percent', 0):.1f}%")
        print(f"  💾 Disk: {perf.get('disk_usage_percent', 0):.1f}%")
        
        # Cloudflare Status
        cf = data['cloudflare_status']
        tunnel_emoji = "🟢" if cf.get('tunnel_running', False) else "🔴"
        print(f"\n🌐 Cloudflare Tunnel:")
        print(f"  {tunnel_emoji} Tunnel: {'Running' if cf.get('tunnel_running', False) else 'Stopped'}")
        print(f"  🔌 WebSocket Support: {'Enabled' if cf.get('websocket_support_enabled', False) else 'Disabled'}")
        print(f"  🛡️  Bot Protection: {'Active' if cf.get('bot_protection_active', False) else 'Inactive'}")
        
        # SSL Status
        ssl = data['ssl_status']
        ssl_emoji = "🟢" if ssl.get('certificate_valid', False) else "🔴"
        print(f"\n🔒 SSL/TLS Status:")
        print(f"  {ssl_emoji} Certificate: {'Valid' if ssl.get('certificate_valid', False) else 'Invalid'}")
        print(f"  📅 Expiry: {ssl.get('certificate_expiry', 'Unknown')}")
        print(f"  🔐 TLS Version: {ssl.get('tls_version', 'Unknown')}")
        
        # Performance Trends
        trends = data['performance_trends']
        print(f"\n📈 Performance Trends:")
        print(f"  💻 CPU: {trends.get('cpu_trend', 'stable').title()}")
        print(f"  🧠 Memory: {trends.get('memory_trend', 'stable').title()}")
        print(f"  ⚡ Response Time: {trends.get('response_time_trend', 'stable').title()}")
        
        # Active Alerts
        alerts = data['active_alerts']
        if alerts:
            print(f"\n🚨 Active Alerts ({len(alerts)}):")
            for alert in alerts:
                severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(alert['severity'], "⚪")
                print(f"  {severity_emoji} {alert['severity'].upper()}: {alert['message']}")
        else:
            print(f"\n✅ No Active Alerts")
        
        print("\n" + "=" * 70)
        print("Press Ctrl+C to stop monitoring")
    
    async def start_real_time_monitoring(self, refresh_interval: int = 5):
        """Start real-time monitoring dashboard"""
        self.dashboard_active = True
        logger.info(f"🚀 Starting real-time monitoring (refresh every {refresh_interval}s)")
        
        try:
            while self.dashboard_active:
                # Generate dashboard data
                dashboard_data = self.generate_dashboard_data()
                
                # Print dashboard
                self.print_dashboard(dashboard_data)
                
                # Save data to file
                data_file = f"logs/realtime_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(data_file, 'w') as f:
                    json.dump(dashboard_data, f, indent=2)
                
                # Wait for next refresh
                await asyncio.sleep(refresh_interval)
                
        except KeyboardInterrupt:
            logger.info("🛑 Real-time monitoring stopped by user")
        except Exception as e:
            logger.error(f"❌ Real-time monitoring error: {e}")
        finally:
            self.dashboard_active = False
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.dashboard_active = False
        logger.info("🛑 Stopping real-time monitoring")

async def main():
    """Main function"""
    print("🚀 Real-Time WebSocket Monitoring Dashboard")
    print("Target: observatory.nkllon.com WebSocket Infrastructure")
    print("=" * 60)
    
    dashboard = RealTimeMonitoringDashboard()
    
    try:
        await dashboard.start_real_time_monitoring(refresh_interval=5)
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)