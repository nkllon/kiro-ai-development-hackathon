"""
Makefile Integrator Core Validation

This module was extracted from makefile_integrator_core.py
as part of RM-DDD compliance refactoring.
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
from .exceptions import MakefileIntegrationError, MakefileNotFoundError, MakeTargetExecutionError
from .config import get_config
from src.rm_ddd.core.health import ModuleHealth


def validate_makefile_integration(self) -> ValidationResult:
    """Validate makefile integration completeness"""
    with self._time_operation('validate_makefile_integration'):
        try:
            errors = []
            warnings = []
            suggestions = []
            if not self.makefile_base_path.exists():
                errors.append(f'Makefile base path does not exist: {self.makefile_base_path}')
            if not self._makefile_cache:
                warnings.append('No makefiles found in base path')
            if not self._target_cache:
                warnings.append('No makefile targets found')
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
                        warnings.append(f'... and {len(domains_without_targets) - 5} more')
                    suggestions.append('Generate makefile targets for domains without coverage')
            common_targets = ['test', 'lint', 'format', 'clean', 'build']
            missing_common = [target for target in common_targets if target not in self._target_cache]
            if missing_common:
                suggestions.append(f"Consider adding common targets: {', '.join(missing_common)}")
            for makefile_path, targets in self._makefile_cache.items():
                if not targets:
                    warnings.append(f'No targets found in {makefile_path}')
            return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, suggestions=suggestions)
        except Exception as e:
            self._handle_error(e, 'validate_makefile_integration')
            return ValidationResult(is_valid=False, errors=[f'Validation failed: {str(e)}'], warnings=[], suggestions=[])

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

