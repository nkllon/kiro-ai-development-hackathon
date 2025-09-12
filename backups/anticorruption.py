"""
Anti-corruption layer utilities for bounded context integration.

This module provides base classes and utilities for implementing anti-corruption
layers that protect domain models from external system contamination and enable
clean integration between bounded contexts.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from ..core.base import DomainReflectiveModule
from ..core.compliance import ValidationResult
from ..models import DomainException, DomainBoundaries


logger = logging.getLogger(__name__)

# Type variables for generic adapters
ExternalType = TypeVar('ExternalType')
DomainType = TypeVar('DomainType')


@dataclass
class TranslationRule:
    """Defines a translation rule between external and domain models."""
    source_field: str
    target_field: str
    transformation: Optional[str] = None
    validation_rule: Optional[str] = None
    default_value: Any = None
    required: bool = True


@dataclass
class ContextMapping:
    """Defines mapping between bounded contexts."""
    source_context: str
    target_context: str
    relationship_type: str  # customer_supplier, conformist, anticorruption_layer, etc.
    translation_rules: List[TranslationRule] = field(default_factory=list)
    integration_pattern: str = "anticorruption_layer"
    data_flow_direction: str = "bidirectional"  # bidirectional, source_to_target, target_to_source


class ContextTranslator(ABC, Generic[ExternalType, DomainType]):
    """
    Abstract base class for translating between external and domain models.
    
    Provides systematic translation capabilities while protecting domain
    models from external system contamination.
    """
    
    def __init__(self, context_mapping: ContextMapping):
        self.context_mapping = context_mapping
        self._translation_cache: Dict[str, Any] = {}
        self._translation_errors: List[str] = []
    
    @abstractmethod
    def translate_to_domain(self, external_model: ExternalType) -> DomainType:
        """
        Translate external model to domain model.
        
        Args:
            external_model: External system model
            
        Returns:
            DomainType: Translated domain model
            
        Raises:
            DomainException: If translation fails
        """
        pass
    
    @abstractmethod
    def translate_from_domain(self, domain_model: DomainType) -> ExternalType:
        """
        Translate domain model to external model.
        
        Args:
            domain_model: Domain model
            
        Returns:
            ExternalType: Translated external model
            
        Raises:
            DomainException: If translation fails
        """
        pass
    
    def validate_translation(self, 
                           external_model: ExternalType, 
                           domain_model: DomainType) -> ValidationResult:
        """
        Validate that translation maintains data integrity.
        
        Args:
            external_model: Original external model
            domain_model: Translated domain model
            
        Returns:
            ValidationResult: Validation results
        """
        result = ValidationResult(is_valid=True)
        
        try:
            # Apply validation rules from context mapping
            for rule in self.context_mapping.translation_rules:
                if rule.validation_rule:
                    # This would be implemented with actual validation logic
                    pass
            
            # Check required fields
            for rule in self.context_mapping.translation_rules:
                if rule.required:
                    domain_value = getattr(domain_model, rule.target_field, None)
                    if domain_value is None:
                        result.add_error(f"Required field {rule.target_field} is missing")
            
        except Exception as e:
            result.add_error(f"Translation validation failed: {str(e)}")
        
        return result
    
    def get_translation_errors(self) -> List[str]:
        """Get translation errors."""
        return self._translation_errors.copy()
    
    def clear_translation_errors(self):
        """Clear translation errors."""
        self._translation_errors.clear()


class DomainAdapter(DomainReflectiveModule, Generic[ExternalType, DomainType]):
    """
    Adapter for integrating external systems with domain models.
    
    Provides systematic adaptation capabilities while maintaining
    domain integrity and preventing external contamination.
    """
    
    def __init__(self, 
                 domain_context: str,
                 external_system_name: str,
                 translator: ContextTranslator[ExternalType, DomainType]):
        super().__init__(domain_context)
        self.external_system_name = external_system_name
        self.translator = translator
        self._adaptation_metrics = {
            'successful_adaptations': 0,
            'failed_adaptations': 0,
            'last_adaptation': None
        }
    
    async def adapt_from_external(self, external_data: ExternalType) -> DomainType:
        """
        Adapt external data to domain model.
        
        Args:
            external_data: Data from external system
            
        Returns:
            DomainType: Adapted domain model
            
        Raises:
            DomainException: If adaptation fails
        """
        try:
            # Translate external data to domain model
            domain_model = self.translator.translate_to_domain(external_data)
            
            # Validate translation
            validation_result = self.translator.validate_translation(external_data, domain_model)
            if not validation_result.is_valid:
                raise DomainException(
                    f"Translation validation failed: {validation_result.errors}",
                    error_code="TRANSLATION_VALIDATION_FAILED"
                )
            
            # Update metrics
            self._adaptation_metrics['successful_adaptations'] += 1
            self._adaptation_metrics['last_adaptation'] = datetime.now()
            
            logger.info(f"Successfully adapted data from {self.external_system_name}")
            return domain_model
            
        except Exception as e:
            self._adaptation_metrics['failed_adaptations'] += 1
            logger.error(f"Failed to adapt data from {self.external_system_name}: {e}")
            raise DomainException(
                f"Adaptation failed: {str(e)}",
                error_code="ADAPTATION_FAILED",
                context={'external_system': self.external_system_name}
            )
    
    async def adapt_to_external(self, domain_model: DomainType) -> ExternalType:
        """
        Adapt domain model to external format.
        
        Args:
            domain_model: Domain model to adapt
            
        Returns:
            ExternalType: Adapted external format
            
        Raises:
            DomainException: If adaptation fails
        """
        try:
            # Translate domain model to external format
            external_data = self.translator.translate_from_domain(domain_model)
            
            # Update metrics
            self._adaptation_metrics['successful_adaptations'] += 1
            self._adaptation_metrics['last_adaptation'] = datetime.now()
            
            logger.info(f"Successfully adapted data to {self.external_system_name}")
            return external_data
            
        except Exception as e:
            self._adaptation_metrics['failed_adaptations'] += 1
            logger.error(f"Failed to adapt data to {self.external_system_name}: {e}")
            raise DomainException(
                f"Adaptation failed: {str(e)}",
                error_code="ADAPTATION_FAILED",
                context={'external_system': self.external_system_name}
            )
    
    def get_adaptation_metrics(self) -> Dict[str, Any]:
        """Get adaptation metrics."""
        return self._adaptation_metrics.copy()
    
    async def get_module_status(self):
        """Get module status."""
        from ..core.health import ModuleHealth
        from ..models import ModuleStatus
        
        total_adaptations = (self._adaptation_metrics['successful_adaptations'] + 
                           self._adaptation_metrics['failed_adaptations'])
        success_rate = 0.0
        if total_adaptations > 0:
            success_rate = self._adaptation_metrics['successful_adaptations'] / total_adaptations
        
        status = ModuleStatus.AVAILABLE if success_rate > 0.9 else ModuleStatus.DEGRADED
        
        return ModuleHealth(
            status=status,
            message=f"Domain adapter for {self.external_system_name}",
            capabilities=await self.get_module_capabilities(),
            health_indicators={
                'success_rate': success_rate,
                'total_adaptations': total_adaptations,
                'external_system': self.external_system_name
            }
        )
    
    async def get_module_capabilities(self):
        """Get module capabilities."""
        from ..models import ModuleCapability
        
        return [
            ModuleCapability(
                name=f"domain_adapter_{self.external_system_name}",
                description=f"Domain adapter for {self.external_system_name}",
                available=True,
                version="1.0.0"
            )
        ]
    
    async def is_healthy(self) -> bool:
        """Check if adapter is healthy."""
        total_adaptations = (self._adaptation_metrics['successful_adaptations'] + 
                           self._adaptation_metrics['failed_adaptations'])
        if total_adaptations == 0:
            return True  # No adaptations yet, assume healthy
        
        success_rate = self._adaptation_metrics['successful_adaptations'] / total_adaptations
        return success_rate > 0.9
    
    async def get_health_indicators(self):
        """Get health indicators."""
        return {
            'adaptation_metrics': self._adaptation_metrics,
            'external_system': self.external_system_name,
            'translator_errors': len(self.translator.get_translation_errors())
        }
    
    def get_domain_boundaries(self):
        """Get domain boundaries."""
        return DomainBoundaries(
            context=self.domain_context,
            invariants=[
                "External data must be validated before domain integration",
                "Domain models must not leak external system details",
                "Translation must preserve domain integrity"
            ],
            external_dependencies=[self.external_system_name]
        )
    
    def validate_domain_invariants(self):
        """Validate domain invariants."""
        result = ValidationResult(is_valid=True)
        
        # Check translation errors
        translation_errors = self.translator.get_translation_errors()
        if translation_errors:
            result.add_error(f"Translation errors detected: {translation_errors}")
        
        # Check adaptation success rate
        total_adaptations = (self._adaptation_metrics['successful_adaptations'] + 
                           self._adaptation_metrics['failed_adaptations'])
        if total_adaptations > 0:
            success_rate = self._adaptation_metrics['successful_adaptations'] / total_adaptations
            if success_rate < 0.9:
                result.add_warning(f"Low adaptation success rate: {success_rate:.2%}")
        
        return result


class ExternalSystemAdapter(DomainAdapter[Dict[str, Any], Any]):
    """
    Generic adapter for external systems using dictionary-based data.
    
    Provides a concrete implementation for common external system integration
    scenarios where data is exchanged as dictionaries or JSON objects.
    """
    
    def __init__(self, 
                 domain_context: str,
                 external_system_name: str,
                 context_mapping: ContextMapping):
        translator = DictionaryTranslator(context_mapping)
        super().__init__(domain_context, external_system_name, translator)


class DictionaryTranslator(ContextTranslator[Dict[str, Any], Any]):
    """
    Translator for dictionary-based external data.
    
    Provides systematic translation between dictionary data structures
    and domain models using configurable translation rules.
    """
    
    def translate_to_domain(self, external_model: Dict[str, Any]) -> Any:
        """Translate dictionary to domain model."""
        try:
            domain_data = {}
            
            # Apply translation rules
            for rule in self.context_mapping.translation_rules:
                external_value = external_model.get(rule.source_field)
                
                if external_value is None:
                    if rule.required and rule.default_value is None:
                        raise ValueError(f"Required field {rule.source_field} is missing")
                    external_value = rule.default_value
                
                # Apply transformation if specified
                if rule.transformation and external_value is not None:
                    external_value = self._apply_transformation(external_value, rule.transformation)
                
                domain_data[rule.target_field] = external_value
            
            # Return as dictionary for now - in real implementation,
            # this would create the actual domain model instance
            return domain_data
            
        except Exception as e:
            self._translation_errors.append(str(e))
            raise DomainException(
                f"Translation to domain failed: {str(e)}",
                error_code="TRANSLATION_TO_DOMAIN_FAILED"
            )
    
    def translate_from_domain(self, domain_model: Any) -> Dict[str, Any]:
        """Translate domain model to dictionary."""
        try:
            external_data = {}
            
            # If domain model is a dictionary, use it directly
            if isinstance(domain_model, dict):
                domain_data = domain_model
            else:
                # Extract data from domain model
                domain_data = self._extract_domain_data(domain_model)
            
            # Apply reverse translation rules
            for rule in self.context_mapping.translation_rules:
                domain_value = domain_data.get(rule.target_field)
                
                if domain_value is not None:
                    # Apply reverse transformation if needed
                    if rule.transformation:
                        domain_value = self._apply_reverse_transformation(domain_value, rule.transformation)
                    
                    external_data[rule.source_field] = domain_value
            
            return external_data
            
        except Exception as e:
            self._translation_errors.append(str(e))
            raise DomainException(
                f"Translation from domain failed: {str(e)}",
                error_code="TRANSLATION_FROM_DOMAIN_FAILED"
            )
    
    def _apply_transformation(self, value: Any, transformation: str) -> Any:
        """Apply transformation to a value."""
        # This would implement actual transformation logic
        # For now, just return the value unchanged
        return value
    
    def _apply_reverse_transformation(self, value: Any, transformation: str) -> Any:
        """Apply reverse transformation to a value."""
        # This would implement reverse transformation logic
        # For now, just return the value unchanged
        return value
    
    def _extract_domain_data(self, domain_model: Any) -> Dict[str, Any]:
        """Extract data from domain model."""
        if hasattr(domain_model, '__dict__'):
            return domain_model.__dict__
        else:
            # For other types, try to convert to dict
            return dict(domain_model) if hasattr(domain_model, 'keys') else {}


class AntiCorruptionLayer(DomainReflectiveModule):
    """
    Anti-corruption layer for protecting domain models from external contamination.
    
    Coordinates multiple adapters and translators to provide a unified
    interface for external system integration while maintaining domain purity.
    """
    
    def __init__(self, domain_context: str, protected_contexts: List[str]):
        super().__init__(domain_context)
        self.protected_contexts = protected_contexts
        self._adapters: Dict[str, DomainAdapter] = {}
        self._context_mappings: Dict[str, ContextMapping] = {}
        self._integration_metrics = {
            'successful_integrations': 0,
            'failed_integrations': 0,
            'protected_contexts': len(protected_contexts)
        }
    
    def register_adapter(self, external_system: str, adapter: DomainAdapter):
        """
        Register an adapter for an external system.
        
        Args:
            external_system: Name of the external system
            adapter: Domain adapter for the system
        """
        self._adapters[external_system] = adapter
        logger.info(f"Registered adapter for external system: {external_system}")
    
    def register_context_mapping(self, external_system: str, mapping: ContextMapping):
        """
        Register context mapping for an external system.
        
        Args:
            external_system: Name of the external system
            mapping: Context mapping configuration
        """
        self._context_mappings[external_system] = mapping
        logger.info(f"Registered context mapping for: {external_system}")
    
    async def integrate_external_data(self, 
                                    external_system: str, 
                                    external_data: Any) -> Any:
        """
        Integrate external data through anti-corruption layer.
        
        Args:
            external_system: Name of the external system
            external_data: Data from external system
            
        Returns:
            Any: Integrated domain model
            
        Raises:
            DomainException: If integration fails
        """
        if external_system not in self._adapters:
            raise DomainException(
                f"No adapter registered for external system: {external_system}",
                error_code="NO_ADAPTER_REGISTERED"
            )
        
        try:
            adapter = self._adapters[external_system]
            domain_model = await adapter.adapt_from_external(external_data)
            
            self._integration_metrics['successful_integrations'] += 1
            logger.info(f"Successfully integrated data from {external_system}")
            
            return domain_model
            
        except Exception as e:
            self._integration_metrics['failed_integrations'] += 1
            logger.error(f"Failed to integrate data from {external_system}: {e}")
            raise
    
    async def export_domain_data(self, 
                                external_system: str, 
                                domain_model: Any) -> Any:
        """
        Export domain data through anti-corruption layer.
        
        Args:
            external_system: Name of the external system
            domain_model: Domain model to export
            
        Returns:
            Any: Exported external format
            
        Raises:
            DomainException: If export fails
        """
        if external_system not in self._adapters:
            raise DomainException(
                f"No adapter registered for external system: {external_system}",
                error_code="NO_ADAPTER_REGISTERED"
            )
        
        try:
            adapter = self._adapters[external_system]
            external_data = await adapter.adapt_to_external(domain_model)
            
            self._integration_metrics['successful_integrations'] += 1
            logger.info(f"Successfully exported data to {external_system}")
            
            return external_data
            
        except Exception as e:
            self._integration_metrics['failed_integrations'] += 1
            logger.error(f"Failed to export data to {external_system}: {e}")
            raise
    
    def get_registered_systems(self) -> List[str]:
        """Get list of registered external systems."""
        return list(self._adapters.keys())
    
    def get_integration_metrics(self) -> Dict[str, Any]:
        """Get integration metrics."""
        return self._integration_metrics.copy()
    
    async def get_module_status(self):
        """Get module status."""
        from ..core.health import ModuleHealth
        from ..models import ModuleStatus
        
        # Check health of all registered adapters
        healthy_adapters = 0
        for adapter in self._adapters.values():
            if await adapter.is_healthy():
                healthy_adapters += 1
        
        total_adapters = len(self._adapters)
        health_ratio = healthy_adapters / max(total_adapters, 1)
        
        status = ModuleStatus.AVAILABLE if health_ratio > 0.8 else ModuleStatus.DEGRADED
        
        return ModuleHealth(
            status=status,
            message=f"Anti-corruption layer protecting {len(self.protected_contexts)} contexts",
            capabilities=await self.get_module_capabilities(),
            health_indicators={
                'healthy_adapters': healthy_adapters,
                'total_adapters': total_adapters,
                'health_ratio': health_ratio,
                'integration_metrics': self._integration_metrics
            }
        )
    
    async def get_module_capabilities(self):
        """Get module capabilities."""
        from ..models import ModuleCapability
        
        return [
            ModuleCapability(
                name="anti_corruption_layer",
                description="Protects domain models from external contamination",
                available=True,
                version="1.0.0"
            )
        ]
    
    async def is_healthy(self) -> bool:
        """Check if anti-corruption layer is healthy."""
        if not self._adapters:
            return True  # No adapters registered yet
        
        healthy_count = 0
        for adapter in self._adapters.values():
            if await adapter.is_healthy():
                healthy_count += 1
        
        return healthy_count / len(self._adapters) > 0.8
    
    async def get_health_indicators(self):
        """Get health indicators."""
        adapter_health = {}
        for system, adapter in self._adapters.items():
            adapter_health[system] = await adapter.is_healthy()
        
        return {
            'protected_contexts': self.protected_contexts,
            'registered_systems': list(self._adapters.keys()),
            'adapter_health': adapter_health,
            'integration_metrics': self._integration_metrics
        }
    
    def get_domain_boundaries(self):
        """Get domain boundaries."""
        return DomainBoundaries(
            context=self.domain_context,
            invariants=[
                "External systems cannot directly access protected contexts",
                "All external data must pass through registered adapters",
                "Domain models must remain pure and uncontaminated"
            ],
            external_dependencies=list(self._adapters.keys()),
            integration_patterns=["anti_corruption_layer", "adapter_pattern"]
        )
    
    def validate_domain_invariants(self):
        """Validate domain invariants."""
        result = ValidationResult(is_valid=True)
        
        # Check that all protected contexts have appropriate protection
        for context in self.protected_contexts:
            if context not in [mapping.target_context for mapping in self._context_mappings.values()]:
                result.add_warning(f"Protected context {context} has no explicit mapping")
        
        # Check integration success rate
        total_integrations = (self._integration_metrics['successful_integrations'] + 
                            self._integration_metrics['failed_integrations'])
        if total_integrations > 0:
            success_rate = self._integration_metrics['successful_integrations'] / total_integrations
            if success_rate < 0.9:
                result.add_warning(f"Low integration success rate: {success_rate:.2%}")
        
        return result