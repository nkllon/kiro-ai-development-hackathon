"""
Backward Compatibility Layer for unified_beast_mode_system

This module provides backward compatibility for existing integrations
that use the original fragmented specifications.

Original specs supported: beast-mode-framework, integrated-beast-mode-system
Consolidated interface: BeastModeSystemInterface

Generated: 2025-09-05 11:28:02
"""

import warnings
from typing import Any, Dict, List, Optional

try:
    from src.spec_reconciliation.beast_mode_system import BeastModeSystemInterface
except ImportError:
    # Fallback if consolidated interface not available
    class BeastModeSystemInterface:
        def __init__(self, *args, **kwargs):
            pass
        
        def __getattr__(self, name):
            raise NotImplementedError(f"Consolidated interface not available: {name}")


class CompatibilityWarning(UserWarning):
    """Warning for deprecated interface usage"""
    pass



class Beast_Mode_FrameworkCompatibility:
    """
    Backward compatibility wrapper for beast-mode-framework
    
    This class provides the old interface while delegating to the
    consolidated BeastModeSystemInterface implementation.
    """
    
    def __init__(self, *args, **kwargs):
        warnings.warn(
            f"{self.__class__.__name__} is deprecated. "
            f"Use BeastModeSystemInterface instead.",
            CompatibilityWarning,
            stacklevel=2
        )
        
        # Initialize the consolidated interface
        self._consolidated_interface = BeastModeSystemInterface(*args, **kwargs)
    
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
            raise AttributeError(f"'Beast_Mode_FrameworkCompatibility' object has no attribute '{name}'")


# Convenience aliases for backward compatibility
Beast_Mode_FrameworkInterface = Beast_Mode_FrameworkCompatibility
Beast_Mode_FrameworkController = Beast_Mode_FrameworkCompatibility
Beast_Mode_FrameworkManager = Beast_Mode_FrameworkCompatibility


class Integrated_Beast_Mode_SystemCompatibility:
    """
    Backward compatibility wrapper for integrated-beast-mode-system
    
    This class provides the old interface while delegating to the
    consolidated BeastModeSystemInterface implementation.
    """
    
    def __init__(self, *args, **kwargs):
        warnings.warn(
            f"{self.__class__.__name__} is deprecated. "
            f"Use BeastModeSystemInterface instead.",
            CompatibilityWarning,
            stacklevel=2
        )
        
        # Initialize the consolidated interface
        self._consolidated_interface = BeastModeSystemInterface(*args, **kwargs)
    
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
            raise AttributeError(f"'Integrated_Beast_Mode_SystemCompatibility' object has no attribute '{name}'")


# Convenience aliases for backward compatibility
Integrated_Beast_Mode_SystemInterface = Integrated_Beast_Mode_SystemCompatibility
Integrated_Beast_Mode_SystemController = Integrated_Beast_Mode_SystemCompatibility
Integrated_Beast_Mode_SystemManager = Integrated_Beast_Mode_SystemCompatibility

