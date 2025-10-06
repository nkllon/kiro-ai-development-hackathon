"""
Integration Validation Engine
Implements mathematical validation of component integration contracts
with runtime verification and performance validation.
"""

import importlib
import importlib.util
import logging
import time
import traceback
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import sys

from .dag_registry import MathematicalDAGRegistry, ComponentNode


@dataclass
class ValidationResult:
    """Result of component validation"""
    component_name: str
    success: bool
    error_message: Optional[str] = None
    warnings: List[str] = None
    execution_time: float = 0.0
    imports_validated: int = 0
    exports_validated: int = 0
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


@dataclass
class InterfaceContract:
    """Mathematical interface contract between components"""
    component_name: str
    exports: Set[str]
    imports: Set[str]
    version: str = "1.0.0"
    constraints: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.constraints is None:
            self.constraints = {}
    
    def is_compatible_with(self, other: 'InterfaceContract') -> bool:
        """
        Mathematical compatibility check using set theory
        Returns True if this component's exports satisfy other's imports
        """
        return self.exports >= other.imports
    
    def get_missing_exports(self, other: 'InterfaceContract') -> Set[str]:
        """Get exports that are missing to satisfy other component's imports"""
        return other.imports - self.exports


class IntegrationValidator:
    """
    Mathematical Integration Validation Engine
    
    Validates component integration using mathematical proofs:
    - Set theory for import/export satisfaction
    - Runtime verification for actual availability
    - Performance validation for mathematical constraints
    """
    
    def __init__(self, dag_registry: MathematicalDAGRegistry):
        self.dag_registry = dag_registry
        self.logger = logging.getLogger("integration_governance.validator")
        
        # Validation state
        self.validation_results: Dict[str, ValidationResult] = {}
        self.contract_registry: Dict[str, InterfaceContract] = {}
        
        self.logger.info("Integration validator initialized")
    
    def validate_component(self, component_name: str) -> ValidationResult:
        """
        Validate a single component's integration
        Mathematical guarantee: Comprehensive validation of all contracts
        """
        start_time = time.time()
        self.logger.info(f"Validating component: {component_name}")
        
        if component_name not in self.dag_registry.components:
            return ValidationResult(
                component_name=component_name,
                success=False,
                error_message=f"Component {component_name} not found in registry"
            )
        
        component = self.dag_registry.components[component_name]
        warnings = []
        
        try:
            # Step 1: Mathematical contract validation
            contract_result = self._validate_contracts(component)
            if not contract_result:
                return ValidationResult(
                    component_name=component_name,
                    success=False,
                    error_message="Contract validation failed",
                    execution_time=time.time() - start_time
                )
            
            # Step 2: Runtime import validation
            import_result = self._validate_runtime_imports(component)
            if not import_result.success:
                return import_result
            
            # Step 3: Export availability validation
            export_result = self._validate_exports(component)
            if not export_result.success:
                return export_result
            
            # Step 4: Performance validation
            perf_warnings = self._validate_performance_constraints(component)
            warnings.extend(perf_warnings)
            
            # Success!
            result = ValidationResult(
                component_name=component_name,
                success=True,
                warnings=warnings,
                execution_time=time.time() - start_time,
                imports_validated=len(component.imports),
                exports_validated=len(component.exports)
            )
            
            self.validation_results[component_name] = result
            self.logger.info(f"✅ Component {component_name} validated successfully")
            return result
            
        except Exception as e:
            error_msg = f"Validation failed: {str(e)}"
            self.logger.error(f"❌ Component {component_name} validation failed: {error_msg}")
            
            result = ValidationResult(
                component_name=component_name,
                success=False,
                error_message=error_msg,
                execution_time=time.time() - start_time
            )
            
            self.validation_results[component_name] = result
            return result
    
    def _validate_contracts(self, component: ComponentNode) -> bool:
        """
        Validate mathematical contracts using set theory
        Mathematical guarantee: Imports ⊆ Available_Exports
        """
        # Get component's contract
        contract = InterfaceContract(
            component_name=component.name,
            exports=component.exports,
            imports=component.internal_imports  # Only validate internal imports
        )
        
        # Check if all internal imports can be satisfied
        for import_name in component.internal_imports:
            providing_component = self.dag_registry._find_providing_component(import_name)
            if not providing_component:
                self.logger.error(f"No component provides import: {import_name}")
                return False
            
            provider = self.dag_registry.components[providing_component]
            provider_contract = InterfaceContract(
                component_name=provider.name,
                exports=provider.exports,
                imports=provider.internal_imports
            )
            
            # Mathematical validation: provider exports must satisfy component imports
            if not provider_contract.is_compatible_with(contract):
                missing = provider_contract.get_missing_exports(contract)
                self.logger.error(f"Contract violation: {provider.name} missing exports: {missing}")
                return False
        
        return True
    
    def _validate_runtime_imports(self, component: ComponentNode) -> ValidationResult:
        """
        Validate that imports actually work at runtime
        Mathematical guarantee: Actual import success/failure
        """
        try:
            # Add project root to Python path temporarily
            original_path = sys.path.copy()
            project_root = str(Path(component.file_path).parent.parent.parent)
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            
            try:
                # Test import the component
                spec = importlib.util.spec_from_file_location(component.name, component.file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    return ValidationResult(
                        component_name=component.name,
                        success=True,
                        imports_validated=len(component.imports)
                    )
                else:
                    return ValidationResult(
                        component_name=component.name,
                        success=False,
                        error_message="Could not create module spec"
                    )
            finally:
                # Restore original Python path
                sys.path = original_path
                
        except Exception as e:
            return ValidationResult(
                component_name=component.name,
                success=False,
                error_message=f"Runtime import failed: {str(e)}"
            )
    
    def _validate_exports(self, component: ComponentNode) -> ValidationResult:
        """
        Validate that declared exports actually exist
        Mathematical guarantee: Declared exports ⊆ Actual exports
        """
        try:
            # Import the component and check exports
            spec = importlib.util.spec_from_file_location(component.name, component.file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Check that all declared exports exist
                missing_exports = []
                for export in component.exports:
                    if not hasattr(module, export):
                        missing_exports.append(export)
                
                if missing_exports:
                    return ValidationResult(
                        component_name=component.name,
                        success=False,
                        error_message=f"Missing declared exports: {missing_exports}"
                    )
                
                return ValidationResult(
                    component_name=component.name,
                    success=True,
                    exports_validated=len(component.exports)
                )
            else:
                return ValidationResult(
                    component_name=component.name,
                    success=False,
                    error_message="Could not load module for export validation"
                )
                
        except Exception as e:
            return ValidationResult(
                component_name=component.name,
                success=False,
                error_message=f"Export validation failed: {str(e)}"
            )
    
    def _validate_performance_constraints(self, component: ComponentNode) -> List[str]:
        """
        Validate performance constraints
        Mathematical guarantee: Measurable performance bounds
        """
        warnings = []
        
        # Check file size constraints
        file_path = Path(component.file_path)
        if file_path.exists():
            file_size = file_path.stat().st_size
            
            # Mathematical constraint: files > 50KB may have performance issues
            if file_size > 50 * 1024:
                warnings.append(f"Large file size: {file_size / 1024:.1f}KB (consider refactoring)")
            
            # Mathematical constraint: too many imports may indicate coupling issues
            if len(component.imports) > 20:
                warnings.append(f"High import count: {len(component.imports)} (consider decoupling)")
            
            # Mathematical constraint: too many exports may indicate SRP violation
            if len(component.exports) > 15:
                warnings.append(f"High export count: {len(component.exports)} (consider splitting)")
        
        return warnings
    
    def validate_all_components(self) -> Dict[str, ValidationResult]:
        """
        Validate all components in topological order
        Mathematical guarantee: Dependencies validated before dependents
        """
        self.logger.info("Starting comprehensive component validation")
        
        if not self.dag_registry.topological_order:
            self.dag_registry._analyze_graph_properties()
        
        if self.dag_registry.cycles:
            raise CyclicDependencyError(self.dag_registry.cycles[0])
        
        # Validate in topological order
        for component_name in self.dag_registry.topological_order:
            result = self.validate_component(component_name)
            if not result.success:
                self.logger.error(f"Validation failed for {component_name}, stopping validation")
                break
        
        return self.validation_results
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of all validation results"""
        if not self.validation_results:
            return {"status": "no_validations_run"}
        
        total = len(self.validation_results)
        successful = len([r for r in self.validation_results.values() if r.success])
        failed = total - successful
        
        total_time = sum(r.execution_time for r in self.validation_results.values())
        avg_time = total_time / total if total > 0 else 0
        
        return {
            "total_components": total,
            "successful_validations": successful,
            "failed_validations": failed,
            "success_rate": (successful / total) * 100 if total > 0 else 0,
            "total_validation_time": total_time,
            "average_validation_time": avg_time,
            "mathematical_guarantee": successful == total
        }


# Factory function
def create_validator(dag_registry: MathematicalDAGRegistry) -> IntegrationValidator:
    """Create integration validator with DAG registry"""
    return IntegrationValidator(dag_registry)


# Export main classes
__all__ = ["IntegrationValidator", "ValidationResult", "InterfaceContract", "create_validator"]