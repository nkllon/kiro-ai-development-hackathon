#!/usr/bin/env python3
"""
AI Memory Palace Health Monitor.

Standalone health monitoring script that can be run as a daemon
to continuously monitor the AI Memory Palace system health.
"""

import sys
import time
import signal
import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from beast_mode.ai_memory_palace.deployment import DeploymentCLI


class HealthMonitor:
    """Standalone health monitor for AI Memory Palace"""
    
    def __init__(self, check_interval: int = 30, log_file: Optional[str] = None):
        self.check_interval = check_interval
        self.running = False
        self.cli = DeploymentCLI()
        
        # Setup logging
        log_level = logging.INFO
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        if log_file:
            logging.basicConfig(
                level=log_level,
                format=log_format,
                handlers=[
                    logging.FileHandler(log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        else:
            logging.basicConfig(level=log_level, format=log_format)
        
        self.logger = logging.getLogger('HealthMonitor')
        
        # Health tracking
        self.health_history = []
        self.alert_counts = {}
        self.last_alert_times = {}
        
        # Signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def start(self):
        """Start the health monitoring loop"""
        self.running = True
        self.logger.info("🏥 AI Memory Palace Health Monitor started")
        self.logger.info(f"Check interval: {self.check_interval} seconds")
        
        try:
            while self.running:
                self._perform_health_check()
                time.sleep(self.check_interval)
        
        except KeyboardInterrupt:
            self.logger.info("Health monitor interrupted by user")
        
        except Exception as e:
            self.logger.error(f"Health monitor error: {e}")
        
        finally:
            self.logger.info("🏥 AI Memory Palace Health Monitor stopped")
    
    def stop(self):
        """Stop the health monitoring loop"""
        self.running = False
    
    def _perform_health_check(self):
        """Perform comprehensive health check"""
        try:
            check_timestamp = datetime.now()
            
            # Get deployment status
            deployment_status = self.cli.status()
            
            # Get health check results
            health_results = self.cli.health_check()
            
            # Combine results
            health_report = {
                "timestamp": check_timestamp.isoformat(),
                "deployment_status": deployment_status,
                "health_results": health_results,
                "overall_health": self._calculate_overall_health(deployment_status, health_results)
            }
            
            # Store in history (keep last 100 checks)
            self.health_history.append(health_report)
            if len(self.health_history) > 100:
                self.health_history.pop(0)
            
            # Check for alerts
            self._check_alerts(health_report)
            
            # Log health status
            overall_health = health_report["overall_health"]
            if overall_health == "healthy":
                self.logger.info(f"✅ System healthy - {check_timestamp.strftime('%H:%M:%S')}")
            elif overall_health == "degraded":
                self.logger.warning(f"⚠️ System degraded - {check_timestamp.strftime('%H:%M:%S')}")
            else:
                self.logger.error(f"❌ System unhealthy - {check_timestamp.strftime('%H:%M:%S')}")
            
            # Log component details if not healthy
            if overall_health != "healthy":
                self._log_health_details(health_report)
        
        except Exception as e:
            self.logger.error(f"💥 Health check error: {e}")
    
    def _calculate_overall_health(self, deployment_status: Dict[str, Any], 
                                 health_results: Dict[str, Any]) -> str:
        """Calculate overall system health"""
        # Check deployment status
        if deployment_status["status"] != "deployed":
            return "unhealthy"
        
        if not deployment_status["config_loaded"] or not deployment_status["config_valid"]:
            return "degraded"
        
        # Check component health
        components = deployment_status.get("components_initialized", {})
        unhealthy_components = [name for name, status in components.items() if not status]
        
        if unhealthy_components:
            if len(unhealthy_components) > len(components) / 2:
                return "unhealthy"
            else:
                return "degraded"
        
        # Check health results
        if health_results.get("overall_status") == "unhealthy":
            return "unhealthy"
        elif health_results.get("overall_status") == "degraded":
            return "degraded"
        
        return "healthy"
    
    def _check_alerts(self, health_report: Dict[str, Any]):
        """Check for alert conditions"""
        try:
            overall_health = health_report["overall_health"]
            timestamp = health_report["timestamp"]
            
            # Alert on unhealthy system
            if overall_health == "unhealthy":
                self._trigger_alert("system_unhealthy", {
                    "message": "AI Memory Palace system is unhealthy",
                    "timestamp": timestamp,
                    "details": health_report
                })
            
            # Alert on degraded system (with rate limiting)
            elif overall_health == "degraded":
                if self._should_send_alert("system_degraded", minutes=15):
                    self._trigger_alert("system_degraded", {
                        "message": "AI Memory Palace system is degraded",
                        "timestamp": timestamp,
                        "details": health_report
                    })
            
            # Check for component failures
            deployment_status = health_report["deployment_status"]
            components = deployment_status.get("components_initialized", {})
            
            for component, status in components.items():
                if not status:
                    alert_key = f"component_failed_{component}"
                    if self._should_send_alert(alert_key, minutes=10):
                        self._trigger_alert(alert_key, {
                            "message": f"Component {component} has failed",
                            "component": component,
                            "timestamp": timestamp
                        })
            
            # Check health history for trends
            self._check_health_trends()
        
        except Exception as e:
            self.logger.error(f"💥 Alert check error: {e}")
    
    def _should_send_alert(self, alert_key: str, minutes: int = 5) -> bool:
        """Check if alert should be sent based on rate limiting"""
        now = datetime.now()
        last_alert = self.last_alert_times.get(alert_key)
        
        if not last_alert:
            return True
        
        time_since_last = now - last_alert
        return time_since_last > timedelta(minutes=minutes)
    
    def _trigger_alert(self, alert_type: str, alert_data: Dict[str, Any]):
        """Trigger an alert"""
        try:
            # Update alert tracking
            self.alert_counts[alert_type] = self.alert_counts.get(alert_type, 0) + 1
            self.last_alert_times[alert_type] = datetime.now()
            
            # Log alert
            self.logger.error(f"🚨 ALERT [{alert_type}]: {alert_data.get('message', 'Unknown alert')}")
            
            # Here you could integrate with external alerting systems:
            # - Send email notifications
            # - Post to Slack/Discord
            # - Send to monitoring systems (Prometheus, etc.)
            # - Write to alert log file
            
            # For now, just log the alert details
            alert_log = {
                "alert_type": alert_type,
                "timestamp": datetime.now().isoformat(),
                "count": self.alert_counts[alert_type],
                "data": alert_data
            }
            
            self.logger.error(f"Alert details: {json.dumps(alert_log, indent=2)}")
        
        except Exception as e:
            self.logger.error(f"💥 Alert trigger error: {e}")
    
    def _check_health_trends(self):
        """Check health history for concerning trends"""
        if len(self.health_history) < 10:
            return
        
        # Check last 10 health checks
        recent_checks = self.health_history[-10:]
        
        # Count unhealthy checks
        unhealthy_count = sum(1 for check in recent_checks 
                             if check["overall_health"] == "unhealthy")
        
        degraded_count = sum(1 for check in recent_checks 
                            if check["overall_health"] == "degraded")
        
        # Alert on trends
        if unhealthy_count >= 5:
            if self._should_send_alert("trend_unhealthy", minutes=30):
                self._trigger_alert("trend_unhealthy", {
                    "message": f"System has been unhealthy for {unhealthy_count}/10 recent checks",
                    "unhealthy_count": unhealthy_count,
                    "total_checks": len(recent_checks)
                })
        
        elif degraded_count >= 7:
            if self._should_send_alert("trend_degraded", minutes=20):
                self._trigger_alert("trend_degraded", {
                    "message": f"System has been degraded for {degraded_count}/10 recent checks",
                    "degraded_count": degraded_count,
                    "total_checks": len(recent_checks)
                })
    
    def _log_health_details(self, health_report: Dict[str, Any]):
        """Log detailed health information"""
        deployment_status = health_report["deployment_status"]
        
        # Log component status
        components = deployment_status.get("components_initialized", {})
        for component, status in components.items():
            status_icon = "✅" if status else "❌"
            self.logger.info(f"  {status_icon} {component}: {'initialized' if status else 'failed'}")
        
        # Log configuration status
        self.logger.info(f"  Config loaded: {deployment_status['config_loaded']}")
        self.logger.info(f"  Config valid: {deployment_status['config_valid']}")
        self.logger.info(f"  Health monitoring: {deployment_status['health_monitoring_active']}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary statistics"""
        if not self.health_history:
            return {"error": "No health data available"}
        
        recent_checks = self.health_history[-20:] if len(self.health_history) >= 20 else self.health_history
        
        health_counts = {}
        for check in recent_checks:
            health = check["overall_health"]
            health_counts[health] = health_counts.get(health, 0) + 1
        
        return {
            "total_checks": len(self.health_history),
            "recent_checks": len(recent_checks),
            "health_distribution": health_counts,
            "alert_counts": self.alert_counts.copy(),
            "last_check": self.health_history[-1]["timestamp"] if self.health_history else None,
            "uptime_percentage": (health_counts.get("healthy", 0) / len(recent_checks)) * 100 if recent_checks else 0
        }


def main():
    """Main health monitor entry point"""
    parser = argparse.ArgumentParser(
        description="AI Memory Palace Health Monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--interval', type=int, default=30,
                       help='Health check interval in seconds (default: 30)')
    parser.add_argument('--log-file', type=str,
                       help='Log file path (default: stdout only)')
    parser.add_argument('--daemon', action='store_true',
                       help='Run as daemon (background process)')
    parser.add_argument('--summary', action='store_true',
                       help='Show health summary and exit')
    
    args = parser.parse_args()
    
    try:
        monitor = HealthMonitor(
            check_interval=args.interval,
            log_file=args.log_file
        )
        
        if args.summary:
            # Show summary and exit
            summary = monitor.get_health_summary()
            print("🏥 AI Memory Palace Health Summary:")
            print(json.dumps(summary, indent=2))
            return 0
        
        if args.daemon:
            # Run as daemon (simplified - in production you'd use proper daemonization)
            print(f"Starting health monitor as daemon (PID: {os.getpid()})")
            print(f"Check interval: {args.interval} seconds")
            if args.log_file:
                print(f"Logging to: {args.log_file}")
        
        # Start monitoring
        monitor.start()
        
        return 0
    
    except KeyboardInterrupt:
        print("\n⏹️ Health monitor stopped by user")
        return 0
    
    except Exception as e:
        print(f"💥 Health monitor error: {e}")
        return 1


if __name__ == '__main__':
    import os
    sys.exit(main())