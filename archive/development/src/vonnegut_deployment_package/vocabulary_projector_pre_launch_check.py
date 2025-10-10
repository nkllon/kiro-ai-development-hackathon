#!/usr/bin/env python3
"""
Multi-Dimensional Vocabulary Projector Pre-Launch Check
=======================================================

Validates system readiness for DAG orchestration execution.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass

@dataclass
class CheckResult:
    """Result of a pre-launch check."""
    name: str
    passed: bool
    message: str
    details: str = ""

class VocabularyProjectorPreLaunchCheck:
    """Pre-launch validation for vocabulary projector DAG execution."""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.results: List[CheckResult] = []
    
    def run_all_checks(self) -> bool:
        """Run all pre-launch checks."""
        print("🔍 Multi-Dimensional Vocabulary Projector Pre-Launch Check")
        print("=" * 60)
        
        checks = [
            self.check_python_environment,
            self.check_project_structure,
            self.check_vocabulary_source_data,
            self.check_core_implementation,
            self.check_dag_orchestration_infrastructure,
            self.check_output_directories,
            self.check_dependencies,
            self.check_permissions,
            self.check_disk_space,
            self.check_existing_projections
        ]
        
        for check in checks:
            try:
                result = check()
                self.results.append(result)
                status = "✅" if result.passed else "❌"
                print(f"{status} {result.name}: {result.message}")
                if result.details and not result.passed:
                    print(f"   Details: {result.details}")
            except Exception as e:
                self.results.append(CheckResult(
                    name=check.__name__,
                    passed=False,
                    message=f"Check failed with exception: {str(e)}"
                ))
                print(f"❌ {check.__name__}: Exception - {str(e)}")
        
        # Summary
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        
        print("\n" + "=" * 60)
        print(f"📊 Pre-Launch Check Summary: {passed}/{total} checks passed")
        
        if passed == total:
            print("🚀 System ready for DAG orchestration launch!")
            return True
        else:
            print("⚠️  System not ready. Please address failed checks before launch.")
            self.print_failed_checks()
            return False
    
    def check_python_environment(self) -> CheckResult:
        """Check Python version and virtual environment."""
        try:
            python_version = sys.version_info
            if python_version.major != 3 or python_version.minor < 9:
                return CheckResult(
                    name="Python Environment",
                    passed=False,
                    message=f"Python {python_version.major}.{python_version.minor} detected",
                    details="Python 3.9+ required for vocabulary projector"
                )
            
            # Check if in virtual environment
            in_venv = hasattr(sys, 'real_prefix') or (
                hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
            )
            
            return CheckResult(
                name="Python Environment",
                passed=True,
                message=f"Python {python_version.major}.{python_version.minor}.{python_version.micro}" + 
                       (" (venv)" if in_venv else " (system)")
            )
        except Exception as e:
            return CheckResult(
                name="Python Environment",
                passed=False,
                message="Failed to check Python environment",
                details=str(e)
            )
    
    def check_project_structure(self) -> CheckResult:
        """Check required project structure exists."""
        required_paths = [
            "src/multi_dimensional_vocabulary_projector.py",
            ".kiro/specs/multi-dimensional-vocabulary-projector/requirements.md",
            ".kiro/specs/multi-dimensional-vocabulary-projector/design.md",
            ".kiro/specs/multi-dimensional-vocabulary-projector/tasks.md",
            "docs/ubiquitous_language_vocabulary.md"
        ]
        
        missing_paths = []
        for path in required_paths:
            if not (self.project_root / path).exists():
                missing_paths.append(path)
        
        if missing_paths:
            return CheckResult(
                name="Project Structure",
                passed=False,
                message=f"{len(missing_paths)} required files missing",
                details=f"Missing: {', '.join(missing_paths)}"
            )
        
        return CheckResult(
            name="Project Structure",
            passed=True,
            message="All required project files present"
        )
    
    def check_vocabulary_source_data(self) -> CheckResult:
        """Check vocabulary source data quality."""
        vocab_file = self.project_root / "docs/ubiquitous_language_vocabulary.md"
        
        if not vocab_file.exists():
            return CheckResult(
                name="Vocabulary Source Data",
                passed=False,
                message="Vocabulary source file not found",
                details="docs/ubiquitous_language_vocabulary.md missing"
            )
        
        try:
            content = vocab_file.read_text()
            
            # Basic content validation
            if len(content) < 1000:
                return CheckResult(
                    name="Vocabulary Source Data",
                    passed=False,
                    message="Vocabulary file appears incomplete",
                    details=f"File size: {len(content)} characters (expected >1000)"
                )
            
            # Check for key sections
            required_sections = ["Definition:", "Context:", "Related Terms:"]
            missing_sections = [s for s in required_sections if s not in content]
            
            if missing_sections:
                return CheckResult(
                    name="Vocabulary Source Data",
                    passed=False,
                    message="Vocabulary file missing required sections",
                    details=f"Missing: {', '.join(missing_sections)}"
                )
            
            # Count terms (rough estimate)
            term_count = content.count("### ")
            
            return CheckResult(
                name="Vocabulary Source Data",
                passed=True,
                message=f"Vocabulary file valid (~{term_count} terms)"
            )
            
        except Exception as e:
            return CheckResult(
                name="Vocabulary Source Data",
                passed=False,
                message="Failed to read vocabulary file",
                details=str(e)
            )
    
    def check_core_implementation(self) -> CheckResult:
        """Check core implementation can be imported."""
        try:
            # Try to import the main module
            sys.path.insert(0, str(self.project_root / "src"))
            import multi_dimensional_vocabulary_projector as mvp
            
            # Check key classes exist
            required_classes = [
                "VocabularyTerm",
                "ProjectionDimension", 
                "MultiDimensionalVocabularyProjector"
            ]
            
            missing_classes = []
            for cls_name in required_classes:
                if not hasattr(mvp, cls_name):
                    missing_classes.append(cls_name)
            
            if missing_classes:
                return CheckResult(
                    name="Core Implementation",
                    passed=False,
                    message="Missing required classes",
                    details=f"Missing: {', '.join(missing_classes)}"
                )
            
            # Try to instantiate the main class
            projector = mvp.MultiDimensionalVocabularyProjector()
            
            return CheckResult(
                name="Core Implementation",
                passed=True,
                message="Core implementation imports and instantiates successfully"
            )
            
        except ImportError as e:
            return CheckResult(
                name="Core Implementation",
                passed=False,
                message="Failed to import core module",
                details=str(e)
            )
        except Exception as e:
            return CheckResult(
                name="Core Implementation",
                passed=False,
                message="Core implementation error",
                details=str(e)
            )
    
    def check_dag_orchestration_infrastructure(self) -> CheckResult:
        """Check DAG orchestration infrastructure availability."""
        dag_paths = [
            "src/dag_orchestration/core/dag_orchestrator.py",
            "src/dag_orchestration/execution/parallel_execution_engine.py",
            "src/dag_orchestration/execution/dependency_aware_scheduler.py"
        ]
        
        available_paths = []
        for path in dag_paths:
            if (self.project_root / path).exists():
                available_paths.append(path)
        
        if len(available_paths) == 0:
            return CheckResult(
                name="DAG Orchestration Infrastructure",
                passed=False,
                message="No DAG orchestration infrastructure found",
                details="Will use simple sequential execution"
            )
        elif len(available_paths) < len(dag_paths):
            return CheckResult(
                name="DAG Orchestration Infrastructure",
                passed=True,
                message=f"Partial DAG infrastructure ({len(available_paths)}/{len(dag_paths)} components)",
                details="Some advanced features may not be available"
            )
        else:
            return CheckResult(
                name="DAG Orchestration Infrastructure",
                passed=True,
                message="Full DAG orchestration infrastructure available"
            )
    
    def check_output_directories(self) -> CheckResult:
        """Check output directories can be created."""
        try:
            output_dir = self.project_root / "docs/vocabulary_projections"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Test write permissions
            test_file = output_dir / "test_write.tmp"
            test_file.write_text("test")
            test_file.unlink()
            
            return CheckResult(
                name="Output Directories",
                passed=True,
                message=f"Output directory ready: {output_dir}"
            )
            
        except Exception as e:
            return CheckResult(
                name="Output Directories",
                passed=False,
                message="Cannot create or write to output directory",
                details=str(e)
            )
    
    def check_dependencies(self) -> CheckResult:
        """Check required Python dependencies."""
        required_modules = [
            "json",
            "pathlib", 
            "dataclasses",
            "enum",
            "typing"
        ]
        
        missing_modules = []
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)
        
        if missing_modules:
            return CheckResult(
                name="Dependencies",
                passed=False,
                message=f"{len(missing_modules)} required modules missing",
                details=f"Missing: {', '.join(missing_modules)}"
            )
        
        return CheckResult(
            name="Dependencies",
            passed=True,
            message="All required dependencies available"
        )
    
    def check_permissions(self) -> CheckResult:
        """Check file system permissions."""
        try:
            # Check read permissions on source files
            src_file = self.project_root / "src/multi_dimensional_vocabulary_projector.py"
            if not os.access(src_file, os.R_OK):
                return CheckResult(
                    name="Permissions",
                    passed=False,
                    message="Cannot read source files",
                    details=f"No read access to {src_file}"
                )
            
            # Check write permissions on output directory
            output_dir = self.project_root / "docs"
            if not os.access(output_dir, os.W_OK):
                return CheckResult(
                    name="Permissions",
                    passed=False,
                    message="Cannot write to output directory",
                    details=f"No write access to {output_dir}"
                )
            
            return CheckResult(
                name="Permissions",
                passed=True,
                message="File system permissions OK"
            )
            
        except Exception as e:
            return CheckResult(
                name="Permissions",
                passed=False,
                message="Permission check failed",
                details=str(e)
            )
    
    def check_disk_space(self) -> CheckResult:
        """Check available disk space."""
        try:
            import shutil
            
            # Check available space in output directory
            output_dir = self.project_root / "docs"
            total, used, free = shutil.disk_usage(output_dir)
            
            # Need at least 10MB for projections
            min_space_mb = 10
            free_mb = free / (1024 * 1024)
            
            if free_mb < min_space_mb:
                return CheckResult(
                    name="Disk Space",
                    passed=False,
                    message=f"Insufficient disk space: {free_mb:.1f}MB available",
                    details=f"Need at least {min_space_mb}MB for vocabulary projections"
                )
            
            return CheckResult(
                name="Disk Space",
                passed=True,
                message=f"Sufficient disk space: {free_mb:.1f}MB available"
            )
            
        except Exception as e:
            return CheckResult(
                name="Disk Space",
                passed=True,  # Non-critical check
                message="Could not check disk space (non-critical)",
                details=str(e)
            )
    
    def check_existing_projections(self) -> CheckResult:
        """Check status of existing projections."""
        try:
            projections_dir = self.project_root / "docs/vocabulary_projections"
            
            if not projections_dir.exists():
                return CheckResult(
                    name="Existing Projections",
                    passed=True,
                    message="No existing projections (clean start)"
                )
            
            projection_files = list(projections_dir.glob("vocabulary_*.md"))
            
            if not projection_files:
                return CheckResult(
                    name="Existing Projections",
                    passed=True,
                    message="Projection directory exists but empty"
                )
            
            # Check if projections are recent
            import time
            now = time.time()
            recent_files = []
            old_files = []
            
            for file in projection_files:
                age_hours = (now - file.stat().st_mtime) / 3600
                if age_hours < 24:
                    recent_files.append(file.name)
                else:
                    old_files.append(file.name)
            
            message = f"{len(projection_files)} existing projections"
            if recent_files:
                message += f" ({len(recent_files)} recent)"
            if old_files:
                message += f" ({len(old_files)} old)"
            
            return CheckResult(
                name="Existing Projections",
                passed=True,
                message=message,
                details="Existing projections will be overwritten"
            )
            
        except Exception as e:
            return CheckResult(
                name="Existing Projections",
                passed=True,  # Non-critical check
                message="Could not check existing projections",
                details=str(e)
            )
    
    def print_failed_checks(self):
        """Print details of failed checks."""
        failed_checks = [r for r in self.results if not r.passed]
        
        if not failed_checks:
            return
        
        print("\n❌ Failed Checks:")
        for check in failed_checks:
            print(f"   • {check.name}: {check.message}")
            if check.details:
                print(f"     {check.details}")
    
    def get_launch_readiness_report(self) -> Dict[str, Any]:
        """Get detailed launch readiness report."""
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        
        return {
            "ready_for_launch": passed == total,
            "checks_passed": passed,
            "total_checks": total,
            "success_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%",
            "failed_checks": [
                {"name": r.name, "message": r.message, "details": r.details}
                for r in self.results if not r.passed
            ],
            "recommendations": self._get_recommendations()
        }
    
    def _get_recommendations(self) -> List[str]:
        """Get recommendations based on check results."""
        recommendations = []
        
        failed_checks = [r for r in self.results if not r.passed]
        
        for check in failed_checks:
            if "Python" in check.name:
                recommendations.append("Upgrade to Python 3.9+ and consider using a virtual environment")
            elif "Project Structure" in check.name:
                recommendations.append("Ensure all required project files are present before launch")
            elif "Vocabulary" in check.name:
                recommendations.append("Verify vocabulary source data is complete and properly formatted")
            elif "Core Implementation" in check.name:
                recommendations.append("Fix import errors in core implementation before proceeding")
            elif "Permissions" in check.name:
                recommendations.append("Check file system permissions for source and output directories")
        
        if not recommendations:
            recommendations.append("System is ready for DAG orchestration launch")
        
        return recommendations

def main():
    """Run pre-launch check."""
    checker = VocabularyProjectorPreLaunchCheck()
    
    # Run all checks
    ready = checker.run_all_checks()
    
    # Generate report
    report = checker.get_launch_readiness_report()
    
    # Save report
    report_file = Path("vocabulary_projector_pre_launch_report.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Exit with appropriate code
    sys.exit(0 if ready else 1)

if __name__ == "__main__":
    main()