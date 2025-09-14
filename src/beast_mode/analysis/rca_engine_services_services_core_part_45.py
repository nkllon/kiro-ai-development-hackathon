from src.rm_ddd.core.health import ModuleHealth

def _generate_makefile_specific_fix(self, root_cause: RootCause) -> SystematicFix:
    """Generate Makefile-specific systematic fix"""
    fix_id = f'fix_{root_cause.cause_type.value}_{int(time.time())}'
    if root_cause.cause_type == RootCauseType.MAKEFILE_ERROR:
        return SystematicFix(fix_id=fix_id, root_cause=root_cause, fix_description='Fix Makefile errors by correcting syntax and target definitions', implementation_steps=['Identify specific Makefile error from message', 'Check for tab vs space issues (use tabs for indentation)', 'Verify target definitions and dependencies', 'Add missing targets or fix existing ones', 'Validate Makefile syntax with make -n', 'Test make targets execute correctly'], validation_criteria=['Makefile syntax is valid', 'make help command succeeds', 'Target dependencies are correct', 'Make targets execute without errors'], rollback_plan='Restore original Makefile from backup', estimated_time_minutes=8)
    elif root_cause.cause_type == RootCauseType.BUILD_DEPENDENCY_ERROR:
        return SystematicFix(fix_id=fix_id, root_cause=root_cause, fix_description='Fix build dependency errors by installing required tools and libraries', implementation_steps=['Identify missing build dependencies from error', 'Check system package manager for required tools', 'Install missing build tools (make, gcc, etc.)', 'Verify tool versions are compatible', 'Update PATH if necessary', 'Test build process with dependencies'], validation_criteria=['All required build tools are available', 'Tool versions meet requirements', 'Build process completes successfully', 'No dependency errors in build output'], rollback_plan='Remove installed packages if they cause conflicts', estimated_time_minutes=15)
    else:
        return SystematicFix(fix_id=fix_id, root_cause=root_cause, fix_description=f'Generic Makefile fix for {root_cause.cause_type.value}', implementation_steps=[f'Analyze {root_cause.cause_type.value} systematically', 'Review Makefile documentation', 'Implement appropriate fix', 'Validate fix resolves root cause'], validation_criteria=['Makefile error no longer occurs', 'Build process completes successfully'], rollback_plan='Revert changes if fix fails', estimated_time_minutes=10)

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

