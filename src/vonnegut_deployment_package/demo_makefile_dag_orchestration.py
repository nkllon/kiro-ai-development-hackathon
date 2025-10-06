#!/usr/bin/env python3
"""
Demonstration of DAG-Orchestrated Makefile Governance

Shows the makefile governance system working with DAG orchestration
for parallel validation and repair of multiple makefiles.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.makefile_governance.integration.dag_orchestration_integration import (
    create_makefile_dag_orchestrator
)


async def demo_parallel_validation():
    """Demonstrate parallel makefile validation."""
    print("🚀 DAG-Orchestrated Makefile Governance Demo")
    print("=" * 60)
    
    # Initialize orchestrator
    print("📋 Initializing DAG orchestrator...")
    orchestrator = create_makefile_dag_orchestrator(max_workers=4)
    
    # Get system health
    print("\n🏥 System Health Check:")
    health = orchestrator.get_health_status()
    print(f"   Status: {health.status.value.upper()}")
    print(f"   Health Score: {health.health_score:.2f}")
    if health.issues:
        print("   Issues:")
        for issue in health.issues:
            print(f"     - {issue}")
    
    # Find makefiles to validate
    print("\n🔍 Discovering makefiles...")
    makefile_paths = []
    
    # Look for common makefile locations
    search_paths = [
        Path("Makefile"),
        Path("makefile"),
        Path("GNUmakefile"),
        Path("src/Makefile"),
        Path("tests/Makefile"),
        Path("scripts/Makefile")
    ]
    
    for path in search_paths:
        if path.exists():
            makefile_paths.append(path)
            print(f"   Found: {path}")
    
    # Also search for makefiles in subdirectories
    for makefile in Path(".").rglob("Makefile*"):
        if makefile.is_file() and makefile not in makefile_paths:
            makefile_paths.append(makefile)
            print(f"   Found: {makefile}")
    
    if not makefile_paths:
        print("   No makefiles found. Creating a demo makefile...")
        demo_makefile = create_demo_makefile()
        makefile_paths = [demo_makefile]
    
    print(f"\n📊 Validating {len(makefile_paths)} makefiles in parallel...")
    
    # Configure validation options
    validation_options = {
        "syntax_priority": 10,
        "governance_priority": 8,
        "health_priority": 5
    }
    
    try:
        # Execute parallel validation
        results = await orchestrator.validate_makefiles_parallel(
            makefile_paths, validation_options
        )
        
        # Display results
        print("\n📈 Validation Results:")
        print("-" * 40)
        
        summary = results.get("orchestration_summary", {})
        print(f"Orchestration ID: {summary.get('orchestration_id', 'N/A')}")
        print(f"Status: {summary.get('status', 'unknown').upper()}")
        print(f"Total Tasks: {summary.get('total_tasks', 0)}")
        print(f"Completed Tasks: {summary.get('completed_tasks', 0)}")
        print(f"Failed Tasks: {summary.get('failed_tasks', 0)}")
        print(f"Duration: {summary.get('duration_seconds', 0):.2f} seconds")
        
        # Individual makefile results
        print(f"\n📋 Individual Results:")
        syntax_results = results.get("syntax_results", {})
        governance_results = results.get("governance_results", {})
        
        for makefile_path in syntax_results.keys():
            print(f"\n  📄 {makefile_path}:")
            
            # Syntax validation
            syntax = syntax_results.get(makefile_path, {})
            if syntax.get("is_valid", False):
                print("    ✅ Syntax: VALID")
            else:
                error_count = syntax.get("error_count", 0)
                print(f"    ❌ Syntax: INVALID ({error_count} errors)")
                
                # Show first few errors
                errors = syntax.get("errors", [])
                for error in errors[:3]:
                    print(f"       Line {error['line']}: {error['message']}")
                if len(errors) > 3:
                    print(f"       ... and {len(errors) - 3} more errors")
            
            # Governance validation
            governance = governance_results.get(makefile_path, {})
            if governance.get("is_compliant", False):
                print("    ✅ Governance: COMPLIANT")
            else:
                violation_count = governance.get("violation_count", 0)
                print(f"    ⚠️  Governance: NON-COMPLIANT ({violation_count} violations)")
                
                # Show first few violations
                violations = governance.get("violations", [])
                for violation in violations[:3]:
                    print(f"       Line {violation['line']}: {violation['message']}")
                if len(violations) > 3:
                    print(f"       ... and {len(violations) - 3} more violations")
            
            # Quality metrics
            quality_score = governance.get("quality_score", 0)
            complexity_score = governance.get("complexity_score", 0)
            print(f"    📊 Quality Score: {quality_score:.2f}")
            print(f"    🔧 Complexity Score: {complexity_score:.2f}")
            
            # Recommendations
            recommendations = governance.get("recommendations", [])
            if recommendations:
                print("    💡 Recommendations:")
                for rec in recommendations[:2]:
                    print(f"       - {rec}")
                if len(recommendations) > 2:
                    print(f"       ... and {len(recommendations) - 2} more")
        
        # Overall statistics
        successful = len(results.get("successful_validations", []))
        failed = len(results.get("failed_validations", []))
        
        print(f"\n📊 Summary:")
        print(f"   Successful Validations: {successful}")
        print(f"   Failed Validations: {failed}")
        print(f"   Success Rate: {successful / max(len(makefile_paths), 1):.1%}")
        
        # Performance metrics
        task_durations = results.get("task_durations", {})
        if task_durations:
            avg_duration = sum(task_durations.values()) / len(task_durations)
            print(f"   Average Task Duration: {avg_duration:.2f} seconds")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def demo_parallel_repair():
    """Demonstrate parallel makefile repair."""
    print("\n🔧 DAG-Orchestrated Makefile Repair Demo")
    print("=" * 60)
    
    # Create a makefile with known issues for repair demo
    demo_makefile = create_broken_demo_makefile()
    makefile_paths = [demo_makefile]
    
    print(f"📄 Created demo makefile with syntax errors: {demo_makefile}")
    
    # Initialize orchestrator
    orchestrator = create_makefile_dag_orchestrator(max_workers=2)
    
    # Configure repair options
    repair_options = {
        "create_backup": True,
        "repair_priority": 10,
        "validation_priority": 5
    }
    
    print(f"\n🔧 Repairing {len(makefile_paths)} makefiles in parallel...")
    
    try:
        # Execute parallel repair
        results = await orchestrator.repair_makefiles_parallel(
            makefile_paths, repair_options
        )
        
        # Display results
        print("\n📈 Repair Results:")
        print("-" * 40)
        
        summary = results.get("orchestration_summary", {})
        print(f"Orchestration ID: {summary.get('orchestration_id', 'N/A')}")
        print(f"Status: {summary.get('status', 'unknown').upper()}")
        print(f"Duration: {summary.get('duration_seconds', 0):.2f} seconds")
        
        # Individual repair results
        repair_results = results.get("repair_results", {})
        validation_results = results.get("validation_results", {})
        
        for makefile_path in repair_results.keys():
            print(f"\n  📄 {makefile_path}:")
            
            # Repair results
            repair = repair_results.get(makefile_path, {})
            if repair.get("repair_successful", False):
                print("    ✅ Repair: SUCCESSFUL")
                backup_path = repair.get("backup_path")
                if backup_path:
                    print(f"       Backup created: {backup_path}")
            else:
                print("    ❌ Repair: FAILED")
            
            # Post-repair validation
            validation = validation_results.get(makefile_path, {})
            if validation.get("is_valid", False):
                print("    ✅ Post-Repair Validation: PASSED")
            else:
                error_count = validation.get("error_count", 0)
                print(f"    ❌ Post-Repair Validation: FAILED ({error_count} errors remaining)")
        
        # Cleanup demo files
        cleanup_demo_files([demo_makefile])
        
        return results
        
    except Exception as e:
        print(f"\n❌ Repair failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_demo_makefile() -> Path:
    """Create a demo makefile for testing."""
    demo_path = Path("demo_makefile_temp")
    
    demo_content = """# Demo Makefile for DAG Orchestration Testing
