"""
Backward Compatibility Layer for unified_rdi_rm_analysis_system

This module provides backward compatibility for existing integrations
that use the original fragmented specifications.

Original specs supported: rdi-rm-compliance-check, rm-rdi-analysis-system
Consolidated interface: RDIRMAnalysisSystemInterface

Generated: 2025-09-05 08:31:35
"""

import warnings
from typing import Any, Dict, List, Optional

try:
    from src.spec_reconciliation.rdi_rm_analysis_system import RDIRMAnalysisSystemInterface
except ImportError:
    # Fallback if consolidated interface not available
    class RDIRMAnalysisSystemInterface:
        def __init__(self, *args, **kwargs):
            pass
        
        def __getattr__(self, name):
            raise NotImplementedError(f"Consolidated interface not available: {name}")


class CompatibilityWarning(UserWarning):
    """Warning for deprecated interface usage"""
    pass



class Rdi_Rm_Compliance_CheckCompatibility:
    """
    Backward compatibility wrapper for rdi-rm-compliance-check
    
    This class provides the old interface while delegating to the
    consolidated RDIRMAnalysisSystemInterface implementation.
    """
    
    def __init__(self, *args, **kwargs):
        warnings.warn(
            f"{self.__class__.__name__} is deprecated. "
            f"Use RDIRMAnalysisSystemInterface instead.",
            CompatibilityWarning,
            stacklevel=2
        )
        
        # Initialize the consolidated interface
        self._consolidated_interface = RDIRMAnalysisSystemInterface(*args, **kwargs)
    
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
            raise AttributeError(f"'Rdi_Rm_Compliance_CheckCompatibility' object has no attribute '{name}'")


# Convenience aliases for backward compatibility
Rdi_Rm_Compliance_CheckInterface = Rdi_Rm_Compliance_CheckCompatibility
Rdi_Rm_Compliance_CheckController = Rdi_Rm_Compliance_CheckCompatibility
Rdi_Rm_Compliance_CheckManager = Rdi_Rm_Compliance_CheckCompatibility


class Rm_Rdi_Analysis_SystemCompatibility:
    """
    Backward compatibility wrapper for rm-rdi-analysis-system
    
    This class provides the old interface while delegating to the
    consolidated RDIRMAnalysisSystemInterface implementation.
    """
    
    def __init__(self, *args, **kwargs):
        warnings.warn(
            f"{self.__class__.__name__} is deprecated. "
            f"Use RDIRMAnalysisSystemInterface instead.",
            CompatibilityWarning,
            stacklevel=2
        )
        
        # Initialize the consolidated interface
        self._consolidated_interface = RDIRMAnalysisSystemInterface(*args, **kwargs)
    
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
            raise AttributeError(f"'Rm_Rdi_Analysis_SystemCompatibility' object has no attribute '{name}'")


# Convenience aliases for backward compatibility
Rm_Rdi_Analysis_SystemInterface = Rm_Rdi_Analysis_SystemCompatibility
Rm_Rdi_Analysis_SystemController = Rm_Rdi_Analysis_SystemCompatibility
Rm_Rdi_Analysis_SystemManager = Rm_Rdi_Analysis_SystemCompatibility

