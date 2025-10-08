#!/usr/bin/env python3
"""
Demo script for Technical Debt Patch Annotation Reporting and Dashboard System

This script demonstrates the comprehensive reporting capabilities including
inventory reports, trend analysis, and executive dashboards with real sample data.

Requirements demonstrated: 8.1, 8.2, 8.3, 8.4, 8.5
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from ..core.models import PatchAnnotation, DebtLevel, BypassType
from .dashboard import (
    PatchDashboard, ReportGenerator, ReportFormat, TimeRange,
    InventoryReport, TrendAnalysis, ExecutiveDashboard
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_sample_patches() -> List[PatchAnnotation]:
    """Create sample patch data for demonstration."""
    patches = []
    
    # Create patches with various characteristics
    patch_data = [
        {
            'reason': 'Temporary workaround for API rate limiting',
            'upstream_issue': 'API-ISSUE-456',
            'cleanup_task': 'Replace with proper retry mechanism when API v2 available',
            'debt_level': DebtLevel.MEDIUM,
            'bypass_type': BypassType.INTEGRATION,
            'component': 'data_processor',
            'created_date': datetime.now() - timedelta(days=15),
            'expected_resolution': datetime.now() + timedelta(days=30),
            'validation_criteria': ['API v2 integration tests pass', 'Rate limiting removed']
        },
        {
            'reason': 'Security bypass for legacy authentication system',
            'upstream_issue': 'SEC-789',
            'cleanup_task': 'Implement proper OAuth2 flow',
            'debt_level': DebtLevel.CRITICAL,
            'bypass_type': BypassType.SECURITY,
            'component': 'auth_service',
            'created_date': datetime.now() - timedelta(days=45),
            'expected_resolution': datetime.now() - timedelta(days=5),  # Overdue
            'validation_criteria': ['OAuth2 tests pass', 'Security audit approval']
        },
        {
            'reason': 'Performance optimization for large datasets',
            'upstream_issue': 'PERF-123',
            'cleanup_task': 'Implement proper pagination and caching',
            'debt_level': DebtLevel.HIGH,
            'bypass_type': BypassType.PERFORMANCE,
            'component': 'data_processor',
            'created_date': datetime.now() - timedelta(days=30),
            'expected_resolution': datetime.now() + timedelta(days=14),
            'validation_criteria': ['Performance benchmarks meet SLA', 'Memory usage optimized']
        },
        {
            'reason': 'Compliance workaround for GDPR requirements',
            'upstream_issue': 'COMP-456',
            'cleanup_task': 'Implement proper data anonymization',
            'debt_level': DebtLevel.HIGH,
            'bypass_type': BypassType.COMPLIANCE,
            'component': 'user_service',
            'created_date': datetime.now() - timedelta(days=60),
            'expected_resolution': datetime.now() + timedelta(days=7),
            'validation_criteria': ['GDPR compliance verified', 'Legal team approval']
        },
        {
            'reason': 'Architecture bypass for microservice communication',
            'upstream_issue': 'ARCH-789',
            'cleanup_task': 'Implement proper service mesh communication',
            'debt_level': DebtLevel.MEDIUM,
            'bypass_type': BypassType.ARCHITECTURE,
            'component': 'api_gateway',
            'created_date': datetime.now() - timedelta(days=20),
            'expected_resolution': datetime.now() + timedelta(days=45),
            'validation_criteria': ['Service mesh tests pass', 'Circuit breaker functional']
        },
        {
            'reason': 'Quick fix for database connection pooling',
            'upstream_issue': 'DB-321',
            'cleanup_task': 'Implement proper connection pool management',
            'debt_level': DebtLevel.LOW,
            'bypass_type': BypassType.PERFORMANCE,
            'component': 'database_layer',
            'created_date': datetime.now() - timedelta(days=10),
            'expected_resolution': datetime.now() + timedelta(days=60),
            'validation_criteria': ['Connection pool metrics stable', 'No connection leaks']
        },
        {
            'reason': 'Integration patch for third-party service',
            'upstream_issue': 'INT-654',
            'cleanup_task': 'Update to latest API version',
            'debt_level': DebtLevel.MEDIUM,
            'bypass_type': BypassType.INTEGRATION,
            'component': 'payment_service',
            'created_date': datetime.now() - timedelta(days=25),
            'expected_resolution': datetime.now() + timedelta(days=21),
            'validation_criteria': ['API v3 integration complete', 'Payment tests pass']
        },
        {
            'reason': 'Critical security patch for input validation',
            'upstream_issue': 'SEC-999',
            'cleanup_task': 'Implement comprehensive input sanitization',
            'debt_level': DebtLevel.CRITICAL,
            'bypass_type': BypassType.SECURITY,
            'component': 'api_gateway',
            'created_date': datetime.now() - timedelta(days=5),
            'expected_resolution': datetime.now() + timedelta(days=3),
            'validation_criteria': ['Security scan passes', 'Penetration test approval']
        }
    ]
    
    for i, data in enumerate(patch_data):
        patch = PatchAnnotation(
            reason=data['reason'],
            upstream_issue=data['upstream_issue'],
            cleanup_task=data['cleanup_task'],
            debt_level=data['debt_level'],
            bypass_type=data['bypass_type'],
            component=data['component'],
            created_date=data['created_date'],
            expected_resolution=data['expected_resolution'],
            validation_criteria=data['validation_criteria'],
            file_path=f"src/{data['component']}/main.py",
            line_start=100 + i * 10,
            line_end=110 + i * 10,
            created_by=f"developer_{i % 3 + 1}",
            assigned_to=f"team_lead_{i % 2 + 1}"
        )
        patches.append(patch)
    
    return patches


def demo_inventory_report(generator: ReportGenerator, patches: List[PatchAnnotation]):
    """Demonstrate inventory report generation."""
    logger.info("=== INVENTORY REPORT DEMO ===")
    
    # Generate inventory report
    inventory = generator.generate_inventory_report(
        patches=patches,
        include_recommendations=True
    )
    
    # Display key metrics
    print(f"\n📊 INVENTORY REPORT SUMMARY")
    print(f"Report ID: {inventory.report_id}")
    print(f"Total Patches: {inventory.total_patches}")
    print(f"Generated At: {inventory.generated_at}")
    
    print(f"\n🔍 SEVERITY DISTRIBUTION:")
    for severity, count in inventory.severity_distribution.items():
        print(f"  {severity}: {count} patches")
    
    print(f"\n🏗️ TOP COMPONENTS BY DEBT:")
    for component, debt_score in inventory.top_components_by_debt[:5]:
        print(f"  {component}: {debt_score:.1f} debt score")
    
    print(f"\n⚠️ OVERDUE PATCHES: {len(inventory.overdue_patches)}")
    for patch in inventory.overdue_patches:
        days_overdue = (datetime.now() - patch.expected_resolution).days
        print(f"  {patch.patch_id}: {days_overdue} days overdue ({patch.component})")
    
    print(f"\n📈 AGING ANALYSIS:")
    aging = inventory.aging_analysis
    print(f"  Average Age: {aging['average_age_days']:.1f} days")
    print(f"  Oldest Patch: {aging['oldest_patch_days']} days")
    print(f"  Age Distribution: {aging['age_distribution']}")
    
    print(f"\n💡 RECOMMENDATIONS:")
    for i, rec in enumerate(inventory.recommendations, 1):
        print(f"  {i}. {rec}")
    
    # Export report
    json_path = generator.export_report(inventory, ReportFormat.JSON)
    html_path = generator.export_report(inventory, ReportFormat.HTML)
    print(f"\n📁 Reports exported to:")
    print(f"  JSON: {json_path}")
    print(f"  HTML: {html_path}")


def demo_trend_analysis(generator: ReportGenerator, patches: List[PatchAnnotation]):
    """Demonstrate trend analysis generation."""
    logger.info("=== TREND ANALYSIS DEMO ===")
    
    # Generate trend analysis
    trends = generator.generate_trend_analysis(
        patches=patches,
        time_range=TimeRange.LAST_30_DAYS,
        include_projections=True
    )
    
    # Display key metrics
    print(f"\n📈 TREND ANALYSIS SUMMARY")
    print(f"Report ID: {trends.report_id}")
    print(f"Time Range: {trends.time_range.value}")
    print(f"Data Points: {len(trends.data_points)}")
    
    print(f"\n📊 TREND ANALYSIS:")
    print(f"  Creation Trend: {trends.creation_trend}")
    print(f"  Resolution Trend: {trends.resolution_trend}")
    print(f"  Net Debt Trend: {trends.net_debt_trend}")
    
    print(f"\n🔍 KEY INSIGHTS:")
    for i, insight in enumerate(trends.key_insights, 1):
        print(f"  {i}. {insight}")
    
    print(f"\n📊 PERFORMANCE METRICS:")
    for metric, value in trends.performance_metrics.items():
        print(f"  {metric}: {value}")
    
    if trends.projections:
        print(f"\n🔮 PROJECTIONS:")
        for key, value in trends.projections.items():
            print(f"  {key}: {value}")
    
    print(f"\n💡 RECOMMENDATIONS:")
    for i, rec in enumerate(trends.recommendations, 1):
        print(f"  {i}. {rec}")


def demo_executive_dashboard(generator: ReportGenerator, patches: List[PatchAnnotation]):
    """Demonstrate executive dashboard generation."""
    logger.info("=== EXECUTIVE DASHBOARD DEMO ===")
    
    # Generate executive dashboard
    cleanup_data = {
        'completed_tasks': 12,
        'total_tasks': 25,
        'in_progress_tasks': 8,
        'blocked_tasks': 2
    }
    
    executive = generator.generate_executive_dashboard(
        patches=patches,
        cleanup_data=cleanup_data
    )
    
    # Display key metrics
    print(f"\n🎯 EXECUTIVE DASHBOARD SUMMARY")
    print(f"Report ID: {executive.report_id}")
    print(f"System Health Score: {executive.system_health_score:.1f}/100")
    print(f"Total Technical Debt: {executive.total_technical_debt:.1f}")
    print(f"Debt Trend: {executive.debt_trend}")
    
    print(f"\n🚨 CRITICAL ISSUES:")
    for i, issue in enumerate(executive.critical_issues, 1):
        print(f"  {i}. {issue}")
    
    print(f"\n🎯 TOP PRIORITIES:")
    for i, priority in enumerate(executive.top_priorities, 1):
        print(f"  {i}. {priority}")
    
    print(f"\n📊 CLEANUP PROGRESS:")
    progress = executive.cleanup_progress
    print(f"  Total Tasks: {progress.total_cleanup_tasks}")
    print(f"  Completed: {progress.completed_tasks}")
    print(f"  In Progress: {progress.in_progress_tasks}")
    print(f"  Blocked: {progress.blocked_tasks}")
    print(f"  Completion: {progress.completion_percentage:.1f}%")
    
    print(f"\n💰 ROI METRICS:")
    for metric, value in executive.roi_metrics.items():
        if isinstance(value, float) and value > 1000:
            print(f"  {metric}: ${value:,.0f}")
        else:
            print(f"  {metric}: {value}")
    
    print(f"\n🎯 ACTIONABLE INSIGHTS:")
    for i, insight in enumerate(executive.actionable_insights, 1):
        print(f"  {i}. {insight['title']}: {insight['description']}")
        print(f"     Impact: {insight['impact']}, Effort: {insight['effort']}, Timeline: {insight['timeline']}")
    
    print(f"\n📅 NEXT REVIEW: {executive.next_review_date}")


def demo_dashboard_metrics(generator: ReportGenerator, patches: List[PatchAnnotation]):
    """Demonstrate dashboard metrics."""
    logger.info("=== DASHBOARD METRICS DEMO ===")
    
    # Get dashboard metrics
    metrics = generator.get_dashboard_metrics(patches)
    
    print(f"\n📊 REAL-TIME DASHBOARD METRICS")
    print(f"Total Patches: {metrics.total_patches}")
    print(f"Critical Patches: {metrics.critical_patches}")
    print(f"Overdue Patches: {metrics.overdue_patches}")
    print(f"Patches Resolved This Month: {metrics.patches_resolved_this_month}")
    print(f"Average Resolution Time: {metrics.average_resolution_time_days:.1f} days")
    print(f"Debt Score Trend: {metrics.debt_score_trend:+.1f}%")
    print(f"Cleanup Velocity: {metrics.cleanup_velocity:.1f} patches/week")
    print(f"System Health Score: {metrics.system_health_score:.1f}/100")
    
    print(f"\n🎯 TOP RISK COMPONENTS:")
    for i, component in enumerate(metrics.top_risk_components, 1):
        print(f"  {i}. {component}")
    
    print(f"\n📅 UPCOMING DEADLINES:")
    for patch_id, deadline in metrics.upcoming_deadlines:
        days_until = (deadline - datetime.now()).days
        print(f"  {patch_id}: {days_until} days ({deadline.strftime('%Y-%m-%d')})")


def demo_comprehensive_dashboard(dashboard: PatchDashboard, patches: List[PatchAnnotation]):
    """Demonstrate comprehensive dashboard functionality."""
    logger.info("=== COMPREHENSIVE DASHBOARD DEMO ===")
    
    # Generate comprehensive report
    comprehensive = dashboard.generate_comprehensive_report(
        patches=patches,
        include_trends=True,
        include_executive_summary=True
    )
    
    print(f"\n🎯 COMPREHENSIVE DASHBOARD REPORT")
    print(f"Report ID: {comprehensive['report_id']}")
    print(f"Generated At: {comprehensive['generated_at']}")
    
    print(f"\n📊 SUMMARY:")
    summary = comprehensive['summary']
    print(f"  Total Patches: {summary['total_patches']}")
    print(f"  System Health Score: {summary['system_health_score']:.1f}/100")
    print(f"  Critical Issues: {summary['critical_issues_count']}")
    
    print(f"\n💡 CLEANUP RECOMMENDATIONS:")
    for i, rec in enumerate(summary['cleanup_recommendations'], 1):
        print(f"  {i}. {rec}")
    
    # Export comprehensive report
    export_path = dashboard.export_dashboard_report(
        comprehensive, 
        ReportFormat.JSON,
        "comprehensive_dashboard_report.json"
    )
    print(f"\n📁 Comprehensive report exported to: {export_path}")


def main():
    """Main demo function."""
    logger.info("Starting Technical Debt Patch Annotation Reporting Demo")
    
    try:
        # Create sample data
        patches = create_sample_patches()
        logger.info(f"Created {len(patches)} sample patches for demonstration")
        
        # Initialize reporting components
        config = {
            'report_storage_path': 'demo_reports',
            'cache_ttl_minutes': 30,
            'auto_refresh_enabled': True
        }
        
        generator = ReportGenerator(config)
        dashboard = PatchDashboard(config)
        
        # Demonstrate each reporting capability
        demo_inventory_report(generator, patches)
        print("\n" + "="*80)
        
        demo_trend_analysis(generator, patches)
        print("\n" + "="*80)
        
        demo_executive_dashboard(generator, patches)
        print("\n" + "="*80)
        
        demo_dashboard_metrics(generator, patches)
        print("\n" + "="*80)
        
        demo_comprehensive_dashboard(dashboard, patches)
        print("\n" + "="*80)
        
        # Show health status
        print(f"\n🏥 SYSTEM HEALTH STATUS")
        generator_health = generator.get_health_status()
        dashboard_health = dashboard.get_health_status()
        
        print(f"Report Generator: {generator_health.status.value} (Score: {generator_health.health_score:.2f})")
        print(f"Dashboard System: {dashboard_health.status.value} (Score: {dashboard_health.health_score:.2f})")
        
        if generator_health.issues:
            print(f"Generator Issues: {generator_health.issues}")
        if dashboard_health.issues:
            print(f"Dashboard Issues: {dashboard_health.issues}")
        
        logger.info("Demo completed successfully!")
        print(f"\n✅ Technical Debt Patch Annotation Reporting Demo completed successfully!")
        print(f"📁 Check the 'demo_reports' directory for generated report files.")
        
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}")
        print(f"\n❌ Demo failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()