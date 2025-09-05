#!/usr/bin/env python3
"""
CLI Usage Examples for Spec Reconciliation System

This file contains practical examples of using the CLI for common tasks.
Run these examples to understand CLI functionality and integration patterns.
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import List, Dict, Any


class CLIExampleRunner:
    """Helper class to run CLI examples and demonstrate functionality"""
    
    def __init__(self):
        self.cli_module = "src.spec_reconciliation.cli"
        self.examples_run = []
        self.results = {}
    
    def run_command(self, args: List[str], description: str = "") -> Dict[str, Any]:
        """Run a CLI command and capture results"""
        cmd = [sys.executable, "-m", self.cli_module] + args
        
        print(f"\n{'='*60}")
        print(f"Example: {description}")
        print(f"Command: {' '.join(cmd)}")
        print(f"{'='*60}")
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            output = {
                'command': ' '.join(cmd),
                'description': description,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
            
            if output['success']:
                print("✅ SUCCESS")
                if output['stdout']:
                    print("Output:")
                    print(output['stdout'])
            else:
                print("❌ ERROR")
                if output['stderr']:
                    print("Error:")
                    print(output['stderr'])
            
            self.examples_run.append(output)
            return output
            
        except subprocess.TimeoutExpired:
            print("⏰ TIMEOUT - Command took too long")
            return {
                'command': ' '.join(cmd),
                'description': description,
                'error': 'timeout',
                'success': False
            }
        except Exception as e:
            print(f"💥 EXCEPTION - {e}")
            return {
                'command': ' '.join(cmd),
                'description': description,
                'error': str(e),
                'success': False
            }
    
    def create_sample_spec(self, filename: str, content: str) -> Path:
        """Create a sample spec file for testing"""
        spec_path = Path(filename)
        spec_path.parent.mkdir(parents=True, exist_ok=True)
        spec_path.write_text(content)
        return spec_path
    
    def cleanup_sample_files(self, files: List[Path]):
        """Clean up sample files after examples"""
        for file_path in files:
            try:
                if file_path.exists():
                    file_path.unlink()
                    # Remove empty directories
                    if file_path.parent.exists() and not any(file_path.parent.iterdir()):
                        file_path.parent.rmdir()
            except Exception as e:
                print(f"Warning: Could not clean up {file_path}: {e}")


def example_1_basic_help():
    """Example 1: Basic help and command discovery"""
    runner = CLIExampleRunner()
    
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Help and Command Discovery")
    print("="*80)
    
    # Main help
    runner.run_command(["--help"], "Show main CLI help")
    
    # Subcommand help
    runner.run_command(["governance", "--help"], "Show governance subcommand help")
    runner.run_command(["validate", "--help"], "Show validation subcommand help")
    runner.run_command(["analyze", "--help"], "Show analysis subcommand help")
    
    return runner.examples_run


def example_2_governance_workflow():
    """Example 2: Complete governance workflow"""
    runner = CLIExampleRunner()
    
    print("\n" + "="*80)
    print("EXAMPLE 2: Governance Workflow")
    print("="*80)
    
    # Step 1: Check governance status
    runner.run_command(
        ["governance", "--status"], 
        "Check current governance system status"
    )
    
    # Step 2: Create a sample spec for validation
    sample_spec = runner.create_sample_spec(
        "temp_examples/sample_spec.md",
        """# Sample Spec for Testing

## Requirements

### Requirement 1
**User Story:** As a developer, I want PDCA functionality, so that I can improve systematically.

#### Acceptance Criteria
1. WHEN planning THEN system SHALL use model registry
2. WHEN executing THEN system SHALL follow ReflectiveModule pattern

## Interface

class SampleModule(ReflectiveModule):
    def get_module_status(self):
        return {"status": "healthy"}
    
    def is_healthy(self):
        return True
"""
    )
    
    # Step 3: Validate the spec
    runner.run_command(
        ["governance", "--validate-spec", str(sample_spec)],
        "Validate sample spec for overlaps and conflicts"
    )
    
    # Step 4: Check for overlaps
    runner.run_command(
        ["governance", "--check-overlaps"],
        "Check for overlaps across all specs"
    )
    
    # Cleanup
    runner.cleanup_sample_files([sample_spec])
    
    return runner.examples_run


def example_3_validation_workflow():
    """Example 3: Complete validation workflow"""
    runner = CLIExampleRunner()
    
    print("\n" + "="*80)
    print("EXAMPLE 3: Validation Workflow")
    print("="*80)
    
    # Create sample specs with different issues
    terminology_spec = runner.create_sample_spec(
        "temp_examples/terminology_test.md",
        """# Terminology Test Spec

