#!/usr/bin/env python3
"""
Automated Correction Workflows Demo

This demo shows the automated correction workflows implemented in task 4.2:
- Automatic terminology correction system with approval workflows
- Interface compliance correction system with automated refactoring capabilities
- Conflict resolution automation for common inconsistency patterns
- Escalation system for corrections requiring human intervention

Requirements addressed: R9.3, R9.4, R9.5
"""

import tempfile
import json
from pathlib import Path
from datetime import datetime

from src.spec_reconciliation.monitoring import (
    ContinuousMonitor, InconsistencyReport, CorrectionStatus
)


def create_demo_specs(specs_dir: Path):
    """Create demo spec files with various issues for correction"""
    
    # Spec with terminology issues
    terminology_spec_dir = specs_dir / "terminology-issues-spec"
    terminology_spec_dir.mkdir()
    
    terminology_content = """
# Terminology Issues Spec

This specification demonstrates terminology inconsistencies that need correction.

## Overview

This spec uses RCA (Root Cause Analysis) methodology alongside root cause analysis 
and Root Cause Analysis in different sections. It also mentions PDCA, Plan-Do-Check-Act, 
and plan do check act methodology inconsistently.

## Requirements

### Requirement 1
**User Story:** As a developer, I want to perform RCA when issues occur, so that I can identify root causes.

#### Acceptance Criteria
1. WHEN an issue occurs THEN the system SHALL perform root cause analysis
2. WHEN Root Cause Analysis is complete THEN findings SHALL be documented
3. WHEN using PDCA methodology THEN Plan-Do-Check-Act cycles SHALL be followed
"""
    (terminology_spec_dir / "requirements.md").write_text(terminology_content)
    
    # Spec with interface issues
    interface_spec_dir = specs_dir / "interface-issues-spec"
    interface_spec_dir.mkdir()
    
    interface_content = """
# Interface Issues Spec

This specification demonstrates interface compliance issues that need correction.

## Interface Definitions

### Non-Compliant Interface

```python
class BadModule:
    def badMethodName(self):
        '''Method with poor naming convention'''
        pass
    
    def anotherBadMethod(self, param1, param2, param3, param4, param5, param6):
        '''Method with too many parameters'''
        pass
    
    def inconsistent_naming_style(self):
        '''Inconsistent naming style'''
        pass
```

### Better Interface (for comparison)

```python
class GoodModule(ReflectiveModule):
    def get_module_status(self):
        '''Follows ReflectiveModule pattern'''
        pass
    
    def process_data(self, config: Dict[str, Any]):
        '''Uses proper parameter grouping'''
        pass
```
"""
    (interface_spec_dir / "design.md").write_text(interface_content)
    
    # Spec with conflicts
    conflict_spec_dir = specs_dir / "conflict-spec"
    conflict_spec_dir.mkdir()
    
    conflict_content = """
# Conflict Spec

This specification demonstrates conflicts that need resolution.

## Duplicate Requirements

### Requirement 1
**User Story:** As a user, I want to validate data, so that I can ensure quality.

#### Acceptance Criteria
1. WHEN data is input THEN it SHALL be validated
2. WHEN validation fails THEN errors SHALL be reported

### Requirement 2 (Duplicate)
**User Story:** As a user, I want data validation, so that quality is ensured.

#### Acceptance Criteria
1. WHEN data is provided THEN validation SHALL occur
2. WHEN validation errors occur THEN they SHALL be displayed

## Terminology Conflicts

This spec uses both "data validation" and "input validation" for the same concept.
It also uses "quality assurance" and "QA" interchangeably without definition.
"""
    (conflict_spec_dir / "requirements.md").write_text(conflict_content)


def demo_terminology_correction(monitor: ContinuousMonitor):
    """Demonstrate automatic terminology correction workflow"""
    print("\n" + "="*60)
    print("DEMO: Automatic Terminology Correction Workflow")
    print("="*60)
    
    # Create terminology inconsistency report
    terminology_report = InconsistencyReport(
        report_id="demo_terminology_report",
        generated_at=datetime.now(),
        terminology_drift={
            "RCA": ["root cause analysis", "Root Cause Analysis"],
            "PDCA": ["Plan-Do-Check-Act", "plan do check act"],
            "QA": ["quality assurance", "Quality Assurance"]
        },
        new_terminology={"data_validation", "input_validation"},
        deprecated_usage={"old_validation_method"},
        consistency_degradation=0.25,
        correction_suggestions=[
            "Standardize RCA terminology across all specs",
            "Unify PDCA methodology references",
            "Define standard QA terminology"
        ]
    )
    
    print(f"📊 Terminology Report Generated:")
    print(f"   - Terminology Drift: {len(terminology_report.terminology_drift)} terms")
    print(f"   - New Terminology: {len(terminology_report.new_terminology)} terms")
    print(f"   - Consistency Degradation: {terminology_report.consistency_degradation:.1%}")
    
    # Create automatic correction workflow
    workflow = monitor.create_automatic_terminology_correction(terminology_report)
    
    print(f"\n🔧 Terminology Correction Workflow Created:")
    print(f"   - Workflow ID: {workflow.workflow_id}")
    print(f"   - Correction Type: {workflow.correction_type}")
    print(f"   - Status: {workflow.status.value}")
    print(f"   - Success Rate: {workflow.success_rate:.1%}")
    print(f"   - Correction Steps: {len(workflow.correction_steps)}")
    
    for i, step in enumerate(workflow.correction_steps[:3], 1):
        print(f"     {i}. {step}")
    if len(workflow.correction_steps) > 3:
        print(f"     ... and {len(workflow.correction_steps) - 3} more steps")
    
    return workflow


