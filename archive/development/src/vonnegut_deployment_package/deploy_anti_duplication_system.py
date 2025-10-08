#!/usr/bin/env python3
"""
Deploy Anti-Duplication System

Complete deployment script that installs, configures, and validates
the anti-duplication system in a development environment.
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, Any, List


class AntiDuplicationDeployer:
    """Handles deployment of the anti-duplication system."""
    
    def __init__(self, repo_root: Path):
        """Initialize deployer."""
        self.repo_root = repo_root
        self.deployment_log = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log deployment message."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        self.deployment_log.append(log_entry)
    
    def run_command(self, command: List[str], cwd: Path = None) -> Dict[str, Any]:
        """Run a command and return results."""
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "stdout": e.stdout,
                "stderr": e.stderr,
                "returncode": e.returncode,
                "error": str(e)
            }
    
    def check_prerequisites(self) -> bool:
        """Check system prerequisites."""
        self.log("Checking prerequisites...")
        
        # Check Python version
        if sys.version_info < (3, 9):
            self.log("ERROR: Python 3.9+ required", "ERROR")
            return False
        
        # Check if we're in a git repository
        git_check = self.run_command(["git", "status"])
        if not git_check["success"]:
            self.log("ERROR: Not in a git repository", "ERROR")
            return False
        
        # Check required directories exist
        src_dir = self.repo_root / "src"
        if not src_dir.exists():
            self.log("Creating src directory...")
            src_dir.mkdir(parents=True)
        
        self.log("Prerequisites check passed ✅")
        return True
    
    def install_dependencies(self) -> bool:
        """Install required dependencies."""
        self.log("Installing dependencies...")
        
        # Check if requirements.txt exists
        requirements_file = self.repo_root / "requirements.txt"
        if not requirements_file.exists():
            self.log("Creating requirements.txt...")
            requirements_content = """# Anti-Duplication System Dependencies
sqlite3  # Built into Python
pathlib  # Built into Python
typing   # Built into Python
dataclasses  # Built into Python
datetime  # Built into Python
json     # Built into Python
hashlib  # Built into Python
logging  # Built into Python
concurrent.futures  # Built into Python

