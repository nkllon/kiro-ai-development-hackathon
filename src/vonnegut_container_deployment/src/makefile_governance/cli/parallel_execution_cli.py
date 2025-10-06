#!/usr/bin/env python3
"""
Parallel Execution CLI for Makefile Governance

Command-line interface for DAG-orchestrated parallel execution of makefile
validation and governance tasks.
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.makefile_governance.integration.dag_orchestration_integration import (
    MakefileDAGOrchestrator,
    create_makefile_dag_orchestrator
)


class MakefileParallelExecutionCLI:
    """
    CLI for parallel execution of makefile governance tasks.
    """
    
    def __init__(self):
        self.orchestrator: Optional[MakefileDAGOrchestrator] = None
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create command-line argument parser."""
        parser = argparse.ArgumentParser(
            description="DAG-orchestrated parallel execution for makefile governance",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Validate multiple makefiles in parallel
  python -m src.makefile_governance.cli.parallel_execution_cli validate Makefile */Makefile
  
  # Repair makefiles with parallel execution
  python -m src.makefile_governance.cli.parallel_execution_cli repair Makefile --backup
  
  # Get system health status
  python -m src.makefile_governance.cli.parallel_execution_cli health
  
  # Get orchestration statistics
  python -m src.makefile_governance.cli.parallel_execution_cli stats
            """
        )
        
        # Global options
        parser.add_argument(
            "--workers", "-w",
            type=int,
            default=4,
            help="Maximum number of parallel workers (default: 4)"
        )
        
        parser.add_argument(
            "--output", "-o",
            choices=["json", "text", "summary"],
            default="text",
            help="Output format (default: text)"
        )
        
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Enable verbose output"
        )
        
        # Subcommands
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        
        # Validate command
        validate_parser = subparsers.add_parser(
            "validate",
            help="Validate makefiles in parallel"
        )
        validate_parser.add_argument(
            "makefiles",
            nargs="+",
            help="Makefile paths to validate"
        )
        validate_parser.add_argument(
            "--syntax-only",
            action="store_true",
            help="Only perform syntax validation"
        )
        validate_parser.add_argument(
            "--governance-only",
            action="store_true",
            help="Only perform governance validation"
        )
        validate_parser.add_argument(
            "--priority",
            type=int,
            default=10,
            help="Task priority (default: 10)"
        )
        
        # Repair command
        repair_parser = subparsers.add_parser(
            "repair",
            help="Repair makefiles in parallel"
        )
        repair_parser.add_argument(
            "makefiles",
            nargs="+",
            help="Makefile paths to repair"
        )
        repair_parser.add_argument(
            "--backup",
            action="store_true",
            help="Create backup before repair"
        )
        repair_parser.add_argument(
            "--no-validation",
            action="store_true",
            help="Skip post-repair validation"
        )
        
        # Health command
        health_parser = subparsers.add_parser(
            "health",
            help="Get system health status"
        )
        health_parser.add_argument(
            "--alerts-only",
            action="store_true",
            help="Show only active alerts"
        )
        
        # Statistics command
        stats_parser = subparsers.add_parser(
            "stats",
            help="Get orchestration statistics"
        )
        stats_parser.add_argument(
            "--component",
            choices=["orchestrator", "dag", "health", "all"],
            default="all",
            help="Statistics component to show (default: all)"
        )
        
        return parser
    
    async def run(self, args: List[str]) -> int:
        """Run the CLI with given arguments."""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)
        
        if not parsed_args.command:
            parser.print_help()
            return 1
        
        try:
            # Initialize orchestrator
            self.orchestrator = create_makefile_dag_orchestrator(
                max_workers=parsed_args.workers
            )
            
            # Execute command
            if parsed_args.command == "validate":
                return await self._handle_validate(parsed_args)
            elif parsed_args.command == "repair":
                return await self._handle_repair(parsed_args)
            elif parsed_args.command == "health":
                return await self._handle_health(parsed_args)
            elif parsed_args.command == "stats":
                return await self._handle_stats(parsed_args)
            else:
                print(f"Unknown command: {parsed_args.command}", file=sys.stderr)
                return 1
                
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            if parsed_args.verbose:
                import traceback
                traceback.print_exc()
            return 1
    
    async def _handle_validate(self, args) -> int:
        """Handle validate command."""
        # Resolve makefile paths
        makefile_paths = []
        for pattern in args.makefiles:
            path = Path(pattern)
            if path.is_file():
                makefile_paths.append(path)
            elif "*" in pattern:
                # Handle glob patterns
                parent = path.parent if path.parent != Path(".") else Path.cwd()
                makefile_paths.extend(parent.glob(path.name))
            else:
                print(f"Warning: Makefile not found: {pattern}", file=sys.stderr)
        
        if not makefile_paths:
            print("Error: No valid makefiles found", file=sys.stderr)
            return 1
        
        # Prepare validation options
        validation_options = {
            "syntax_priority": args.priority,
            "governance_priority": args.priority - 1,
            "health_priority": args.priority - 2
        }
        
        if args.syntax_only:
            validation_options["governance_enabled"] = False
            validation_options["health_enabled"] = False
        elif args.governance_only:
            validation_options["syntax_enabled"] = False
            validation_options["health_enabled"] = False
        
        # Execute validation
        if args.verbose:
            print(f"Validating {len(makefile_paths)} makefiles in parallel...")
        
        results = await self.orchestrator.validate_makefiles_parallel(
            makefile_paths, validation_options
        )
        
        # Output results
        self._output_validation_results(results, args)
        
        # Return appropriate exit code
        failed_count = len(results.get("failed_validations", []))
        return 0 if failed_count == 0 else 1
    
    async def _handle_repair(self, args) -> int:
        """Handle repair command."""
        # Resolve makefile paths
        makefile_paths = []
        for pattern in args.makefiles:
            path = Path(pattern)
            if path.is_file():
                makefile_paths.append(path)
            else:
                print(f"Warning: Makefile not found: {pattern}", file=sys.stderr)
        
        if not makefile_paths:
            print("Error: No valid makefiles found", file=sys.stderr)
            return 1
        
        # Prepare repair options
        repair_options = {
            "create_backup": args.backup,
            "skip_validation": args.no_validation,
            "repair_priority": 10,
            "validation_priority": 5
        }
        
        # Execute repair
        if args.verbose:
            print(f"Repairing {len(makefile_paths)} makefiles in parallel...")
        
        results = await self.orchestrator.repair_makefiles_parallel(
            makefile_paths, repair_options
        )
        
        # Output results
        self._output_repair_results(results, args)
        
        # Return appropriate exit code
        failed_count = len(results.get("failed_repairs", []))
        return 0 if failed_count == 0 else 1
    
    async def _handle_health(self, args) -> int:
        """Handle health command."""
        health_status = self.orchestrator.get_health_status()
        
        if args.output == "json":
            health_data = {
                "module_id": health_status.module_id,
                "status": health_status.status.value,
                "health_score": health_status.health_score,
                "issues": health_status.issues,
                "last_check": health_status.last_check.isoformat(),
                "uptime_seconds": health_status.uptime_seconds,
                "error_count": health_status.error_count,
                "warning_count": health_status.warning_count
            }
            print(json.dumps(health_data, indent=2))
        else:
            print(f"System Health Status: {health_status.status.value.upper()}")
            print(f"Health Score: {health_status.health_score:.2f}")
            print(f"Uptime: {health_status.uptime_seconds:.1f} seconds")
            
            if health_status.issues:
                print(f"\nIssues ({len(health_status.issues)}):")
                for issue in health_status.issues:
                    print(f"  - {issue}")
            
            if not args.alerts_only:
                print(f"\nError Count: {health_status.error_count}")
                print(f"Warning Count: {health_status.warning_count}")
        
        return 0 if health_status.status.value == "healthy" else 1
    
    async def _handle_stats(self, args) -> int:
        """Handle stats command."""
        stats = self.orchestrator.get_orchestration_statistics()
        
        if args.output == "json":
            if args.component == "all":
                print(json.dumps(stats, indent=2))
            else:
                component_stats = stats.get(args.component, {})
                print(json.dumps(component_stats, indent=2))
        else:
            if args.component in ["orchestrator", "all"]:
                makefile_stats = stats.get("makefile_orchestrator", {})
                print("Makefile Orchestrator Statistics:")
                print(f"  Total Orchestrations: {makefile_stats.get('total_orchestrations', 0)}")
                print(f"  Successful: {makefile_stats.get('successful_orchestrations', 0)}")
                print(f"  Failed: {makefile_stats.get('failed_orchestrations', 0)}")
                print(f"  Success Rate: {makefile_stats.get('success_rate', 0):.1%}")
                print()
            
            if args.component in ["dag", "all"]:
                dag_stats = stats.get("dag_orchestrator", {})
                print("DAG Orchestrator Statistics:")
                print(f"  Total Orchestrations: {dag_stats.get('total_orchestrations', 0)}")
                print(f"  Success Rate: {dag_stats.get('success_rate', 0):.1%}")
                print(f"  Average Duration: {dag_stats.get('average_duration_seconds', 0):.2f}s")
                print()
            
            if args.component in ["health", "all"]:
                health_stats = stats.get("system_health", {})
                print("System Health Statistics:")
                print(f"  Status: {health_stats.get('status', 'unknown').upper()}")
                print(f"  Health Score: {health_stats.get('health_score', 0):.2f}")
                print(f"  Active Alerts: {health_stats.get('active_alerts', 0)}")
                print(f"  Recommendations: {len(health_stats.get('recommendations', []))}")
        
        return 0
    
    def _output_validation_results(self, results: Dict[str, Any], args) -> None:
        """Output validation results in the specified format."""
        if args.output == "json":
            print(json.dumps(results, indent=2))
        elif args.output == "summary":
            summary = results.get("orchestration_summary", {})
            print(f"Validation Summary:")
            print(f"  Status: {summary.get('status', 'unknown').upper()}")
            print(f"  Total Tasks: {summary.get('total_tasks', 0)}")
            print(f"  Completed: {summary.get('completed_tasks', 0)}")
            print(f"  Failed: {summary.get('failed_tasks', 0)}")
            print(f"  Duration: {summary.get('duration_seconds', 0):.2f}s")
            
            successful = len(results.get("successful_validations", []))
            failed = len(results.get("failed_validations", []))
            print(f"  Successful Validations: {successful}")
            print(f"  Failed Validations: {failed}")
        else:
            # Text output
            print("Makefile Validation Results")
            print("=" * 50)
            
            # Orchestration summary
            summary = results.get("orchestration_summary", {})
            print(f"Orchestration ID: {summary.get('orchestration_id', 'N/A')}")
            print(f"Status: {summary.get('status', 'unknown').upper()}")
            print(f"Duration: {summary.get('duration_seconds', 0):.2f} seconds")
            print()
            
            # Individual results
            syntax_results = results.get("syntax_results", {})
            governance_results = results.get("governance_results", {})
            
            for makefile_path in syntax_results.keys():
                print(f"Makefile: {makefile_path}")
                
                # Syntax results
                syntax = syntax_results.get(makefile_path, {})
                if syntax.get("is_valid", False):
                    print("  ✓ Syntax: VALID")
                else:
                    print(f"  ✗ Syntax: INVALID ({syntax.get('error_count', 0)} errors)")
                    if args.verbose and syntax.get("errors"):
                        for error in syntax["errors"][:3]:  # Show first 3 errors
                            print(f"    Line {error['line']}: {error['message']}")
                
                # Governance results
                governance = governance_results.get(makefile_path, {})
                if governance.get("is_compliant", False):
                    print("  ✓ Governance: COMPLIANT")
                else:
                    violations = governance.get("violation_count", 0)
                    print(f"  ✗ Governance: NON-COMPLIANT ({violations} violations)")
                    if args.verbose and governance.get("violations"):
                        for violation in governance["violations"][:3]:  # Show first 3 violations
                            print(f"    Line {violation['line']}: {violation['message']}")
                
                print(f"  Quality Score: {governance.get('quality_score', 0):.2f}")
                print()
    
    def _output_repair_results(self, results: Dict[str, Any], args) -> None:
        """Output repair results in the specified format."""
        if args.output == "json":
            print(json.dumps(results, indent=2))
        elif args.output == "summary":
            summary = results.get("orchestration_summary", {})
            print(f"Repair Summary:")
            print(f"  Status: {summary.get('status', 'unknown').upper()}")
            print(f"  Duration: {summary.get('duration_seconds', 0):.2f}s")
            
            successful = len(results.get("successful_repairs", []))
            failed = len(results.get("failed_repairs", []))
            print(f"  Successful Repairs: {successful}")
            print(f"  Failed Repairs: {failed}")
        else:
            # Text output
            print("Makefile Repair Results")
            print("=" * 50)
            
            # Orchestration summary
            summary = results.get("orchestration_summary", {})
            print(f"Orchestration ID: {summary.get('orchestration_id', 'N/A')}")
            print(f"Status: {summary.get('status', 'unknown').upper()}")
            print(f"Duration: {summary.get('duration_seconds', 0):.2f} seconds")
            print()
            
            # Individual results
            repair_results = results.get("repair_results", {})
            validation_results = results.get("validation_results", {})
            
            for makefile_path in repair_results.keys():
                print(f"Makefile: {makefile_path}")
                
                # Repair results
                repair = repair_results.get(makefile_path, {})
                if repair.get("repair_successful", False):
                    print("  ✓ Repair: SUCCESSFUL")
                    if repair.get("backup_path"):
                        print(f"    Backup: {repair['backup_path']}")
                else:
                    print("  ✗ Repair: FAILED")
                
                # Post-repair validation
                validation = validation_results.get(makefile_path, {})
                if validation.get("is_valid", False):
                    print("  ✓ Post-Repair Validation: PASSED")
                else:
                    errors = validation.get("error_count", 0)
                    print(f"  ✗ Post-Repair Validation: FAILED ({errors} errors remaining)")
                
                print()


async def main():
    """Main entry point for the CLI."""
    cli = MakefileParallelExecutionCLI()
    exit_code = await cli.run(sys.argv[1:])
    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())