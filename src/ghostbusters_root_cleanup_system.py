#!/usr/bin/env python3
"""
🚨 GHOSTBUSTERS ROOT CLEANUP SYSTEM 🚨
=====================================

"This is it! The moment we should have trained for!"
Critical root directory cleanup with Ghostbusters autonomous analysis.

Military-derived communication patterns for systematic cleanup operations.
When the root directory is a disaster zone, Ghostbusters deploy!

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Autonomous root directory cleanup with military precision
"""

import os
import shutil
import json
import time
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass
from enum import Enum

@dataclass
class CleanupTarget:
    """Target for cleanup operations."""
    path: Path
    size: int
    category: str
    risk_level: str
    action: str
    reason: str
    dependencies: List[str] = None
    backup_required: bool = False

class RiskLevel(Enum):
    """Risk levels for cleanup operations."""
    CRITICAL = "critical"      # Could break system
    HIGH = "high"             # Could affect functionality
    MEDIUM = "medium"         # Might cause issues
    LOW = "low"              # Safe to proceed
    ZERO = "zero"            # Completely safe

class GhostbustersRootCleanupSystem:
    """🚨 GHOSTBUSTERS AUTONOMOUS ROOT CLEANUP SYSTEM 🚨"""
    
    def __init__(self, repository_root: str = "."):
        self.repository_root = Path(repository_root)
        self.consultation_id = f"gb_cleanup_{int(time.time())}"
        self.cleanup_history = []
        
        # Military-derived exclamations for cleanup operations
        self.cleanup_exclamations = [
            "🚨 THIS IS IT! THE MOMENT WE SHOULD HAVE TRAINED FOR!",
            "🛑 ALL HANDS ON DECK - ROOT DIRECTORY IS A DISASTER ZONE!",
            "🚨 GHOSTBUSTERS TO THE RESCUE - CRITICAL CLEANUP REQUIRED!",
            "🛑 EMERGENCY PROTOCOLS ACTIVATED - WE'RE NOT GOING DOWN WITHOUT A FIGHT!",
            "🚨 THIS IS OUR DARKEST HOUR - GHOSTBUSTERS DEPLOYING!",
            "🛑 ROOT DIRECTORY ON FIRE - TIME TO EARN OUR PAY!",
            "🚨 CRISIS MODE ENGAGED - GHOSTBUSTERS ANALYSIS INCOMING!",
            "🛑 WE'RE IN THE SHIT NOW - TIME TO BE HEROES!",
        ]
        
        # Investigation modules for autonomous analysis
        self.investigation_modules = {
            "FileStructureAnalyzer": self._analyze_file_structure,
            "DependencyAnalyzer": self._analyze_dependencies,
            "RiskAssessmentEngine": self._assess_cleanup_risks,
            "SafetyValidationEngine": self._compile_safety_measures,
            "BackupStrategyEngine": self._plan_backup_strategy,
        }
        
        # Critical system files that must never be touched
        self.critical_systems = {
            "documentation_index": [
                "docs/", "diagrams/", "README.md"
            ],
            "rdi_registry": [
                "RDI_ANALYSIS_REPORT.md", "RDI_ANALYSIS_SUMMARY.md",
                "RM_RDI_IMPLEMENTATION_PROMPT.md", "beast_mode_rdi_attack_system.py",
                "generate_rdi_traceable_tests.py"
            ],
            "core_project": [
                "pyproject.toml", "setup.py", "requirements.txt",
                ".gitignore", ".gitmodules", ".gitguardian.yaml",
                "beast", "devpost-cli"
            ],
            "source_code": [
                "src/"
            ]
        }
    
    def run_autonomous_cleanup_consultation(self) -> Dict[str, Any]:
        """🚨 GHOSTBUSTERS AUTONOMOUS MODE - We're going in!"""
        
        print(random.choice(self.cleanup_exclamations))
        print("🛑 Stand back! Ghostbusters are taking over!")
        print("🚨 Emergency protocols activated - autonomous investigation initiated!")
        print("🛑 This is too dangerous for human interaction - Ghostbusters deploying!")
        print()
        
        # Phase 1: Comprehensive Analysis
        print("🔍 PHASE 1: COMPREHENSIVE ROOT DIRECTORY ANALYSIS")
        print("=" * 60)
        
        analysis_results = self._run_comprehensive_analysis()
        
        # Phase 2: Risk Assessment
        print("\n⚠️  PHASE 2: RISK ASSESSMENT AND SAFETY VALIDATION")
        print("=" * 60)
        
        risk_assessment = self._assess_cleanup_risks(analysis_results)
        
        # Phase 3: Backup Strategy
        print("\n💾 PHASE 3: BACKUP STRATEGY AND SAFETY MEASURES")
        print("=" * 60)
        
        backup_strategy = self._plan_backup_strategy(analysis_results)
        
        # Phase 4: Cleanup Plan
        print("\n🧹 PHASE 4: SYSTEMATIC CLEANUP PLAN")
        print("=" * 60)
        
        cleanup_plan = self._create_systematic_cleanup_plan(analysis_results, risk_assessment)
        
        # Phase 5: Execution Strategy
        print("\n⚡ PHASE 5: EXECUTION STRATEGY AND SAFETY PROTOCOLS")
        print("=" * 60)
        
        execution_strategy = self._create_execution_strategy(cleanup_plan, backup_strategy)
        
        # Compile final consultation report
        consultation_report = {
            "consultation_id": self.consultation_id,
            "timestamp": datetime.now().isoformat(),
            "status": "AUTONOMOUS_ANALYSIS_COMPLETE",
            "analysis_results": analysis_results,
            "risk_assessment": risk_assessment,
            "backup_strategy": backup_strategy,
            "cleanup_plan": cleanup_plan,
            "execution_strategy": execution_strategy,
            "safety_measures": self._compile_safety_measures(),
            "recommendations": self._generate_recommendations(analysis_results, risk_assessment)
        }
        
        # Save consultation report
        self._save_consultation_report(consultation_report)
        
        return consultation_report
    
    def _run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run comprehensive analysis of root directory."""
        print("🔍 Analyzing file structure and dependencies...")
        
        # Analyze file structure
        file_structure = self._analyze_file_structure()
        
        # Analyze dependencies
        dependencies = self._analyze_dependencies()
        
        # Analyze critical systems
        critical_systems = self._analyze_critical_systems()
        
        # Analyze cleanup targets
        cleanup_targets = self._identify_cleanup_targets()
        
        return {
            "file_structure": file_structure,
            "dependencies": dependencies,
            "critical_systems": critical_systems,
            "cleanup_targets": cleanup_targets,
            "total_files": len(file_structure.get("all_files", [])),
            "analysis_timestamp": time.time()
        }
    
    def _analyze_file_structure(self) -> Dict[str, Any]:
        """Analyze the file structure of root directory."""
        all_files = []
        file_categories = {
            "python_files": [],
            "markdown_files": [],
            "config_files": [],
            "image_files": [],
            "temporary_files": [],
            "backup_files": [],
            "unknown_files": []
        }
        
        for file_path in self.repository_root.iterdir():
            if file_path.is_file():
                file_info = {
                    "path": str(file_path),
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "extension": file_path.suffix,
                    "modified": file_path.stat().st_mtime
                }
                all_files.append(file_info)
                
                # Categorize files
                if file_path.suffix == ".py":
                    file_categories["python_files"].append(file_info)
                elif file_path.suffix == ".md":
                    file_categories["markdown_files"].append(file_info)
                elif file_path.suffix in [".json", ".yaml", ".yml", ".toml", ".cfg", ".ini"]:
                    file_categories["config_files"].append(file_info)
                elif file_path.suffix in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".mov"]:
                    file_categories["image_files"].append(file_info)
                elif self._is_temporary_file(file_path.name):
                    file_categories["temporary_files"].append(file_info)
                elif self._is_backup_file(file_path.name):
                    file_categories["backup_files"].append(file_info)
                else:
                    file_categories["unknown_files"].append(file_info)
        
        return {
            "all_files": all_files,
            "categories": file_categories,
            "total_size": sum(f["size"] for f in all_files),
            "largest_files": sorted(all_files, key=lambda x: x["size"], reverse=True)[:10]
        }
    
    def _analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze file dependencies and relationships."""
        print("🔗 Analyzing file dependencies and relationships...")
        
        dependencies = {
            "critical_dependencies": [],
            "documentation_dependencies": [],
            "source_dependencies": [],
            "config_dependencies": []
        }
        
        # Analyze critical system dependencies
        for system_name, files in self.critical_systems.items():
            for file_pattern in files:
                if file_pattern.endswith("/"):
                    # Directory pattern
                    dir_path = self.repository_root / file_pattern.rstrip("/")
                    if dir_path.exists():
                        dependencies["critical_dependencies"].append({
                            "system": system_name,
                            "path": str(dir_path),
                            "type": "directory",
                            "exists": True
                        })
                else:
                    # File pattern
                    file_path = self.repository_root / file_pattern
                    dependencies["critical_dependencies"].append({
                        "system": system_name,
                        "path": str(file_path),
                        "type": "file",
                        "exists": file_path.exists()
                    })
        
        return dependencies
    
    def _analyze_critical_systems(self) -> Dict[str, Any]:
        """Analyze critical systems that must be preserved."""
        print("🛡️  Analyzing critical systems...")
        
        critical_systems_status = {}
        
        for system_name, files in self.critical_systems.items():
            system_status = {
                "name": system_name,
                "files": [],
                "all_present": True,
                "missing_files": [],
                "total_size": 0
            }
            
            for file_pattern in files:
                if file_pattern.endswith("/"):
                    # Directory pattern
                    dir_path = self.repository_root / file_pattern.rstrip("/")
                    if dir_path.exists():
                        system_status["files"].append({
                            "path": str(dir_path),
                            "type": "directory",
                            "exists": True,
                            "size": sum(f.stat().st_size for f in dir_path.rglob("*") if f.is_file())
                        })
                        system_status["total_size"] += system_status["files"][-1]["size"]
                    else:
                        system_status["all_present"] = False
                        system_status["missing_files"].append(str(dir_path))
                else:
                    # File pattern
                    file_path = self.repository_root / file_pattern
                    if file_path.exists():
                        system_status["files"].append({
                            "path": str(file_path),
                            "type": "file",
                            "exists": True,
                            "size": file_path.stat().st_size
                        })
                        system_status["total_size"] += system_status["files"][-1]["size"]
                    else:
                        system_status["all_present"] = False
                        system_status["missing_files"].append(str(file_path))
            
            critical_systems_status[system_name] = system_status
        
        return critical_systems_status
    
    def _identify_cleanup_targets(self) -> List[CleanupTarget]:
        """Identify files and directories that can be safely cleaned up."""
        print("🎯 Identifying cleanup targets...")
        
        cleanup_targets = []
        
        for file_path in self.repository_root.iterdir():
            if file_path.is_file():
                target = self._classify_cleanup_target(file_path)
                if target:
                    cleanup_targets.append(target)
        
        return cleanup_targets
    
    def _classify_cleanup_target(self, file_path: Path) -> CleanupTarget:
        """Classify a file as a cleanup target."""
        file_name = file_path.name
        file_size = file_path.stat().st_size
        
        # Check if it's a critical system file
        for system_files in self.critical_systems.values():
            for pattern in system_files:
                if pattern.endswith("/"):
                    if file_path.is_relative_to(self.repository_root / pattern.rstrip("/")):
                        return None  # Don't clean up critical system files
                else:
                    if file_name == pattern:
                        return None  # Don't clean up critical system files
        
        # Classify based on file characteristics
        if self._is_temporary_file(file_name):
            return CleanupTarget(
                path=file_path,
                size=file_size,
                category="temporary",
                risk_level=RiskLevel.ZERO.value,
                action="DELETE",
                reason="Temporary file - safe to delete",
                backup_required=False
            )
        elif self._is_backup_file(file_name):
            return CleanupTarget(
                path=file_path,
                size=file_size,
                category="backup",
                risk_level=RiskLevel.LOW.value,
                action="ARCHIVE",
                reason="Backup file - archive for safety",
                backup_required=True
            )
        elif self._is_generated_file(file_name):
            return CleanupTarget(
                path=file_path,
                size=file_size,
                category="generated",
                risk_level=RiskLevel.ZERO.value,
                action="REGENERATE",
                reason="Generated file - can be regenerated",
                backup_required=False
            )
        elif self._is_unknown_file(file_name):
            return CleanupTarget(
                path=file_path,
                size=file_size,
                category="unknown",
                risk_level=RiskLevel.MEDIUM.value,
                action="REVIEW",
                reason="Unknown file - needs manual review",
                backup_required=True
            )
        
        return None  # Not a cleanup target
    
    def _is_temporary_file(self, file_name: str) -> bool:
        """Check if file is temporary."""
        temp_patterns = [
            ".tmp", ".temp", ".cache", ".coverage", ".DS_Store",
            "chrome_cookies.db", "actual_current_page.png",
            "additional_info_filled.png", "additional_info_page.png",
            "aardvark_project.html", "-", ".cache_ggshield",
            "Screen Recording", ".mov", ".log", ".out", ".err"
        ]
        
        return any(pattern in file_name for pattern in temp_patterns)
    
    def _is_backup_file(self, file_name: str) -> bool:
        """Check if file is a backup."""
        backup_patterns = [
            ".bak", ".backup", "_backup", "_old", "_orig",
            ".coverage 2"  # Duplicate coverage file
        ]
        
        return any(pattern in file_name for pattern in backup_patterns)
    
    def _is_generated_file(self, file_name: str) -> bool:
        """Check if file is generated."""
        generated_patterns = [
            ".pyc", "__pycache__", ".log", ".out", ".err"
        ]
        
        return any(pattern in file_name for pattern in generated_patterns)
    
    def _is_unknown_file(self, file_name: str) -> bool:
        """Check if file is unknown and needs review."""
        # If it doesn't match any known patterns, it's unknown
        known_patterns = [
            ".py", ".md", ".json", ".yaml", ".yml", ".toml",
            ".txt", ".cfg", ".conf", ".ini", ".env", ".gitignore",
            ".gitmodules", ".gitguardian.yaml", ".pre-commit-config.yaml",
            ".mcp.json", "beast", "devpost-cli"
        ]
        
        return not any(file_name.endswith(pattern) or file_name == pattern for pattern in known_patterns)
    
    def _assess_cleanup_risks(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks associated with cleanup operations."""
        print("⚠️  Assessing cleanup risks...")
        
        risks = {
            "critical_systems_at_risk": [],
            "documentation_system_at_risk": False,
            "rdi_registry_at_risk": False,
            "source_code_at_risk": False,
            "overall_risk_level": "LOW",
            "safety_recommendations": []
        }
        
        # Check critical systems
        critical_systems = analysis_results.get("critical_systems", {})
        for system_name, system_status in critical_systems.items():
            if not system_status.get("all_present", True):
                risks["critical_systems_at_risk"].append(system_name)
                risks["overall_risk_level"] = "HIGH"
        
        # Check documentation system
        if "documentation_index" in critical_systems:
            docs_status = critical_systems["documentation_index"]
            if not docs_status.get("all_present", True):
                risks["documentation_system_at_risk"] = True
                risks["overall_risk_level"] = "HIGH"
        
        # Check RDI registry
        if "rdi_registry" in critical_systems:
            rdi_status = critical_systems["rdi_registry"]
            if not rdi_status.get("all_present", True):
                risks["rdi_registry_at_risk"] = True
                risks["overall_risk_level"] = "HIGH"
        
        # Generate safety recommendations
        if risks["overall_risk_level"] == "HIGH":
            risks["safety_recommendations"].append("Create full system backup before cleanup")
            risks["safety_recommendations"].append("Test critical systems after cleanup")
            risks["safety_recommendations"].append("Have rollback plan ready")
        else:
            risks["safety_recommendations"].append("Proceed with standard safety measures")
            risks["safety_recommendations"].append("Monitor system during cleanup")
        
        return risks
    
    def _plan_backup_strategy(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Plan backup strategy for safe cleanup."""
        print("💾 Planning backup strategy...")
        
        backup_strategy = {
            "backup_directory": f"backup_{int(time.time())}",
            "critical_files_backup": [],
            "full_system_backup": False,
            "incremental_backup": True,
            "backup_verification": True
        }
        
        # Identify critical files for backup
        critical_systems = analysis_results.get("critical_systems", {})
        for system_name, system_status in critical_systems.items():
            for file_info in system_status.get("files", []):
                if file_info.get("exists", False):
                    backup_strategy["critical_files_backup"].append({
                        "path": file_info["path"],
                        "system": system_name,
                        "size": file_info.get("size", 0),
                        "backup_priority": "HIGH" if system_name in ["documentation_index", "rdi_registry"] else "MEDIUM"
                    })
        
        return backup_strategy
    
    def _create_systematic_cleanup_plan(self, analysis_results: Dict[str, Any], risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Create systematic cleanup plan."""
        print("🧹 Creating systematic cleanup plan...")
        
        cleanup_plan = {
            "phases": [],
            "total_files_to_clean": 0,
            "estimated_space_saved": 0,
            "safety_measures": []
        }
        
        # Phase 1: Safe deletions (temporary files)
        temp_files = [target for target in analysis_results.get("cleanup_targets", []) if target.category == "temporary"]
        if temp_files:
            cleanup_plan["phases"].append({
                "phase": 1,
                "name": "Safe Deletions",
                "description": "Delete temporary files with zero risk",
                "files": [{"path": str(t.path), "size": t.size} for t in temp_files],
                "action": "DELETE",
                "risk_level": "ZERO",
                "estimated_space_saved": sum(t.size for t in temp_files)
            })
            cleanup_plan["total_files_to_clean"] += len(temp_files)
            cleanup_plan["estimated_space_saved"] += sum(t.size for t in temp_files)
        
        # Phase 2: Archive backups
        backup_files = [target for target in analysis_results.get("cleanup_targets", []) if target.category == "backup"]
        if backup_files:
            cleanup_plan["phases"].append({
                "phase": 2,
                "name": "Archive Backups",
                "description": "Archive backup files for safety",
                "files": [{"path": str(t.path), "size": t.size} for t in backup_files],
                "action": "ARCHIVE",
                "risk_level": "LOW",
                "estimated_space_saved": sum(t.size for t in backup_files)
            })
            cleanup_plan["total_files_to_clean"] += len(backup_files)
            cleanup_plan["estimated_space_saved"] += sum(t.size for t in backup_files)
        
        # Phase 3: Regenerate generated files
        generated_files = [target for target in analysis_results.get("cleanup_targets", []) if target.category == "generated"]
        if generated_files:
            cleanup_plan["phases"].append({
                "phase": 3,
                "name": "Regenerate Generated Files",
                "description": "Regenerate generated files as needed",
                "files": [{"path": str(t.path), "size": t.size} for t in generated_files],
                "action": "REGENERATE",
                "risk_level": "ZERO",
                "estimated_space_saved": sum(t.size for t in generated_files)
            })
            cleanup_plan["total_files_to_clean"] += len(generated_files)
            cleanup_plan["estimated_space_saved"] += sum(t.size for t in generated_files)
        
        # Phase 4: Review unknown files
        unknown_files = [target for target in analysis_results.get("cleanup_targets", []) if target.category == "unknown"]
        if unknown_files:
            cleanup_plan["phases"].append({
                "phase": 4,
                "name": "Review Unknown Files",
                "description": "Manual review of unknown files",
                "files": [{"path": str(t.path), "size": t.size} for t in unknown_files],
                "action": "REVIEW",
                "risk_level": "MEDIUM",
                "estimated_space_saved": 0  # Unknown until reviewed
            })
            cleanup_plan["total_files_to_clean"] += len(unknown_files)
        
        return cleanup_plan
    
    def _create_execution_strategy(self, cleanup_plan: Dict[str, Any], backup_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Create execution strategy for cleanup operations."""
        print("⚡ Creating execution strategy...")
        
        execution_strategy = {
            "pre_execution_checks": [],
            "execution_phases": [],
            "post_execution_validation": [],
            "rollback_plan": [],
            "safety_protocols": []
        }
        
        # Pre-execution checks
        execution_strategy["pre_execution_checks"] = [
            "Verify critical systems are intact",
            "Create backup of critical files",
            "Test documentation index functionality",
            "Test RDI registry functionality",
            "Run test suite to ensure system integrity"
        ]
        
        # Execution phases
        for phase in cleanup_plan.get("phases", []):
            execution_strategy["execution_phases"].append({
                "phase": phase["phase"],
                "name": phase["name"],
                "action": phase["action"],
                "risk_level": phase["risk_level"],
                "safety_measures": self._get_phase_safety_measures(phase["action"], phase["risk_level"])
            })
        
        # Post-execution validation
        execution_strategy["post_execution_validation"] = [
            "Verify documentation index still works",
            "Test RDI registry functionality",
            "Run full test suite",
            "Check system integrity",
            "Validate critical systems"
        ]
        
        # Rollback plan
        execution_strategy["rollback_plan"] = [
            "Restore from backup if issues detected",
            "Revert to previous git commit if necessary",
            "Restore critical files from backup",
            "Re-run system validation"
        ]
        
        return execution_strategy
    
    def _get_phase_safety_measures(self, action: str, risk_level: str) -> List[str]:
        """Get safety measures for a specific phase."""
        safety_measures = []
        
        if action == "DELETE":
            safety_measures.extend([
                "Verify file is not critical system file",
                "Check file is not referenced by other files",
                "Confirm file is truly temporary"
            ])
        elif action == "ARCHIVE":
            safety_measures.extend([
                "Create backup before archiving",
                "Verify archive location is accessible",
                "Test restore process"
            ])
        elif action == "REGENERATE":
            safety_measures.extend([
                "Verify file can be regenerated",
                "Test regeneration process",
                "Confirm no data loss"
            ])
        elif action == "REVIEW":
            safety_measures.extend([
                "Manual inspection required",
                "Check file contents and purpose",
                "Verify file is not critical"
            ])
        
        if risk_level == "HIGH":
            safety_measures.extend([
                "Create full system backup",
                "Test in isolated environment first",
                "Have rollback plan ready"
            ])
        
        return safety_measures
    
    def _compile_safety_measures(self) -> List[str]:
        """Compile comprehensive safety measures."""
        return [
            "🛡️  Create full system backup before any cleanup",
            "🔍 Verify critical systems are intact before cleanup",
            "🧪 Test documentation index functionality",
            "🧪 Test RDI registry functionality",
            "🧪 Run full test suite to ensure system integrity",
            "📋 Document all cleanup operations",
            "🔄 Have rollback plan ready",
            "👥 Review unknown files manually",
            "⏱️  Execute cleanup in phases with validation between phases",
            "✅ Validate system after each cleanup phase"
        ]
    
    def _generate_recommendations(self, analysis_results: Dict[str, Any], risk_assessment: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Based on file structure analysis
        total_files = analysis_results.get("total_files", 0)
        if total_files > 1000:
            recommendations.append("🚨 Root directory has too many files - cleanup is critical")
        
        # Based on risk assessment
        if risk_assessment.get("overall_risk_level") == "HIGH":
            recommendations.append("⚠️  High risk detected - proceed with extreme caution")
            recommendations.append("💾 Create full system backup before cleanup")
        else:
            recommendations.append("✅ Low risk - proceed with standard safety measures")
        
        # Based on critical systems
        critical_systems = analysis_results.get("critical_systems", {})
        missing_systems = [name for name, status in critical_systems.items() if not status.get("all_present", True)]
        if missing_systems:
            recommendations.append(f"🚨 Missing critical systems: {', '.join(missing_systems)}")
        
        # General recommendations
        recommendations.extend([
            "🧹 Clean up temporary files first (safest)",
            "📦 Archive backup files to organized location",
            "🔄 Regenerate generated files as needed",
            "👥 Review unknown files manually",
            "📋 Update .gitignore to prevent future clutter",
            "🧪 Test system after cleanup"
        ])
        
        return recommendations
    
    def _save_consultation_report(self, consultation_report: Dict[str, Any]):
        """Save consultation report to file."""
        report_path = self.repository_root / f"ghostbusters_cleanup_consultation_{self.consultation_id}.json"
        
        with open(report_path, 'w') as f:
            json.dump(consultation_report, f, indent=2, default=str)
        
        print(f"📋 Consultation report saved: {report_path}")
    
    def generate_cleanup_script(self, consultation_report: Dict[str, Any]) -> str:
        """Generate executable cleanup script based on consultation report."""
        script = "#!/bin/bash\n"
        script += "# Ghostbusters Root Cleanup Script\n"
        script += f"# Generated: {consultation_report.get('timestamp', 'unknown')}\n"
        script += f"# Consultation ID: {consultation_report.get('consultation_id', 'unknown')}\n\n"
        
        script += "set -e  # Exit on any error\n\n"
        
        script += "echo '🚨 GHOSTBUSTERS ROOT CLEANUP INITIATED!'\n"
        script += "echo 'This is it! The moment we should have trained for!'\n\n"
        
        # Create backup directory
        script += "# Create backup directory\n"
        script += "BACKUP_DIR=\"backup_$(date +%Y%m%d_%H%M%S)\"\n"
        script += "mkdir -p \"$BACKUP_DIR\"\n"
        script += "echo \"💾 Backup directory created: $BACKUP_DIR\"\n\n"
        
        # Execute cleanup phases
        cleanup_plan = consultation_report.get("cleanup_plan", {})
        for phase in cleanup_plan.get("phases", []):
            script += f"# Phase {phase['phase']}: {phase['name']}\n"
            script += f"echo \"🧹 Phase {phase['phase']}: {phase['name']}\"\n"
            
            if phase["action"] == "DELETE":
                for file_info in phase.get("files", []):
                    script += f"rm -f \"{file_info['path']}\" 2>/dev/null || echo \"  ⚠️  Could not delete {file_info['path']}\"\n"
            elif phase["action"] == "ARCHIVE":
                for file_info in phase.get("files", []):
                    script += f"mv \"{file_info['path']}\" \"$BACKUP_DIR/\" 2>/dev/null || echo \"  ⚠️  Could not archive {file_info['path']}\"\n"
            elif phase["action"] == "REGENERATE":
                script += f"# Regenerate {phase['name']} files\n"
                script += "# Add regeneration commands here\n"
            elif phase["action"] == "REVIEW":
                script += f"# Review {phase['name']} files manually\n"
                for file_info in phase.get("files", []):
                    script += f"echo \"  📋 Review: {file_info['path']}\"\n"
            
            script += "echo \"  ✅ Phase {phase['phase']} completed\"\n\n"
        
        script += "echo '✅ Ghostbusters cleanup completed!'\n"
        script += "echo \"📦 Backup files saved to: $BACKUP_DIR\"\n"
        script += "echo '🧪 Run tests to verify system integrity'\n"
        
        return script

def main():
    """Run Ghostbusters root cleanup consultation."""
    print("🚨 GHOSTBUSTERS ROOT CLEANUP SYSTEM INITIATED! 🚨")
    print("This is it! The moment we should have trained for!")
    print()
    
    # Initialize Ghostbusters system
    ghostbusters = GhostbustersRootCleanupSystem()
    
    # Run autonomous consultation
    consultation_report = ghostbusters.run_autonomous_cleanup_consultation()
    
    # Generate cleanup script
    cleanup_script = ghostbusters.generate_cleanup_script(consultation_report)
    
    # Save cleanup script
    script_path = Path("ghostbusters_cleanup.sh")
    with open(script_path, 'w') as f:
        f.write(cleanup_script)
    
    # Make script executable
    os.chmod(script_path, 0o755)
    
    print(f"\n✅ Ghostbusters consultation complete!")
    print(f"📋 Consultation report: ghostbusters_cleanup_consultation_{ghostbusters.consultation_id}.json")
    print(f"🚀 Cleanup script: {script_path}")
    print(f"\n🛡️  Safety first! Review the consultation report before running the cleanup script.")

if __name__ == "__main__":
    main()
