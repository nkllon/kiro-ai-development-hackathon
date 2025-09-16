"""
Auto Fixer - Automatically fix identified issues
"""

import os
import shutil
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from .dag_analyzer import DAGAnalysisResult
from .health_scorer import HealthReport


@dataclass
class FixResult:
    """Result of automatic fixing operation"""
    success: bool
    fixes_applied: List[str]
    warnings: List[str]
    errors: List[str]
    backup_created: bool
    backup_path: Optional[str]


class AutoFixer:
    """Automatically fixes identified Makefile issues"""
    
    def __init__(self):
        self.fix_strategies = {
            'cycles': self._fix_circular_dependencies,
            'orphaned': self._fix_orphaned_nodes,
            'complex_targets': self._fix_complex_targets,
            'naming': self._fix_naming_inconsistencies,
            'documentation': self._add_documentation
        }
    
    def fix_makefile_issues(self, makefile_path: str, 
                          dag_result: DAGAnalysisResult, 
                          health_report: HealthReport) -> FixResult:
        """
        Fix identified issues in the Makefile
        
        Args:
            makefile_path: Path to the Makefile
            dag_result: DAG analysis results
            health_report: Health assessment report
            
        Returns:
            FixResult with fix operation details
        """
        fixes_applied = []
        warnings = []
        errors = []
        backup_path = None
        
        try:
            # Create backup
            backup_path = self._create_backup(makefile_path)
            
            # Read current content
            with open(makefile_path, 'r') as f:
                original_content = f.read()
            
            content = original_content
            
            # Apply fixes based on issues
            for issue in health_report.issues:
                fix_type = self._identify_fix_type(issue)
                if fix_type in self.fix_strategies:
                    try:
                        content, fix_applied = self.fix_strategies[fix_type](
                            content, dag_result, issue
                        )
                        if fix_applied:
                            fixes_applied.append(fix_applied)
                    except Exception as e:
                        errors.append(f"Failed to fix {fix_type}: {str(e)}")
            
            # Apply general improvements
            content, general_fixes = self._apply_general_improvements(content, dag_result)
            fixes_applied.extend(general_fixes)
            
            # Write fixed content if changes were made
            if content != original_content:
                with open(makefile_path, 'w') as f:
                    f.write(content)
            else:
                warnings.append("No fixes were applied - file may already be optimal")
            
            return FixResult(
                success=len(errors) == 0,
                fixes_applied=fixes_applied,
                warnings=warnings,
                errors=errors,
                backup_created=backup_path is not None,
                backup_path=backup_path
            )
            
        except Exception as e:
            # Restore from backup if available
            if backup_path and os.path.exists(backup_path):
                shutil.copy2(backup_path, makefile_path)
                warnings.append(f"Restored from backup due to error: {str(e)}")
            
            return FixResult(
                success=False,
                fixes_applied=fixes_applied,
                warnings=warnings,
                errors=[f"Critical error during fixing: {str(e)}"],
                backup_created=backup_path is not None,
                backup_path=backup_path
            )
    
    def _create_backup(self, makefile_path: str) -> str:
        """Create backup of original file"""
        backup_dir = Path(makefile_path).parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        backup_name = f"{Path(makefile_path).stem}_backup_{int(time.time())}.mk"
        backup_path = backup_dir / backup_name
        
        shutil.copy2(makefile_path, backup_path)
        return str(backup_path)
    
    def _identify_fix_type(self, issue: str) -> str:
        """Identify the type of fix needed for an issue"""
        issue_lower = issue.lower()
        
        if 'circular' in issue_lower or 'cycle' in issue_lower:
            return 'cycles'
        elif 'orphaned' in issue_lower:
            return 'orphaned'
        elif 'complex' in issue_lower:
            return 'complex_targets'
        elif 'naming' in issue_lower:
            return 'naming'
        elif 'documentation' in issue_lower:
            return 'documentation'
        else:
            return 'general'
    
    def _fix_circular_dependencies(self, content: str, dag_result: DAGAnalysisResult, 
                                 issue: str) -> tuple[str, str]:
        """Fix circular dependencies by introducing intermediate targets"""
        # This is a complex fix that would require sophisticated analysis
        # For now, add a warning comment
        warning_comment = "\n# WARNING: Circular dependencies detected - manual review required\n"
        
        if warning_comment not in content:
            content = warning_comment + content
            return content, "Added circular dependency warning comment"
        
        return content, ""
    
    def _fix_orphaned_nodes(self, content: str, dag_result: DAGAnalysisResult, 
                           issue: str) -> tuple[str, str]:
        """Fix orphaned nodes by either removing them or connecting them"""
        fixes_applied = []
        
        # For orphaned nodes, we'll add them to a 'cleanup' target
        if dag_result.orphaned_nodes:
            cleanup_target = "\ncleanup: " + " ".join(dag_result.orphaned_nodes)
            cleanup_target += "\n\t@echo 'Cleaning up orphaned targets'\n"
            
            if "cleanup:" not in content:
                content += cleanup_target
                fixes_applied.append("Created cleanup target for orphaned nodes")
        
        return content, "; ".join(fixes_applied) if fixes_applied else ""
    
    def _fix_complex_targets(self, content: str, dag_result: DAGAnalysisResult, 
                           issue: str) -> tuple[str, str]:
        """Break down complex targets into smaller ones"""
        fixes_applied = []
        
        # Find targets with many commands and suggest breaking them down
        for node_name, node in dag_result.nodes.items():
            if len(node.commands) > 5:
                # Add a comment suggesting refactoring
                target_pattern = f"^{node_name}\\s*:"
                replacement = f"# TODO: Consider breaking down {node_name} into smaller targets\n{node_name}:"
                
                if replacement not in content:
                    content = content.replace(f"{node_name}:", replacement, 1)
                    fixes_applied.append(f"Added refactoring suggestion for {node_name}")
        
        return content, "; ".join(fixes_applied) if fixes_applied else ""
    
    def _fix_naming_inconsistencies(self, content: str, dag_result: DAGAnalysisResult, 
                                  issue: str) -> tuple[str, str]:
        """Fix naming inconsistencies"""
        # This would require more sophisticated analysis and user confirmation
        # For now, add a comment about naming conventions
        naming_comment = "\n# NAMING CONVENTIONS: Use hyphens for multi-word targets (e.g., build-all)\n"
        
        if naming_comment not in content:
            content += naming_comment
            return content, "Added naming conventions comment"
        
        return content, ""
    
    def _add_documentation(self, content: str, dag_result: DAGAnalysisResult, 
                         issue: str) -> tuple[str, str]:
        """Add documentation to undocumented targets"""
        fixes_applied = []
        
        for node_name, node in dag_result.nodes.items():
            # Check if target has documentation
            has_docs = any(cmd.strip().startswith('#') for cmd in node.commands)
            
            if not has_docs and node.commands:
                # Add basic documentation
                target_line = f"{node_name}:"
                doc_comment = f"# {node_name.replace('-', ' ').replace('_', ' ').title()} target\n{target_line}"
                
                if doc_comment not in content:
                    content = content.replace(target_line, doc_comment, 1)
                    fixes_applied.append(f"Added documentation for {node_name}")
        
        return content, "; ".join(fixes_applied) if fixes_applied else ""
    
    def _apply_general_improvements(self, content: str, dag_result: DAGAnalysisResult) -> tuple[str, List[str]]:
        """Apply general improvements to the Makefile"""
        fixes_applied = []
        
        # Add .PHONY declarations for common targets
        common_targets = ['all', 'clean', 'install', 'test', 'help']
        phony_targets = []
        
        for target in common_targets:
            if target in dag_result.nodes:
                phony_targets.append(target)
        
        if phony_targets and '.PHONY:' not in content:
            phony_declaration = f".PHONY: {' '.join(phony_targets)}\n\n"
            content = phony_declaration + content
            fixes_applied.append(f"Added .PHONY declaration for {len(phony_targets)} targets")
        
        # Ensure proper tab indentation for commands
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Check if line looks like a command but doesn't start with tab
            if line.strip() and not line.startswith('\t') and not line.startswith('#') and ':' not in line:
                # This might be a command without proper indentation
                if any(line.strip().startswith(cmd) for cmd in ['echo', '@echo', 'mkdir', 'cp', 'mv', 'rm', 'cd', 'python', 'uv']):
                    line = '\t' + line.strip()
                    fixes_applied.append("Fixed command indentation")
            
            fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        return content, fixes_applied


# Import time for backup naming
import time