.PHONY: help clean test build

help: ## Show this help message
\t@echo "Available targets:"
\t@echo "  build    - Build the project"
\t@echo "  test     - Run tests"
\t@echo "  clean    - Clean build artifacts"

build: ## Build the project
\t@echo "Building project..."
\tpython3 -c "print('Build complete')"

test: build ## Run tests
\t@echo "Running tests..."
\tpython3 -c "print('Tests passed')"

clean: ## Clean build artifacts
\t@echo "Cleaning..."
\t@rm -rf build/ dist/ *.egg-info/

install: build ## Install the project
\t@echo "Installing..."
\tpip install -e .
"""
    
    with open(demo_path, 'w') as f:
        f.write(demo_content)
    
    return demo_path


def create_broken_demo_makefile() -> Path:
    """Create a demo makefile with syntax errors for repair testing."""
    demo_path = Path("broken_demo_makefile_temp")
    
    # Intentionally broken makefile with common syntax errors
    broken_content = """# Broken Demo Makefile for Repair Testing

help:
    echo "This line should start with a tab, not spaces"
    echo "Another line with spaces instead of tabs"

build_project:
\techo "This target name should use kebab-case"
\tpython3 -c 'print("Missing separator on next line")'
echo "This line is missing a tab separator"

test: build_project
\techo "Running tests..."
\tpython3 -c "
\t\tprint('Multi-line Python code')
\t\tprint('with improper escaping')
\t"

