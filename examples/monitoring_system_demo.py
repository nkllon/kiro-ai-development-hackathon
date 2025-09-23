"""
Beast Mode Monitoring System Demo

Demonstrates the comprehensive monitoring, alerting, and recovery
capabilities of the Beast Mode Agent Collaboration Network.
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any

from src.beast_mode.monitoring.system_monitor import SystemMonitor
from src.beast_mode.monitoring.alerting import AlertSeverity
from src.beast_mode.monitoring.recovery import RecoveryResult


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MonitoringDemo:
    """
    Comprehensive demonstration of the Beast Mode monitoring system.

    Shows health monitoring, metrics collection, alerting, and recovery
    in action with realistic scenarios.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.system_monitor = SystemMonitor(redis_url)
        self.demo_running = False

    async def run_demo(self) -> None:
        """Run the complete monitoring system demonstration."""
        logger.info("🚀 Starting Beast Mode Monitoring System Demo")

        try:
            # Start monitoring system
            await self.system_monitor.start_monitoring()
            self.demo_running = True

            # Set up demo callbacks
            self._setup_demo_callbacks()

            # Run demonstration scenarios
            await self._demo_basic_monitoring()
            await self._demo_metrics_collection()
            await self._demo_alerting_system()
            await self._demo_recovery_system()
            await self._demo_integrated_workflow()
            await self._demo_performance_monitoring()

            # Generate final report
            await self._generate_final_report()

        except Exception as e:
            logger.error(f"Demo failed: {e}")
            raise
        finally:
            # Clean up
            await self.system_monitor.stop_monitoring()
            self.demo_running = False
            logger.info("✅ Demo completed successfully")

    def _setup_demo_callbacks(self) -> None:
        """Set up callbacks for demonstration."""

        def alert_handler(alert):
            logger.info(
                f"🚨 ALERT: {alert.name} - {alert.message} (Severity: {alert.severity})"
            )

        def recovery_callback(attempt):
            logger.info(
                f"🔧 RECOVERY: {attempt.action_name} - {attempt.result} ({attempt.message})"
            )

        def status_callback(status):
            logger.info(
                f"📊 STATUS: Health={status.overall_health}, Alerts={status.active_alerts}, "
                f"Throughput={status.message_throughput}, ErrorRate={status.error_rate}%"
            )

        self.system_monitor.alert_manager.add_alert_handler(alert_handler)
        self.system_monitor.recovery_manager.add_recovery_callback(recovery_callback)
        self.system_monitor.add_status_callback(status_callback)

    async def _demo_basic_monitoring(self) -> None:
        """Demonstrate basic health monitoring."""
        logger.info("\n🔍 === BASIC HEALTH MONITORING DEMO ===")

        # Wait for initial health checks
        await asyncio.sleep(2)

        # Get system health
        health = await self.system_monitor.health_monitor.get_system_health()
        logger.info(f"System components monitored: {len(health)}")

        for component_name, component_health in health.items():
            logger.info(
                f"  {component_name}: {component_health.status} - {component_health.message}"
            )

        # Get health summary
        summary = await self.system_monitor.health_monitor.get_health_summary()
        logger.info(
            f"Health Summary: {summary['healthy']} healthy, {summary['degraded']} degraded, "
            f"{summary['unhealthy']} unhealthy"
        )

    async def _demo_metrics_collection(self) -> None:
        """Demonstrate metrics collection."""
        logger.info("\n📈 === METRICS COLLECTION DEMO ===")

        # Simulate message processing activity
        logger.info("Simulating message processing activity...")

        for i in range(50):
            # Simulate message sending with varying latency
            latency = 50 + (i % 10) * 20  # 50-250ms range
            self.system_monitor.record_message_sent(latency_ms=latency)

            # Simulate message receiving with processing time
            processing_time = 25 + (i % 5) * 10  # 25-65ms range
            self.system_monitor.record_message_received(
                processing_time_ms=processing_time
            )

            # Simulate occasional errors
            if i % 15 == 0:
                self.system_monitor.record_error("timeout")
            elif i % 20 == 0:
                self.system_monitor.record_error("connection_failed")

            # Simulate agent connections
            if i % 10 == 0:
                self.system_monitor.record_agent_connection(f"agent_{i//10}", True)

            await asyncio.sleep(0.1)  # Small delay to simulate real timing

        # Get performance report
        report = self.system_monitor.metrics_collector.get_performance_report()
        logger.info("Performance Metrics:")

        if "kpis" in report:
            kpis = report["kpis"]

            if "message_throughput" in kpis:
                throughput = kpis["message_throughput"]
                logger.info(
                    f"  Messages: {throughput['messages_sent']} sent, "
                    f"{throughput['messages_received']} received"
                )

            if "message_latency" in kpis:
                latency = kpis["message_latency"]
                logger.info(
                    f"  Latency: avg={latency['avg_ms']:.1f}ms, "
                    f"p95={latency.get('p95_ms', 0):.1f}ms"
                )

            if "error_rate" in kpis:
                error_rate = kpis["error_rate"]
                logger.info(f"  Error Rate: {error_rate['error_rate_percent']:.1f}%")

    async def _demo_alerting_system(self) -> None:
        """Demonstrate alerting system."""
        logger.info("\n🚨 === ALERTING SYSTEM DEMO ===")

        # Fire various test alerts
        logger.info("Firing test alerts...")

        # Critical alert
        critical_alert_id = await self.system_monitor.alert_manager.fire_alert(
            name="demo_critical_alert",
            message="Critical system failure detected",
            severity=AlertSeverity.CRITICAL,
            source_component="demo_system",
            details={
                "failure_type": "complete_outage",
                "affected_services": ["messaging", "storage"],
            },
        )

        # High severity alert
        high_alert_id = await self.system_monitor.alert_manager.fire_alert(
            name="demo_high_alert",
            message="High error rate detected",
            severity=AlertSeverity.HIGH,
            source_component="message_processor",
            details={"error_rate": 15.5, "threshold": 10.0},
        )

        # Medium severity alert
        medium_alert_id = await self.system_monitor.alert_manager.fire_alert(
            name="demo_medium_alert",
            message="Performance degradation detected",
            severity=AlertSeverity.MEDIUM,
            source_component="latency_monitor",
            details={"avg_latency_ms": 850, "threshold_ms": 500},
        )

        await asyncio.sleep(1)  # Let alerts propagate

        # Show active alerts
        active_alerts = self.system_monitor.alert_manager.get_active_alerts()
        logger.info(f"Active alerts: {len(active_alerts)}")

        for alert in active_alerts:
            logger.info(f"  {alert.severity.upper()}: {alert.name} - {alert.message}")

        # Resolve some alerts
        logger.info("Resolving alerts...")

        await self.system_monitor.alert_manager.resolve_alert(
            medium_alert_id, "Performance improved after optimization"
        )

        await self.system_monitor.alert_manager.resolve_alert(
            high_alert_id, "Error rate returned to normal levels"
        )

        # Show alert summary
        summary = self.system_monitor.alert_manager.get_alert_summary()
        logger.info(
            f"Alert Summary: {summary['active_alerts']} active, "
            f"{summary['recent_alerts_24h']} in last 24h"
        )

    async def _demo_recovery_system(self) -> None:
        """Demonstrate recovery system."""
        logger.info("\n🔧 === RECOVERY SYSTEM DEMO ===")

        # Register custom recovery actions for demo
        await self._register_demo_recovery_actions()

        # Simulate component failures and recovery
        logger.info("Simulating component failures...")

        # Report Redis connection failure
        await self.system_monitor.report_component_failure(
            "redis", "connection_failed", {"error": "Connection refused", "attempts": 3}
        )

        # Report high error rate
        await self.system_monitor.report_component_failure(
            "messaging", "high_error_rate", {"error_rate": 25.0, "threshold": 10.0}
        )

        await asyncio.sleep(1)  # Let recovery system process

        # Manually trigger recovery actions
        logger.info("Triggering recovery actions...")

        # Trigger Redis reconnect
        result = await self.system_monitor.recovery_manager.trigger_recovery(
            "redis_reconnect"
        )
        logger.info(f"Redis reconnect result: {result}")

        # Trigger counter reset
        result = await self.system_monitor.recovery_manager.trigger_recovery(
            "reset_message_counters"
        )
        logger.info(f"Counter reset result: {result}")

        # Show recovery summary
        summary = self.system_monitor.recovery_manager.get_recovery_summary()
        logger.info(
            f"Recovery Summary: {summary['active_recoveries']} active, "
            f"{summary['recent_attempts_24h']} attempts in 24h, "
            f"{summary['success_rate_24h']:.1f}% success rate"
        )

    async def _demo_integrated_workflow(self) -> None:
        """Demonstrate integrated monitoring workflow."""
        logger.info("\n🔄 === INTEGRATED WORKFLOW DEMO ===")

        # Simulate a realistic failure scenario
        logger.info("Simulating realistic failure scenario...")

        # 1. High error rate triggers metrics alert
        for _ in range(100):
            self.system_monitor.record_error("connection_timeout")
        for _ in range(10):
            self.system_monitor.metrics_collector.increment_counter("operations")

        # 2. Manual alert firing (simulating health check failure)
        await self.system_monitor.alert_manager.fire_alert(
            name="redis_connection_failed",
            message="Redis server unreachable",
            severity=AlertSeverity.CRITICAL,
            source_component="redis_health_check",
        )

        # 3. Wait for integrated response
        await asyncio.sleep(2)

        # 4. Check system status
        status = await self.system_monitor.get_system_status()
        logger.info(
            f"System Status: Health={status.overall_health}, "
            f"Alerts={status.active_alerts}, Recoveries={status.active_recoveries}"
        )

        # 5. Show how recovery was triggered by alert
        recovery_history = self.system_monitor.recovery_manager.get_recovery_history(1)
        if recovery_history:
            logger.info("Recovery actions triggered by alerts:")
            for attempt in recovery_history[-3:]:  # Show last 3
                logger.info(
                    f"  {attempt.action_name}: {attempt.result} - {attempt.message}"
                )

    async def _demo_performance_monitoring(self) -> None:
        """Demonstrate performance monitoring capabilities."""
        logger.info("\n⚡ === PERFORMANCE MONITORING DEMO ===")

        # Simulate high-throughput scenario
        logger.info("Simulating high-throughput message processing...")

        start_time = datetime.now()

        # Burst of activity
        for batch in range(10):
            tasks = []
            for i in range(20):  # 20 messages per batch
                task = asyncio.create_task(
                    self._simulate_message_processing(batch * 20 + i)
                )
                tasks.append(task)

            await asyncio.gather(*tasks)
            await asyncio.sleep(0.1)  # Brief pause between batches

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Get performance metrics
        report = self.system_monitor.metrics_collector.get_performance_report()

        logger.info(f"Performance Test Results ({duration:.1f}s):")

        if "kpis" in report:
            kpis = report["kpis"]

            if "message_throughput" in kpis:
                throughput = kpis["message_throughput"]
                total_messages = throughput.get("total_messages", 0)
                messages_per_second = total_messages / duration if duration > 0 else 0
                logger.info(f"  Throughput: {messages_per_second:.1f} messages/second")

            if "message_latency" in kpis:
                latency = kpis["message_latency"]
                logger.info(
                    f"  Latency: avg={latency['avg_ms']:.1f}ms, "
                    f"p95={latency.get('p95_ms', 0):.1f}ms, "
                    f"p99={latency.get('p99_ms', 0):.1f}ms"
                )

    async def _simulate_message_processing(self, message_id: int) -> None:
        """Simulate processing a single message."""
        # Simulate variable processing time
        processing_time = 30 + (message_id % 10) * 5  # 30-75ms

        # Record message received
        self.system_monitor.record_message_received(processing_time_ms=processing_time)

        # Simulate processing delay
        await asyncio.sleep(processing_time / 1000)  # Convert to seconds

        # Record message sent (response)
        response_latency = processing_time + 20  # Add network latency
        self.system_monitor.record_message_sent(latency_ms=response_latency)

        # Simulate occasional errors
        if message_id % 50 == 0:
            self.system_monitor.record_error("processing_timeout")

    async def _register_demo_recovery_actions(self) -> None:
        """Register demo-specific recovery actions."""

        async def demo_service_restart(context):
            logger.info("🔄 Restarting demo service...")
            await asyncio.sleep(1)  # Simulate restart time
            return {
                "result": RecoveryResult.SUCCESS,
                "message": "Demo service restarted successfully",
                "details": {"restart_time": datetime.now().isoformat()},
            }

        async def demo_cache_clear(context):
            logger.info("🗑️ Clearing demo cache...")
            await asyncio.sleep(0.5)  # Simulate cache clear
            return {
                "result": RecoveryResult.SUCCESS,
                "message": "Demo cache cleared",
                "details": {"cleared_entries": 1000},
            }

        await self.system_monitor.recovery_manager.register_recovery_action(
            name="demo_service_restart",
            action_type="restart_service",
            description="Restart demo service",
            action_function=demo_service_restart,
        )

        await self.system_monitor.recovery_manager.register_recovery_action(
            name="demo_cache_clear",
            action_type="clear_cache",
            description="Clear demo cache",
            action_function=demo_cache_clear,
        )

    async def _generate_final_report(self) -> None:
        """Generate and display final comprehensive report."""
        logger.info("\n📋 === FINAL COMPREHENSIVE REPORT ===")

        report = await self.system_monitor.get_comprehensive_report()

        # Pretty print key sections
        logger.info("System Status:")
        system_status = report["system_status"]
        for key, value in system_status.items():
            if key != "timestamp":
                logger.info(f"  {key}: {value}")

        logger.info("\nHealth Summary:")
        health_summary = report["health"]
        for key, value in health_summary.items():
            if key != "last_updated":
                logger.info(f"  {key}: {value}")

        logger.info("\nAlert Summary:")
        alert_summary = report["alerts"]["summary"]
        for key, value in alert_summary.items():
            if key != "last_updated":
                logger.info(f"  {key}: {value}")

        logger.info("\nRecovery Summary:")
        recovery_summary = report["recovery"]["summary"]
        for key, value in recovery_summary.items():
            if key != "last_updated":
                logger.info(f"  {key}: {value}")

        # Save full report to file
        report_filename = (
            f"monitoring_demo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_filename, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"\n📄 Full report saved to: {report_filename}")


async def main():
    """Run the monitoring system demonstration."""
    demo = MonitoringDemo()

    try:
        await demo.run_demo()
    except KeyboardInterrupt:
        logger.info("\n⏹️ Demo interrupted by user")
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
