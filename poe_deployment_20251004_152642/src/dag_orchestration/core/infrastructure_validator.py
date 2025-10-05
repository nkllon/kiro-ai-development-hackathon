#!/usr/bin/env python3
"""
Infrastructure Validator for DAG Orchestration System
====================================================

Formal infrastructure validation component that integrates with the DAG orchestration
system to ensure all preconditions are met before parallel execution.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
    GracefulDegradationResult
)
from src.dag_orchestration.infrastructure.precondition_validator import (
    InfrastructurePreconditionValidator,
    InfrastructureReport,
    PreconditionResult
)


@dataclass
class ValidationPolicy:
    """Infrastructure validation policy configuration."""
    redis_timeout_seconds: float = 5.0
    resource_check_interval_seconds: int = 30
    validation_cache_ttl_seconds: int = 300  # 5 minutes
    require_redis_connectivity: bool = True
    require_minimum_resources: bool = True
    auto_remediation_enabled: bool = False


@dataclass
class ValidationContext:
    """Context for infrastructure validation operations."""
    validation_id: str
    requested_at: datetime
    policy: ValidationPolicy
    execution_requirements: Dict[str, Any]
    cached_results: Optional[InfrastructureReport] = None


class InfrastructureValidator(ReflectiveModule):
    """
    Formal infrastructure validator for DAG orchestration system.
    
    Provides:
    - Continuous infrastructure monitoring
    - Validation caching and optimization
    - Integration with DAG execution pipeline
    - Automatic remediation capabilities
    """
    
    def __init__(self, validation_policy: Optional[ValidationPolicy] = None):
        super().__init__()
        self.module_id = "InfrastructureValidator"
        self._policy = validation_policy or ValidationPolicy()
        self._logger = logging.getLogger(f"dag_orchestration.{self.__class__.__name__}")
        
        # Initialize precondition validator
        self._precondition_validator = InfrastructurePreconditionValidator()
        
        # Validation cache and state
        self._validation_cache: Dict[str, InfrastructureReport] = {}
        self._last_validation_time: Optional[datetime] = None
        self._continuous_monitoring_active = False
        self._monitoring_task: Optional[asyncio.Task] = None
        
        # Validation statistics
        self._validation_count = 0
        self._cache_hits = 0
        self._validation_failures = 0
        
        self._logger.info(f"InfrastructureValidator initialized with policy: {self._policy}")
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "name": "InfrastructureValidator",
            "version": "1.0.0",
            "description": "Formal infrastructure validator for DAG orchestration system",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "validation_policy": {
                "redis_timeout": self._policy.redis_timeout_seconds,
                "cache_ttl": self._policy.validation_cache_ttl_seconds,
                "auto_remediation": self._policy.auto_remediation_enabled
            },
            "statistics": {
                "validation_count": self._validation_count,
                "cache_hits": self._cache_hits,
                "validation_failures": self._validation_failures,
                "cache_size": len(self._validation_cache)
            }
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        try:
            # Check precondition validator health
            precondition_health = self._precondition_validator.get_health_status()
            
            # Check our own state
            issues = []
            health_score = 1.0
            
            if precondition_health.status != ModuleStatus.HEALTHY:
                issues.append(f"Precondition validator unhealthy: {precondition_health.status.value}")
                health_score *= 0.7
            
            if self._validation_failures > 0:
                failure_rate = self._validation_failures / max(self._validation_count, 1)
                if failure_rate > 0.1:  # More than 10% failure rate
                    issues.append(f"High validation failure rate: {failure_rate:.1%}")
                    health_score *= 0.8
            
            if not self._continuous_monitoring_active and self._policy.require_minimum_resources:
                issues.append("Continuous monitoring not active")
                health_score *= 0.9
            
            # Determine overall status
            if health_score >= 0.9:
                status = ModuleStatus.HEALTHY
            elif health_score >= 0.7:
                status = ModuleStatus.WARNING
            else:
                status = ModuleStatus.ERROR
                
        except Exception as e:
            status = ModuleStatus.ERROR
            health_score = 0.0
            issues = [f"Health check failed: {str(e)}"]
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds()
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant"""
        try:
            # In degraded mode, we can still validate but with reduced capabilities
            remaining_capabilities = [
                ModuleCapability.CORE_FUNCTIONALITY,
                ModuleCapability.VALIDATION
            ]
            
            degraded_capabilities = [
                ModuleCapability.MONITORING  # May lose continuous monitoring
            ]
            
            # Stop continuous monitoring if active
            if self._monitoring_task and not self._monitoring_task.done():
                self._monitoring_task.cancel()
                self._continuous_monitoring_active = False
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=degraded_capabilities,
                remaining_capabilities=remaining_capabilities
            )
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[ModuleCapability.CORE_FUNCTIONALITY],
                remaining_capabilities=[],
                error_message=str(e)
            )
    
    async def validate_for_execution(self, execution_requirements: Dict[str, Any]) -> Tuple[bool, InfrastructureReport]:
        """
        Validate infrastructure for specific DAG execution requirements.
        
        Args:
            execution_requirements: Specific requirements for the execution
            
        Returns:
            Tuple of (validation_passed, detailed_report)
        """
        with self.trace_operation("validate_for_execution", execution_requirements=execution_requirements) as trace:
            validation_context = ValidationContext(
                validation_id=f"exec_{datetime.now().timestamp()}",
                requested_at=datetime.now(),
                policy=self._policy,
                execution_requirements=execution_requirements
            )
            
            # Check cache first
            cached_report = self._get_cached_validation(validation_context)
            if cached_report:
                self._cache_hits += 1
                trace.output_result = {
                    'validation_passed': cached_report.overall_status,
                    'cache_hit': True,
                    'validation_time': cached_report.validation_time.isoformat()
                }
                return cached_report.overall_status, cached_report
            
            # Perform fresh validation
            try:
                self._validation_count += 1
                
                # Run comprehensive validation
                report = await self._precondition_validator.validate_all_preconditions()
                
                # Apply execution-specific requirements
                enhanced_report = self._enhance_report_for_execution(report, execution_requirements)
                
                # Cache the results
                self._cache_validation_results(validation_context, enhanced_report)
                
                # Update last validation time
                self._last_validation_time = datetime.now()
                
                trace.output_result = {
                    'validation_passed': enhanced_report.overall_status,
                    'cache_hit': False,
                    'validation_time': enhanced_report.validation_time.isoformat(),
                    'execution_specific_checks': len(execution_requirements)
                }
                
                return enhanced_report.overall_status, enhanced_report
                
            except Exception as e:
                self._validation_failures += 1
                self._logger.error(f"Validation failed: {e}")
                
                # Create failure report
                failure_report = InfrastructureReport(
                    overall_status=False,
                    validation_time=datetime.now(),
                    precondition_results=[
                        PreconditionResult(
                            name="Validation Execution",
                            passed=False,
                            details={'error_type': 'validation_exception'},
                            error_message=str(e)
                        )
                    ],
                    system_info={'validation_error': str(e)},
                    recommendations=[f"Fix validation error: {e}"]
                )
                
                trace.output_result = {
                    'validation_passed': False,
                    'error': str(e)
                }
                
                return False, failure_report
    
    async def start_continuous_monitoring(self) -> bool:
        """
        Start continuous infrastructure monitoring.
        
        Returns:
            bool: True if monitoring started successfully
        """
        with self.trace_operation("start_continuous_monitoring") as trace:
            try:
                if self._continuous_monitoring_active:
                    self._logger.info("Continuous monitoring already active")
                    trace.output_result = {'already_active': True}
                    return True
                
                # Start monitoring task
                self._monitoring_task = asyncio.create_task(self._continuous_monitoring_loop())
                self._continuous_monitoring_active = True
                
                self._logger.info(f"Started continuous monitoring with {self._policy.resource_check_interval_seconds}s interval")
                trace.output_result = {
                    'monitoring_started': True,
                    'check_interval': self._policy.resource_check_interval_seconds
                }
                return True
                
            except Exception as e:
                self._logger.error(f"Failed to start continuous monitoring: {e}")
                trace.output_result = {'error': str(e)}
                return False
    
    async def stop_continuous_monitoring(self) -> bool:
        """
        Stop continuous infrastructure monitoring.
        
        Returns:
            bool: True if monitoring stopped successfully
        """
        with self.trace_operation("stop_continuous_monitoring") as trace:
            try:
                if not self._continuous_monitoring_active:
                    trace.output_result = {'already_stopped': True}
                    return True
                
                # Cancel monitoring task
                if self._monitoring_task and not self._monitoring_task.done():
                    self._monitoring_task.cancel()
                    try:
                        await self._monitoring_task
                    except asyncio.CancelledError:
                        pass
                
                self._continuous_monitoring_active = False
                self._monitoring_task = None
                
                self._logger.info("Stopped continuous monitoring")
                trace.output_result = {'monitoring_stopped': True}
                return True
                
            except Exception as e:
                self._logger.error(f"Failed to stop continuous monitoring: {e}")
                trace.output_result = {'error': str(e)}
                return False
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get validation statistics and performance metrics."""
        cache_hit_rate = self._cache_hits / max(self._validation_count, 1)
        failure_rate = self._validation_failures / max(self._validation_count, 1)
        
        return {
            'total_validations': self._validation_count,
            'cache_hits': self._cache_hits,
            'cache_hit_rate': cache_hit_rate,
            'validation_failures': self._validation_failures,
            'failure_rate': failure_rate,
            'cache_size': len(self._validation_cache),
            'last_validation': self._last_validation_time.isoformat() if self._last_validation_time else None,
            'continuous_monitoring_active': self._continuous_monitoring_active,
            'policy': {
                'cache_ttl_seconds': self._policy.validation_cache_ttl_seconds,
                'check_interval_seconds': self._policy.resource_check_interval_seconds,
                'auto_remediation_enabled': self._policy.auto_remediation_enabled
            }
        }
    
    def clear_validation_cache(self) -> int:
        """
        Clear validation cache.
        
        Returns:
            int: Number of cached entries cleared
        """
        with self.trace_operation("clear_validation_cache") as trace:
            cleared_count = len(self._validation_cache)
            self._validation_cache.clear()
            
            self._logger.info(f"Cleared {cleared_count} cached validation results")
            trace.output_result = {'cleared_entries': cleared_count}
            return cleared_count
    
    async def _continuous_monitoring_loop(self):
        """Continuous monitoring loop for infrastructure state."""
        self._logger.info("Starting continuous infrastructure monitoring loop")
        
        while self._continuous_monitoring_active:
            try:
                # Perform lightweight validation check
                basic_requirements = {
                    'monitoring_check': True,
                    'lightweight': True
                }
                
                validation_passed, report = await self.validate_for_execution(basic_requirements)
                
                if not validation_passed:
                    self._logger.warning(f"Infrastructure validation failed during monitoring: {report.recommendations}")
                
                # Wait for next check
                await asyncio.sleep(self._policy.resource_check_interval_seconds)
                
            except asyncio.CancelledError:
                self._logger.info("Continuous monitoring cancelled")
                break
            except Exception as e:
                self._logger.error(f"Error in continuous monitoring: {e}")
                # Continue monitoring despite errors
                await asyncio.sleep(self._policy.resource_check_interval_seconds)
        
        self._logger.info("Continuous monitoring loop ended")
    
    def _get_cached_validation(self, context: ValidationContext) -> Optional[InfrastructureReport]:
        """Get cached validation results if still valid."""
        cache_key = self._generate_cache_key(context)
        
        if cache_key in self._validation_cache:
            cached_report = self._validation_cache[cache_key]
            
            # Check if cache is still valid
            cache_age = datetime.now() - cached_report.validation_time
            if cache_age.total_seconds() < self._policy.validation_cache_ttl_seconds:
                return cached_report
            else:
                # Remove expired cache entry
                del self._validation_cache[cache_key]
        
        return None
    
    def _cache_validation_results(self, context: ValidationContext, report: InfrastructureReport):
        """Cache validation results for future use."""
        cache_key = self._generate_cache_key(context)
        self._validation_cache[cache_key] = report
        
        # Clean up old cache entries
        self._cleanup_expired_cache()
    
    def _generate_cache_key(self, context: ValidationContext) -> str:
        """Generate cache key for validation context."""
        # Simple cache key based on execution requirements
        req_hash = hash(str(sorted(context.execution_requirements.items())))
        return f"validation_{req_hash}"
    
    def _cleanup_expired_cache(self):
        """Clean up expired cache entries."""
        current_time = datetime.now()
        expired_keys = []
        
        for key, report in self._validation_cache.items():
            cache_age = current_time - report.validation_time
            if cache_age.total_seconds() >= self._policy.validation_cache_ttl_seconds:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._validation_cache[key]
    
    def _enhance_report_for_execution(self, base_report: InfrastructureReport, 
                                    execution_requirements: Dict[str, Any]) -> InfrastructureReport:
        """Enhance validation report with execution-specific requirements."""
        # For now, return the base report
        # Future enhancement: add execution-specific validation checks
        enhanced_recommendations = base_report.recommendations.copy()
        
        # Add execution-specific recommendations
        if execution_requirements.get('parallel_tasks', 0) > 10:
            enhanced_recommendations.append("Consider resource monitoring for high parallel task count")
        
        if execution_requirements.get('memory_intensive', False):
            enhanced_recommendations.append("Monitor memory usage during execution")
        
        # Create enhanced report
        enhanced_report = InfrastructureReport(
            overall_status=base_report.overall_status,
            validation_time=base_report.validation_time,
            precondition_results=base_report.precondition_results,
            system_info=base_report.system_info,
            recommendations=enhanced_recommendations
        )
        
        return enhanced_report


# Convenience functions for integration
async def validate_infrastructure_for_dag_execution(execution_requirements: Dict[str, Any]) -> Tuple[bool, InfrastructureReport]:
    """
    Convenience function to validate infrastructure for DAG execution.
    
    Args:
        execution_requirements: Specific requirements for the DAG execution
        
    Returns:
        Tuple of (validation_passed, detailed_report)
    """
    validator = InfrastructureValidator()
    return await validator.validate_for_execution(execution_requirements)


def create_infrastructure_validator(policy: Optional[ValidationPolicy] = None) -> InfrastructureValidator:
    """
    Factory function to create infrastructure validator with optional policy.
    
    Args:
        policy: Optional validation policy configuration
        
    Returns:
        InfrastructureValidator instance
    """
    return InfrastructureValidator(policy)