clean
\techo "Missing colon after target name"

# Missing .PHONY declarations for side-effect targets
"""
    
    with open(demo_path, 'w') as f:
        f.write(broken_content)
    
    return demo_path


def cleanup_demo_files(file_paths: List[Path]):
    """Clean up demo files."""
    for path in file_paths:
        try:
            if path.exists():
                path.unlink()
                print(f"🧹 Cleaned up: {path}")
        except Exception as e:
            print(f"⚠️  Could not clean up {path}: {e}")


async def demo_orchestration_statistics():
    """Demonstrate orchestration statistics."""
    print("\n📊 DAG Orchestration Statistics Demo")
    print("=" * 60)
    
    orchestrator = create_makefile_dag_orchestrator(max_workers=4)
    
    # Get comprehensive statistics
    stats = orchestrator.get_orchestration_statistics()
    
    print("📈 Makefile Orchestrator Statistics:")
    makefile_stats = stats.get("makefile_orchestrator", {})
    print(f"   Total Orchestrations: {makefile_stats.get('total_orchestrations', 0)}")
    print(f"   Successful: {makefile_stats.get('successful_orchestrations', 0)}")
    print(f"   Failed: {makefile_stats.get('failed_orchestrations', 0)}")
    print(f"   Success Rate: {makefile_stats.get('success_rate', 0):.1%}")
    
    print("\n🎯 DAG Orchestrator Statistics:")
    dag_stats = stats.get("dag_orchestrator", {})
    print(f"   Total Orchestrations: {dag_stats.get('total_orchestrations', 0)}")
    print(f"   Success Rate: {dag_stats.get('success_rate', 0):.1%}")
    print(f"   Average Duration: {dag_stats.get('average_duration_seconds', 0):.2f}s")
    
    print("\n🏥 System Health Statistics:")
    health_stats = stats.get("system_health", {})
    print(f"   Status: {health_stats.get('status', 'unknown').upper()}")
    print(f"   Health Score: {health_stats.get('health_score', 0):.2f}")
    print(f"   Active Alerts: {health_stats.get('active_alerts', 0)}")
    print(f"   Recommendations: {len(health_stats.get('recommendations', []))}")


async def main():
    """Main demonstration function."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Run validation demo
        validation_results = await demo_parallel_validation()
        
        # Run repair demo
        repair_results = await demo_parallel_repair()
        
        # Show statistics
        await demo_orchestration_statistics()
        
        print("\n🎉 DAG-Orchestrated Makefile Governance Demo Complete!")
        print("=" * 60)
        
        if validation_results and repair_results:
            print("✅ All demos completed successfully")
            return 0
        else:
            print("⚠️  Some demos encountered issues")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)