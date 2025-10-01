#!/usr/bin/env python3
"""
Prepare Spec for Execution CLI
=============================

Unified command-line interface for transforming any specification into
executable, monitored, and orchestrated implementation pipelines.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import sys
import argparse
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
    from src.spec_framework.core.spec_analyzer import SpecAnalyzer, analyze_spec
    from src.spec_framework.orchestrators.dag_task_generator import DAGTaskGenerator, generate_dag_plan
    from src.spec_framework.validation.prelaunch_validator import PreLaunchValidator, validate_spec_readiness
    from src.spec_framework.generators.task_script_generator import TaskScriptGenerator, generate_scripts_for_spec
except ImportError as e:
    print(f"❌ Critical import failure: {e}")
    print("Ensure Beast Mode infrastructure and spec framework are available")
    sys.exit(1)


class PrepareSpecCLI(ReflectiveModule):
    """Unified CLI for preparing specifications for execution."""
    
    def __init__(self):
        super().__init__()
        self.spec_analyzer = SpecAnalyzer()
        self.dag_generator = DAGTaskGenerator()
        self.validator = PreLaunchValidator()
        self.script_generator = TaskScriptGenerator()
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return component capabilities."""
        return {
            'commands': ['analyze', 'validate', 'generate', 'prepare', 'status'],
            'output_formats': ['json', 'yaml', 'text'],
            'batch_processing': True,
            'interactive_mode': True
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Return component health status."""
        return {
            'status': 'healthy',
            'components_ready': True,
            'spec_analyzer': True,
            'dag_generator': True,
            'validator': True,
            'script_generator': True
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Return module information."""
        return {
            'name': 'PrepareSpecCLI',
            'version': '1.0.0',
            'description': 'Unified CLI for preparing specifications for execution',
            'dependencies': ['SpecAnalyzer', 'DAGTaskGenerator', 'PreLaunchValidator', 'TaskScriptGenerator'],
            'workflow_control': 'prepare-spec-for-execution'
        }
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation on errors."""
        return {
            'degraded_mode': True,
            'error': str(error),
            'available_functions': ['basic_analysis'],
            'recommendation': 'Use individual components directly'
        }
    
    def analyze_command(self, args: argparse.Namespace) -> int:
        """Analyze specification structure and content."""
        print("🔍 Analyzing Specification")
        print("=" * 50)
        
        try:
            spec_data = self.spec_analyzer.analyze_specification(args.spec_path)
            
            print(f"Specification: {spec_data.spec_name}")
            print(f"Path: {spec_data.spec_path}")
            print(f"Completeness Score: {spec_data.completeness_score:.1%}")
            
            print(f"\\nComponents:")
            print(f"  Requirements: {len(spec_data.requirements)}")
            print(f"  Design Sections: {len(spec_data.design_sections)}")
            print(f"  Tasks: {len(spec_data.tasks)}")
            
            if spec_data.validation_errors:
                print(f"\\n⚠️ Validation Issues ({len(spec_data.validation_errors)}):")
                for error in spec_data.validation_errors[:5]:
                    print(f"  • {error}")
                if len(spec_data.validation_errors) > 5:
                    print(f"  ... and {len(spec_data.validation_errors) - 5} more")
            
            # Generate traceability matrix
            traceability = self.spec_analyzer.generate_traceability_matrix(spec_data)
            print(f"\\n📊 Traceability:")
            print(f"  Requirements Coverage: {traceability['coverage_stats']['coverage_percentage']:.1f}%")
            print(f"  Orphaned Requirements: {len(traceability['orphaned_requirements'])}")
            print(f"  Orphaned Tasks: {len(traceability['orphaned_tasks'])}")
            
            # Output detailed results if requested
            if args.output:
                output_data = self.spec_analyzer.to_dict(spec_data)
                output_data['traceability_matrix'] = traceability
                
                output_path = Path(args.output)
                if args.format == 'json':
                    output_path.write_text(json.dumps(output_data, indent=2))
                    print(f"\\n📄 Detailed analysis saved to: {output_path}")
            
            print("\\n✅ Analysis complete")
            return 0
            
        except Exception as e:
            print(f"\\n❌ Analysis failed: {e}")
            return 1
    
    def validate_command(self, args: argparse.Namespace) -> int:
        """Validate specification readiness for execution."""
        print("🔍 Validating Specification Readiness")
        print("=" * 50)
        
        try:
            report = self.validator.validate_specification_readiness(
                args.spec_path, 
                force_refresh=args.force
            )
            
            # Summary already displayed by validator
            
            # Output detailed results if requested
            if args.output:
                output_data = {
                    'spec_name': report.spec_name,
                    'overall_status': report.overall_status,
                    'confidence_score': report.confidence_score,
                    'summary': {
                        'total_checks': report.total_checks,
                        'passed_checks': report.passed_checks,
                        'warning_checks': report.warning_checks,
                        'failed_checks': report.failed_checks,
                        'critical_failures': report.critical_failures
                    },
                    'validation_results': [
                        {
                            'check_name': result.check_name,
                            'severity': result.severity.value,
                            'status': result.status,
                            'message': result.message,
                            'remediation': result.remediation
                        }
                        for result in report.validation_results
                    ],
                    'recommendations': report.recommendations,
                    'execution_time': report.execution_time
                }
                
                output_path = Path(args.output)
                if args.format == 'json':
                    output_path.write_text(json.dumps(output_data, indent=2))
                    print(f"\\n📄 Validation report saved to: {output_path}")
            
            # Return appropriate exit code
            if report.overall_status == "ready":
                return 0
            elif report.overall_status == "warnings":
                return 0 if args.allow_warnings else 1
            else:
                return 1
            
        except Exception as e:
            print(f"\\n❌ Validation failed: {e}")
            return 1
    
    def generate_command(self, args: argparse.Namespace) -> int:
        """Generate DAG execution plan and task definitions."""
        print("🔄 Generating DAG Execution Plan")
        print("=" * 50)
        
        try:
            execution_plan = self.dag_generator.generate_dag_execution_plan(
                args.spec_path,
                execution_strategy=getattr(args, 'strategy', 'conservative')
            )
            
            print(f"Specification: {execution_plan.spec_name}")
            print(f"Total Tasks: {execution_plan.total_tasks}")
            print(f"Execution Groups: {len(execution_plan.execution_groups)}")
            
            print(f"\\n⏱️ Timing Estimates:")
            print(f"  Sequential Time: {execution_plan.estimated_sequential_time:.1f} hours")
            print(f"  Parallel Time: {execution_plan.estimated_parallel_time:.1f} hours")
            print(f"  Efficiency Gain: {execution_plan.efficiency_gain:.1f}%")
            
            print(f"\\n📋 Execution Groups:")
            for i, group in enumerate(execution_plan.execution_groups):
                print(f"  {i+1}. {group.phase.title()} ({len(group.tasks)} tasks, {group.estimated_duration:.1f}h)")
            
            # Output detailed results if requested
            if args.output:
                output_data = self.dag_generator.to_dict(execution_plan)
                
                output_path = Path(args.output)
                if args.format == 'json':
                    output_path.write_text(json.dumps(output_data, indent=2))
                    print(f"\\n📄 Execution plan saved to: {output_path}")
            
            print("\\n✅ DAG generation complete")
            return 0
            
        except Exception as e:
            print(f"\\n❌ DAG generation failed: {e}")
            return 1
    
    def prepare_command(self, args: argparse.Namespace) -> int:
        """Complete preparation: analyze, validate, generate DAG, and create scripts."""
        print("🚀 Preparing Specification for Execution")
        print("=" * 50)
        
        try:
            # Step 1: Analyze specification
            print("\\n1️⃣ Analyzing specification...")
            spec_data = self.spec_analyzer.analyze_specification(args.spec_path)
            print(f"   ✅ Found {len(spec_data.tasks)} tasks, {len(spec_data.requirements)} requirements")
            
            # Step 2: Validate readiness (if not skipped)
            if not args.skip_validation:
                print("\\n2️⃣ Validating readiness...")
                report = self.validator.validate_specification_readiness(args.spec_path)
                
                if report.overall_status == "failed":
                    print("   ❌ Validation failed - cannot proceed")
                    return 1
                elif report.overall_status == "warnings":
                    print("   ⚠️ Validation has warnings")
                    if not args.allow_warnings:
                        print("   Use --allow-warnings to proceed anyway")
                        return 1
                else:
                    print("   ✅ Validation passed")
            
            # Step 3: Generate DAG execution plan
            print("\\n3️⃣ Generating execution plan...")
            execution_plan = self.dag_generator.generate_dag_execution_plan(
                args.spec_path,
                execution_strategy=getattr(args, 'strategy', 'conservative')
            )
            print(f"   ✅ Generated plan with {execution_plan.efficiency_gain:.1f}% efficiency gain")
            
            # Step 4: Generate execution scripts
            print("\\n4️⃣ Generating execution scripts...")
            output_dir = args.output or f"scripts/{spec_data.spec_name}"
            scripts = self.script_generator.generate_all_scripts(
                spec_data, 
                execution_plan, 
                output_dir
            )
            
            print(f"   ✅ Generated {len(scripts)} scripts in {output_dir}")
            for script_type, script in scripts.items():
                print(f"      • {script.script_name}")
            
            # Step 5: Generate summary report
            print("\\n5️⃣ Generating summary report...")
            summary = self._generate_preparation_summary(spec_data, execution_plan, scripts, output_dir)
            
            summary_path = Path(output_dir) / "PREPARATION_SUMMARY.md"
            summary_path.write_text(summary)
            print(f"   ✅ Summary saved to {summary_path}")
            
            print("\\n🎉 Specification preparation complete!")
            print(f"\\n📋 Next steps:")
            print(f"   1. Review preparation summary: {summary_path}")
            print(f"   2. Run prelaunch validation: python3 {output_dir}/{spec_data.spec_name.lower().replace('-', '_')}_prelaunch_check_v2.py")
            print(f"   3. Launch execution: python3 {output_dir}/{spec_data.spec_name.lower().replace('-', '_')}_launch_v2.py")
            print(f"   4. Or run in background: ./{output_dir}/{spec_data.spec_name.lower().replace('-', '_')}_background_launch_v2.sh")
            
            return 0
            
        except Exception as e:
            print(f"\\n❌ Preparation failed: {e}")
            return 1
    
    def status_command(self, args: argparse.Namespace) -> int:
        """Show status of specification preparation."""
        print("📊 Specification Status")
        print("=" * 50)
        
        try:
            spec_path = Path(args.spec_path)
            
            # Check if spec exists and is valid
            if not spec_path.exists():
                print(f"❌ Specification not found: {spec_path}")
                return 1
            
            # Analyze current state
            spec_data = self.spec_analyzer.analyze_specification(str(spec_path))
            
            print(f"Specification: {spec_data.spec_name}")
            print(f"Path: {spec_data.spec_path}")
            print(f"Completeness: {spec_data.completeness_score:.1%}")
            
            # Check for generated scripts
            script_dir = spec_path.parent / "scripts" / spec_data.spec_name
            if script_dir.exists():
                scripts = list(script_dir.glob("*_v2.*"))
                print(f"\\n📜 Generated Scripts ({len(scripts)}):")
                for script in scripts:
                    print(f"   • {script.name}")
                
                # Check for summary
                summary_file = script_dir / "PREPARATION_SUMMARY.md"
                if summary_file.exists():
                    print(f"\\n📋 Preparation Summary: {summary_file}")
                    print("   ✅ Specification is prepared for execution")
                else:
                    print("\\n⚠️ No preparation summary found")
            else:
                print("\\n❓ No generated scripts found")
                print("   Run 'prepare-spec prepare' to generate execution scripts")
            
            # Quick validation check
            try:
                report = self.validator.validate_specification_readiness(str(spec_path))
                print(f"\\n🔍 Readiness: {report.overall_status.upper()} ({report.confidence_score:.1%})")
            except Exception as e:
                print(f"\\n⚠️ Could not check readiness: {e}")
            
            return 0
            
        except Exception as e:
            print(f"\\n❌ Status check failed: {e}")
            return 1
    
    def _generate_preparation_summary(self, spec_data, execution_plan, scripts, output_dir) -> str:
        """Generate preparation summary report."""
        return f'''# Specification Preparation Summary

## Specification Details
- **Name**: {spec_data.spec_name}
- **Path**: {spec_data.spec_path}
- **Completeness Score**: {spec_data.completeness_score:.1%}
- **Preparation Date**: {datetime.now().isoformat()}

## Components
- **Requirements**: {len(spec_data.requirements)}
- **Design Sections**: {len(spec_data.design_sections)}
- **Tasks**: {len(spec_data.tasks)}

## Execution Plan
- **Total Tasks**: {execution_plan.total_tasks}
- **Execution Groups**: {len(execution_plan.execution_groups)}
- **Sequential Time**: {execution_plan.estimated_sequential_time:.1f} hours
- **Parallel Time**: {execution_plan.estimated_parallel_time:.1f} hours
- **Efficiency Gain**: {execution_plan.efficiency_gain:.1f}%
- **Strategy**: {execution_plan.execution_strategy.value}

## Generated Scripts
{chr(10).join(f"- **{script.script_type.title()}**: `{script.script_name}`" for script in scripts.values())}

## Execution Instructions

### 1. Prelaunch Validation
```bash
python3 {output_dir}/{spec_data.spec_name.lower().replace('-', '_')}_prelaunch_check_v2.py
```

### 2. Direct Execution
```bash
python3 {output_dir}/{spec_data.spec_name.lower().replace('-', '_')}_launch_v2.py
```

### 3. Background Execution
```bash
# Start execution
./{output_dir}/{spec_data.spec_name.lower().replace('-', '_')}_background_launch_v2.sh run

# Check status
./{output_dir}/{spec_data.spec_name.lower().replace('-', '_')}_background_launch_v2.sh status

# View logs
./{output_dir}/{spec_data.spec_name.lower().replace('-', '_')}_background_launch_v2.sh logs

# Stop execution
./{output_dir}/{spec_data.spec_name.lower().replace('-', '_')}_background_launch_v2.sh stop
```

## Success Criteria
- All prelaunch validations pass
- {execution_plan.efficiency_gain:.1f}% efficiency gain through parallel execution
- Complete execution tracking and monitoring
- Systematic error handling and recovery

---
Generated by Prepare Spec for Execution v1.0
Workflow Control: spec-creation-dag-compliance-v2
'''


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog='prepare-spec',
        description='Prepare specifications for execution with parallel DAG orchestration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  prepare-spec analyze .kiro/specs/my-feature
  prepare-spec validate .kiro/specs/my-feature --output validation_report.json
  prepare-spec generate .kiro/specs/my-feature --strategy aggressive
  prepare-spec prepare .kiro/specs/my-feature --output scripts/my-feature
  prepare-spec status .kiro/specs/my-feature
        '''
    )
    
    # Global options
    parser.add_argument('--version', action='version', version='prepare-spec 1.0.0')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze specification structure and content')
    analyze_parser.add_argument('spec_path', help='Path to specification directory')
    analyze_parser.add_argument('--output', '-o', help='Output file for detailed results')
    analyze_parser.add_argument('--format', choices=['json', 'yaml'], default='json', help='Output format')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate specification readiness')
    validate_parser.add_argument('spec_path', help='Path to specification directory')
    validate_parser.add_argument('--output', '-o', help='Output file for validation report')
    validate_parser.add_argument('--format', choices=['json', 'yaml'], default='json', help='Output format')
    validate_parser.add_argument('--force', action='store_true', help='Force refresh validation cache')
    validate_parser.add_argument('--allow-warnings', action='store_true', help='Allow warnings in validation')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate DAG execution plan')
    generate_parser.add_argument('spec_path', help='Path to specification directory')
    generate_parser.add_argument('--output', '-o', help='Output file for execution plan')
    generate_parser.add_argument('--format', choices=['json', 'yaml'], default='json', help='Output format')
    generate_parser.add_argument('--strategy', choices=['conservative', 'aggressive', 'sequential'], 
                                default='conservative', help='Execution strategy')
    
    # Prepare command (main command)
    prepare_parser = subparsers.add_parser('prepare', help='Complete preparation for execution')
    prepare_parser.add_argument('spec_path', help='Path to specification directory')
    prepare_parser.add_argument('--output', '-o', help='Output directory for generated scripts')
    prepare_parser.add_argument('--strategy', choices=['conservative', 'aggressive', 'sequential'], 
                                default='conservative', help='Execution strategy')
    prepare_parser.add_argument('--skip-validation', action='store_true', help='Skip prelaunch validation')
    prepare_parser.add_argument('--allow-warnings', action='store_true', help='Allow warnings in validation')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show specification preparation status')
    status_parser.add_argument('spec_path', help='Path to specification directory')
    
    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        cli = PrepareSpecCLI()
        
        if args.command == 'analyze':
            return cli.analyze_command(args)
        elif args.command == 'validate':
            return cli.validate_command(args)
        elif args.command == 'generate':
            return cli.generate_command(args)
        elif args.command == 'prepare':
            return cli.prepare_command(args)
        elif args.command == 'status':
            return cli.status_command(args)
        else:
            print(f"❌ Unknown command: {args.command}")
            return 1
            
    except KeyboardInterrupt:
        print("\\n🛑 Operation cancelled by user")
        return 130
    except Exception as e:
        print(f"\\n❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())