"""
Backward Compatibility Layer for unified_testing_rca_framework

This module provides backward compatibility for existing integrations
that use the original fragmented specifications.

Original specs supported: test-rca-integration, test-rca-issues-resolution
Consolidated interface: TestingRCAFrameworkInterface

Generated: 2025-09-05 08:31:35
"""

import warnings
from typing import Any, Dict, List, Optional

try:
    from src.spec_reconciliation.testing_rca_framework import TestingRCAFrameworkInterface
except ImportError:
    # Fallback if consolidated interface not available
    class TestingRCAFrameworkInterface:
        def __init__(self, *args, **kwargs):
            pass
        
        def __getattr__(self, name):
            raise NotImplementedError(f"Consolidated interface not available: {name}")


class CompatibilityWarning(UserWarning):
    """Warning for deprecated interface usage"""
    pass



class Test_Rca_IntegrationCompatibility:
    """
    Backward compatibility wrapper for test-rca-integration
    
    This class provides the old interface while delegating to the
    consolidated TestingRCAFrameworkInterface implementation.
    """
    
    def __init__(self, *args, **kwargs):
        warnings.warn(
            f"{self.__class__.__name__} is deprecated. "
            f"Use TestingRCAFrameworkInterface instead.",
            CompatibilityWarning,
            stacklevel=2
        )
        
        # Initialize the consolidated interface
        self._consolidated_interface = TestingRCAFrameworkInterface(*args, **kwargs)
    
    def __getattr__(self, name: str) -> Any:
        """
        Delegate attribute access to consolidated interface
        with method name mapping if needed.
        """
        # Map old method names to new ones
        method_mappings = {
            "execute_beast_mode": "execute_pdca_cycle",
            "check_tool_status": "manage_tool_health",
            "perform_rca": "execute_comprehensive_rca",
            "run_test_suite": "execute_integrated_testing",
            "check_compliance": "validate_rdi_compliance"
        }
        
        # Use mapped method name if available
        mapped_name = method_mappings.get(name, name)
        
        if hasattr(self._consolidated_interface, mapped_name):
            return getattr(self._consolidated_interface, mapped_name)
        else:
            raise AttributeError(f"'Test_Rca_IntegrationCompatibility' object has no attribute '{name}'")


# Convenience aliases for backward compatibility
Test_Rca_IntegrationInterface = Test_Rca_IntegrationCompatibility
Test_Rca_IntegrationController = Test_Rca_IntegrationCompatibility
Test_Rca_IntegrationManager = Test_Rca_IntegrationCompatibility


class Test_Rca_Issues_ResolutionCompatibility:
    """
    Backward compatibility wrapper for test-rca-issues-resolution
    
    This class provides the old interface while delegating to the
    consolidated TestingRCAFrameworkInterface implementation.
    """
    
    def __init__(self, *args, **kwargs):
        warnings.warn(
            f"{self.__class__.__name__} is deprecated. "
            f"Use TestingRCAFrameworkInterface instead.",
            CompatibilityWarning,
            stacklevel=2
        )
        
        # Initialize the consolidated interface
        self._consolidated_interface = TestingRCAFrameworkInterface(*args, **kwargs)
    
    def __getattr__(self, name: str) -> Any:
        """
        Delegate attribute access to consolidated interface
        with method name mapping if needed.
        """
        # Map old method names to new ones
        method_mappings = {
            "execute_beast_mode": "execute_pdca_cycle",
            "check_tool_status": "manage_tool_health",
            "perform_rca": "execute_comprehensive_rca",
            "run_test_suite": "execute_integrated_testing",
            "check_compliance": "validate_rdi_compliance"
        }
        
        # Use mapped method name if available
        mapped_name = method_mappings.get(name, name)
        
        if hasattr(self._consolidated_interface, mapped_name):
            return getattr(self._consolidated_interface, mapped_name)
        else:
            raise AttributeError(f"'Test_Rca_Issues_ResolutionCompatibility' object has no attribute '{name}'")


# Convenience aliases for backward compatibility
Test_Rca_Issues_ResolutionInterface = Test_Rca_Issues_ResolutionCompatibility
Test_Rca_Issues_ResolutionController = Test_Rca_Issues_ResolutionCompatibility
Test_Rca_Issues_ResolutionManager = Test_Rca_Issues_ResolutionCompatibility