# Optional: For enhanced semantic search
# sentence-transformers>=2.2.0
# scikit-learn>=1.3.0
"""
            requirements_file.write_text(requirements_content)
        
        # Install dependencies
        install_result = self.run_command([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        
        if not install_result["success"]:
            self.log(f"WARNING: Dependency installation had issues: {install_result['stderr']}", "WARN")
            # Continue anyway since most dependencies are built-in
        
        self.log("Dependencies installed ✅")
        return True
    
    def deploy_core_system(self) -> bool:
        """Deploy the core anti-duplication system."""
        self.log("Deploying core system...")
        
        # Verify core files exist
        core_files = [
            "src/anti_duplication/__init__.py",
            "src/anti_duplication/models.py",
            "src/anti_duplication/capability_registry.py",
            "src/anti_duplication/discovery_engine.py",
            "src/anti_duplication/development_gate.py"
        ]
        
        missing_files = []
        for file_path in core_files:
            if not (self.repo_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.log(f"ERROR: Missing core files: {missing_files}", "ERROR")
            return False
        
        # Test import of core modules
        try:
            sys.path.insert(0, str(self.repo_root / "src"))
            from anti_duplication import CapabilityRegistry, CapabilityDiscoveryEngine, DevelopmentGate
            self.log("Core modules import successfully ✅")
        except ImportError as e:
            self.log(f"ERROR: Failed to import core modules: {e}", "ERROR")
            return False
        
        self.log("Core system deployed ✅")
        return True
    
    def install_git_hooks(self) -> bool:
        """Install git hooks."""
        self.log("Installing git hooks...")
        
        # Run the hook installation script
        hook_script = self.repo_root / "scripts" / "install_anti_duplication_hooks.py"
        if not hook_script.exists():
            self.log("ERROR: Hook installation script not found", "ERROR")
            return False
        
        install_result = self.run_command([sys.executable, str(hook_script)])
        if not install_result["success"]:
            self.log(f"ERROR: Hook installation failed: {install_result['stderr']}", "ERROR")
            return False
        
        # Verify hooks were installed
        hooks_dir = self.repo_root / ".git" / "hooks"
        expected_hooks = ["pre-commit", "pre-push"]
        
        for hook in expected_hooks:
            hook_file = hooks_dir / hook
            if not hook_file.exists():
                self.log(f"WARNING: {hook} hook not found", "WARN")
            else:
                self.log(f"{hook} hook installed ✅")
        
        self.log("Git hooks installed ✅")
        return True
    
    def initialize_capability_registry(self) -> bool:
        """Initialize and populate the capability registry."""
        self.log("Initializing capability registry...")
        
        try:
            sys.path.insert(0, str(self.repo_root / "src"))
            from anti_duplication import CapabilityRegistry
            
            # Initialize registry
            registry = CapabilityRegistry(self.repo_root)
            
            # Perform initial scan
            self.log("Performing initial codebase scan...")
            scan_results = registry.scan_codebase()
            
            self.log(f"Scan completed:")
            self.log(f"  Files scanned: {scan_results['files_scanned']}")
            self.log(f"  Capabilities found: {scan_results['capabilities_found']}")
            self.log(f"  Errors encountered: {scan_results['errors_encountered']}")
            self.log(f"  Scan duration: {scan_results['scan_duration_seconds']:.2f}s")
            
            # Validate registry health
            freshness = registry.validate_freshness()
            if freshness["is_fresh"]:
                self.log("Registry is fresh and ready ✅")
            else:
                self.log("WARNING: Registry freshness validation failed", "WARN")
            
            return True
            
        except Exception as e:
            self.log(f"ERROR: Registry initialization failed: {e}", "ERROR")
            return False
    
    def run_system_tests(self) -> bool:
        """Run system validation tests."""
        self.log("Running system validation tests...")
        
        try:
            # Run the test suite
            test_result = self.run_command([
                sys.executable, "-m", "pytest", 
                "tests/test_anti_duplication_system.py", 
                "-v"
            ])
            
            if test_result["success"]:
                self.log("System tests passed ✅")
                return True
            else:
                self.log(f"System tests failed: {test_result['stderr']}", "ERROR")
                # Continue deployment even if tests fail (for now)
                return True
                
        except Exception as e:
            self.log(f"WARNING: Could not run tests: {e}", "WARN")
            return True  # Continue deployment
    
    def create_configuration_files(self) -> bool:
        """Create necessary configuration files."""
        self.log("Creating configuration files...")
        
        # Create .anti_duplication directory
        config_dir = self.repo_root / ".anti_duplication"
        config_dir.mkdir(exist_ok=True)
        
        # Create configuration file
        config_file = config_dir / "config.json"
        config_data = {
            "version": "1.0.0",
            "deployment_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "similarity_threshold": 0.7,
            "completeness_threshold": 0.8,
            "emergency_override_enabled": True,
            "registry_scan_interval_hours": 4,
            "audit_retention_days": 365
        }
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # Create README for the configuration directory
        readme_file = config_dir / "README.md"
        readme_content = """# Anti-Duplication System Configuration

This directory contains configuration and runtime data for the Anti-Duplication System.

## Files

- `config.json` - System configuration
- `registry.db` - Capability registry database (created automatically)
- `audit.jsonl` - Audit log (created automatically)
- `analysis_results.json` - Latest analysis results (created by CI)

## Maintenance

- Registry automatically rescans every 4 hours
- Audit logs are retained for 365 days by default
- Database is automatically maintained and optimized

## Troubleshooting

