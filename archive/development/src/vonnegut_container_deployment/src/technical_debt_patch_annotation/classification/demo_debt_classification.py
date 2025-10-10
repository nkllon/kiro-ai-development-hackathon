#!/usr/bin/env python3
"""
Demo script for Technical Debt Classification System

This script demonstrates the debt classification and impact assessment
capabilities with sample patch data.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.technical_debt_patch_annotation.core.models import (
    PatchAnnotation, DebtLevel, BypassType
)
from src.technical_debt_patch_annotation.classification.debt_classifier import (
    DebtClassifier, ImpactAssessmentEngine
)


def create_sample_patches() -> list[PatchAnnotation]:
    """Create sample patches for demonstration."""
    patches = []
    
    # Critical security patch
    patches.append(PatchAnnotation(
        patch_id="PATCH-SEC001",
        reason="Temporary bypass of authentication for emergency access",
        upstream_issue="SEC-2024-001",
        cleanup_task="Implement proper emergency access protocol",
        debt_level=DebtLevel.CRITICAL,
        bypass_type=BypassType.SECURITY,
        component="authentication_service",
        expected_resolution=datetime.now() - timedelta(days=5),  # Overdue
        validation_criteria=["Emergency access protocol implemented", "Security audit passed"],
        created_by="security_team",
        assigned_to="backend_team"
    ))
    
    # High priority architecture patch
    patches.append(PatchAnnotation(
        patch_id="PATCH-ARCH001",
        reason="Direct database access bypassing ORM for performance",
        upstream_issue="PERF-2024-015",
        cleanup_task="Optimize ORM queries and remove direct SQL",
        debt_level=DebtLevel.HIGH,
        bypass_type=BypassType.ARCHITECTURE,
        component="data_processor",
        expected_resolution=datetime.now() + timedelta(days=14),
        validation_criteria=["ORM performance meets requirements", "Direct SQL removed"],
        created_by="performance_team",
        assigned_to="data_team"
    ))
    
    # Multiple medium patches in same component
    for i in range(3):
        patches.append(PatchAnnotation(
            patch_id=f"PATCH-API{i:03d}",
            reason=f"Hardcoded timeout for external service {i+1}",
            upstream_issue=f"EXT-2024-{i+10:03d}",
            cleanup_task=f"Implement configurable timeout for service {i+1}",
            debt_level=DebtLevel.MEDIUM,
            bypass_type=BypassType.INTEGRATION,
            component="api_gateway",
            expected_resolution=datetime.now() + timedelta(days=30),
            validation_criteria=[f"Service {i+1} timeout configurable", "Integration tests pass"],
            created_by="integration_team",
            assigned_to="api_team"
        ))
    
    # Performance patches
    patches.append(PatchAnnotation(
        patch_id="PATCH-PERF001",
        reason="Disabled caching for debugging, forgot to re-enable",
        upstream_issue="DEBUG-2024-008",
        cleanup_task="Re-enable caching with proper debug flags",
        debt_level=DebtLevel.HIGH,
        bypass_type=BypassType.PERFORMANCE,
        component="cache_manager",
        expected_resolution=datetime.now() + timedelta(days=7),
        validation_criteria=["Caching re-enabled", "Performance benchmarks met"],
        created_by="debug_team",
        assigned_to="performance_team"
    ))
    
    # Low priority utility patches
    for i in range(2):
        patches.append(PatchAnnotation(
            patch_id=f"PATCH-UTIL{i:03d}",
            reason=f"Temporary logging configuration {i+1}",
            upstream_issue=f"LOG-2024-{i+5:03d}",
            cleanup_task=f"Implement proper logging config {i+1}",
            debt_level=DebtLevel.LOW,
            bypass_type=BypassType.ARCHITECTURE,  # Using ARCHITECTURE instead of CONFIGURATION
            component="logging_utility",
            expected_resolution=datetime.now() + timedelta(days=60),
            validation_criteria=[f"Logging config {i+1} properly structured"],
            created_by="ops_team",
            assigned_to="utility_team"
        ))
    
    # Compliance patch
    patches.append(PatchAnnotation(
        patch_id="PATCH-COMP001",
        reason="Temporary data retention bypass for migration",
        upstream_issue="COMP-2024-012",
        cleanup_task="Implement compliant data retention policy",
        debt_level=DebtLevel.CRITICAL,
        bypass_type=BypassType.COMPLIANCE,
        component="data_retention_service",
        expected_resolution=datetime.now() + timedelta(days=3),
        validation_criteria=["Compliant retention policy active", "Audit requirements met"],
        created_by="compliance_team",
        assigned_to="data_team"
    ))
    
    return patches


def demonstrate_classification():
    """Demonstrate the debt classification system."""
    print("=== Technical Debt Classification Demo ===\n")
    
    # Create sample patches
    patches = create_sample_patches()
    print(f"Created {len(patches)} sample patches for analysis\n")
    
    # Initialize classifier
    config = {
        'alert_thresholds': {
            'component_debt_score': 10.0,  # Lower threshold for demo
            'critical_patch_count': 1,
            'total_patch_count': 5,
            'overdue_patch_count': 1,
            'maintenance_burden_score': 15.0
        },
        'notifications_enabled': True,
        'notification_channels': ['log']
    }
    
    classifier = DebtClassifier(config)
    
    # Perform classification
    print("Performing debt classification analysis...")
    results = classifier.classify_patches(patches)
    
    # Display results
    print("\n=== CLASSIFICATION RESULTS ===")
    print(f"Risk Level: {results['risk_assessment']['risk_level'].upper()}")
    print(f"Total Patches: {results['summary']['total_patches']}")
    print(f"Total Debt Score: {results['summary']['total_debt_score']:.1f}")
    print(f"Hotspots Detected: {results['summary']['hotspots_detected']}")
    print(f"New Alerts: {results['summary']['new_alerts']}")
    
    print("\n=== COMPONENT IMPACT ANALYSIS ===")
    for component, impact in results['component_impacts'].items():
        print(f"\nComponent: {component}")
        print(f"  Patches: {impact['patch_count']}")
        print(f"  Debt Score: {impact['debt_score']:.1f}")
        print(f"  Risk Factors: {', '.join(impact['risk_factors'])}")
        print(f"  Recommendations: {'; '.join(impact['recommendations'])}")
    
    print("\n=== DEBT HOTSPOTS ===")
    for hotspot in results['debt_hotspots']:
        print(f"\nHotspot: {hotspot['component']} ({hotspot['type']})")
        print(f"  Severity: {hotspot['severity']:.1f}")
        print(f"  Priority: {hotspot['priority']}")
        print(f"  Description: {hotspot['description']}")
    
    print("\n=== RISK ASSESSMENT ===")
    risk = results['risk_assessment']
    print(f"Risk Level: {risk['risk_level']}")
    print(f"Top Risk Factors:")
    for factor in risk['top_risk_factors']:
        print(f"  - {factor}")
    print(f"Components at Risk: {', '.join(risk['components_at_risk'])}")
    print(f"Cleanup Timeline: {risk['cleanup_timeline']}")
    
    print("\n=== MAINTENANCE ANALYSIS ===")
    maintenance = results['maintenance_analysis']
    print(f"Total Burden Score: {maintenance['total_burden_score']:.1f}")
    print(f"Average Daily Cost: {maintenance['average_daily_cost']:.2f}")
    print(f"High Burden Patches: {', '.join(maintenance['high_burden_patches'])}")
    
    print("\n=== ACTIVE ALERTS ===")
    for alert in results['alerts']:
        print(f"\n{alert['severity'].upper()} Alert - {alert['component']}")
        print(f"  Message: {alert['message']}")
        print(f"  Actions: {'; '.join(alert['actions'])}")
    
    # Demonstrate individual component analysis
    print("\n=== DETAILED COMPONENT ANALYSIS ===")
    impact_engine = ImpactAssessmentEngine()
    
    # Analyze API gateway component specifically
    api_patches = [p for p in patches if p.component == "api_gateway"]
    if api_patches:
        api_impact = impact_engine.assess_component_impact("api_gateway", api_patches)
        print(f"\nAPI Gateway Detailed Analysis:")
        print(f"  Component Type: {api_impact.component_type.value}")
        print(f"  Patch Distribution: Critical={api_impact.critical_patches}, High={api_impact.high_patches}, Medium={api_impact.medium_patches}, Low={api_impact.low_patches}")
        print(f"  Maintenance Burden: {api_impact.maintenance_burden_score:.1f}")
        print(f"  Risk Factors: {', '.join(api_impact.risk_factors)}")
    
    # Demonstrate maintenance burden calculation
    print("\n=== MAINTENANCE BURDEN ANALYSIS ===")
    for patch in patches[:3]:  # Show first 3 patches
        burden = impact_engine.calculate_maintenance_burden(patch)
        print(f"\nPatch {patch.patch_id}:")
        print(f"  Burden Category: {burden.burden_category}")
        print(f"  Daily Cost: {burden.daily_maintenance_cost:.2f}")
        print(f"  Total Burden Score: {burden.total_burden_score:.1f}")
        print(f"  Complexity Factor: {burden.complexity_factor:.2f}")
    
    # Show alert management
    print("\n=== ALERT MANAGEMENT ===")
    active_alerts = classifier.get_active_alerts()
    print(f"Total Active Alerts: {len(active_alerts)}")
    
    if active_alerts:
        # Acknowledge first alert
        first_alert = active_alerts[0]
        print(f"Acknowledging alert: {first_alert.alert_id}")
        classifier.acknowledge_alert(first_alert.alert_id)
        
        # Clear acknowledged alerts
        cleared = classifier.clear_acknowledged_alerts()
        print(f"Cleared {cleared} acknowledged alerts")
        print(f"Remaining active alerts: {len(classifier.get_active_alerts())}")
    
    print("\n=== DEMO COMPLETE ===")
    print("The debt classification system successfully:")
    print("✓ Analyzed patch severity and impact")
    print("✓ Identified debt hotspots")
    print("✓ Generated risk assessment")
    print("✓ Calculated maintenance burden")
    print("✓ Triggered threshold-based alerts")
    print("✓ Provided actionable recommendations")


if __name__ == "__main__":
    try:
        demonstrate_classification()
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)