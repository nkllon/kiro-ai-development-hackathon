#!/usr/bin/env python3
"""
Runtime State Registry Phase 2 Demo
====================================

Demonstration script showing the complete Phase 2 system in action:
- State Reconciliation Engine
- Drift Detection System  
- Compliance Monitoring
- Auto-Remediation Engine

This script provides a comprehensive demo of the three-layer state reconciliation
system with drift detection, compliance monitoring, and intelligent remediation.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any
import argparse

from src.runtime_state_registry.reconciliation.state_reconciliation_engine import (
    StateReconciliationEngine, ReconciliationStrategy
)
from src.runtime_state_registry.compliance.drift_detector import DriftDetector
from src.runtime_state_registry.compliance.compliance_monitor import ComplianceMonitor
from src.runtime_state_registry.remediation.auto_remediation_engine import AutoRemediationEngine


class RuntimeStateRegistryPhase2Demo:
    """Demo orchestrator for Phase 2 system."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize Phase 2 components
        self.reconciliation_engine = StateReconciliationEngine(
            reconciliation_strategy=ReconciliationStrategy.HIERARCHICAL,
            compliance_threshold=0.8,
            auto_remediation_enabled=False
        )
        
        self.drift_detector = DriftDetector(
            confidence_threshold=0.7,
            enable_auto_remediation_suggestions=True
        )
        
        self.compliance_monitor = ComplianceMonitor(
            monitoring_interval=60,
            compliance_threshold=0.8,
            critical_threshold=0.5
        )
        
        self.remediation_engine = AutoRemediationEngine(
            auto_execute_safe_actions=True,
            auto_execute_cautious_actions=False,
            max_concurrent_executions=3
        )
        
        # Demo service data
        self.demo_services = self._create_demo_service_data()
    
    def _create_demo_service_data(self) -> Dict[str, Dict[str, Any]]:
        """Create realistic demo service data showing various drift scenarios."""
        return {
            "web_frontend": {
                "spec_state": {
                    "service_name": "web_frontend",
                    "version": "2.1.0",
                    "port": 8080,
                    "replicas": 3,
                    "health_check": "/health",
                    "environment": "production",
                    "cpu_limit": "500m",
                    "memory_limit": "512Mi"
                },
                "cms_state": {
                    "service_name": "web_frontend", 
                    "version": "2.0.5",
                    "port": 8080,
                    "replicas": 2,
                    "health_check": "/health",
                    "environment": "production",
                    "cpu_limit": "400m",
                    "memory_limit": "512Mi"
                },
                "runtime_state": {
                    "service_name": "web_frontend",
                    "version": "2.0.5",
                    "port": 8080,
                    "replicas": 2,
                    "status": "running",
                    "health_status": "healthy",
                    "cpu_usage": "350m",
                    "memory_usage": "480Mi"
                }
            },
            "api_backend": {
                "spec_state": {
                    "service_name": "api_backend",
                    "version": "1.5.0",
                    "port": 3000,
                    "replicas": 2,
                    "health_check": "/api/health",
                    "database_url": "postgresql://db:5432/api"
                },
                "cms_state": {
                    "service_name": "api_backend",
                    "version": "1.5.0", 
                    "port": 3000,
                    "replicas": 2,
                    "health_check": "/api/health",
                    "database_url": "postgresql://db:5432/api"
                },
                "runtime_state": {
                    "service_name": "api_backend",
                    "version": "1.5.0",
                    "port": 3000,
                    "replicas": 2,
                    "status": "running",
                    "health_status": "healthy",
                    "database_connected": True
                }
            },
            "database": {
                "spec_state": {
                    "service_name": "database",
                    "version": "13.0",
                    "port": 5432,
                    "storage": "100Gi",
                    "backup_enabled": True
                },
                "cms_state": {
                    "service_name": "database",
                    "version": "13.0",
                    "port": 5432,
                    "storage": "100Gi",
                    "backup_enabled": True
                },
                "runtime_state": {
                    "service_name": "database",
                    "version": "13.0",
                    "port": 5432,
                    "status": "running",
                    "health_status": "healthy",
                    "connections": 15,
                    "storage_used": "45Gi"
                }
            },
            "cache_service": {
                "spec_state": {
                    "service_name": "cache_service",
                    "version": "6.2.0",
                    "port": 6379,
                    "memory_limit": "1Gi"
                },
                "cms_state": {
                    "service_name": "cache_service",
                    "version": "6.0.0",  # Version drift
                    "port": 6379,
                    "memory_limit": "512Mi"  # Resource drift
                },
                "runtime_state": {
                    "service_name": "cache_service",
                    "version": "6.0.0",
                    "port": 6379,
                    "status": "running",
                    "health_status": "degraded",  # Health issue
                    "memory_usage": "480Mi"
                }
            },
            "orphaned_service": {
                # Only runtime state - orphaned service
                "runtime_state": {
                    "service_name": "orphaned_service",
                    "version": "1.0.0",
                    "port": 9999,
                    "status": "running",
                    "health_status": "unknown"
                }
            },
            "missing_service": {
                # Only spec and CMS state - missing service
                "spec_state": {
                    "service_name": "missing_service",
                    "version": "1.2.0",
                    "port": 7777,
                    "replicas": 1
                },
                "cms_state": {
                    "service_name": "missing_service",
                    "version": "1.2.0",
                    "port": 7777,
                    "replicas": 1
                }
            }
        }
    
    async def run_complete_demo(self):
        """Run complete Phase 2 system demonstration."""
        print("🚀 Runtime State Registry Phase 2 Demo")
        print("=" * 50)
        
        # Step 1: System Initialization
        print("\n📋 Step 1: System Initialization")
        await self._demo_system_initialization()
        
        # Step 2: State Reconciliation
        print("\n🔄 Step 2: Three-Layer State Reconciliation")
        reconciliation_results = await self._demo_state_reconciliation()
        
        # Step 3: Drift Detection
        print("\n🔍 Step 3: Configuration Drift Detection")
        drift_results = await self._demo_drift_detection()
        
        # Step 4: Compliance Monitoring
        print("\n📊 Step 4: Compliance Monitoring")
        compliance_results = await self._demo_compliance_monitoring()
        
        # Step 5: Auto-Remediation
        print("\n🔧 Step 5: Intelligent Auto-Remediation")
        remediation_results = await self._demo_auto_remediation(drift_results)
        
        # Step 6: System Summary
        print("\n📈 Step 6: System Summary & Analytics")
        await self._demo_system_summary(reconciliation_results, drift_results, 
                                       compliance_results, remediation_results)
        
        print("\n✅ Phase 2 Demo Complete!")
        print("=" * 50)
    
    async def _demo_system_initialization(self):
        """Demonstrate system initialization and capabilities."""
        print("Initializing Phase 2 components...")
        
        components = [
            ("State Reconciliation Engine", self.reconciliation_engine),
            ("Drift Detector", self.drift_detector),
            ("Compliance Monitor", self.compliance_monitor),
            ("Auto-Remediation Engine", self.remediation_engine)
        ]
        
        for name, component in components:
            capabilities = component.get_capabilities()
            info = component.get_module_info()
            
            print(f"  ✅ {name}")
            print(f"     Version: {info['version']}")
            print(f"     Status: {info['status']}")
            print(f"     Features: {len(capabilities.get('features', []))}")
        
        print(f"\n📊 Demo Services: {len(self.demo_services)} services configured")
        for service_name, service_data in self.demo_services.items():
            layers = []
            if service_data.get("spec_state"):
                layers.append("Spec")
            if service_data.get("cms_state"):
                layers.append("CMS")
            if service_data.get("runtime_state"):
                layers.append("Runtime")
            
            print(f"  • {service_name}: {' + '.join(layers)} layers")
    
    async def _demo_state_reconciliation(self):
        """Demonstrate three-layer state reconciliation."""
        print("Performing three-layer state reconciliation...")
        
        # Mock the data collection methods
        async def mock_collect_spec_state(service_name):
            return self.demo_services.get(service_name, {}).get("spec_state")
        
        async def mock_collect_cms_state(service_name):
            return self.demo_services.get(service_name, {}).get("cms_state")
        
        async def mock_collect_runtime_state(service_name):
            return self.demo_services.get(service_name, {}).get("runtime_state")
        
        # Patch the methods
        self.reconciliation_engine._collect_spec_state = mock_collect_spec_state
        self.reconciliation_engine._collect_cms_state = mock_collect_cms_state
        self.reconciliation_engine._collect_runtime_state = mock_collect_runtime_state
        
        # Mock service discovery
        async def mock_discover_services():
            return set(self.demo_services.keys())
        
        self.reconciliation_engine._discover_all_services = mock_discover_services
        
        # Perform reconciliation
        results = await self.reconciliation_engine.reconcile_all_services()
        
        print(f"\n🔄 Reconciliation Results ({len(results)} services):")
        for service_name, result in results.items():
            status_icon = "✅" if result.compliance_score >= 0.8 else "⚠️" if result.compliance_score >= 0.5 else "❌"
            print(f"  {status_icon} {service_name}")
            print(f"     Compliance Score: {result.compliance_score:.3f}")
            print(f"     Drift Severity: {result.drift_severity.value}")
            print(f"     Conflicts: {len(result.conflicts_detected)}")
            print(f"     Remediation Actions: {len(result.remediation_actions)}")
        
        # Show compliance summary
        summary = self.reconciliation_engine.get_compliance_summary()
        print(f"\n📊 Overall System Compliance:")
        print(f"  • Status: {summary['status']}")
        print(f"  • Average Compliance: {summary.get('average_compliance', 0):.3f}")
        print(f"  • Trend: {summary.get('compliance_trend', 'unknown')}")
        
        return results
    
    async def _demo_drift_detection(self):
        """Demonstrate configuration drift detection."""
        print("Analyzing configuration drift patterns...")
        
        drift_results = {}
        
        for service_name, service_data in self.demo_services.items():
            result = await self.drift_detector.detect_service_drift(
                service_name=service_name,
                spec_state=service_data.get("spec_state"),
                cms_state=service_data.get("cms_state"),
                runtime_state=service_data.get("runtime_state")
            )
            drift_results[service_name] = result
        
        print(f"\n🔍 Drift Detection Results ({len(drift_results)} services):")
        
        for service_name, result in drift_results.items():
            severity_icon = {
                "low": "🟢",
                "medium": "🟡", 
                "high": "🟠",
                "critical": "🔴"
            }.get(result.drift_severity.value, "⚪")
            
            print(f"  {severity_icon} {service_name}")
            print(f"     Drift Severity: {result.drift_severity.value}")
            print(f"     Detected Drifts: {len(result.detected_drifts)}")
            print(f"     Confidence: {result.confidence_score:.3f}")
            
            if result.orphaned_services:
                print(f"     🏃 Orphaned: {', '.join(result.orphaned_services)}")
            
            if result.missing_services:
                print(f"     ❓ Missing: {', '.join(result.missing_services)}")
            
            if result.drift_categories:
                categories = [cat.value for cat in result.drift_categories]
                print(f"     📂 Categories: {', '.join(categories)}")
        
        # Show drift summary
        summary = self.drift_detector.get_drift_summary()
        if summary.get("status") != "no_data":
            print(f"\n📊 System-Wide Drift Analysis:")
            print(f"  • Total Drifts: {summary.get('total_drifts_detected', 0)}")
            print(f"  • Orphaned Services: {len(summary.get('orphaned_services', []))}")
            print(f"  • Missing Services: {len(summary.get('missing_services', []))}")
            print(f"  • Trend: {summary.get('drift_trend', 'unknown')}")
        
        return drift_results
    
    async def _demo_compliance_monitoring(self):
        """Demonstrate compliance monitoring system."""
        print("Monitoring compliance across all services...")
        
        # Check compliance for all services
        compliance_scores = await self.compliance_monitor.check_compliance(self.demo_services)
        
        print(f"\n📊 Compliance Monitoring Results:")
        for service_name, score in compliance_scores.items():
            status_icon = "✅" if score >= 0.8 else "⚠️" if score >= 0.5 else "❌"
            print(f"  {status_icon} {service_name}: {score:.3f}")
        
        # Generate compliance report
        report = await self.compliance_monitor.generate_compliance_report(reporting_period_hours=1)
        
        print(f"\n📋 Compliance Report:")
        print(f"  • Services Analyzed: {report.services_analyzed}")
        print(f"  • Overall Score: {report.overall_compliance_score:.3f}")
        print(f"  • Compliance Trend: {report.compliance_trend.value}")
        print(f"  • Active Alerts: {len(report.active_alerts)}")
        print(f"  • Recommendations: {len(report.recommendations)}")
        
        # Show recommendations
        if report.recommendations:
            print(f"\n💡 Top Recommendations:")
            for i, rec in enumerate(report.recommendations[:3], 1):
                print(f"  {i}. {rec['title']} (Priority: {rec['priority']})")
                print(f"     {rec['description']}")
        
        # Show active alerts
        alerts = self.compliance_monitor.get_active_alerts()
        if alerts:
            print(f"\n🚨 Active Alerts ({len(alerts)}):")
            for alert in alerts[:3]:  # Show top 3
                severity_icon = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🟢"
                }.get(alert.severity.value, "⚪")
                
                print(f"  {severity_icon} {alert.alert_type}")
                print(f"     Service: {alert.service_name}")
                print(f"     Message: {alert.message}")
        
        return {
            "compliance_scores": compliance_scores,
            "compliance_report": report,
            "active_alerts": alerts
        }
    
    async def _demo_auto_remediation(self, drift_results):
        """Demonstrate intelligent auto-remediation."""
        print("Assessing remediation opportunities...")
        
        remediation_plans = {}
        remediation_executions = {}
        
        for service_name, drift_result in drift_results.items():
            if len(drift_result.detected_drifts) > 0:
                # Assess remediation safety
                plan = await self.remediation_engine.assess_remediation_safety(drift_result)
                remediation_plans[service_name] = plan
                
                print(f"\n🔧 Remediation Plan for {service_name}:")
                print(f"  • Actions: {len(plan.actions)}")
                print(f"  • Overall Safety: {plan.overall_safety.value}")
                print(f"  • Estimated Duration: {plan.estimated_total_duration}s")
                print(f"  • Requires Approval: {plan.requires_approval}")
                
                # Show individual actions
                for action in plan.actions[:3]:  # Show first 3 actions
                    safety_icon = {
                        "safe": "🟢",
                        "cautious": "🟡",
                        "risky": "🟠", 
                        "dangerous": "🔴"
                    }.get(action.safety_level.value, "⚪")
                    
                    print(f"    {safety_icon} {action.action_type.value}")
                    print(f"       Description: {action.description}")
                    print(f"       Impact: {action.estimated_impact}")
                    print(f"       Rollback: {'Yes' if action.rollback_possible else 'No'}")
                
                # Execute safe actions (demo mode - no actual execution)
                if not plan.requires_approval:
                    print(f"  ✅ Auto-executing safe actions...")
                    executions = await self.remediation_engine.execute_remediation_plan(plan)
                    remediation_executions[service_name] = executions
                    
                    for action_id, execution in executions.items():
                        status_icon = {
                            "completed": "✅",
                            "failed": "❌",
                            "pending": "⏳"
                        }.get(execution.status.value, "⚪")
                        
                        print(f"    {status_icon} Action {action_id}: {execution.status.value}")
                else:
                    print(f"  ⏳ Manual approval required for risky actions")
        
        # Show remediation statistics
        stats = self.remediation_engine.get_remediation_statistics()
        if stats.get("total_executions", 0) > 0:
            print(f"\n📊 Remediation Statistics:")
            print(f"  • Total Executions: {stats['total_executions']}")
            print(f"  • Success Rate: {stats['success_rate']:.1%}")
            print(f"  • Average Duration: {stats['average_duration_seconds']:.1f}s")
            print(f"  • Rollback Rate: {stats['rollback_success_rate']:.1%}")
        
        return {
            "remediation_plans": remediation_plans,
            "remediation_executions": remediation_executions,
            "remediation_stats": stats
        }
    
    async def _demo_system_summary(self, reconciliation_results, drift_results, 
                                  compliance_results, remediation_results):
        """Show comprehensive system summary and analytics."""
        print("Generating comprehensive system analytics...")
        
        # Calculate overall metrics
        total_services = len(self.demo_services)
        
        # Compliance metrics
        avg_compliance = sum(r.compliance_score for r in reconciliation_results.values()) / len(reconciliation_results)
        compliant_services = sum(1 for r in reconciliation_results.values() if r.compliance_score >= 0.8)
        
        # Drift metrics
        total_drifts = sum(len(r.detected_drifts) for r in drift_results.values())
        critical_drifts = sum(1 for r in drift_results.values() if r.drift_severity.value == "critical")
        
        # Remediation metrics
        total_plans = len(remediation_results.get("remediation_plans", {}))
        auto_executed = len(remediation_results.get("remediation_executions", {}))
        
        print(f"\n📈 System Health Dashboard:")
        print(f"  🏢 Total Services: {total_services}")
        print(f"  📊 Average Compliance: {avg_compliance:.3f}")
        print(f"  ✅ Compliant Services: {compliant_services}/{total_services} ({compliant_services/total_services:.1%})")
        print(f"  🔍 Total Drifts Detected: {total_drifts}")
        print(f"  🔴 Critical Drifts: {critical_drifts}")
        print(f"  🔧 Remediation Plans: {total_plans}")
        print(f"  ⚡ Auto-Executed: {auto_executed}")
        
        # Service health matrix
        print(f"\n🎯 Service Health Matrix:")
        print("  Service Name          | Compliance | Drift      | Remediation")
        print("  " + "-" * 60)
        
        for service_name in self.demo_services.keys():
            compliance_score = reconciliation_results[service_name].compliance_score
            drift_severity = drift_results[service_name].drift_severity.value
            has_remediation = service_name in remediation_results.get("remediation_plans", {})
            
            compliance_status = "✅" if compliance_score >= 0.8 else "⚠️" if compliance_score >= 0.5 else "❌"
            drift_status = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}.get(drift_severity, "⚪")
            remediation_status = "🔧" if has_remediation else "➖"
            
            print(f"  {service_name:<20} | {compliance_status} {compliance_score:.3f}  | {drift_status} {drift_severity:<8} | {remediation_status}")
        
        # Recommendations summary
        compliance_report = compliance_results.get("compliance_report")
        if compliance_report and compliance_report.recommendations:
            print(f"\n💡 Key Recommendations:")
            for i, rec in enumerate(compliance_report.recommendations[:3], 1):
                priority_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(rec["priority"], "⚪")
                print(f"  {i}. {priority_icon} {rec['title']}")
        
        # System trends
        print(f"\n📈 System Trends:")
        reconciliation_summary = self.reconciliation_engine.get_compliance_summary()
        drift_summary = self.drift_detector.get_drift_summary()
        
        print(f"  • Compliance Trend: {reconciliation_summary.get('compliance_trend', 'unknown')}")
        print(f"  • Drift Trend: {drift_summary.get('drift_trend', 'unknown')}")
        
        # Next steps
        print(f"\n🎯 Recommended Next Steps:")
        if critical_drifts > 0:
            print(f"  1. 🔴 Address {critical_drifts} critical drift(s) immediately")
        if compliant_services < total_services:
            non_compliant = total_services - compliant_services
            print(f"  2. ⚠️ Improve compliance for {non_compliant} service(s)")
        if auto_executed < total_plans:
            manual_plans = total_plans - auto_executed
            print(f"  3. 🔧 Review {manual_plans} manual remediation plan(s)")
        
        print(f"  4. 📊 Continue monitoring for compliance trends")
        print(f"  5. 🔄 Schedule regular reconciliation cycles")


async def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(description="Runtime State Registry Phase 2 Demo")
    parser.add_argument("--component", choices=["reconciliation", "drift", "compliance", "remediation", "all"],
                       default="all", help="Component to demo")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run demo
    demo = RuntimeStateRegistryPhase2Demo()
    
    if args.component == "all":
        await demo.run_complete_demo()
    else:
        # Run specific component demo
        if args.component == "reconciliation":
            await demo._demo_state_reconciliation()
        elif args.component == "drift":
            await demo._demo_drift_detection()
        elif args.component == "compliance":
            await demo._demo_compliance_monitoring()
        elif args.component == "remediation":
            drift_results = await demo._demo_drift_detection()
            await demo._demo_auto_remediation(drift_results)


if __name__ == "__main__":
    asyncio.run(main())