This spec uses RCA and root cause analysis inconsistently.
It also mentions PDCA methodology and Plan-Do-Check-Act approach.
The ReflectiveModule pattern should be used throughout.

Some new terminology: systematic_improvement, proactive_maintenance.
"""
    )
    
    interface_spec = runner.create_sample_spec(
        "temp_examples/interface_test.md",
        """# Interface Test Spec

## Good Interface

class GoodModule(ReflectiveModule):
    def get_module_status(self):
        return {"status": "healthy"}
    
    def is_healthy(self):
        return True
        
    def get_health_indicators(self):
        return []

## Bad Interface

class BadModule:
    def badMethodName(self):
        pass
    
    def anotherBadMethod(self, p1, p2, p3, p4, p5):
        pass
"""
    )
    
    # Step 1: Validate terminology
    runner.run_command(
        ["validate", "--terminology", str(terminology_spec)],
        "Validate terminology consistency"
    )
    
    # Step 2: Validate interfaces
    runner.run_command(
        ["validate", "--interfaces", str(interface_spec)],
        "Validate interface compliance"
    )
    
    # Step 3: Generate consistency score
    runner.run_command(
        ["validate", "--consistency-score", str(terminology_spec), str(interface_spec)],
        "Generate overall consistency score"
    )
    
    # Cleanup
    runner.cleanup_sample_files([terminology_spec, interface_spec])
    
    return runner.examples_run


def example_4_analysis_workflow():
    """Example 4: Analysis and monitoring workflow"""
    runner = CLIExampleRunner()
    
    print("\n" + "="*80)
    print("EXAMPLE 4: Analysis and Monitoring Workflow")
    print("="*80)
    
    # Step 1: Analyze all specs
    runner.run_command(
        ["analyze", "--all-specs"],
        "Analyze all existing specs in the system"
    )
    
    # Step 2: Generate overlap matrix
    runner.run_command(
        ["analyze", "--overlap-matrix"],
        "Generate overlap matrix (feature in development)"
    )
    
    return runner.examples_run


def example_5_error_handling():
    """Example 5: Error handling and edge cases"""
    runner = CLIExampleRunner()
    
    print("\n" + "="*80)
    print("EXAMPLE 5: Error Handling and Edge Cases")
    print("="*80)
    
    # Test invalid command
    runner.run_command(
        ["invalid-command"],
        "Test invalid command handling"
    )
    
    # Test missing file
    runner.run_command(
        ["validate", "--terminology", "nonexistent_file.md"],
        "Test missing file handling"
    )
    
    # Test missing required argument
    runner.run_command(
        ["governance", "--validate-spec"],
        "Test missing required argument"
    )
    
    return runner.examples_run


def example_6_batch_processing():
    """Example 6: Batch processing multiple specs"""
    runner = CLIExampleRunner()
    
    print("\n" + "="*80)
    print("EXAMPLE 6: Batch Processing Multiple Specs")
    print("="*80)
    
    # Create multiple sample specs
    specs = []
    for i in range(3):
        spec = runner.create_sample_spec(
            f"temp_examples/batch_spec_{i}.md",
            f"""# Batch Test Spec {i}

This is spec number {i} for batch processing testing.
Uses PDCA methodology and ReflectiveModule pattern.

## Interface

class BatchModule{i}(ReflectiveModule):
    def get_module_status(self):
        return {{"spec_id": {i}}}
"""
        )
        specs.append(spec)
    
    # Validate all specs together
    spec_paths = [str(spec) for spec in specs]
    runner.run_command(
        ["validate", "--consistency-score"] + spec_paths,
        "Batch validate multiple specs"
    )
    
    # Individual validation
    for i, spec in enumerate(specs):
        runner.run_command(
            ["validate", "--terminology", str(spec)],
            f"Individual validation of spec {i}"
        )
    
    # Cleanup
    runner.cleanup_sample_files(specs)
    
    return runner.examples_run


def example_7_integration_patterns():
    """Example 7: Integration patterns and advanced usage"""
    runner = CLIExampleRunner()
    
    print("\n" + "="*80)
    print("EXAMPLE 7: Integration Patterns and Advanced Usage")
    print("="*80)
    
    # Create a comprehensive spec
    comprehensive_spec = runner.create_sample_spec(
        "temp_examples/comprehensive_spec.md",
        """# Comprehensive Integration Test Spec

## Overview
This spec demonstrates comprehensive integration testing patterns.

## Requirements

### Requirement 1: PDCA Integration
**User Story:** As a system architect, I want PDCA methodology integration, so that continuous improvement is systematic.

#### Acceptance Criteria
1. WHEN planning THEN system SHALL use model registry
2. WHEN doing THEN system SHALL execute with ReflectiveModule pattern
3. WHEN checking THEN system SHALL validate against consistency metrics
4. WHEN acting THEN system SHALL implement automated corrections

