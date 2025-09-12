"""
Makefile Integration System

This module provides integration with the existing makefile system,
allowing domain operations to be executed through makefile targets.
"""

import os
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .base import DomainSystemComponent
from .interfaces import MakefileIntegratorInterface
from .models import Domain, MakeTarget, ExecutionResult, ValidationResult
from .exceptions import (
    MakefileIntegrationError, MakefileNotFoundError, MakeTargetExecutionError
)
from .config import get_config


class MakefileIntegrator(DomainSystemComponent, MakefileIntegratorInterface):
    """
    Integrates domain operations with makefile system
    
    Provides makefile integration capabilities including:
    - Parsing existing makefile structure
    - Mapping domains to makefile targets
    - Executing makefile operations with domain context
    - Generating domain-specific makefile targets
    - Validating makefile integration completeness
    """
    
    def __init__(self, registry_manager=None, config: Optional[Dict[str, Any]] = None):
        super().__init__("makefile_integrator", config)
        
        # Configuration
        self.config_obj = get_config()
        self.makefile_base_path = Path(self.config_obj.get("makefile_base_path", "makefiles"))
        self.execution_timeout = self.config_obj.get("makefile_timeout_seconds", 300)
        self.parallel_execution = self.config_obj.get("makefile_parallel_execution", True)
        self.log_output = self.config_obj.get("makefile_log_output", True)
        
        # Registry manager (will be injected)
        self.registry_manager = registry_manager
        
        # Makefile state
        self._makefile_cache = {}
        self._target_cache = {}
        self._domain_target_mapping = {}
        self._last_scan_time = None
        
        # Statistics
        self.executions_count = 0
        self.successful_executions = 0
        self.failed_executions = 0
        self.total_execution_time = 0.0
        
        # Project root
        self.project_root = Path.cwd()
        
        self.logger.info(f"Initialized MakefileIntegrator with base path: {self.makefile_base_path}")
        
        # Scan makefiles on initialization
        self._scan_makefiles()
    
    def set_registry_manager(self, registry_manager):
        """Set the registry manager (dependency injection)"""
        self.registry_manager = registry_manager
        self._build_domain_target_mapping()
    
    def set_project_root(self, project_root: str):
        """Set the project root directory"""
        self.project_root = Path(project_root)
        self.makefile_base_path = self.project_root / "makefiles"
        self.logger.info(f"Set project root to: {self.project_root}")
        self._scan_makefiles()
    
    def _scan_makefiles(self):
        """Scan and parse all makefiles in the base path"""
        with self._time_operation("scan_makefiles"):
            try:
                if not self.makefile_base_path.exists():
                    self.logger.warning(f"Makefile base path does not exist: {self.makefile_base_path}")
                    return
                
                self._makefile_cache = {}
                self._target_cache = {}
                
                # Scan for makefile files
                makefile_patterns = ["*.mk", "Makefile*", "makefile*"]
                makefile_files = []
                
                for pattern in makefile_patterns:
                    makefile_files.extend(self.makefile_base_path.glob(pattern))
                
                # Parse each makefile
                for makefile_path in makefile_files:
                    try:
                        targets = self._parse_makefile(makefile_path)
                        self._makefile_cache[str(makefile_path)] = targets
                        
                        # Add targets to global target cache
                        for target in targets:
                            self._target_cache[target.name] = target
                        
                        self.logger.debug(f"Parsed {len(targets)} targets from {makefile_path}")
                        
                    except Exception as e:
                        self.logger.error(f"Failed to parse makefile {makefile_path}: {e}")
                
                self._last_scan_time = datetime.now()
                self.logger.info(f"Scanned {len(makefile_files)} makefiles, found {len(self._target_cache)} targets")
                
            except Exception as e:
                self._handle_error(e, "scan_makefiles")
    
    def _parse_makefile(self, makefile_path: Path) -> List[MakeTarget]:
        """Parse a makefile and extract targets"""
        targets = []
        
        try:
            with open(makefile_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple makefile parsing (could be enhanced with proper parser)
            lines = content.split('\n')
            current_target = None
            current_commands = []
            current_description = ""
            
            for line in lines:
                line = line.rstrip()
                
                # Skip empty lines and comments (except description comments)
                if not line:
                    continue
                
                # Check for description comments
                if line.startswith('#') and current_target is None:
                    current_description = line[1:].strip()
                    continue
                
                # Check for target definition (line with colon)
                if ':' in line and not line.startswith('\t') and not line.startswith(' '):
                    # Save previous target if exists
                    if current_target:
                        target = MakeTarget(
                            name=current_target,
                            description=current_description,
                            dependencies=self._parse_dependencies(current_target),
                            commands=current_commands.copy(),
                            domain_specific=self._is_domain_specific_target(current_target)
                        )
                        targets.append(target)
                    
                    # Start new target
                    target_line = line.split(':')[0].strip()
                    current_target = target_line
                    current_commands = []
                    # Keep description for next target
                
                # Check for command lines (indented with tab or spaces)
                elif line.startswith('\t') or (line.startswith(' ') and current_target):
                    command = line.strip()
                    if command and not command.startswith('#'):
                        current_commands.append(command)
                
                # Reset description after target
                elif current_target and not line.startswith('\t') and not line.startswith(' '):
                    current_description = ""
            
            # Save last target
            if current_target:
                target = MakeTarget(
                    name=current_target,
                    description=current_description,
                    dependencies=self._parse_dependencies(current_target),
                    commands=current_commands.copy(),
                    domain_specific=self._is_domain_specific_target(current_target)
                )
                targets.append(target)
            
        except Exception as e:
            self.logger.error(f"Error parsing makefile {makefile_path}: {e}")
        
        return targets
    
    def _parse_dependencies(self, target_line: str) -> List[str]:
        """Parse target dependencies from target line"""
        if ':' in target_line:
            parts = target_line.split(':', 1)
            if len(parts) > 1 and parts[1].strip():
                return [dep.strip() for dep in parts[1].split()]
        return []
    
    def _is_domain_specific_target(self, target_name: str) -> bool:
        """Check if a target is domain-specific"""
        # Simple heuristic - could be enhanced
        domain_indicators = [
            "domain", "component", "module", "service",
            "test-", "lint-", "format-", "validate-"
        ]
        
        target_lower = target_name.lower()
        return any(indicator in target_lower for indicator in domain_indicators)
    
    def _build_domain_target_mapping(self):
        """Build mapping between domains and makefile targets"""
        if not self.registry_manager:
            return
        
        with self._time_operation("build_domain_mapping"):
            try:
                self._domain_target_mapping = {}
                all_domains = self.registry_manager.get_all_domains()
                
                for domain_name, domain in all_domains.items():
                    matching_targets = []
                    
                    # Look for targets that match domain name
                    for target_name, target in self._target_cache.items():
                        if self._target_matches_domain(target_name, domain_name, domain):
                            matching_targets.append(target)
                    
                    self._domain_target_mapping[domain_name] = matching_targets
                
                self.logger.info(f"Built domain-target mapping for {len(all_domains)} domains")
                
            except Exception as e:
                self._handle_error(e, "build_domain_mapping")
    
    def _target_matches_domain(self, target_name: str, domain_name: str, domain: Domain) -> bool:
        """Check if a makefile target matches a domain"""
        target_lower = target_name.lower()
        domain_lower = domain_name.lower()
        
        # Direct name match
        if domain_lower in target_lower:
            return True
        
        # Check against domain patterns and content indicators
        for pattern in domain.patterns:
            pattern_parts = pattern.lower().split('/')
            for part in pattern_parts:
                if part and part in target_lower:
                    return True
        
        for indicator in domain.content_indicators:
            if indicator.lower() in target_lower:
                return True
        
        return False
    
    def get_domain_targets(self, domain_name: str) -> List[MakeTarget]:
        """Get available makefile targets for a domain"""
        with self._time_operation("get_domain_targets"):
            try:
                # Ensure mapping is built
                if not self._domain_target_mapping and self.registry_manager:
                    self._build_domain_target_mapping()
                
                return self._domain_target_mapping.get(domain_name, [])
                
            except Exception as e:
                self._handle_error(e, "get_domain_targets")
                return []
    
    def execute_domain_operation(self, domain: str, operation: str) -> ExecutionResult:
        """Execute makefile operation for a domain"""
        with self._time_operation("execute_domain_operation"):
            start_time = time.time()
            self.executions_count += 1
            
            try:
                # Find the target to execute
                target_name = f"{operation}-{domain}" if operation != domain else domain
                
                # Look for exact match first
                target = self._target_cache.get(target_name)
                if not target:
                    # Look for partial matches
                    for name, tgt in self._target_cache.items():
                        if operation in name.lower() and domain in name.lower():
                            target = tgt
                            target_name = name
                            break
                
                if not target:
                    raise MakefileIntegrationError(f"No makefile target found for domain '{domain}' operation '{operation}'")
                
                # Execute the makefile target
                result = self._execute_make_target(target_name)
                
                if result.success:
                    self.successful_executions += 1
                else:
                    self.failed_executions += 1
                
                execution_time = time.time() - start_time
                self.total_execution_time += execution_time
                
                return result
                
            except Exception as e:
                self.failed_executions += 1
                self._handle_error(e, "execute_domain_operation")
                
                return ExecutionResult(
                    success=False,
                    target=f"{operation}-{domain}",
                    output="",
                    error_output=str(e),
                    execution_time_ms=int((time.time() - start_time) * 1000),
                    exit_code=-1
                )
    
    def _execute_make_target(self, target_name: str) -> ExecutionResult:
        """Execute a specific makefile target"""
        start_time = time.time()
        
        try:
            # Build make command
            cmd = ["make", "-C", str(self.project_root), target_name]
            
            # Execute command
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.execution_timeout,
                cwd=self.project_root
            )
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Log output if enabled
            if self.log_output:
                if process.stdout:
                    self.logger.debug(f"Make output for {target_name}: {process.stdout}")
                if process.stderr:
                    self.logger.debug(f"Make errors for {target_name}: {process.stderr}")
            
            success = process.returncode == 0
            
            return ExecutionResult(
                success=success,
                target=target_name,
                output=process.stdout or "",
                error_output=process.stderr or "",
                execution_time_ms=execution_time_ms,
                exit_code=process.returncode
            )
            
        except subprocess.TimeoutExpired:
            execution_time_ms = int((time.time() - start_time) * 1000)
            return ExecutionResult(
                success=False,
                target=target_name,
                output="",
                error_output=f"Execution timed out after {self.execution_timeout} seconds",
                execution_time_ms=execution_time_ms,
                exit_code=-1
            )
        
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            return ExecutionResult(
                success=False,
                target=target_name,
                output="",
                error_output=str(e),
                execution_time_ms=execution_time_ms,
                exit_code=-1
            )
    
    def generate_domain_targets(self, domain: Domain) -> List[MakeTarget]:
        """Generate makefile targets for a domain"""
        with self._time_operation("generate_domain_targets"):
            try:
                targets = []
                domain_name = domain.name
                
                # Generate common domain targets
                target_templates = [
                    {
                        "name": f"test-{domain_name}",
                        "description": f"Run tests for {domain_name} domain",
                        "commands": [
                            f"@echo 'Running tests for {domain_name} domain'",
                            f"python3 -m pytest tests/unit/{domain_name}/ -v"
                        ]
                    },
                    {
                        "name": f"lint-{domain_name}",
                        "description": f"Run linter for {domain_name} domain",
                        "commands": [
                            f"@echo 'Linting {domain_name} domain'",
                            f"{domain.tools.linter} src/**/{domain_name}/**/*.py"
                        ]
                    },
                    {
                        "name": f"format-{domain_name}",
                        "description": f"Format code for {domain_name} domain",
                        "commands": [
                            f"@echo 'Formatting {domain_name} domain'",
                            f"{domain.tools.formatter} src/**/{domain_name}/**/*.py"
                        ]
                    },
                    {
                        "name": f"validate-{domain_name}",
                        "description": f"Validate {domain_name} domain",
                        "commands": [
                            f"@echo 'Validating {domain_name} domain'",
                            f"{domain.tools.validator} src/**/{domain_name}/**/*.py"
                        ]
                    },
                    {
                        "name": f"health-{domain_name}",
                        "description": f"Check health of {domain_name} domain",
                        "commands": [
                            f"@echo 'Checking health of {domain_name} domain'",
                            f"python3 -c \"from src.beast_mode.domain_index import DomainHealthMonitor; monitor = DomainHealthMonitor(); print(monitor.check_domain_health('{domain_name}'))\""
                        ]
                    }
                ]
                
                # Create MakeTarget objects
                for template in target_templates:
                    target = MakeTarget(
                        name=template["name"],
                        description=template["description"],
                        dependencies=[],
                        commands=template["commands"],
                        domain_specific=True,
                        estimated_duration="1-5 minutes"
                    )
                    targets.append(target)
                
                return targets
                
            except Exception as e:
                self._handle_error(e, "generate_domain_targets")
                return []
    
    def validate_makefile_integration(self) -> ValidationResult:
        """Validate makefile integration completeness"""
        with self._time_operation("validate_makefile_integration"):
            try:
                errors = []
                warnings = []
                suggestions = []
                
                # Check if makefile base path exists
                if not self.makefile_base_path.exists():
                    errors.append(f"Makefile base path does not exist: {self.makefile_base_path}")
                
                # Check if we have any makefiles
                if not self._makefile_cache:
                    warnings.append("No makefiles found in base path")
                
                # Check if we have domain targets
                if not self._target_cache:
                    warnings.append("No makefile targets found")
                
                # Check domain coverage
                if self.registry_manager:
                    all_domains = self.registry_manager.get_all_domains()
                    domains_without_targets = []
                    
                    for domain_name in all_domains:
                        domain_targets = self.get_domain_targets(domain_name)
                        if not domain_targets:
                            domains_without_targets.append(domain_name)
                    
                    if domains_without_targets:
                        warnings.append(f"Domains without makefile targets: {', '.join(domains_without_targets[:5])}")
                        if len(domains_without_targets) > 5:
                            warnings.append(f"... and {len(domains_without_targets) - 5} more")
                        
                        suggestions.append("Generate makefile targets for domains without coverage")
                
                # Check for common targets
                common_targets = ["test", "lint", "format", "clean", "build"]
                missing_common = [target for target in common_targets if target not in self._target_cache]
                
                if missing_common:
                    suggestions.append(f"Consider adding common targets: {', '.join(missing_common)}")
                
                # Check makefile syntax (basic)
                for makefile_path, targets in self._makefile_cache.items():
                    if not targets:
                        warnings.append(f"No targets found in {makefile_path}")
                
                return ValidationResult(
                    is_valid=len(errors) == 0,
                    errors=errors,
                    warnings=warnings,
                    suggestions=suggestions
                )
                
            except Exception as e:
                self._handle_error(e, "validate_makefile_integration")
                return ValidationResult(
                    is_valid=False,
                    errors=[f"Validation failed: {str(e)}"],
                    warnings=[],
                    suggestions=[]
                )
    
    def update_makefile_targets(self, domain: Domain, targets: List[MakeTarget]) -> bool:
        """Update makefile targets for a domain"""
        with self._time_operation("update_makefile_targets"):
            try:
                # Generate makefile content for domain
                makefile_content = self._generate_makefile_content(domain, targets)
                
                # Write to domain-specific makefile
                domain_makefile = self.makefile_base_path / f"{domain.name}.mk"
                
                with open(domain_makefile, 'w', encoding='utf-8') as f:
                    f.write(makefile_content)
                
                # Update cache
                self._makefile_cache[str(domain_makefile)] = targets
                for target in targets:
                    self._target_cache[target.name] = target
                
                self.logger.info(f"Updated makefile targets for domain {domain.name}")
                return True
                
            except Exception as e:
                self._handle_error(e, "update_makefile_targets")
                return False
    
    def _generate_makefile_content(self, domain: Domain, targets: List[MakeTarget]) -> str:
        """Generate makefile content for domain targets"""
        lines = [
            f"# Makefile for {domain.name} domain",
            f"# Generated by Beast Mode Domain Index System",
            f"# Generated at: {datetime.now().isoformat()}",
            "",
            f"# Domain: {domain.name}",
            f"# Description: {domain.description}",
            "",
        ]
        
        # Add targets
        for target in targets:
            lines.append(f"# {target.description}")
            
            # Target definition
            target_line = target.name
            if target.dependencies:
                target_line += f": {' '.join(target.dependencies)}"
            lines.append(f"{target_line}:")
            
            # Commands
            for command in target.commands:
                lines.append(f"\t{command}")
            
            lines.append("")  # Empty line between targets
        
        return "\n".join(lines)
    
    def get_makefile_health(self) -> Dict[str, Any]:
        """Get health status of makefile integration"""
        try:
            validation = self.validate_makefile_integration()
            
            return {
                "integration_valid": validation.is_valid,
                "total_makefiles": len(self._makefile_cache),
                "total_targets": len(self._target_cache),
                "domain_specific_targets": sum(1 for t in self._target_cache.values() if t.domain_specific),
                "domains_with_targets": len([d for d in self._domain_target_mapping.values() if d]),
                "last_scan_time": self._last_scan_time.isoformat() if self._last_scan_time else None,
                "execution_statistics": {
                    "total_executions": self.executions_count,
                    "successful_executions": self.successful_executions,
                    "failed_executions": self.failed_executions,
                    "success_rate": self.successful_executions / max(self.executions_count, 1),
                    "average_execution_time_ms": (self.total_execution_time / max(self.executions_count, 1)) * 1000
                },
                "validation_results": {
                    "errors": validation.errors,
                    "warnings": validation.warnings,
                    "suggestions": validation.suggestions
                }
            }
            
        except Exception as e:
            self._handle_error(e, "get_makefile_health")
            return {"error": str(e)}
    
    def rescan_makefiles(self) -> bool:
        """Rescan makefiles and rebuild caches"""
        try:
            self.logger.info("Rescanning makefiles")
            self._scan_makefiles()
            if self.registry_manager:
                self._build_domain_target_mapping()
            return True
        except Exception as e:
            self._handle_error(e, "rescan_makefiles")
            return False
    
    def get_integrator_stats(self) -> Dict[str, Any]:
        """Get makefile integrator statistics"""
        return {
            "makefiles_found": len(self._makefile_cache),
            "targets_found": len(self._target_cache),
            "domain_mappings": len(self._domain_target_mapping),
            "executions_performed": self.executions_count,
            "execution_success_rate": self.successful_executions / max(self.executions_count, 1),
            "last_scan_time": self._last_scan_time.isoformat() if self._last_scan_time else None,
            "makefile_base_path": str(self.makefile_base_path),
            "parallel_execution_enabled": self.parallel_execution,
            "performance_metrics": self.performance_metrics
        }