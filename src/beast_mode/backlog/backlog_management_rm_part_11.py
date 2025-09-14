from src.rm_ddd.core.health import ModuleHealth

    def _check_boundary_violations(self) -> List[str]:
        """Check for architectural boundary violations"""
        violations = []
        
        # Check if we're doing dependency management (should be delegated)
        # Check if we're doing validation (should be delegated to Ghostbusters)
        # Check if we're doing direct data persistence (should be abstracted)
        
        # For now, return empty as this is the base implementation
        return violations
        

        
    # Core backlog operations (delegated to BacklogCoreOperations)
    