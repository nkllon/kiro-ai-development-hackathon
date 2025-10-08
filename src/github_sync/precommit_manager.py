"""
Pre-commit hook integration for GitHub synchronization.

This module provides pre-commit hook execution, validation, and guidance
for resolving common pre-commit issues while maintaining code quality standards.
"""

import os
import subprocess
import logging
import json
import yaml
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class PreCommitResult(Enum):
    """Pre-commit execution results."""
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    NOT_CONFIGURED = "not_configured"


@dataclass
class HookFailure:
    """Represents a failed pre-commit hook."""
    hook_id: str
    hook_name: str
    exit_code: int
    output: str
    files_affected: List[str]
    error_type: str
    suggested_fix: str


@dataclass
class PreCommitConfig:
    """Pre-commit configuration information."""
    config_file: Path
    hooks: List[Dict[str, Any]]
    repos: List[Dict[str, Any]]
    is_installed: bool


class PreCommitManager:
    """
    Manages pre-commit hook execution and provides guidance for resolving issues.
    
    This class runs pre-commit hooks, analyzes failures, and provides specific
    guidance for resolving common pre-commit issues.
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize pre-commit manager.
        
        Args:
            repo_path: Path to the Git repository
        """
        self.repo_path = Path(repo_path)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.config_file = self.repo_path / ".pre-commit-config.yaml"
        
        # Common error patterns and their fixes
        self.error_patterns = {
            'trailing-whitespace': {
                'description': 'Files have trailing whitespace',
                'fix_command': 'pre-commit run trailing-whitespace --all-files',
                'manual_fix': 'Remove trailing spaces from the end of lines'
            },
            'end-of-file-fixer': {
                'description': 'Files missing newline at end',
                'fix_command': 'pre-commit run end-of-file-fixer --all-files',
                'manual_fix': 'Add a newline at the end of each file'
            },
            'check-yaml': {
                'description': 'YAML files have syntax errors',
                'fix_command': None,
                'manual_fix': 'Fix YAML syntax errors in the affected files'
            },
            'check-json': {
                'description': 'JSON files have syntax errors',
                'fix_command': None,
                'manual_fix': 'Fix JSON syntax errors in the affected files'
            },
            'black': {
                'description': 'Python code formatting issues',
                'fix_command': 'black .',
                'manual_fix': 'Run black formatter on Python files'
            },
            'isort': {
                'description': 'Python import sorting issues',
                'fix_command': 'isort .',
                'manual_fix': 'Run isort to fix import ordering'
            },
            'flake8': {
                'description': 'Python linting issues',
                'fix_command': None,
                'manual_fix': 'Fix Python linting issues reported by flake8'
            },
            'mypy': {
                'description': 'Python type checking issues',
                'fix_command': None,
                'manual_fix': 'Fix Python type annotations and type errors'
            },
            'bandit': {
                'description': 'Security issues detected',
                'fix_command': None,
                'manual_fix': 'Fix security issues identified by bandit'
            },
            'prettier': {
                'description': 'Code formatting issues',
                'fix_command': 'prettier --write .',
                'manual_fix': 'Run prettier to format code files'
            },
            'eslint': {
                'description': 'JavaScript/TypeScript linting issues',
                'fix_command': 'eslint --fix .',
                'manual_fix': 'Fix JavaScript/TypeScript linting issues'
            }
        }
    
    def is_pre_commit_configured(self) -> bool:
        """
        Check if pre-commit is configured in the repository.
        
        Returns:
            True if pre-commit configuration exists
        """
        return self.config_file.exists()
    
    def is_pre_commit_installed(self) -> bool:
        """
        Check if pre-commit is installed and hooks are set up.
        
        Returns:
            True if pre-commit is installed
        """
        try:
            # Check if pre-commit command is available
            result = subprocess.run(
                ["pre-commit", "--version"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                return False
            
            # Check if hooks are installed
            git_hooks_dir = self.repo_path / ".git" / "hooks"
            pre_commit_hook = git_hooks_dir / "pre-commit"
            
            return pre_commit_hook.exists()
            
        except FileNotFoundError:
            return False
    
    def get_pre_commit_config(self) -> Optional[PreCommitConfig]:
        """
        Load and parse pre-commit configuration.
        
        Returns:
            PreCommitConfig object or None if not configured
        """
        if not self.is_pre_commit_configured():
            return None
        
        try:
            with open(self.config_file, 'r') as f:
                config_data = yaml.safe_load(f)
            
            repos = config_data.get('repos', [])
            hooks = []
            
            # Extract all hooks from all repos
            for repo in repos:
                repo_hooks = repo.get('hooks', [])
                hooks.extend(repo_hooks)
            
            return PreCommitConfig(
                config_file=self.config_file,
                hooks=hooks,
                repos=repos,
                is_installed=self.is_pre_commit_installed()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse pre-commit config: {e}")
            return None
    
    def install_pre_commit_hooks(self) -> bool:
        """
        Install pre-commit hooks in the repository.
        
        Returns:
            True if installation was successful
        """
        if not self.is_pre_commit_configured():
            self.logger.error("Pre-commit not configured - no .pre-commit-config.yaml found")
            return False
        
        try:
            result = subprocess.run(
                ["pre-commit", "install"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            self.logger.info("Pre-commit hooks installed successfully")
            self.logger.debug(f"Install output: {result.stdout}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install pre-commit hooks: {e}")
            self.logger.error(f"Error output: {e.stderr}")
            return False
        except FileNotFoundError:
            self.logger.error("Pre-commit command not found - please install pre-commit")
            return False
    
    def run_pre_commit_hooks(self, files: Optional[List[str]] = None, 
                           all_files: bool = False) -> Tuple[PreCommitResult, List[HookFailure]]:
        """
        Run pre-commit hooks on specified files or all files.
        
        Args:
            files: Specific files to check (None for staged files)
            all_files: Run on all files instead of just staged files
            
        Returns:
            Tuple of (result, list of failures)
        """
        if not self.is_pre_commit_configured():
            return PreCommitResult.NOT_CONFIGURED, []
        
        if not self.is_pre_commit_installed():
            self.logger.warning("Pre-commit hooks not installed, installing now...")
            if not self.install_pre_commit_hooks():
                return PreCommitResult.FAILED, []
        
        try:
            # Build command
            cmd = ["pre-commit", "run"]
            
            if all_files:
                cmd.append("--all-files")
            elif files:
                cmd.extend(["--files"] + files)
            
            # Add verbose output for better error analysis
            cmd.append("--verbose")
            
            self.logger.info(f"Running pre-commit: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False  # Don't raise exception on non-zero exit
            )
            
            # Parse the output to identify failures
            failures = self._parse_pre_commit_output(result.stdout, result.stderr)
            
            if result.returncode == 0:
                self.logger.info("All pre-commit hooks passed")
                return PreCommitResult.SUCCESS, []
            else:
                self.logger.warning(f"Pre-commit hooks failed with exit code {result.returncode}")
                return PreCommitResult.FAILED, failures
                
        except FileNotFoundError:
            self.logger.error("Pre-commit command not found")
            return PreCommitResult.FAILED, []
        except Exception as e:
            self.logger.error(f"Error running pre-commit hooks: {e}")
            return PreCommitResult.FAILED, []
    
    def _parse_pre_commit_output(self, stdout: str, stderr: str) -> List[HookFailure]:
        """
        Parse pre-commit output to identify specific failures.
        
        Args:
            stdout: Standard output from pre-commit
            stderr: Standard error from pre-commit
            
        Returns:
            List of HookFailure objects
        """
        failures = []
        
        # Split output into lines
        lines = (stdout + "\n" + stderr).split('\n')
        
        current_hook = None
        current_output = []
        
        for line in lines:
            line = line.strip()
            
            # Look for hook execution lines
            if "..." in line and ("PASSED" in line or "FAILED" in line or "SKIPPED" in line):
                # Process previous hook if it failed
                if current_hook and "FAILED" in current_hook:
                    hook_id = self._extract_hook_id(current_hook)
                    if hook_id:
                        failure = self._create_hook_failure(
                            hook_id, current_hook, current_output
                        )
                        if failure:
                            failures.append(failure)
                
                # Start new hook
                current_hook = line
                current_output = []
                
            elif current_hook and line:
                # Collect output for current hook
                current_output.append(line)
        
        # Process last hook if it failed
        if current_hook and "FAILED" in current_hook:
            hook_id = self._extract_hook_id(current_hook)
            if hook_id:
                failure = self._create_hook_failure(
                    hook_id, current_hook, current_output
                )
                if failure:
                    failures.append(failure)
        
        return failures
    
    def _extract_hook_id(self, hook_line: str) -> Optional[str]:
        """
        Extract hook ID from a pre-commit output line.
        
        Args:
            hook_line: Line containing hook execution info
            
        Returns:
            Hook ID or None
        """
        # Look for pattern like "hook-name..."
        parts = hook_line.split("...")
        if parts:
            return parts[0].strip()
        return None
    
    def _create_hook_failure(self, hook_id: str, hook_line: str, 
                           output_lines: List[str]) -> Optional[HookFailure]:
        """
        Create a HookFailure object from hook execution info.
        
        Args:
            hook_id: Hook identifier
            hook_line: Hook execution line
            output_lines: Output lines from hook execution
            
        Returns:
            HookFailure object or None
        """
        # Extract files affected from output
        files_affected = []
        for line in output_lines:
            if line.startswith("- ") or ":" in line:
                # Try to extract filename
                parts = line.split(":")
                if parts:
                    potential_file = parts[0].strip("- ").strip()
                    if "/" in potential_file or "." in potential_file:
                        files_affected.append(potential_file)
        
        # Determine error type and suggested fix
        error_type = "unknown"
        suggested_fix = "Please check the hook output for specific issues"
        
        for pattern, info in self.error_patterns.items():
            if pattern in hook_id.lower():
                error_type = pattern
                if info['fix_command']:
                    suggested_fix = f"Run: {info['fix_command']}"
                else:
                    suggested_fix = info['manual_fix']
                break
        
        return HookFailure(
            hook_id=hook_id,
            hook_name=hook_id,
            exit_code=1,  # Assume failure
            output="\n".join(output_lines),
            files_affected=files_affected,
            error_type=error_type,
            suggested_fix=suggested_fix
        )
    
    def get_resolution_guidance(self, failures: List[HookFailure]) -> Dict[str, Any]:
        """
        Generate comprehensive resolution guidance for hook failures.
        
        Args:
            failures: List of hook failures
            
        Returns:
            Dictionary with resolution guidance
        """
        guidance = {
            'summary': f"{len(failures)} pre-commit hook(s) failed",
            'failures': [],
            'quick_fixes': [],
            'manual_fixes': [],
            'bypass_option': False
        }
        
        auto_fixable = []
        manual_fixes = []
        
        for failure in failures:
            failure_info = {
                'hook': failure.hook_id,
                'description': self.error_patterns.get(failure.error_type, {}).get(
                    'description', 'Hook failed'
                ),
                'files': failure.files_affected,
                'suggested_fix': failure.suggested_fix,
                'output': failure.output
            }
            guidance['failures'].append(failure_info)
            
            # Categorize fixes
            pattern_info = self.error_patterns.get(failure.error_type, {})
            if pattern_info.get('fix_command'):
                auto_fixable.append({
                    'hook': failure.hook_id,
                    'command': pattern_info['fix_command']
                })
            else:
                manual_fixes.append({
                    'hook': failure.hook_id,
                    'description': pattern_info.get('manual_fix', 'Manual fix required')
                })
        
        guidance['quick_fixes'] = auto_fixable
        guidance['manual_fixes'] = manual_fixes
        
        # Only suggest bypass for certain types of failures
        safe_to_bypass = ['trailing-whitespace', 'end-of-file-fixer', 'prettier']
        if all(f.error_type in safe_to_bypass for f in failures):
            guidance['bypass_option'] = True
        
        return guidance
    
    def apply_auto_fixes(self, failures: List[HookFailure]) -> Dict[str, bool]:
        """
        Apply automatic fixes for fixable hook failures.
        
        Args:
            failures: List of hook failures
            
        Returns:
            Dictionary mapping hook IDs to fix success status
        """
        results = {}
        
        for failure in failures:
            pattern_info = self.error_patterns.get(failure.error_type, {})
            fix_command = pattern_info.get('fix_command')
            
            if not fix_command:
                results[failure.hook_id] = False
                continue
            
            try:
                # Run the fix command
                cmd = fix_command.split()
                result = subprocess.run(
                    cmd,
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                self.logger.info(f"Applied auto-fix for {failure.hook_id}")
                results[failure.hook_id] = True
                
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Auto-fix failed for {failure.hook_id}: {e}")
                results[failure.hook_id] = False
            except Exception as e:
                self.logger.error(f"Error applying auto-fix for {failure.hook_id}: {e}")
                results[failure.hook_id] = False
        
        return results
    
    def check_pre_commit_before_commit(self, ask_for_bypass: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Check pre-commit hooks before allowing a commit.
        
        Args:
            ask_for_bypass: Whether to ask user for bypass permission
            
        Returns:
            Tuple of (can_proceed, bypass_reason)
        """
        if not self.is_pre_commit_configured():
            self.logger.info("No pre-commit configuration found, proceeding with commit")
            return True, None
        
        # Run pre-commit hooks
        result, failures = self.run_pre_commit_hooks()
        
        if result == PreCommitResult.SUCCESS:
            return True, None
        
        if result == PreCommitResult.NOT_CONFIGURED:
            return True, None
        
        if result == PreCommitResult.FAILED:
            # Generate guidance
            guidance = self.get_resolution_guidance(failures)
            
            # Log detailed failure information
            self.logger.error("Pre-commit hooks failed:")
            for failure_info in guidance['failures']:
                self.logger.error(f"  - {failure_info['hook']}: {failure_info['description']}")
                self.logger.error(f"    Fix: {failure_info['suggested_fix']}")
            
            # Try auto-fixes first
            if guidance['quick_fixes']:
                self.logger.info("Attempting to apply automatic fixes...")
                fix_results = self.apply_auto_fixes(failures)
                
                # Re-run hooks after auto-fixes
                result, remaining_failures = self.run_pre_commit_hooks()
                if result == PreCommitResult.SUCCESS:
                    self.logger.info("Auto-fixes successful, pre-commit hooks now pass")
                    return True, None
                
                failures = remaining_failures
                guidance = self.get_resolution_guidance(failures)
            
            # If we still have failures, provide guidance
            if ask_for_bypass and guidance['bypass_option']:
                bypass_message = (
                    f"Pre-commit hooks failed but can be bypassed. "
                    f"Failures: {', '.join(f['hook'] for f in guidance['failures'])}"
                )
                return False, bypass_message
            
            return False, None
        
        return False, None
    
    def commit_with_bypass(self, commit_message: str, reason: str) -> bool:
        """
        Create a commit bypassing pre-commit hooks with documentation.
        
        Args:
            commit_message: Original commit message
            reason: Reason for bypassing hooks
            
        Returns:
            True if commit was successful
        """
        try:
            # Add bypass reason to commit message
            full_message = f"{commit_message}\n\nPre-commit bypass: {reason}"
            
            # Commit with --no-verify to bypass hooks
            result = subprocess.run(
                ["git", "commit", "-m", full_message, "--no-verify"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            self.logger.warning(f"Committed with pre-commit bypass: {reason}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to commit with bypass: {e}")
            return False
    
    def get_pre_commit_status(self) -> Dict[str, Any]:
        """
        Get comprehensive pre-commit status information.
        
        Returns:
            Dictionary with pre-commit status
        """
        config = self.get_pre_commit_config()
        
        status = {
            'configured': self.is_pre_commit_configured(),
            'installed': self.is_pre_commit_installed(),
            'config_file': str(self.config_file) if self.config_file.exists() else None,
            'hooks_count': len(config.hooks) if config else 0,
            'repos_count': len(config.repos) if config else 0
        }
        
        if config:
            status['hooks'] = [
                {
                    'id': hook.get('id', 'unknown'),
                    'name': hook.get('name', hook.get('id', 'unknown')),
                    'language': hook.get('language', 'unknown')
                }
                for hook in config.hooks
            ]
        
        return status