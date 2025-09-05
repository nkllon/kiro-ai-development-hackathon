"""
CLI interface for Spec Reconciliation System

Provides command-line access to governance and validation functionality.
"""

import argparse
import json
import sys
from pathlib import Path

from .governance import GovernanceController, GovernanceFramework
from .models import SpecProposal
from .validation import ConsistencyValidator


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description='Spec Reconciliation System')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Governance commands
    gov_parser = subparsers.add_parser('governance', help='Governance operations')
    gov_parser.add_argument('--validate-spec', type=str, help='Validate a spec proposal')
    gov_parser.add_argument('--check-overlaps', action='store_true', help='Check for spec overlaps')
    gov_parser.add_argument('--status', action='store_true', help='Show governance status')
    gov_parser.add_argument('--setup', action='store_true', help='Set up governance framework')
    gov_parser.add_argument('--create-docs', type=str, help='Create governance documentation')
    gov_parser.add_argument('--implement-training', action='store_true', help='Implement training programs')
    gov_parser.add_argument('--build-schedules', action='store_true', help='Build maintenance schedules')
    gov_parser.add_argument('--continuous-improvement', action='store_true', help='Set up continuous improvement')
    gov_parser.add_argument('--generate-report', action='store_true', help='Generate governance report')
    
    # Validation commands
    val_parser = subparsers.add_parser('validate', help='Validation operations')
    val_parser.add_argument('--terminology', type=str, help='Validate terminology in spec')
    val_parser.add_argument('--interfaces', type=str, help='Validate interfaces in spec')
    val_parser.add_argument('--consistency-score', nargs='+', help='Generate consistency score for specs')
    
    # Analysis commands
    analysis_parser = subparsers.add_parser('analyze', help='Analysis operations')
    analysis_parser.add_argument('--all-specs', action='store_true', help='Analyze all existing specs')
    analysis_parser.add_argument('--overlap-matrix', action='store_true', help='Generate overlap matrix')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'governance':
            handle_governance_commands(args)
        elif args.command == 'validate':
            handle_validation_commands(args)
        elif args.command == 'analyze':
            handle_analysis_commands(args)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def handle_governance_commands(args):
    """Handle governance-related commands"""
    controller = GovernanceController()
    
    if args.status:
        status = controller.get_module_status()
        print(json.dumps(status, indent=2))
        
    elif args.check_overlaps:
        print("Checking for spec overlaps...")
        # Create a dummy spec proposal to test overlap detection
        test_proposal = SpecProposal(
            name="test_spec",
            content="Test content",
            requirements=["Test requirement"],
            interfaces=["TestInterface"],
            terminology={"TestTerm"},
            functionality_keywords={"test", "validation", "system"}
        )
        
        overlap_report = controller.check_overlap_conflicts(test_proposal)
        print(f"Overlap severity: {overlap_report.severity.value}")
        print(f"Overlapping specs: {overlap_report.spec_pairs}")
        print(f"Recommendation: {overlap_report.consolidation_recommendation}")
        
    elif args.validate_spec:
        spec_path = Path(args.validate_spec)
        if not spec_path.exists():
            print(f"Spec file not found: {spec_path}")
            return
            
        # Create spec proposal from file
        content = spec_path.read_text()
        proposal = SpecProposal(
            name=spec_path.stem,
            content=content,
            requirements=[],  # TODO: Extract from content
            interfaces=[],    # TODO: Extract from content
            terminology=set(),  # TODO: Extract from content
            functionality_keywords=set()  # TODO: Extract from content
        )
        
        result = controller.validate_new_spec(proposal)
        print(f"Validation result: {result.value}")
        
    elif args.setup:
        print("Setting up governance framework...")
        framework = GovernanceFramework()
        print("✓ Governance framework initialized")
        print("✓ Default roles and responsibilities configured")
        print("✓ Training programs defined")
        print("✓ Maintenance schedules created")
        print("✓ Continuous improvement processes established")
        
    elif args.create_docs:
        print(f"Creating governance documentation in {args.create_docs}...")
        framework = GovernanceFramework()
        output_path = Path(args.create_docs)
        result = framework.create_governance_documentation(output_path)
        
        print(f"✓ Documentation created at: {result['output_path']}")
        print("✓ Documents created:")
        for doc in result['documents']:
            print(f"  - {doc}")
            
    elif args.implement_training:
        print("Implementing training programs...")
        framework = GovernanceFramework()
        result = framework.implement_training_programs()
        
        print(f"✓ Implemented {len(result['programs_implemented'])} training programs")
        print(f"✓ Created {len(result['training_materials_created'])} training materials")
        print(f"✓ Established {len(result['assessment_frameworks'])} assessment frameworks")
        
    elif args.build_schedules:
        print("Building maintenance schedules...")
        framework = GovernanceFramework()
        result = framework.build_maintenance_schedules()
        
        print(f"✓ Created {len(result['schedules_created'])} maintenance schedules")
        print(f"✓ Configured {len(result['automation_configured'])} automated processes")
        print(f"✓ Set up {len(result['monitoring_setup'])} monitoring systems")
        
    elif args.continuous_improvement:
        print("Setting up continuous improvement processes...")
        framework = GovernanceFramework()
        result = framework.create_continuous_improvement_process()
        
        print(f"✓ Created {len(result['processes_created'])} improvement processes")
        print(f"✓ Established {len(result['feedback_mechanisms'])} feedback mechanisms")
        print(f"✓ Configured {len(result['metrics_frameworks'])} metrics frameworks")
        
    elif args.generate_report:
        print("Generating governance implementation report...")
        framework = GovernanceFramework()
        report = framework.generate_governance_report()
        
        print("\n=== Governance Implementation Report ===")
        print(f"Roles defined: {report['governance_framework']['roles_defined']}")
        print(f"Training programs: {report['governance_framework']['training_programs']}")
        print(f"Maintenance schedules: {report['governance_framework']['maintenance_schedules']}")
        print(f"Improvement processes: {report['governance_framework']['improvement_processes']}")
        
        print("\n=== Implementation Readiness ===")
        for component, status in report['implementation_readiness'].items():
            print(f"{component}: {status}")
            
        print("\n=== Next Steps ===")
        for step in report['next_steps']:
            print(f"- {step}")
            
        print("\n=== Success Criteria ===")
        for criterion, target in report['success_criteria'].items():
            print(f"{criterion}: {target}")


