#!/usr/bin/env python3
"""
Conditional Execution Pattern for DAG Orchestration
==================================================

Implementation of conditional DAG execution based on runtime conditions
and results with dynamic path selection and validation.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
import uuid

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
    GracefulDegradationResult
)
from src.dag_orchestration.execution.parallel_execution_engine import TaskDefinition


class ConditionType(Enum):
    """Types of execution conditions."""
    RESULT_BASED = "result_based"
    METRIC_BASED = "metric_based"
    TIME_BASED = "time_based"
    RESOURCE_BASED = "resource_based"
    CUSTOM = "custom"


class ComparisonOperator(Enum):
    """Comparison operators for conditions."""
    EQUALS = "=="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN = "in"
    NOT_IN = "not_in"


@dataclass
class ExecutionCondition:
    """Definition of an execution condition."""
    condition_id: str
    name: str
    condition_type: ConditionType
    operator: ComparisonOperator
    expected_value: Any
    actual_value_source: str  # Path to value in execution context
    description: str = ""
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConditionEvaluator(ABC):
    """Abstract base class for condition evaluators."""
    
    @abstractmethod
    def evaluate(self, condition: ExecutionCondition, context: Dict[str, Any]) -> bool:
        """Evaluate condition against execution context."""
        pass


class DefaultConditionEvaluator(ConditionEvaluator):
    """Default implementation of condition evaluator."""
    
    def __init__(self):
        self._logger = logging.getLogger(f"dag_orchestration.{self.__class__.__name__}")
    
    def evaluate(self, condition: ExecutionCondition, context: Dict[str, Any]) -> bool:
        """Evaluate condition against execution context."""
        if not condition.enabled:
            return True  # Disabled conditions always pass
        
        try:
            # Extract actual value from context
            actual_value = self._extract_value(condition.actual_value_source, context)
            expected_value = condition.expected_value
            
            # Perform comparison based on operator
            result = self._compare_values(actual_value, expected_value, condition.operator)
            
            self._logger.debug(f"Condition {condition.condition_id}: {actual_value} {condition.operator.value} {expected_value} = {result}")
            return result
            
        except Exception as e:
            self._logger.error(f"Failed to evaluate condition {condition.condition_id}: {e}")
            return False  # Fail safe
    
    def _extract_value(self, value_source: str, context: Dict[str, Any]) -> Any:
        """Extract value from context using dot notation path."""
        keys = value_source.split('.')
        value = context
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            elif hasattr(value, key):
                value = getattr(value, key)
            else:
                raise ValueError(f"Value source '{value_source}' not found in context")
        
        return value
    
    def _compare_values(self, actual: Any, expected: Any, operator: ComparisonOperator) -> bool:
        """Compare values using specified operator."""
        if operator == ComparisonOperator.EQUALS:
            return actual == expected
        elif operator == ComparisonOperator.NOT_EQUALS:
            return actual != expected
        elif operator == ComparisonOperator.GREATER_THAN:
            return actual > expected
        elif operator == ComparisonOperator.LESS_THAN:
            return actual < expected
        elif operator == ComparisonOperator.GREATER_EQUAL:
            return actual >= expected
        elif operator == ComparisonOperator.LESS_EQUAL:
            return actual <= expected
        elif operator == ComparisonOperator.CONTAINS:
            return expected in actual
        elif operator == ComparisonOperator.NOT_CONTAINS:
            return expected not in actual
        elif operator == ComparisonOperator.IN:
            return actual in expected
        elif operator == ComparisonOperator.NOT_IN:
            return actual not in expected
        else:
            raise ValueError(f"Unsupported operator: {operator}")


@dataclass
class ConditionalTask:
    """Task with conditional execution logic."""
    task_definition: TaskDefinition
    conditions: List[ExecutionCondition]
    condition_logic: str = "AND"  # AND, OR, CUSTOM
    custom_logic_function: Optional[Callable[[List[bool]], bool]] = None
    fallback_tasks: List[TaskDefinition] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConditionalResult:
    """Result of conditional execution."""
    execution_id: str
    task_id: str
    conditions_evaluated: List[Dict[str, Any]]
    condition_result: bool
    executed_task: Optional[TaskDefinition]
    execution_result: Any = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConditionalExecutor(ReflectiveModule):
    """
    Executor for conditional DAG execution.
    
    Features:
    - Runtime condition evaluation
    - Dynamic task path selection
    - Fallback task execution
    - Condition result caching
    - Performance monitoring
    """
    
    def __init__(self, condition_evaluator: Optional[ConditionEvaluator] = None):
        super().__init__()
        self.module_id = "ConditionalExecutor"
        self._condition_evaluator = condition_evaluator or DefaultConditionEvaluator()
        self._logger = logging.getLogger(f"dag_orchestration.{self.__class__.__name__}")
        
        # Execution state
        self._active_executions: Dict[str, Dict[str, Any]] = {}
        self._condition_cache: Dict[str, Dict[str, bool]] = {}
        
        # Statistics
        self._total_evaluations = 0
        self._successful_evaluations = 0
        self._failed_evaluations = 0
        self._condition_hit_rate = {}
        
        self._logger.info("ConditionalExecutor initialized")
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "name": "ConditionalExecutor",
            "version": "1.0.0",
            "description": "Executor for conditional DAG execution",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "statistics": {
                "total_evaluations": self._total_evaluations,
                "successful_evaluations": self._successful_evaluations,
                "failed_evaluations": self._failed_evaluations,
                "success_rate": self._successful_evaluations / max(self._total_evaluations, 1),
                "active_executions": len(self._active_executions),
                "cached_conditions": len(self._condition_cache),
                "condition_hit_rates": self._condition_hit_rate
            }
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        try:
            issues = []
            health_score = 1.0
            
            # Check evaluation statistics
            if self._total_evaluations > 0:
                success_rate = self._successful_evaluations / self._total_evaluations
                if success_rate < 0.9:
                    issues.append(f"Low evaluation success rate: {success_rate:.1%}")
                    health_score *= 0.7
            
            # Check active executions
            if len(self._active_executions) > 20:
                issues.append(f"High number of active executions: {len(self._active_executions)}")
                health_score *= 0.8
            
            # Check condition evaluator
            if not self._condition_evaluator:
                issues.append("No condition evaluator configured")
                health_score *= 0.5
            
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
            # In degraded mode, disable condition caching and use simpler evaluation
            remaining_capabilities = [
                ModuleCapability.CORE_FUNCTIONALITY,
                ModuleCapability.DATA_PROCESSING
            ]
            
            degraded_capabilities = [
                ModuleCapability.VALIDATION
            ]
            
            # Clear cache to reduce memory usage
            self._condition_cache.clear()
            
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
    
    async def execute_conditional_task(self, conditional_task: ConditionalTask,
                                     execution_context: Dict[str, Any],
                                     execution_id: Optional[str] = None) -> ConditionalResult:
        """
        Execute conditional task based on runtime conditions.
        
        Args:
            conditional_task: Task with conditional execution logic
            execution_context: Runtime context for condition evaluation
            execution_id: Optional execution identifier
            
        Returns:
            ConditionalResult with execution details
        """
        with self.trace_operation("execute_conditional_task",
                                task_id=conditional_task.task_definition.task_id,
                                execution_id=execution_id) as trace:
            
            execution_id = execution_id or str(uuid.uuid4())
            start_time = datetime.now()
            
            try:
                # Track execution
                self._active_executions[execution_id] = {
                    'start_time': start_time,
                    'task_id': conditional_task.task_definition.task_id,
                    'status': 'evaluating_conditions'
                }
                self._total_evaluations += 1
                
                # Evaluate conditions
                condition_results = []
                for condition in conditional_task.conditions:
                    condition_result = await self._evaluate_condition_with_cache(
                        condition, execution_context, execution_id
                    )
                    condition_results.append({
                        'condition_id': condition.condition_id,
                        'condition_name': condition.name,
                        'result': condition_result,
                        'expected_value': condition.expected_value,
                        'actual_value': self._extract_actual_value(condition, execution_context)
                    })
                
                # Apply condition logic
                overall_condition_result = self._apply_condition_logic(
                    conditional_task, condition_results
                )
                
                # Determine which task to execute
                if overall_condition_result:
                    task_to_execute = conditional_task.task_definition
                    self._logger.info(f"Conditions passed for task {task_to_execute.task_id}")
                else:
                    # Use fallback task if available
                    if conditional_task.fallback_tasks:
                        task_to_execute = conditional_task.fallback_tasks[0]  # Use first fallback
                        self._logger.info(f"Conditions failed, using fallback task {task_to_execute.task_id}")
                    else:
                        task_to_execute = None
                        self._logger.info(f"Conditions failed and no fallback available for task {conditional_task.task_definition.task_id}")
                
                # Execute selected task
                execution_result = None
                if task_to_execute:
                    self._active_executions[execution_id]['status'] = 'executing_task'
                    execution_result = await self._execute_task(task_to_execute, execution_context)
                
                # Calculate execution time
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                
                # Create result
                result = ConditionalResult(
                    execution_id=execution_id,
                    task_id=conditional_task.task_definition.task_id,
                    conditions_evaluated=condition_results,
                    condition_result=overall_condition_result,
                    executed_task=task_to_execute,
                    execution_result=execution_result,
                    execution_time=execution_time,
                    metadata={
                        'condition_logic': conditional_task.condition_logic,
                        'fallback_available': len(conditional_task.fallback_tasks) > 0,
                        'execution_context_keys': list(execution_context.keys())
                    }
                )
                
                # Update statistics
                self._successful_evaluations += 1
                self._update_condition_hit_rates(conditional_task.conditions, condition_results)
                
                trace.output_result = {
                    'execution_id': execution_id,
                    'condition_result': overall_condition_result,
                    'executed_task': task_to_execute.task_id if task_to_execute else None,
                    'execution_time': execution_time
                }
                
                return result
                
            except Exception as e:
                self._failed_evaluations += 1
                self._logger.error(f"Conditional execution {execution_id} failed: {e}")
                
                trace.output_result = {
                    'execution_id': execution_id,
                    'error': str(e)
                }
                
                raise e
                
            finally:
                # Cleanup
                if execution_id in self._active_executions:
                    del self._active_executions[execution_id]
    
    async def _evaluate_condition_with_cache(self, condition: ExecutionCondition,
                                           context: Dict[str, Any],
                                           execution_id: str) -> bool:
        """Evaluate condition with caching support."""
        # Create cache key
        context_hash = str(hash(str(sorted(context.items()))))
        cache_key = f"{condition.condition_id}_{context_hash}"
        
        # Check cache
        if execution_id in self._condition_cache and cache_key in self._condition_cache[execution_id]:
            return self._condition_cache[execution_id][cache_key]
        
        # Evaluate condition
        result = self._condition_evaluator.evaluate(condition, context)
        
        # Cache result
        if execution_id not in self._condition_cache:
            self._condition_cache[execution_id] = {}
        self._condition_cache[execution_id][cache_key] = result
        
        return result
    
    def _extract_actual_value(self, condition: ExecutionCondition, context: Dict[str, Any]) -> Any:
        """Extract actual value for condition from context."""
        try:
            keys = condition.actual_value_source.split('.')
            value = context
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                elif hasattr(value, key):
                    value = getattr(value, key)
                else:
                    return None
            
            return value
        except Exception:
            return None
    
    def _apply_condition_logic(self, conditional_task: ConditionalTask,
                             condition_results: List[Dict[str, Any]]) -> bool:
        """Apply condition logic to determine overall result."""
        if not condition_results:
            return True  # No conditions means always execute
        
        results = [cr['result'] for cr in condition_results]
        
        if conditional_task.condition_logic == "AND":
            return all(results)
        elif conditional_task.condition_logic == "OR":
            return any(results)
        elif conditional_task.condition_logic == "CUSTOM" and conditional_task.custom_logic_function:
            return conditional_task.custom_logic_function(results)
        else:
            # Default to AND logic
            return all(results)
    
    async def _execute_task(self, task: TaskDefinition, context: Dict[str, Any]) -> Any:
        """Execute a task with given context."""
        if task.execution_function:
            if asyncio.iscoroutinefunction(task.execution_function):
                return await task.execution_function(*task.execution_args, **task.execution_kwargs)
            else:
                return task.execution_function(*task.execution_args, **task.execution_kwargs)
        else:
            return f"Task {task.task_id} executed successfully"
    
    def _update_condition_hit_rates(self, conditions: List[ExecutionCondition],
                                  condition_results: List[Dict[str, Any]]) -> None:
        """Update condition hit rate statistics."""
        for condition, result in zip(conditions, condition_results):
            condition_id = condition.condition_id
            
            if condition_id not in self._condition_hit_rate:
                self._condition_hit_rate[condition_id] = {'hits': 0, 'total': 0}
            
            self._condition_hit_rate[condition_id]['total'] += 1
            if result['result']:
                self._condition_hit_rate[condition_id]['hits'] += 1
    
    def create_condition(self, condition_id: str, name: str,
                        condition_type: ConditionType, operator: ComparisonOperator,
                        expected_value: Any, actual_value_source: str,
                        description: str = "") -> ExecutionCondition:
        """Create a new execution condition."""
        return ExecutionCondition(
            condition_id=condition_id,
            name=name,
            condition_type=condition_type,
            operator=operator,
            expected_value=expected_value,
            actual_value_source=actual_value_source,
            description=description
        )
    
    def create_conditional_task(self, task_definition: TaskDefinition,
                              conditions: List[ExecutionCondition],
                              condition_logic: str = "AND",
                              fallback_tasks: Optional[List[TaskDefinition]] = None) -> ConditionalTask:
        """Create a new conditional task."""
        return ConditionalTask(
            task_definition=task_definition,
            conditions=conditions,
            condition_logic=condition_logic,
            fallback_tasks=fallback_tasks or []
        )
    
    def get_condition_statistics(self) -> Dict[str, Any]:
        """Get condition evaluation statistics."""
        hit_rates = {}
        for condition_id, stats in self._condition_hit_rate.items():
            hit_rates[condition_id] = {
                'hit_rate': stats['hits'] / max(stats['total'], 1),
                'total_evaluations': stats['total'],
                'successful_evaluations': stats['hits']
            }
        
        return {
            'total_evaluations': self._total_evaluations,
            'successful_evaluations': self._successful_evaluations,
            'failed_evaluations': self._failed_evaluations,
            'success_rate': self._successful_evaluations / max(self._total_evaluations, 1),
            'condition_hit_rates': hit_rates,
            'active_executions': len(self._active_executions),
            'cached_conditions': sum(len(cache) for cache in self._condition_cache.values())
        }
    
    def clear_condition_cache(self, execution_id: Optional[str] = None) -> None:
        """Clear condition cache for specific execution or all."""
        if execution_id:
            if execution_id in self._condition_cache:
                del self._condition_cache[execution_id]
        else:
            self._condition_cache.clear()
        
        self._logger.info(f"Cleared condition cache for {'execution ' + execution_id if execution_id else 'all executions'}")


# Convenience functions
def create_conditional_executor(condition_evaluator: Optional[ConditionEvaluator] = None) -> ConditionalExecutor:
    """Factory function to create conditional executor."""
    return ConditionalExecutor(condition_evaluator=condition_evaluator)


def create_result_condition(condition_id: str, name: str, 
                          result_path: str, operator: ComparisonOperator,
                          expected_value: Any) -> ExecutionCondition:
    """Create a result-based condition."""
    return ExecutionCondition(
        condition_id=condition_id,
        name=name,
        condition_type=ConditionType.RESULT_BASED,
        operator=operator,
        expected_value=expected_value,
        actual_value_source=result_path
    )


def create_metric_condition(condition_id: str, name: str,
                          metric_path: str, operator: ComparisonOperator,
                          threshold: float) -> ExecutionCondition:
    """Create a metric-based condition."""
    return ExecutionCondition(
        condition_id=condition_id,
        name=name,
        condition_type=ConditionType.METRIC_BASED,
        operator=operator,
        expected_value=threshold,
        actual_value_source=metric_path
    )