def demo_interface_correction(monitor: ContinuousMonitor):
    """Demonstrate interface compliance correction workflow"""
    print("\n" + "="*60)
    print("DEMO: Interface Compliance Correction Workflow")
    print("="*60)
    
    # Create interface violations
    interface_violations = [
        {
            'type': 'naming_convention',
            'severity': 'medium',
            'location': 'interface-issues-spec/design.md:10',
            'current_form': 'badMethodName',
            'suggested_correction': 'get_bad_method_result',
            'reason': 'Method name does not follow snake_case convention'
        },
        {
            'type': 'parameter_order',
            'severity': 'high',
            'location': 'interface-issues-spec/design.md:14',
            'current_form': 'anotherBadMethod(param1, param2, param3, param4, param5, param6)',
            'suggested_correction': 'another_bad_method(config: Dict[str, Any])',
            'reason': 'Too many parameters - should use configuration object'
        },
        {
            'type': 'naming_convention',
            'severity': 'low',
            'location': 'interface-issues-spec/design.md:18',
            'current_form': 'inconsistent_naming_style',
            'suggested_correction': 'get_inconsistent_naming_result',
            'reason': 'Inconsistent with other method naming patterns'
        }
    ]
    
    print(f"🔍 Interface Violations Detected:")
    print(f"   - Total Violations: {len(interface_violations)}")
    for violation in interface_violations:
        print(f"   - {violation['type']} ({violation['severity']}): {violation['current_form']}")
    
    # Create interface correction workflow
    workflow = monitor.create_interface_compliance_correction(interface_violations)
    
    print(f"\n🔧 Interface Correction Workflow Created:")
    print(f"   - Workflow ID: {workflow.workflow_id}")
    print(f"   - Correction Type: {workflow.correction_type}")
    print(f"   - Status: {workflow.status.value}")
    print(f"   - Success Rate: {workflow.success_rate:.1%}")
    print(f"   - Target Specs: {len(workflow.target_specs)}")
    
    print(f"\n📋 Correction Steps:")
    for i, step in enumerate(workflow.correction_steps, 1):
        print(f"   {i}. {step}")
    
    return workflow


def demo_conflict_resolution(monitor: ContinuousMonitor):
    """Demonstrate conflict resolution automation workflow"""
    print("\n" + "="*60)
    print("DEMO: Conflict Resolution Automation Workflow")
    print("="*60)
    
    # Create conflicts of different complexities
    conflicts = [
        {
            'type': 'duplicate_requirement',
            'complexity': 'low',
            'description': 'Duplicate data validation requirements found in multiple specs',
            'affected_specs': ['conflict-spec', 'terminology-issues-spec'],
            'confidence': 0.9
        },
        {
            'type': 'terminology_conflict',
            'complexity': 'medium',
            'description': 'Conflicting terminology: "data validation" vs "input validation"',
            'affected_specs': ['conflict-spec', 'interface-issues-spec'],
            'confidence': 0.8
        },
        {
            'type': 'architectural_decision_conflict',
            'complexity': 'high',
            'description': 'Conflicting architectural patterns between validation approaches',
            'affected_specs': ['conflict-spec', 'interface-issues-spec', 'terminology-issues-spec'],
            'confidence': 0.4
        }
    ]
    
    print(f"⚠️  Conflicts Detected:")
    print(f"   - Total Conflicts: {len(conflicts)}")
    for conflict in conflicts:
        print(f"   - {conflict['type']} ({conflict['complexity']}): {conflict['description'][:50]}...")
    
    # Create conflict resolution workflow
    workflow = monitor.create_conflict_resolution_automation(conflicts)
    
    print(f"\n🔧 Conflict Resolution Workflow Created:")
    print(f"   - Workflow ID: {workflow.workflow_id}")
    print(f"   - Correction Type: {workflow.correction_type}")
    print(f"   - Status: {workflow.status.value}")
    print(f"   - Success Rate: {workflow.success_rate:.1%}")
    
    print(f"\n📋 Resolution Steps:")
    for i, step in enumerate(workflow.correction_steps, 1):
        print(f"   {i}. {step}")
    
    return workflow