### Requirement 2: Governance Integration
**User Story:** As a governance controller, I want automated oversight, so that spec fragmentation is prevented.

#### Acceptance Criteria
1. WHEN new specs are proposed THEN system SHALL check for overlaps
2. WHEN conflicts are detected THEN system SHALL trigger consolidation workflows
3. WHEN terminology drifts THEN system SHALL enforce consistency

## Design

### Architecture
The system follows a layered architecture with prevention-first approach.

### Interfaces

class ComprehensiveModule(ReflectiveModule):
    def get_module_status(self):
        return {
            "module_name": "ComprehensiveModule",
            "pdca_cycles_completed": 42,
            "governance_violations": 0,
            "consistency_score": 0.95
        }
    
    def is_healthy(self):
        return True
        
    def get_health_indicators(self):
        return [
            "pdca_cycle_health",
            "governance_compliance",
            "terminology_consistency"
        ]
    
    def execute_pdca_cycle(self, context):
        # Implementation details
        pass
    
    def validate_governance_compliance(self):
        # Implementation details
        pass

### Data Models

@dataclass
class IntegrationMetrics:
    pdca_effectiveness: float
    governance_compliance: float
    terminology_consistency: float
    overall_integration_score: float

## Testing Strategy

The module will be tested using:
1. Unit tests for individual methods
2. Integration tests for PDCA workflows
3. Governance compliance tests
4. End-to-end validation tests

## Error Handling

Comprehensive error handling includes:
- PDCA cycle failures
- Governance violations
- Terminology inconsistencies
- Integration failures
"""
    )
    
    # Comprehensive validation workflow
    runner.run_command(
        ["governance", "--validate-spec", str(comprehensive_spec)],
        "Validate comprehensive spec"
    )
    
    runner.run_command(
        ["validate", "--terminology", str(comprehensive_spec)],
        "Check terminology in comprehensive spec"
    )
    
    runner.run_command(
        ["validate", "--interfaces", str(comprehensive_spec)],
        "Check interfaces in comprehensive spec"
    )
    
    runner.run_command(
        ["validate", "--consistency-score", str(comprehensive_spec)],
        "Generate consistency score for comprehensive spec"
    )
    
    # Cleanup
    runner.cleanup_sample_files([comprehensive_spec])
    
    return runner.examples_run


def run_all_examples():
    """Run all CLI usage examples"""
    print("🚀 Starting CLI Usage Examples")
    print("="*80)
    
    all_results = []
    
    try:
        # Run all examples
        all_results.extend(example_1_basic_help())
        all_results.extend(example_2_governance_workflow())
        all_results.extend(example_3_validation_workflow())
        all_results.extend(example_4_analysis_workflow())
        all_results.extend(example_5_error_handling())
        all_results.extend(example_6_batch_processing())
        all_results.extend(example_7_integration_patterns())
        
    except KeyboardInterrupt:
        print("\n⚠️  Examples interrupted by user")
    except Exception as e:
        print(f"\n💥 Error running examples: {e}")
    
    # Summary
    print("\n" + "="*80)
    print("📊 EXAMPLES SUMMARY")
    print("="*80)
    
    total_examples = len(all_results)
    successful_examples = len([r for r in all_results if r.get('success', False)])
    failed_examples = total_examples - successful_examples
    
    print(f"Total examples run: {total_examples}")
    print(f"Successful: {successful_examples}")
    print(f"Failed: {failed_examples}")
    
    if failed_examples > 0:
        print("\n❌ Failed Examples:")
        for result in all_results:
            if not result.get('success', False):
                print(f"  - {result.get('description', 'Unknown')}")
                if 'error' in result:
                    print(f"    Error: {result['error']}")
    
    print(f"\n✅ Success rate: {(successful_examples/total_examples)*100:.1f}%")
    
    return all_results


if __name__ == "__main__":
    """
    Run CLI usage examples
    
    Usage:
        python examples/cli_usage_examples.py
        
    Or run individual examples:
        python -c "from examples.cli_usage_examples import example_1_basic_help; example_1_basic_help()"
    """
    
    # Check if we're in the right directory
    if not Path("src/spec_reconciliation/cli.py").exists():
        print("❌ Error: Please run this script from the project root directory")
        print("   Current directory should contain src/spec_reconciliation/cli.py")
        sys.exit(1)
    
    # Run all examples
    results = run_all_examples()
    
    # Save results for analysis
    results_file = Path("examples/cli_usage_results.json")
    try:
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📁 Results saved to: {results_file}")
    except Exception as e:
        print(f"\n⚠️  Could not save results: {e}")