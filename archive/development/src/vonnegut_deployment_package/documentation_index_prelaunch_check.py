#!/usr/bin/env python3
"""
Documentation Index Generator - Pre-Launch Validation
===================================================

Validates system readiness for parallel DAG execution of documentation index generator tasks.
Ensures all prerequisites, dependencies, and existing implementation are properly analyzed.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentationIndexPreLaunchChecker:
    """Pre-launch validation for documentation index generator DAG execution."""
    
    def __init__(self):
        self.repository_root = Path.cwd()
        self.spec_path = self.repository_root / ".kiro" / "specs" / "documentation-index-generator"
        self.existing_implementation = self.repository_root / "src" / "documentation_index_generator.py"
        self.validation_results = []
        self.critical_failures = []
        
    def run_comprehensive_check(self) -> Dict[str, Any]:
        """Run all pre-launch validation checks."""
        logger.info("🚀 Documentation Index Generator Pre-Launch Validation Starting...")
        
        checks = [
            ("Specification Files", self.check_specification_files),
            ("Existing Implementation", self.check_existing_implementation),
            ("Python Environment", self.check_python_environment),
            ("Git Repository", self.check_git_repository),
            ("Directory Structure", self.check_directory_structure),
            ("Dependencies", self.check_dependencies),
            ("Beast Mode Framework", self.check_beast_mode_framework),
            ("Documentation Corpus", self.check_documentation_corpus),
            ("Test Infrastructure", self.check_test_infrastructure),
            ("Parallel Execution", self.check_parallel_execution_readiness),
            ("Resource Availability", self.check_resource_availability)
        ]
        
        results = {
            "overall_status": "unknown",
            "checks": {},
            "critical_failures": [],
            "warnings": [],
            "recommendations": [],
            "existing_implementation_analysis": {}
        }
        
        for check_name, check_function in checks:
            logger.info(f"🔍 Running {check_name} validation...")
            try:
                check_result = check_function()
                results["checks"][check_name] = check_result
                
                if not check_result["passed"]:
                    if check_result.get("critical", False):
                        self.critical_failures.append(f"{check_name}: {check_result['message']}")
                    else:
                        results["warnings"].append(f"{check_name}: {check_result['message']}")
                        
            except Exception as e:
                error_msg = f"{check_name} validation failed: {str(e)}"
                logger.error(error_msg)
                self.critical_failures.append(error_msg)
                results["checks"][check_name] = {
                    "passed": False,
                    "critical": True,
                    "message": str(e)
                }
        
        # Analyze existing implementation
        results["existing_implementation_analysis"] = self.analyze_existing_implementation()
        
        # Determine overall status
        if self.critical_failures:
            results["overall_status"] = "FAILED"
            results["critical_failures"] = self.critical_failures
        elif results["warnings"]:
            results["overall_status"] = "WARNING"
        else:
            results["overall_status"] = "READY"
            
        # Add recommendations
        results["recommendations"] = self.generate_recommendations(results)
        
        return results
    
    def check_specification_files(self) -> Dict[str, Any]:
        """Validate specification files exist and are properly formatted."""
        required_files = ["requirements.md", "design.md", "tasks.md"]
        missing_files = []
        
        for file_name in required_files:
            file_path = self.spec_path / file_name
            if not file_path.exists():
                missing_files.append(file_name)
            elif file_path.stat().st_size == 0:
                missing_files.append(f"{file_name} (empty)")
        
        if missing_files:
            return {
                "passed": False,
                "critical": True,
                "message": f"Missing specification files: {', '.join(missing_files)}",
                "details": {"missing_files": missing_files}
            }
        
        # Check tasks.md format
        tasks_content = (self.spec_path / "tasks.md").read_text()
        task_count = tasks_content.count("- [ ]")
        
        return {
            "passed": True,
            "message": f"All specification files present. Found {task_count} tasks.",
            "details": {"task_count": task_count}
        }
    
    def check_existing_implementation(self) -> Dict[str, Any]:
        """Validate existing implementation and analyze its structure."""
        if not self.existing_implementation.exists():
            return {
                "passed": False,
                "critical": True,
                "message": "Existing implementation not found at src/documentation_index_generator.py"
            }
        
        try:
            content = self.existing_implementation.read_text()
            
            # Analyze implementation
            line_count = len(content.split('\n'))
            class_count = content.count('class ')
            function_count = content.count('def ')
            has_main = '__main__' in content
            
            # Check for key components
            has_document_info = 'DocumentInfo' in content
            has_categorization = 'categorize' in content.lower()
            has_index_generation = 'generate' in content.lower() and 'index' in content.lower()
            
            return {
                "passed": True,
                "message": f"Existing implementation found: {line_count} lines, {class_count} classes, {function_count} functions",
                "details": {
                    "line_count": line_count,
                    "class_count": class_count,
                    "function_count": function_count,
                    "has_main": has_main,
                    "has_document_info": has_document_info,
                    "has_categorization": has_categorization,
                    "has_index_generation": has_index_generation,
                    "file_size": self.existing_implementation.stat().st_size
                }
            }
            
        except Exception as e:
            return {
                "passed": False,
                "critical": True,
                "message": f"Failed to analyze existing implementation: {str(e)}"
            }
    
    def check_python_environment(self) -> Dict[str, Any]:
        """Validate Python environment and version."""
        try:
            python_version = sys.version_info
            if python_version < (3, 9):
                return {
                    "passed": False,
                    "critical": True,
                    "message": f"Python 3.9+ required, found {python_version.major}.{python_version.minor}"
                }
            
            # Check virtual environment
            in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
            
            return {
                "passed": True,
                "message": f"Python {python_version.major}.{python_version.minor}.{python_version.micro}, venv: {in_venv}",
                "details": {
                    "version": f"{python_version.major}.{python_version.minor}.{python_version.micro}",
                    "virtual_env": in_venv
                }
            }
            
        except Exception as e:
            return {
                "passed": False,
                "critical": True,
                "message": f"Python environment check failed: {str(e)}"
            }
    
    def check_git_repository(self) -> Dict[str, Any]:
        """Validate git repository status and configuration."""
        try:
            # Check if we're in a git repository
            result = subprocess.run(["git", "rev-parse", "--git-dir"], 
                                  capture_output=True, text=True, cwd=self.repository_root)
            if result.returncode != 0:
                return {
                    "passed": False,
                    "critical": True,
                    "message": "Not in a git repository"
                }
            
            # Check git status
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  capture_output=True, text=True, cwd=self.repository_root)
            
            untracked_files = [line for line in result.stdout.split('\n') if line.startswith('??')]
            modified_files = [line for line in result.stdout.split('\n') if line and not line.startswith('??')]
            
            return {
                "passed": True,
                "message": f"Git repository ready. {len(untracked_files)} untracked, {len(modified_files)} modified files",
                "details": {
                    "untracked_count": len(untracked_files),
                    "modified_count": len(modified_files)
                }
            }
            
        except Exception as e:
            return {
                "passed": False,
                "critical": True,
                "message": f"Git repository check failed: {str(e)}"
            }
    
    def check_directory_structure(self) -> Dict[str, Any]:
        """Validate required directory structure exists."""
        required_dirs = [
            ".kiro",
            ".kiro/specs",
            ".kiro/steering",
            "src",
            "tests",
            "scripts",
            "docs"
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            full_path = self.repository_root / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)
        
        if missing_dirs:
            return {
                "passed": False,
                "critical": True,
                "message": f"Missing required directories: {', '.join(missing_dirs)}"
            }
        
        return {
            "passed": True,
            "message": "All required directories present"
        }
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Check if required dependencies are available."""
        required_packages = [
            "pathlib",
            "typing",
            "dataclasses",
            "enum",
            "datetime",
            "json",
            "re"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            return {
                "passed": False,
                "critical": True,
                "message": f"Missing required packages: {', '.join(missing_packages)}"
            }
        
        return {
            "passed": True,
            "message": "All required dependencies available"
        }
    
    def check_beast_mode_framework(self) -> Dict[str, Any]:
        """Check Beast Mode framework availability."""
        beast_mode_path = self.repository_root / "src" / "beast_mode"
        
        if not beast_mode_path.exists():
            return {
                "passed": False,
                "critical": False,
                "message": "Beast Mode framework not found in src/beast_mode"
            }
        
        # Check for ReflectiveModule
        core_path = beast_mode_path / "core"
        if core_path.exists():
            return {
                "passed": True,
                "message": "Beast Mode framework available"
            }
        
        return {
            "passed": False,
            "critical": False,
            "message": "Beast Mode framework incomplete (missing core)"
        }
    
    def check_documentation_corpus(self) -> Dict[str, Any]:
        """Analyze existing documentation corpus for processing."""
        try:
            # Count markdown files
            markdown_files = []
            for root, dirs, files in os.walk(self.repository_root):
                # Skip certain directories
                if any(skip in root for skip in ['.git', '.venv', '__pycache__', 'node_modules']):
                    continue
                    
                for file in files:
                    if file.endswith('.md') and not file.startswith('.'):
                        markdown_files.append(Path(root) / file)
            
            total_size = sum(f.stat().st_size for f in markdown_files if f.exists())
            
            # Analyze docs directory
            docs_dir = self.repository_root / "docs"
            docs_files = len([f for f in markdown_files if str(f).startswith(str(docs_dir))])
            
            return {
                "passed": True,
                "message": f"Documentation corpus: {len(markdown_files)} markdown files, {total_size/1024:.1f}KB total",
                "details": {
                    "total_markdown_files": len(markdown_files),
                    "docs_directory_files": docs_files,
                    "total_size_bytes": total_size,
                    "average_file_size": total_size / len(markdown_files) if markdown_files else 0
                }
            }
            
        except Exception as e:
            return {
                "passed": False,
                "critical": False,
                "message": f"Documentation corpus analysis failed: {str(e)}"
            }
    
    def check_test_infrastructure(self) -> Dict[str, Any]:
        """Validate test generation infrastructure."""
        test_generator_path = self.repository_root / "scripts" / "generate_missing_tests.py"
        
        if not test_generator_path.exists():
            return {
                "passed": False,
                "critical": False,
                "message": "Test generator script not found"
            }
        
        tests_dir = self.repository_root / "tests"
        if not tests_dir.exists():
            return {
                "passed": False,
                "critical": False,
                "message": "Tests directory not found"
            }
        
        return {
            "passed": True,
            "message": "Test infrastructure available"
        }
    
    def check_parallel_execution_readiness(self) -> Dict[str, Any]:
        """Check system readiness for parallel task execution."""
        try:
            import concurrent.futures
            import multiprocessing
            
            cpu_count = multiprocessing.cpu_count()
            
            # Test parallel execution capability
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                futures = [executor.submit(lambda: True) for _ in range(2)]
                results = [f.result() for f in futures]
            
            return {
                "passed": True,
                "message": f"Parallel execution ready, {cpu_count} CPUs available",
                "details": {"cpu_count": cpu_count}
            }
            
        except Exception as e:
            return {
                "passed": False,
                "critical": True,
                "message": f"Parallel execution check failed: {str(e)}"
            }
    
    def check_resource_availability(self) -> Dict[str, Any]:
        """Check system resource availability."""
        try:
            import shutil
            
            # Check disk space
            disk_usage = shutil.disk_usage(self.repository_root)
            free_gb = disk_usage.free / (1024**3)
            
            if free_gb < 0.5:
                return {
                    "passed": False,
                    "critical": True,
                    "message": f"Insufficient disk space: {free_gb:.1f}GB free"
                }
            
            return {
                "passed": True,
                "message": f"Resources available: {free_gb:.1f}GB free disk space",
                "details": {"free_disk_gb": free_gb}
            }
            
        except Exception as e:
            return {
                "passed": False,
                "critical": False,
                "message": f"Resource check failed: {str(e)}"
            }
    
    def analyze_existing_implementation(self) -> Dict[str, Any]:
        """Analyze existing implementation for migration planning."""
        if not self.existing_implementation.exists():
            return {"status": "not_found"}
        
        try:
            content = self.existing_implementation.read_text()
            
            # Extract key components
            analysis = {
                "status": "found",
                "components": {
                    "DocumentInfo": "DocumentInfo" in content,
                    "DocumentCategory": "DocumentCategory" in content,
                    "DocumentationIndexGenerator": "DocumentationIndexGenerator" in content,
                    "discover_documents": "discover_documents" in content,
                    "generate_category_indexes": "generate_category_indexes" in content,
                    "_categorize_document": "_categorize_document" in content,
                    "_determine_audience": "_determine_audience" in content,
                    "_determine_status": "_determine_status" in content
                },
                "features": {
                    "frontmatter_parsing": "frontmatter" in content.lower(),
                    "github_integration": "github" in content.lower(),
                    "statistics_generation": "statistics" in content.lower(),
                    "template_system": "template" in content.lower(),
                    "error_handling": "try:" in content and "except" in content
                },
                "metrics": {
                    "line_count": len(content.split('\n')),
                    "class_count": content.count('class '),
                    "function_count": content.count('def '),
                    "import_count": content.count('import '),
                    "comment_lines": len([line for line in content.split('\n') if line.strip().startswith('#')])
                }
            }
            
            return analysis
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        if results["overall_status"] == "FAILED":
            recommendations.append("❌ CRITICAL: Fix all critical failures before launching")
            recommendations.append("📋 Review critical_failures list for specific issues")
        
        if results["overall_status"] == "WARNING":
            recommendations.append("⚠️  WARNING: Address warnings for optimal execution")
            recommendations.append("🚀 Launch possible but may encounter issues")
        
        if results["overall_status"] == "READY":
            recommendations.append("✅ READY: All systems go for parallel DAG execution")
            recommendations.append("🎯 Estimated execution time: 14-19 hours")
            recommendations.append("👥 Recommended workers: 4 parallel")
        
        # Specific recommendations based on existing implementation
        impl_analysis = results.get("existing_implementation_analysis", {})
        if impl_analysis.get("status") == "found":
            recommendations.append("🔄 MIGRATION: Existing implementation detected - plan incremental refactoring")
            recommendations.append("💾 BACKUP: Create backup of existing implementation before migration")
            
            components = impl_analysis.get("components", {})
            missing_components = [name for name, exists in components.items() if not exists]
            if missing_components:
                recommendations.append(f"🔧 COMPONENTS: Missing components detected: {', '.join(missing_components)}")
        
        # Documentation corpus recommendations
        checks = results.get("checks", {})
        if "Documentation Corpus" in checks:
            corpus_details = checks["Documentation Corpus"].get("details", {})
            file_count = corpus_details.get("total_markdown_files", 0)
            
            if file_count > 100:
                recommendations.append("📚 LARGE CORPUS: Consider performance optimization for large document set")
            if file_count < 10:
                recommendations.append("📄 SMALL CORPUS: Perfect for testing and validation")
        
        return recommendations
    
    def save_results(self, results: Dict[str, Any]) -> str:
        """Save validation results to file."""
        output_file = self.spec_path / "LAUNCH_READINESS.md"
        
        content = f"""# Documentation Index Generator - Launch Readiness Report

## Overall Status: {results['overall_status']}

Generated: {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}

## Validation Summary

"""
        
        for check_name, check_result in results["checks"].items():
            status_icon = "✅" if check_result["passed"] else ("❌" if check_result.get("critical") else "⚠️")
            content += f"- {status_icon} **{check_name}**: {check_result['message']}\n"
        
        # Add existing implementation analysis
        impl_analysis = results.get("existing_implementation_analysis", {})
        if impl_analysis.get("status") == "found":
            content += "\n## Existing Implementation Analysis\n\n"
            
            components = impl_analysis.get("components", {})
            content += "### Components Found\n"
            for component, exists in components.items():
                icon = "✅" if exists else "❌"
                content += f"- {icon} {component}\n"
            
            features = impl_analysis.get("features", {})
            content += "\n### Features Detected\n"
            for feature, exists in features.items():
                icon = "✅" if exists else "❌"
                content += f"- {icon} {feature.replace('_', ' ').title()}\n"
            
            metrics = impl_analysis.get("metrics", {})
            content += f"\n### Code Metrics\n"
            content += f"- **Lines of Code**: {metrics.get('line_count', 0)}\n"
            content += f"- **Classes**: {metrics.get('class_count', 0)}\n"
            content += f"- **Functions**: {metrics.get('function_count', 0)}\n"
            content += f"- **Imports**: {metrics.get('import_count', 0)}\n"
        
        if results["critical_failures"]:
            content += "\n## Critical Failures\n\n"
            for failure in results["critical_failures"]:
                content += f"- ❌ {failure}\n"
        
        if results["warnings"]:
            content += "\n## Warnings\n\n"
            for warning in results["warnings"]:
                content += f"- ⚠️ {warning}\n"
        
        content += "\n## Recommendations\n\n"
        for recommendation in results["recommendations"]:
            content += f"- {recommendation}\n"
        
        content += f"""
## Next Steps

### If Status is READY ✅
```bash
# Launch parallel DAG execution
./scripts/documentation_index_background_launch.sh
```

### If Status is WARNING ⚠️
1. Review warnings above
2. Decide if acceptable risk
3. Launch with caution or fix issues first

### If Status is FAILED ❌
1. Fix all critical failures
2. Re-run pre-launch check
3. Do not launch until READY

## Technical Details

```json
{json.dumps(results, indent=2)}
```
"""
        
        output_file.write_text(content)
        return str(output_file)

def main():
    """Main execution function."""
    checker = DocumentationIndexPreLaunchChecker()
    
    print("🚀 Documentation Index Generator - Pre-Launch Validation")
    print("=" * 65)
    
    results = checker.run_comprehensive_check()
    
    # Save results
    output_file = checker.save_results(results)
    
    # Print summary
    print(f"\n📊 Validation Complete - Status: {results['overall_status']}")
    print(f"📄 Full report saved to: {output_file}")
    
    if results["overall_status"] == "READY":
        print("\n✅ SYSTEM READY FOR PARALLEL DAG EXECUTION")
        print("🚀 Run: ./scripts/documentation_index_background_launch.sh")
    elif results["overall_status"] == "WARNING":
        print("\n⚠️  SYSTEM HAS WARNINGS - REVIEW BEFORE LAUNCH")
        print("📋 Check warnings in the report above")
    else:
        print("\n❌ SYSTEM NOT READY - CRITICAL FAILURES DETECTED")
        print("🔧 Fix critical issues before attempting launch")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())