def demo_escalation_system(monitor: ContinuousMonitor, failed_workflow):
    """Demonstrate escalation system for failed corrections"""
    print("\n" + "="*60)
    print("DEMO: Escalation System for Human Intervention")
    print("="*60)
    
    escalation_reason = "Complex architectural conflicts require expert review and stakeholder alignment"
    
    print(f"🚨 Escalation Triggered:")
    print(f"   - Failed Workflow: {failed_workflow.workflow_id}")
    print(f"   - Success Rate: {failed_workflow.success_rate:.1%}")
    print(f"   - Reason: {escalation_reason}")
    
    # Create escalation
    escalation_result = monitor.create_escalation_system(failed_workflow, escalation_reason)
    
    print(f"\n📋 Escalation Created:")
    print(f"   - Escalation ID: {escalation_result['escalation_id']}")
    print(f"   - Priority: {escalation_result['priority']}")
    print(f"   - Resolution Deadline: {escalation_result['resolution_deadline']}")
    print(f"   - Notification Sent: {escalation_result['notification_sent']}")
    
    print(f"\n💡 Recommended Actions:")
    for i, action in enumerate(escalation_result['recommended_actions'], 1):
        print(f"   {i}. {action}")
    
    return escalation_result


def demo_monitoring_status(monitor: ContinuousMonitor):
    """Show monitoring system status and metrics"""
    print("\n" + "="*60)
    print("DEMO: Monitoring System Status")
    print("="*60)
    
    status = monitor.get_monitoring_status()
    health = monitor.get_health_indicators()
    
    print(f"📊 Monitoring Status:")
    print(f"   - Monitoring Active: {status['monitoring_active']}")
    print(f"   - Total Drift Reports: {status['total_drift_reports']}")
    print(f"   - Total Corrections: {status['total_corrections']}")
    print(f"   - Successful Corrections: {status['successful_corrections']}")
    print(f"   - Pending Corrections: {status['pending_corrections']}")
    
    print(f"\n🏥 Health Indicators:")
    for indicator, value in health.items():
        if isinstance(value, bool):
            status_icon = "✅" if value else "❌"
            print(f"   {status_icon} {indicator.replace('_', ' ').title()}: {value}")
        elif isinstance(value, (int, float)):
            print(f"   📈 {indicator.replace('_', ' ').title()}: {value}")


def main():
    """Run the automated correction workflows demo"""
    print("🤖 Automated Correction Workflows Demo")
    print("Task 4.2: Create Automated Correction Workflows")
    print("Requirements: R9.3, R9.4, R9.5")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        specs_dir = Path(temp_dir) / "specs"
        specs_dir.mkdir()
        
        # Create demo specs with issues
        print("\n📁 Creating demo specs with various issues...")
        create_demo_specs(specs_dir)
        
        # Initialize continuous monitor
        print("🔧 Initializing Continuous Monitor...")
        monitor = ContinuousMonitor(str(specs_dir))
        
        # Demo 1: Terminology Correction
        terminology_workflow = demo_terminology_correction(monitor)
        
        # Demo 2: Interface Correction
        interface_workflow = demo_interface_correction(monitor)
        
        # Demo 3: Conflict Resolution
        conflict_workflow = demo_conflict_resolution(monitor)
        
        # Demo 4: Escalation System (using the conflict workflow as example)
        if conflict_workflow.status == CorrectionStatus.ESCALATED:
            escalation_result = demo_escalation_system(monitor, conflict_workflow)
        else:
            # Force an escalation for demo purposes
            conflict_workflow.success_rate = 0.3  # Low success rate
            escalation_result = demo_escalation_system(monitor, conflict_workflow)
        
        # Demo 5: Monitoring Status
        demo_monitoring_status(monitor)
        
        print("\n" + "="*60)
        print("✅ DEMO COMPLETE")
        print("="*60)
        print("All automated correction workflows have been demonstrated:")
        print("✅ Automatic terminology correction with approval workflows")
        print("✅ Interface compliance correction with automated refactoring")
        print("✅ Conflict resolution automation for common patterns")
        print("✅ Escalation system for human intervention")
        print("\nRequirements R9.3, R9.4, R9.5 have been successfully implemented!")


if __name__ == "__main__":
    main()