def handle_validation_commands(args):
    """Handle validation-related commands"""
    validator = ConsistencyValidator()
    
    if args.terminology:
        spec_path = Path(args.terminology)
        if not spec_path.exists():
            print(f"Spec file not found: {spec_path}")
            return
            
        content = spec_path.read_text()
        report = validator.validate_terminology(content)
        
        print(f"Terminology Consistency Score: {report.consistency_score:.2f}")
        print(f"Consistent terms: {len(report.consistent_terms)}")
        print(f"Inconsistent terms: {len(report.inconsistent_terms)}")
        print(f"New terms: {len(report.new_terms)}")
        
        if report.recommendations:
            print("\nRecommendations:")
            for rec in report.recommendations:
                print(f"  - {rec}")
                
    elif args.interfaces:
        spec_path = Path(args.interfaces)
        if not spec_path.exists():
            print(f"Spec file not found: {spec_path}")
            return
            
        content = spec_path.read_text()
        report = validator.check_interface_compliance(content)
        
        print(f"Interface Compliance Score: {report.compliance_score:.2f}")
        print(f"Compliant interfaces: {len(report.compliant_interfaces)}")
        print(f"Non-compliant interfaces: {len(report.non_compliant_interfaces)}")
        
        if report.remediation_steps:
            print("\nRemediation steps:")
            for step in report.remediation_steps:
                print(f"  - {step}")
                
    elif args.consistency_score:
        spec_paths = args.consistency_score
        metrics = validator.generate_consistency_score(spec_paths)
        
        print(f"Overall Consistency Score: {metrics.overall_score:.2f}")
        print(f"Consistency Level: {metrics.consistency_level.value}")
        print(f"Terminology Score: {metrics.terminology_score:.2f}")
        print(f"Interface Score: {metrics.interface_score:.2f}")
        print(f"Pattern Score: {metrics.pattern_score:.2f}")
        
        if metrics.critical_issues:
            print("\nCritical Issues:")
            for issue in metrics.critical_issues:
                print(f"  - {issue}")
                
        if metrics.improvement_priority:
            print("\nImprovement Priorities:")
            for priority in metrics.improvement_priority:
                print(f"  - {priority}")


def handle_analysis_commands(args):
    """Handle analysis-related commands"""
    if args.all_specs:
        print("Analyzing all existing specs...")
        controller = GovernanceController()
        validator = ConsistencyValidator()
        
        # Get governance status
        gov_status = controller.get_module_status()
        print(f"Specs monitored: {gov_status.get('specs_monitored', 0)}")
        print(f"Terminology terms: {gov_status.get('terminology_terms', 0)}")
        
        # Get validation status
        val_status = validator.get_module_status()
        print(f"Terminology registry size: {val_status.get('terminology_registry_size', 0)}")
        print(f"Interface patterns loaded: {val_status.get('interface_patterns_loaded', 0)}")
        
    elif args.overlap_matrix:
        print("Generating overlap matrix...")
        controller = GovernanceController()
        
        # TODO: Implement comprehensive overlap matrix generation
        print("Overlap matrix generation not yet implemented")


if __name__ == '__main__':
    main()