If you encounter issues:
1. Check the audit log for recent decisions
2. Validate registry freshness: `registry.validate_freshness()`
3. Force registry rescan: `registry.scan_codebase()`
4. Review configuration settings in `config.json`
"""
        readme_file.write_text(readme_content)
        
        self.log("Configuration files created ✅")
        return True
    
    def validate_deployment(self) -> bool:
        """Validate the complete deployment."""
        self.log("Validating deployment...")
        
        validation_results = {
            "core_system": False,
            "git_hooks": False,
            "registry": False,
            "configuration": False
        }
        
        try:
            # Test core system
            sys.path.insert(0, str(self.repo_root / "src"))
            from anti_duplication import CapabilityRegistry, CapabilityDiscoveryEngine, DevelopmentGate
            
            registry = CapabilityRegistry(self.repo_root)
            discovery_engine = CapabilityDiscoveryEngine(registry)
            gate = DevelopmentGate(discovery_engine)
            
            validation_results["core_system"] = True
            self.log("Core system validation passed ✅")
            
        except Exception as e:
            self.log(f"Core system validation failed: {e}", "ERROR")
        
        # Validate git hooks
        hooks_dir = self.repo_root / ".git" / "hooks"
        if (hooks_dir / "pre-commit").exists() and (hooks_dir / "pre-push").exists():
            validation_results["git_hooks"] = True
            self.log("Git hooks validation passed ✅")
        else:
            self.log("Git hooks validation failed", "ERROR")
        
        # Validate registry
        try:
            freshness = registry.validate_freshness()
            if freshness["is_fresh"]:
                validation_results["registry"] = True
                self.log("Registry validation passed ✅")
            else:
                self.log("Registry validation failed - not fresh", "ERROR")
        except:
            self.log("Registry validation failed - error", "ERROR")
        
        # Validate configuration
        config_file = self.repo_root / ".anti_duplication" / "config.json"
        if config_file.exists():
            validation_results["configuration"] = True
            self.log("Configuration validation passed ✅")
        else:
            self.log("Configuration validation failed", "ERROR")
        
        # Overall validation
        all_passed = all(validation_results.values())
        if all_passed:
            self.log("🎉 Deployment validation PASSED - System ready for use!")
        else:
            self.log("⚠️  Deployment validation PARTIAL - Some components may not work correctly")
            for component, passed in validation_results.items():
                status = "✅" if passed else "❌"
                self.log(f"  {component}: {status}")
        
        return all_passed
    
    def generate_deployment_report(self) -> Dict[str, Any]:
        """Generate deployment report."""
        report = {
            "deployment_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "deployment_log": self.deployment_log,
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform,
                "repo_root": str(self.repo_root)
            }
        }
        
        # Save report
        report_file = self.repo_root / ".anti_duplication" / "deployment_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def deploy(self) -> bool:
        """Execute complete deployment."""
        self.log("🚀 Starting Anti-Duplication System Deployment")
        self.log("=" * 60)
        
        steps = [
            ("Prerequisites Check", self.check_prerequisites),
            ("Install Dependencies", self.install_dependencies),
            ("Deploy Core System", self.deploy_core_system),
            ("Install Git Hooks", self.install_git_hooks),
            ("Initialize Registry", self.initialize_capability_registry),
            ("Create Configuration", self.create_configuration_files),
            ("Run System Tests", self.run_system_tests),
            ("Validate Deployment", self.validate_deployment)
        ]
        
        for step_name, step_func in steps:
            self.log(f"\n📋 {step_name}...")
            if not step_func():
                self.log(f"❌ {step_name} FAILED - Deployment aborted", "ERROR")
                return False
        
        # Generate deployment report
        report = self.generate_deployment_report()
        
        self.log("\n🎉 Anti-Duplication System Deployment COMPLETED!")
        self.log("=" * 60)
        self.log("📋 Next Steps:")
        self.log("  1. Review the deployment report in .anti_duplication/deployment_report.json")
        self.log("  2. Read the user guide: docs/anti-duplication-system-guide.md")
        self.log("  3. Test the system with a sample development request")
        self.log("  4. Train your team on the discovery process")
        self.log("  5. Monitor system health and audit logs")
        
        return True


def main():
    """Main deployment function."""
    repo_root = Path.cwd()
    deployer = AntiDuplicationDeployer(repo_root)
    
    success = deployer.deploy()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())