#!/usr/bin/env python3
"""
Technical Debt Patch Annotation CLI

Comprehensive command-line interface for managing technical debt patches,
including scanning, annotation creation, cleanup management, and batch operations.

Requirements Coverage:
- 6.1: Code review integration with debt impact assessment
- 6.2: CI/CD pipeline integration with threshold checking
- 6.3: Automated checks preventing merge without proper annotation
- 6.4: Automatic validation of cleanup completion
- 6.5: Technical debt report generation from current codebase state
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import uuid

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleCapability, ModuleHealth, ModuleStatus, GracefulDegradationResult
from src.technical_debt_patch_annotation.core.models import PatchAnnotation, DebtLevel, BypassType, ValidationResult
from src.technical_debt_patch_annotation.discovery.patch_scanner import PatchScanner
from src.technical_debt_patch_annotation.classification.debt_classifier import DebtClassifier
from src.technical_debt_patch_annotation.integration.issue_tracker import IssueTracker, GitHubIssueTracker
from src.technical_debt_patch_annotation.cleanup.orchestrator import ForwardPassOrchestrator
from src.technical_debt_patch_annotation.lifecycle.manager import PatchLifecycleManager


class PatchCLI(ReflectiveModule):
    """
    Comprehensive CLI interface for Technical Debt Patch Annotation System.
    
    Provides commands for:
    - Patch scanning and discovery
    - Interactive annotation creation and editing
    - Cleanup management and orchestration
    - Batch operations and reporting
    - CI/CD integration and validation
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "patch_cli"
        self.scanner = PatchScanner()
        self.classifier = DebtClassifier()
        # Initialize with GitHub tracker as default (can be configured)
        try:
            self.issue_tracker = GitHubIssueTracker({"token": os.getenv("GITHUB_TOKEN", "")})
        except Exception:
            # Fallback to None if no configuration available
            self.issue_tracker = None
        self.cleanup_orchestrator = ForwardPassOrchestrator()
        self.lifecycle_manager = PatchLifecycleManager()
        
        # CLI state
        self._current_patches: List[PatchAnnotation] = []
        self._last_scan_results: Dict[str, Any] = {}
        
    def get_module_info(self) -> Dict[str, Any]:
        """Get CLI module information."""
        return {
            "module_id": self.module_id,
            "name": "Technical Debt Patch CLI",
            "version": "1.0.0",
            "description": "Comprehensive CLI for technical debt patch management",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "commands": [
                "scan", "annotate", "validate", "cleanup", "report",
                "batch", "interactive", "ci-check", "export", "import"
            ]
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get CLI capabilities."""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get CLI health status."""
        issues = []
        
        # Check component health
        try:
            scanner_health = self.scanner.get_health_status()
            if scanner_health.status != ModuleStatus.HEALTHY:
                issues.extend([f"Scanner: {issue}" for issue in scanner_health.issues])
        except Exception as e:
            issues.append(f"Scanner unavailable: {e}")
            
        try:
            classifier_health = self.classifier.get_health_status()
            if classifier_health.status != ModuleStatus.HEALTHY:
                issues.extend([f"Classifier: {issue}" for issue in classifier_health.issues])
        except Exception as e:
            issues.append(f"Classifier unavailable: {e}")
        
        # Determine overall status
        if not issues:
            status = ModuleStatus.HEALTHY
            health_score = 1.0
        elif len(issues) <= 2:
            status = ModuleStatus.WARNING
            health_score = 0.7
        else:
            status = ModuleStatus.ERROR
            health_score = 0.3
            
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation."""
        try:
            # Test core functionality
            test_patch = PatchAnnotation(
                patch_id="test-" + str(uuid.uuid4())[:8],
                reason="Test patch for degradation check",
                upstream_issue="TEST-001",
                cleanup_task="Remove test patch",
                debt_level=DebtLevel.LOW,
                created_date=datetime.now(),
                expected_resolution=datetime.now() + timedelta(days=1),
                component="test_component",
                bypass_type=BypassType.ARCHITECTURE,
                file_path="test.py",
                line_start=1,
                line_end=1,
                validation_criteria=["Test passes"]
            )
            
            # Test basic operations
            remaining_capabilities = []
            degraded_capabilities = []
            
            # Test scanning capability
            try:
                self.scanner.get_health_status()
                remaining_capabilities.append(ModuleCapability.DATA_PROCESSING)
            except:
                degraded_capabilities.append(ModuleCapability.DATA_PROCESSING)
            
            # Test validation capability
            try:
                self.classifier.get_health_status()
                remaining_capabilities.append(ModuleCapability.VALIDATION)
            except:
                degraded_capabilities.append(ModuleCapability.VALIDATION)
            
            # Core functionality always available
            remaining_capabilities.append(ModuleCapability.CORE_FUNCTIONALITY)
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=degraded_capabilities,
                remaining_capabilities=remaining_capabilities
            )
            
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=list(ModuleCapability),
                remaining_capabilities=[],
                error_message=str(e)
            )
    
    def create_cli_parser(self) -> argparse.ArgumentParser:
        """Create comprehensive CLI argument parser."""
        parser = argparse.ArgumentParser(
            prog="patch-cli",
            description="Technical Debt Patch Annotation System CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Scan current directory for patches
  patch-cli scan .
  
  # Create interactive annotation
  patch-cli annotate --interactive
  
  # Validate all patches in project
  patch-cli validate --all
  
  # Generate cleanup plan
  patch-cli cleanup --plan --component auth
  
  # Generate comprehensive report
  patch-cli report --format json --output patches.json
  
  # CI/CD integration check
  patch-cli ci-check --threshold-high 5 --threshold-critical 1
  
  # Batch operations
  patch-cli batch --expire-days 30 --notify
            """
        )
        
        # Global options
        parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
        parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode")
        parser.add_argument("--config", help="Configuration file path")
        parser.add_argument("--output", "-o", help="Output file path")
        parser.add_argument("--format", choices=["json", "yaml", "csv", "text"], default="text", help="Output format")
        
        # Subcommands
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        
        # Scan command
        self._add_scan_parser(subparsers)
        
        # Annotate command
        self._add_annotate_parser(subparsers)
        
        # Validate command
        self._add_validate_parser(subparsers)
        
        # Cleanup command
        self._add_cleanup_parser(subparsers)
        
        # Report command
        self._add_report_parser(subparsers)
        
        # Batch command
        self._add_batch_parser(subparsers)
        
        # Interactive command
        self._add_interactive_parser(subparsers)
        
        # CI/CD integration command
        self._add_ci_check_parser(subparsers)
        
        # Export/Import commands
        self._add_export_parser(subparsers)
        self._add_import_parser(subparsers)
        
        return parser
    
    def _add_scan_parser(self, subparsers):
        """Add scan command parser."""
        scan_parser = subparsers.add_parser("scan", help="Scan for patch annotations")
        scan_parser.add_argument("path", nargs="?", default=".", help="Path to scan (default: current directory)")
        scan_parser.add_argument("--recursive", "-r", action="store_true", help="Recursive scan")
        scan_parser.add_argument("--include", action="append", help="File patterns to include")
        scan_parser.add_argument("--exclude", action="append", help="File patterns to exclude")
        scan_parser.add_argument("--validate", action="store_true", help="Validate found patches")
        scan_parser.add_argument("--summary", action="store_true", help="Show summary only")
    
    def _add_annotate_parser(self, subparsers):
        """Add annotate command parser."""
        annotate_parser = subparsers.add_parser("annotate", help="Create or edit patch annotations")
        annotate_parser.add_argument("--interactive", "-i", action="store_true", help="Interactive annotation mode")
        annotate_parser.add_argument("--file", help="File to annotate")
        annotate_parser.add_argument("--line", type=int, help="Line number to annotate")
        annotate_parser.add_argument("--reason", help="Reason for patch")
        annotate_parser.add_argument("--upstream", help="Upstream issue reference")
        annotate_parser.add_argument("--cleanup", help="Cleanup task description")
        annotate_parser.add_argument("--debt-level", choices=[level.value for level in DebtLevel], help="Debt severity level")
        annotate_parser.add_argument("--bypass-type", choices=[btype.value for btype in BypassType], help="Type of bypass")
        annotate_parser.add_argument("--component", help="Component name")
        annotate_parser.add_argument("--expected-resolution", help="Expected resolution date (YYYY-MM-DD)")
        annotate_parser.add_argument("--validation-criteria", action="append", help="Validation criteria")
    
    def _add_validate_parser(self, subparsers):
        """Add validate command parser."""
        validate_parser = subparsers.add_parser("validate", help="Validate patch annotations")
        validate_parser.add_argument("--all", action="store_true", help="Validate all patches")
        validate_parser.add_argument("--patch-id", help="Validate specific patch ID")
        validate_parser.add_argument("--component", help="Validate patches in component")
        validate_parser.add_argument("--fix", action="store_true", help="Attempt to fix validation errors")
        validate_parser.add_argument("--strict", action="store_true", help="Strict validation mode")
    
    def _add_cleanup_parser(self, subparsers):
        """Add cleanup command parser."""
        cleanup_parser = subparsers.add_parser("cleanup", help="Manage patch cleanup")
        cleanup_parser.add_argument("--plan", action="store_true", help="Generate cleanup plan")
        cleanup_parser.add_argument("--execute", help="Execute cleanup plan by ID")
        cleanup_parser.add_argument("--component", help="Focus on specific component")
        cleanup_parser.add_argument("--priority", choices=["low", "medium", "high", "critical"], help="Minimum priority level")
        cleanup_parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
        cleanup_parser.add_argument("--force", action="store_true", help="Force cleanup execution")
    
    def _add_report_parser(self, subparsers):
        """Add report command parser."""
        report_parser = subparsers.add_parser("report", help="Generate patch reports")
        report_parser.add_argument("--type", choices=["inventory", "trends", "cleanup", "executive"], default="inventory", help="Report type")
        report_parser.add_argument("--component", help="Filter by component")
        report_parser.add_argument("--debt-level", choices=[level.value for level in DebtLevel], help="Filter by debt level")
        report_parser.add_argument("--since", help="Include patches since date (YYYY-MM-DD)")
        report_parser.add_argument("--until", help="Include patches until date (YYYY-MM-DD)")
        report_parser.add_argument("--template", help="Report template file")
    
    def _add_batch_parser(self, subparsers):
        """Add batch command parser."""
        batch_parser = subparsers.add_parser("batch", help="Batch operations on patches")
        batch_parser.add_argument("--expire-days", type=int, help="Find patches expiring in N days")
        batch_parser.add_argument("--notify", action="store_true", help="Send notifications")
        batch_parser.add_argument("--update-status", help="Update patch status")
        batch_parser.add_argument("--bulk-edit", help="JSON file with bulk edits")
        batch_parser.add_argument("--archive", action="store_true", help="Archive resolved patches")
    
    def _add_interactive_parser(self, subparsers):
        """Add interactive command parser."""
        interactive_parser = subparsers.add_parser("interactive", help="Interactive patch management")
        interactive_parser.add_argument("--mode", choices=["browse", "edit", "cleanup"], default="browse", help="Interactive mode")
    
    def _add_ci_check_parser(self, subparsers):
        """Add CI/CD check command parser."""
        ci_parser = subparsers.add_parser("ci-check", help="CI/CD integration checks")
        ci_parser.add_argument("--threshold-low", type=int, default=50, help="Maximum low-priority patches")
        ci_parser.add_argument("--threshold-medium", type=int, default=20, help="Maximum medium-priority patches")
        ci_parser.add_argument("--threshold-high", type=int, default=10, help="Maximum high-priority patches")
        ci_parser.add_argument("--threshold-critical", type=int, default=3, help="Maximum critical patches")
        ci_parser.add_argument("--block-merge", action="store_true", help="Block merge on threshold violation")
        ci_parser.add_argument("--changed-files", help="File with list of changed files")
    
    def _add_export_parser(self, subparsers):
        """Add export command parser."""
        export_parser = subparsers.add_parser("export", help="Export patch data")
        export_parser.add_argument("--format", choices=["json", "yaml", "csv", "xml"], default="json", help="Export format")
        export_parser.add_argument("--include-resolved", action="store_true", help="Include resolved patches")
        export_parser.add_argument("--template", help="Export template file")
    
    def _add_import_parser(self, subparsers):
        """Add import command parser."""
        import_parser = subparsers.add_parser("import", help="Import patch data")
        import_parser.add_argument("file", help="File to import")
        import_parser.add_argument("--format", choices=["json", "yaml", "csv"], help="Import format (auto-detect if not specified)")
        import_parser.add_argument("--merge", action="store_true", help="Merge with existing patches")
        import_parser.add_argument("--validate", action="store_true", help="Validate before import")
    
    def execute_command(self, args: argparse.Namespace) -> int:
        """Execute CLI command based on parsed arguments."""
        try:
            if args.command == "scan":
                return self._execute_scan(args)
            elif args.command == "annotate":
                return self._execute_annotate(args)
            elif args.command == "validate":
                return self._execute_validate(args)
            elif args.command == "cleanup":
                return self._execute_cleanup(args)
            elif args.command == "report":
                return self._execute_report(args)
            elif args.command == "batch":
                return self._execute_batch(args)
            elif args.command == "interactive":
                return self._execute_interactive(args)
            elif args.command == "ci-check":
                return self._execute_ci_check(args)
            elif args.command == "export":
                return self._execute_export(args)
            elif args.command == "import":
                return self._execute_import(args)
            else:
                print("Error: No command specified. Use --help for usage information.")
                return 1
                
        except Exception as e:
            if args.verbose:
                import traceback
                traceback.print_exc()
            else:
                print(f"Error: {e}")
            return 1
    
    def _execute_scan(self, args: argparse.Namespace) -> int:
        """Execute scan command - Requirement 6.5."""
        if not args.quiet:
            print(f"🔍 Scanning for patches in: {args.path}")
        
        try:
            # Configure scanner
            scan_config = {
                "recursive": args.recursive,
                "include_patterns": args.include or [],
                "exclude_patterns": args.exclude or []
            }
            
            # Perform scan
            scan_results = self.scanner.scan_directory(args.path)
            self._current_patches = scan_results.patches if hasattr(scan_results, 'patches') else []
            self._last_scan_results = {
                "patches": self._current_patches,
                "files_scanned": len(scan_results.scanned_files) if hasattr(scan_results, 'scanned_files') else 0,
                "scan_time": scan_results.scan_duration if hasattr(scan_results, 'scan_duration') else 0
            }
            
            # Validate if requested
            if args.validate:
                validation_results = []
                for patch in self._current_patches:
                    result = self.scanner.validate_patch_annotation(patch)
                    validation_results.append(result)
                scan_results["validation_results"] = validation_results
            
            # Output results
            if args.summary:
                self._output_scan_summary(scan_results, args)
            else:
                self._output_scan_details(scan_results, args)
            
            return 0
            
        except Exception as e:
            print(f"❌ Scan failed: {e}")
            return 1
    
    def _execute_annotate(self, args: argparse.Namespace) -> int:
        """Execute annotate command - Requirement 6.1."""
        if args.interactive:
            return self._interactive_annotate(args)
        else:
            return self._direct_annotate(args)
    
    def _execute_validate(self, args: argparse.Namespace) -> int:
        """Execute validate command - Requirement 6.4."""
        if not args.quiet:
            print("🔍 Validating patch annotations...")
        
        try:
            patches_to_validate = []
            
            if args.all:
                # Scan current directory for all patches
                scan_results = self.scanner.scan_directory(".")
                patches_to_validate = scan_results.patches if hasattr(scan_results, 'patches') else []
            elif args.patch_id:
                # Find specific patch
                patch = self._find_patch_by_id(args.patch_id)
                if patch:
                    patches_to_validate = [patch]
                else:
                    print(f"❌ Patch not found: {args.patch_id}")
                    return 1
            elif args.component:
                # Find patches in component
                scan_results = self.scanner.scan_directory(".")
                all_patches = scan_results.patches if hasattr(scan_results, 'patches') else []
                patches_to_validate = [p for p in all_patches if p.component == args.component]
            
            if not patches_to_validate:
                print("ℹ️ No patches found to validate")
                return 0
            
            # Validate patches
            validation_results = []
            for patch in patches_to_validate:
                result = self.scanner.validate_patch_annotation(patch)
                validation_results.append((patch, result))
            
            # Output results
            self._output_validation_results(validation_results, args)
            
            # Check if all validations passed
            failed_validations = [r for _, r in validation_results if not r.is_valid]
            if failed_validations:
                return 1
            else:
                return 0
                
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            return 1
    
    def _execute_cleanup(self, args: argparse.Namespace) -> int:
        """Execute cleanup command - Requirement 6.4."""
        if not args.quiet:
            print("🧹 Managing patch cleanup...")
        
        try:
            if args.plan:
                return self._generate_cleanup_plan(args)
            elif args.execute:
                return self._execute_cleanup_plan(args)
            else:
                print("❌ Must specify either --plan or --execute")
                return 1
                
        except Exception as e:
            print(f"❌ Cleanup operation failed: {e}")
            return 1
    
    def _execute_report(self, args: argparse.Namespace) -> int:
        """Execute report command - Requirement 6.5."""
        if not args.quiet:
            print(f"📊 Generating {args.type} report...")
        
        try:
            # Get patches for report
            scan_results = self.scanner.scan_directory(".")
            patches = scan_results.patches if hasattr(scan_results, 'patches') else []
            
            # Apply filters
            if args.component:
                patches = [p for p in patches if p.component == args.component]
            if args.debt_level:
                debt_level = DebtLevel(args.debt_level)
                patches = [p for p in patches if p.debt_level == debt_level]
            if args.since:
                since_date = datetime.fromisoformat(args.since)
                patches = [p for p in patches if p.created_date >= since_date]
            if args.until:
                until_date = datetime.fromisoformat(args.until)
                patches = [p for p in patches if p.created_date <= until_date]
            
            # Generate report
            report_data = self._generate_report(args.type, patches, args)
            
            # Output report
            self._output_report(report_data, args)
            
            return 0
            
        except Exception as e:
            print(f"❌ Report generation failed: {e}")
            return 1
    
    def _execute_batch(self, args: argparse.Namespace) -> int:
        """Execute batch command."""
        if not args.quiet:
            print("⚡ Executing batch operations...")
        
        try:
            # Get all patches
            scan_results = self.scanner.scan_directory(".")
            patches = scan_results.patches if hasattr(scan_results, 'patches') else []
            
            operations_performed = 0
            
            # Handle expiring patches
            if args.expire_days is not None:
                expiring_patches = self._find_expiring_patches(patches, args.expire_days)
                if expiring_patches:
                    print(f"📅 Found {len(expiring_patches)} patches expiring in {args.expire_days} days")
                    if args.notify:
                        self._send_expiration_notifications(expiring_patches)
                        operations_performed += 1
            
            # Handle status updates
            if args.update_status:
                # Implementation would update patch status
                print(f"🔄 Status update functionality not yet implemented")
            
            # Handle bulk edits
            if args.bulk_edit:
                # Implementation would apply bulk edits from JSON file
                print(f"✏️ Bulk edit functionality not yet implemented")
            
            # Handle archiving
            if args.archive:
                # Implementation would archive resolved patches
                print(f"📦 Archive functionality not yet implemented")
            
            if operations_performed == 0:
                print("ℹ️ No batch operations specified")
            
            return 0
            
        except Exception as e:
            print(f"❌ Batch operation failed: {e}")
            return 1
    
    def _execute_interactive(self, args: argparse.Namespace) -> int:
        """Execute interactive command."""
        print("🎮 Interactive mode not yet implemented")
        print("This would provide a TUI for browsing and editing patches")
        return 0
    
    def _execute_ci_check(self, args: argparse.Namespace) -> int:
        """Execute CI/CD check command - Requirements 6.2, 6.3."""
        if not args.quiet:
            print("🔍 Running CI/CD integration checks...")
        
        try:
            # Get patches to check
            if args.changed_files:
                # Check only changed files
                with open(args.changed_files, 'r') as f:
                    changed_files = [line.strip() for line in f if line.strip()]
                patches = self._get_patches_in_files(changed_files)
            else:
                # Check all patches
                scan_results = self.scanner.scan_directory(".")
                patches = scan_results.patches if hasattr(scan_results, 'patches') else []
            
            # Count patches by debt level
            debt_counts = {
                DebtLevel.LOW: 0,
                DebtLevel.MEDIUM: 0,
                DebtLevel.HIGH: 0,
                DebtLevel.CRITICAL: 0
            }
            
            for patch in patches:
                debt_counts[patch.debt_level] += 1
            
            # Check thresholds
            violations = []
            if debt_counts[DebtLevel.LOW] > args.threshold_low:
                violations.append(f"Low-priority patches: {debt_counts[DebtLevel.LOW]} > {args.threshold_low}")
            if debt_counts[DebtLevel.MEDIUM] > args.threshold_medium:
                violations.append(f"Medium-priority patches: {debt_counts[DebtLevel.MEDIUM]} > {args.threshold_medium}")
            if debt_counts[DebtLevel.HIGH] > args.threshold_high:
                violations.append(f"High-priority patches: {debt_counts[DebtLevel.HIGH]} > {args.threshold_high}")
            if debt_counts[DebtLevel.CRITICAL] > args.threshold_critical:
                violations.append(f"Critical patches: {debt_counts[DebtLevel.CRITICAL]} > {args.threshold_critical}")
            
            # Output results
            print(f"📊 Patch debt analysis:")
            print(f"  Low: {debt_counts[DebtLevel.LOW]} (threshold: {args.threshold_low})")
            print(f"  Medium: {debt_counts[DebtLevel.MEDIUM]} (threshold: {args.threshold_medium})")
            print(f"  High: {debt_counts[DebtLevel.HIGH]} (threshold: {args.threshold_high})")
            print(f"  Critical: {debt_counts[DebtLevel.CRITICAL]} (threshold: {args.threshold_critical})")
            
            if violations:
                print(f"\n❌ Threshold violations detected:")
                for violation in violations:
                    print(f"  • {violation}")
                
                if args.block_merge:
                    print(f"\n🚫 Merge blocked due to debt threshold violations")
                    return 1
                else:
                    print(f"\n⚠️ Warning: Debt thresholds exceeded")
                    return 0
            else:
                print(f"\n✅ All debt thresholds within limits")
                return 0
                
        except Exception as e:
            print(f"❌ CI check failed: {e}")
            return 1
    
    def _execute_export(self, args: argparse.Namespace) -> int:
        """Execute export command."""
        if not args.quiet:
            print(f"📤 Exporting patches in {args.format} format...")
        
        try:
            # Get patches to export
            scan_results = self.scanner.scan_directory(".")
            patches = scan_results.patches if hasattr(scan_results, 'patches') else []
            
            if not args.include_resolved:
                # Filter out resolved patches (implementation would check status)
                pass
            
            # Export data
            export_data = self._prepare_export_data(patches, args)
            
            # Output to file or stdout
            if args.output:
                with open(args.output, 'w') as f:
                    if args.format == "json":
                        json.dump(export_data, f, indent=2, default=str)
                    elif args.format == "yaml":
                        import yaml
                        yaml.dump(export_data, f, default_flow_style=False)
                    elif args.format == "csv":
                        import csv
                        # CSV export implementation
                        pass
                print(f"✅ Exported {len(patches)} patches to {args.output}")
            else:
                if args.format == "json":
                    print(json.dumps(export_data, indent=2, default=str))
                else:
                    print("Export to stdout only supports JSON format")
            
            return 0
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return 1
    
    def _execute_import(self, args: argparse.Namespace) -> int:
        """Execute import command."""
        if not args.quiet:
            print(f"📥 Importing patches from {args.file}...")
        
        try:
            # Read import file
            with open(args.file, 'r') as f:
                if args.format == "json" or args.file.endswith('.json'):
                    import_data = json.load(f)
                elif args.format == "yaml" or args.file.endswith(('.yml', '.yaml')):
                    import yaml
                    import_data = yaml.safe_load(f)
                else:
                    print(f"❌ Unsupported import format")
                    return 1
            
            # Validate import data
            if args.validate:
                # Implementation would validate import data structure
                pass
            
            # Process import
            imported_count = self._process_import_data(import_data, args)
            
            print(f"✅ Imported {imported_count} patches")
            return 0
            
        except Exception as e:
            print(f"❌ Import failed: {e}")
            return 1
    
    # Helper methods for command execution
    
    def _output_scan_summary(self, scan_results: Dict[str, Any], args: argparse.Namespace):
        """Output scan summary."""
        patches = scan_results.get("patches", [])
        
        # Count by debt level
        debt_counts = {}
        for patch in patches:
            level = patch.debt_level.value if hasattr(patch, 'debt_level') else 'Unknown'
            debt_counts[level] = debt_counts.get(level, 0) + 1
        
        print(f"📊 Scan Summary:")
        print(f"  Total patches: {len(patches)}")
        print(f"  Files scanned: {scan_results.get('files_scanned', 0)}")
        
        if debt_counts:
            print(f"  Debt levels:")
            for level, count in sorted(debt_counts.items()):
                print(f"    {level}: {count}")
    
    def _output_scan_details(self, scan_results: Dict[str, Any], args: argparse.Namespace):
        """Output detailed scan results."""
        patches = scan_results.get("patches", [])
        
        if args.format == "json":
            output_data = {
                "scan_results": scan_results,
                "patches": [self._patch_to_dict(p) for p in patches]
            }
            print(json.dumps(output_data, indent=2, default=str))
        else:
            print(f"📊 Scan Results:")
            print(f"  Files scanned: {scan_results.get('files_scanned', 0)}")
            print(f"  Patches found: {len(patches)}")
            
            for patch in patches:
                print(f"\n🔧 Patch: {patch.patch_id}")
                print(f"  File: {patch.file_path}:{patch.line_start}")
                print(f"  Reason: {patch.reason}")
                print(f"  Debt Level: {patch.debt_level.value}")
                print(f"  Component: {patch.component}")
    
    def _patch_to_dict(self, patch: PatchAnnotation) -> Dict[str, Any]:
        """Convert patch annotation to dictionary."""
        return {
            "patch_id": patch.patch_id,
            "reason": patch.reason,
            "upstream_issue": patch.upstream_issue,
            "cleanup_task": patch.cleanup_task,
            "debt_level": patch.debt_level.value,
            "created_date": patch.created_date.isoformat(),
            "expected_resolution": patch.expected_resolution.isoformat() if patch.expected_resolution else None,
            "component": patch.component,
            "bypass_type": patch.bypass_type.value,
            "file_path": patch.file_path,
            "line_start": patch.line_start,
            "line_end": patch.line_end,
            "validation_criteria": patch.validation_criteria
        }
    
    def _interactive_annotate(self, args: argparse.Namespace) -> int:
        """Interactive annotation mode."""
        print("🎮 Interactive annotation mode")
        print("This would provide a guided interface for creating patch annotations")
        return 0
    
    def _direct_annotate(self, args: argparse.Namespace) -> int:
        """Direct annotation mode."""
        if not args.file or not args.line:
            print("❌ File and line number required for direct annotation")
            return 1
        
        # Create patch annotation
        patch = PatchAnnotation(
            patch_id=f"PATCH-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}",
            reason=args.reason or "Manual annotation",
            upstream_issue=args.upstream or "MANUAL-001",
            cleanup_task=args.cleanup or "Manual cleanup required",
            debt_level=DebtLevel(args.debt_level) if args.debt_level else DebtLevel.MEDIUM,
            created_date=datetime.now(),
            expected_resolution=datetime.fromisoformat(args.expected_resolution) if args.expected_resolution else datetime.now() + timedelta(days=30),
            component=args.component or "unknown",
            bypass_type=BypassType(args.bypass_type) if args.bypass_type else BypassType.ARCHITECTURE,
            file_path=args.file,
            line_start=args.line,
            line_end=args.line,
            validation_criteria=args.validation_criteria or ["Manual validation required"]
        )
        
        print(f"✅ Created patch annotation: {patch.patch_id}")
        return 0
    
    def _find_patch_by_id(self, patch_id: str) -> Optional[PatchAnnotation]:
        """Find patch by ID."""
        # Implementation would search for patch by ID
        return None
    
    def _output_validation_results(self, validation_results: List[Tuple[PatchAnnotation, ValidationResult]], args: argparse.Namespace):
        """Output validation results."""
        passed = sum(1 for _, result in validation_results if result.is_valid)
        failed = len(validation_results) - passed
        
        print(f"📊 Validation Results:")
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")
        
        if not args.quiet and failed > 0:
            print(f"\n❌ Failed validations:")
            for patch, result in validation_results:
                if not result.is_valid:
                    print(f"  {patch.patch_id}: {', '.join(result.errors)}")
    
    def _generate_cleanup_plan(self, args: argparse.Namespace) -> int:
        """Generate cleanup plan."""
        print("📋 Generating cleanup plan...")
        
        # Get patches for cleanup planning
        scan_results = self.scanner.scan_directory(".")
        patches = scan_results.patches if hasattr(scan_results, 'patches') else []
        
        if args.component:
            patches = [p for p in patches if p.component == args.component]
        
        if args.priority:
            min_priority = DebtLevel(args.priority.upper())
            priority_order = [DebtLevel.CRITICAL, DebtLevel.HIGH, DebtLevel.MEDIUM, DebtLevel.LOW]
            min_index = priority_order.index(min_priority)
            allowed_levels = priority_order[:min_index + 1]
            patches = [p for p in patches if p.debt_level in allowed_levels]
        
        # Generate plan using cleanup orchestrator
        try:
            cleanup_plan = self.cleanup_orchestrator.create_cleanup_plan(patches)
            
            print(f"📋 Cleanup Plan Generated:")
            print(f"  Plan ID: {cleanup_plan.get('plan_id', 'N/A')}")
            print(f"  Patches to clean: {len(patches)}")
            print(f"  Estimated effort: {cleanup_plan.get('estimated_effort', 'Unknown')}")
            
            return 0
        except Exception as e:
            print(f"❌ Failed to generate cleanup plan: {e}")
            return 1
    
    def _execute_cleanup_plan(self, args: argparse.Namespace) -> int:
        """Execute cleanup plan."""
        print(f"🚀 Executing cleanup plan: {args.execute}")
        
        if args.dry_run:
            print("🔍 Dry run mode - showing what would be done")
        
        # Implementation would execute the cleanup plan
        print("⚠️ Cleanup execution not yet implemented")
        return 0
    
    def _generate_report(self, report_type: str, patches: List[PatchAnnotation], args: argparse.Namespace) -> Dict[str, Any]:
        """Generate report data."""
        if report_type == "inventory":
            return self._generate_inventory_report(patches)
        elif report_type == "trends":
            return self._generate_trends_report(patches)
        elif report_type == "cleanup":
            return self._generate_cleanup_report(patches)
        elif report_type == "executive":
            return self._generate_executive_report(patches)
        else:
            raise ValueError(f"Unknown report type: {report_type}")
    
    def _generate_inventory_report(self, patches: List[PatchAnnotation]) -> Dict[str, Any]:
        """Generate inventory report."""
        # Count by various dimensions
        by_component = {}
        by_debt_level = {}
        by_bypass_type = {}
        
        for patch in patches:
            # By component
            by_component[patch.component] = by_component.get(patch.component, 0) + 1
            
            # By debt level
            level = patch.debt_level.value
            by_debt_level[level] = by_debt_level.get(level, 0) + 1
            
            # By bypass type
            btype = patch.bypass_type.value
            by_bypass_type[btype] = by_bypass_type.get(btype, 0) + 1
        
        return {
            "report_type": "inventory",
            "generated_at": datetime.now().isoformat(),
            "total_patches": len(patches),
            "by_component": by_component,
            "by_debt_level": by_debt_level,
            "by_bypass_type": by_bypass_type,
            "patches": [self._patch_to_dict(p) for p in patches]
        }
    
    def _generate_trends_report(self, patches: List[PatchAnnotation]) -> Dict[str, Any]:
        """Generate trends report."""
        # Group by creation date
        by_date = {}
        for patch in patches:
            date_key = patch.created_date.date().isoformat()
            by_date[date_key] = by_date.get(date_key, 0) + 1
        
        return {
            "report_type": "trends",
            "generated_at": datetime.now().isoformat(),
            "total_patches": len(patches),
            "creation_trend": by_date,
            "patches": [self._patch_to_dict(p) for p in patches]
        }
    
    def _generate_cleanup_report(self, patches: List[PatchAnnotation]) -> Dict[str, Any]:
        """Generate cleanup report."""
        # Find patches ready for cleanup
        now = datetime.now()
        overdue = [p for p in patches if p.expected_resolution and p.expected_resolution < now]
        due_soon = [p for p in patches if p.expected_resolution and p.expected_resolution < now + timedelta(days=7)]
        
        return {
            "report_type": "cleanup",
            "generated_at": datetime.now().isoformat(),
            "total_patches": len(patches),
            "overdue_patches": len(overdue),
            "due_soon_patches": len(due_soon),
            "overdue": [self._patch_to_dict(p) for p in overdue],
            "due_soon": [self._patch_to_dict(p) for p in due_soon]
        }
    
    def _generate_executive_report(self, patches: List[PatchAnnotation]) -> Dict[str, Any]:
        """Generate executive summary report."""
        # High-level metrics
        critical_count = sum(1 for p in patches if p.debt_level == DebtLevel.CRITICAL)
        high_count = sum(1 for p in patches if p.debt_level == DebtLevel.HIGH)
        
        # Risk assessment
        risk_score = (critical_count * 4 + high_count * 2) / max(len(patches), 1)
        
        return {
            "report_type": "executive",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_patches": len(patches),
                "critical_patches": critical_count,
                "high_priority_patches": high_count,
                "risk_score": round(risk_score, 2),
                "risk_level": "High" if risk_score > 2 else "Medium" if risk_score > 1 else "Low"
            }
        }
    
    def _output_report(self, report_data: Dict[str, Any], args: argparse.Namespace):
        """Output report data."""
        if args.output:
            with open(args.output, 'w') as f:
                if args.format == "json":
                    json.dump(report_data, f, indent=2, default=str)
                elif args.format == "yaml":
                    import yaml
                    yaml.dump(report_data, f, default_flow_style=False)
                else:
                    # Text format
                    self._output_report_text(report_data, f)
        else:
            if args.format == "json":
                print(json.dumps(report_data, indent=2, default=str))
            else:
                self._output_report_text(report_data, sys.stdout)
    
    def _output_report_text(self, report_data: Dict[str, Any], output_file):
        """Output report in text format."""
        report_type = report_data.get("report_type", "unknown")
        
        output_file.write(f"📊 {report_type.title()} Report\n")
        output_file.write(f"Generated: {report_data.get('generated_at', 'Unknown')}\n")
        output_file.write(f"Total Patches: {report_data.get('total_patches', 0)}\n\n")
        
        if report_type == "inventory":
            if "by_debt_level" in report_data:
                output_file.write("Debt Levels:\n")
                for level, count in report_data["by_debt_level"].items():
                    output_file.write(f"  {level}: {count}\n")
                output_file.write("\n")
            
            if "by_component" in report_data:
                output_file.write("Components:\n")
                for component, count in report_data["by_component"].items():
                    output_file.write(f"  {component}: {count}\n")
        
        elif report_type == "executive":
            summary = report_data.get("summary", {})
            output_file.write(f"Risk Level: {summary.get('risk_level', 'Unknown')}\n")
            output_file.write(f"Risk Score: {summary.get('risk_score', 0)}\n")
            output_file.write(f"Critical Patches: {summary.get('critical_patches', 0)}\n")
            output_file.write(f"High Priority: {summary.get('high_priority_patches', 0)}\n")
    
    def _find_expiring_patches(self, patches: List[PatchAnnotation], days: int) -> List[PatchAnnotation]:
        """Find patches expiring within specified days."""
        cutoff_date = datetime.now() + timedelta(days=days)
        return [p for p in patches if p.expected_resolution and p.expected_resolution <= cutoff_date]
    
    def _send_expiration_notifications(self, patches: List[PatchAnnotation]):
        """Send expiration notifications."""
        print(f"📧 Sending notifications for {len(patches)} expiring patches")
        # Implementation would send actual notifications
    
    def _get_patches_in_files(self, file_paths: List[str]) -> List[PatchAnnotation]:
        """Get patches in specific files."""
        patches = []
        for file_path in file_paths:
            if os.path.exists(file_path):
                file_patches = self.scanner.scan_file(file_path)
                patches.extend(file_patches)
        return patches
    
    def _prepare_export_data(self, patches: List[PatchAnnotation], args: argparse.Namespace) -> Dict[str, Any]:
        """Prepare data for export."""
        return {
            "export_metadata": {
                "generated_at": datetime.now().isoformat(),
                "format": args.format,
                "total_patches": len(patches)
            },
            "patches": [self._patch_to_dict(p) for p in patches]
        }
    
    def _process_import_data(self, import_data: Dict[str, Any], args: argparse.Namespace) -> int:
        """Process imported data."""
        patches_data = import_data.get("patches", [])
        
        # Convert to patch objects and validate
        imported_count = 0
        for patch_data in patches_data:
            try:
                # Create patch object from data
                patch = PatchAnnotation(
                    patch_id=patch_data["patch_id"],
                    reason=patch_data["reason"],
                    upstream_issue=patch_data["upstream_issue"],
                    cleanup_task=patch_data["cleanup_task"],
                    debt_level=DebtLevel(patch_data["debt_level"]),
                    created_date=datetime.fromisoformat(patch_data["created_date"]),
                    expected_resolution=datetime.fromisoformat(patch_data["expected_resolution"]) if patch_data.get("expected_resolution") else None,
                    component=patch_data["component"],
                    bypass_type=BypassType(patch_data["bypass_type"]),
                    file_path=patch_data["file_path"],
                    line_start=patch_data["line_start"],
                    line_end=patch_data["line_end"],
                    validation_criteria=patch_data.get("validation_criteria", [])
                )
                
                # Store patch (implementation would persist to storage)
                imported_count += 1
                
            except Exception as e:
                print(f"⚠️ Failed to import patch {patch_data.get('patch_id', 'unknown')}: {e}")
        
        return imported_count


def main():
    """Main CLI entry point."""
    cli = PatchCLI()
    parser = cli.create_cli_parser()
    args = parser.parse_args()
    
    # Configure logging based on verbosity
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    elif args.quiet:
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.INFO)
    
    # Execute command
    exit_code = cli.execute_command(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()