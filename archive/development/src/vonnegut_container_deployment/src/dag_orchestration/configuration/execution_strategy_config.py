#!/usr/bin/env python3
"""
Execution Strategy Configuration for DAG Orchestration
=====================================================

Configurable execution strategies including aggressive parallel, conservative,
and sequential fallback with resource threshold management.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class ExecutionMode(Enum):
    """Execution mode options."""
    AGGRESSIVE_PARALLEL = "aggressive_parallel"
    CONSERVATIVE_PARALLEL = "conservative_parallel"
    SEQUENTIAL_FALLBACK = "sequential_fallback"
    ADAPTIVE = "adaptive"


class ResourceType(Enum):
    """Resource types for monitoring."""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    GPU = "gpu"


@dataclass
class ResourceThresholdConfig:
    """Configuration for resource thresholds."""
    resource_type: ResourceType
    warning_threshold: float  # 0.0 to 1.0
    critical_threshold: float  # 0.0 to 1.0
    action_threshold: float  # 0.0 to 1.0 (when to take action)
    recovery_threshold: float  # 0.0 to 1.0 (when to recover from action)
    monitoring_interval: float = 5.0  # seconds
    enabled: bool = True


@dataclass
class ConcurrencyConfig:
    """Configuration for concurrency management."""
    min_workers: int = 1
    max_workers: int = 20
    default_workers: int = 10
    scale_up_threshold: float = 0.8  # Resource utilization to scale up
    scale_down_threshold: float = 0.3  # Resource utilization to scale down
    scale_up_factor: float = 1.5  # Multiply workers by this factor
    scale_down_factor: float = 0.7  # Multiply workers by this factor
    cooldown_period: float = 30.0  # seconds between scaling actions
    adaptive_scaling: bool = True


@dataclass
class ParallelExecutionConfig:
    """Configuration for parallel execution behavior."""
    task_timeout: float = 300.0  # seconds
    retry_attempts: int = 3
    retry_delay: float = 1.0  # seconds
    failure_threshold: float = 0.2  # Fraction of tasks that can fail
    dependency_timeout: float = 600.0  # seconds to wait for dependencies
    batch_size: int = 10  # Tasks to process in each batch
    queue_size: int = 100  # Maximum queued tasks
    priority_enabled: bool = True
    load_balancing: bool = True


@dataclass
class ExecutionStrategyConfig:
    """Complete execution strategy configuration."""
    name: str
    description: str
    mode: ExecutionMode
    concurrency: ConcurrencyConfig
    parallel_execution: ParallelExecutionConfig
    resource_thresholds: List[ResourceThresholdConfig] = field(default_factory=list)
    fallback_strategy: Optional[str] = None
    monitoring_enabled: bool = True
    auto_optimization: bool = False
    created_at: datetime = field(default_factory=datetime.now)


class ExecutionStrategyManager(ReflectiveModule):
    """
    Manager for execution strategy configurations.
    
    Features:
    - Multiple predefined execution strategies
    - Dynamic strategy switching based on conditions
    - Resource-aware strategy adaptation
    - Performance monitoring and optimization
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "ExecutionStrategyManager"
        self._logger = logging.getLogger(f"dag_orchestration.{self.__class__.__name__}")
        
        # Strategy storage
        self._strategies: Dict[str, ExecutionStrategyConfig] = {}
        self._current_strategy: Optional[str] = None
        self._strategy_history: List[Dict[str, Any]] = []
        
        # Performance tracking
        self._performance_metrics: Dict[str, Dict[str, Any]] = {}
        
        # Initialize default strategies
        self._initialize_default_strategies()
        
        self._logger.info("ExecutionStrategyManager initialized with default strategies")
    
    def _initialize_default_strategies(self) -> None:
        """Initialize default execution strategies."""
        
        # Aggressive Parallel Strategy
        aggressive_strategy = ExecutionStrategyConfig(
            name="aggressive_parallel",
            description="Maximum parallelism for high-performance environments",
            mode=ExecutionMode.AGGRESSIVE_PARALLEL,
            concurrency=ConcurrencyConfig(
                min_workers=5,
                max_workers=50,
                default_workers=20,
                scale_up_threshold=0.7,
                scale_down_threshold=0.2,
                scale_up_factor=2.0,
                scale_down_factor=0.5,
                cooldown_period=15.0,
                adaptive_scaling=True
            ),
            parallel_execution=ParallelExecutionConfig(
                task_timeout=600.0,
                retry_attempts=2,
                retry_delay=0.5,
                failure_threshold=0.1,
                dependency_timeout=300.0,
                batch_size=20,
                queue_size=200,
                priority_enabled=True,
                load_balancing=True
            ),
            resource_thresholds=[
                ResourceThresholdConfig(
                    resource_type=ResourceType.CPU,
                    warning_threshold=0.8,
                    critical_threshold=0.9,
                    action_threshold=0.85,
                    recovery_threshold=0.7
                ),
                ResourceThresholdConfig(
                    resource_type=ResourceType.MEMORY,
                    warning_threshold=0.8,
                    critical_threshold=0.9,
                    action_threshold=0.85,
                    recovery_threshold=0.7
                )
            ],
            fallback_strategy="conservative_parallel",
            auto_optimization=True
        )
        self.register_strategy(aggressive_strategy)
        
        # Conservative Parallel Strategy
        conservative_strategy = ExecutionStrategyConfig(
            name="conservative_parallel",
            description="Balanced approach for stable environments",
            mode=ExecutionMode.CONSERVATIVE_PARALLEL,
            concurrency=ConcurrencyConfig(
                min_workers=2,
                max_workers=20,
                default_workers=10,
                scale_up_threshold=0.8,
                scale_down_threshold=0.3,
                scale_up_factor=1.5,
                scale_down_factor=0.7,
                cooldown_period=30.0,
                adaptive_scaling=True
            ),
            parallel_execution=ParallelExecutionConfig(
                task_timeout=300.0,
                retry_attempts=3,
                retry_delay=1.0,
                failure_threshold=0.2,
                dependency_timeout=600.0,
                batch_size=10,
                queue_size=100,
                priority_enabled=True,
                load_balancing=True
            ),
            resource_thresholds=[
                ResourceThresholdConfig(
                    resource_type=ResourceType.CPU,
                    warning_threshold=0.7,
                    critical_threshold=0.8,
                    action_threshold=0.75,
                    recovery_threshold=0.6
                ),
                ResourceThresholdConfig(
                    resource_type=ResourceType.MEMORY,
                    warning_threshold=0.7,
                    critical_threshold=0.8,
                    action_threshold=0.75,
                    recovery_threshold=0.6
                )
            ],
            fallback_strategy="sequential_fallback",
            auto_optimization=False
        )
        self.register_strategy(conservative_strategy)
        
        # Sequential Fallback Strategy
        sequential_strategy = ExecutionStrategyConfig(
            name="sequential_fallback",
            description="Sequential execution for resource-constrained environments",
            mode=ExecutionMode.SEQUENTIAL_FALLBACK,
            concurrency=ConcurrencyConfig(
                min_workers=1,
                max_workers=3,
                default_workers=1,
                scale_up_threshold=0.9,
                scale_down_threshold=0.1,
                scale_up_factor=1.0,
                scale_down_factor=1.0,
                cooldown_period=60.0,
                adaptive_scaling=False
            ),
            parallel_execution=ParallelExecutionConfig(
                task_timeout=600.0,
                retry_attempts=5,
                retry_delay=2.0,
                failure_threshold=0.5,
                dependency_timeout=1200.0,
                batch_size=1,
                queue_size=50,
                priority_enabled=True,
                load_balancing=False
            ),
            resource_thresholds=[
                ResourceThresholdConfig(
                    resource_type=ResourceType.CPU,
                    warning_threshold=0.6,
                    critical_threshold=0.7,
                    action_threshold=0.65,
                    recovery_threshold=0.5
                ),
                ResourceThresholdConfig(
                    resource_type=ResourceType.MEMORY,
                    warning_threshold=0.6,
                    critical_threshold=0.7,
                    action_threshold=0.65,
                    recovery_threshold=0.5
                )
            ],
            fallback_strategy=None,  # No further fallback
            auto_optimization=False
        )
        self.register_strategy(sequential_strategy)
        
        # Adaptive Strategy
        adaptive_strategy = ExecutionStrategyConfig(
            name="adaptive",
            description="Dynamically adapts based on system conditions",
            mode=ExecutionMode.ADAPTIVE,
            concurrency=ConcurrencyConfig(
                min_workers=1,
                max_workers=30,
                default_workers=10,
                scale_up_threshold=0.8,
                scale_down_threshold=0.3,
                scale_up_factor=1.5,
                scale_down_factor=0.7,
                cooldown_period=20.0,
                adaptive_scaling=True
            ),
            parallel_execution=ParallelExecutionConfig(
                task_timeout=300.0,
                retry_attempts=3,
                retry_delay=1.0,
                failure_threshold=0.2,
                dependency_timeout=600.0,
                batch_size=10,
                queue_size=100,
                priority_enabled=True,
                load_balancing=True
            ),
            resource_thresholds=[
                ResourceThresholdConfig(
                    resource_type=ResourceType.CPU,
                    warning_threshold=0.75,
                    critical_threshold=0.85,
                    action_threshold=0.8,
                    recovery_threshold=0.65
                ),
                ResourceThresholdConfig(
                    resource_type=ResourceType.MEMORY,
                    warning_threshold=0.75,
                    critical_threshold=0.85,
                    action_threshold=0.8,
                    recovery_threshold=0.65
                )
            ],
            fallback_strategy="conservative_parallel",
            auto_optimization=True
        )
        self.register_strategy(adaptive_strategy)
        
        # Set default strategy
        self._current_strategy = "conservative_parallel"
    
    def register_strategy(self, strategy: ExecutionStrategyConfig) -> None:
        """Register an execution strategy."""
        self._strategies[strategy.name] = strategy
        self._logger.info(f"Registered execution strategy: {strategy.name}")
    
    def get_strategy(self, name: str) -> ExecutionStrategyConfig:
        """Get execution strategy by name."""
        if name not in self._strategies:
            raise ValueError(f"Strategy '{name}' not found")
        
        return self._strategies[name]
    
    def set_current_strategy(self, name: str) -> None:
        """Set current execution strategy."""
        if name not in self._strategies:
            raise ValueError(f"Strategy '{name}' not found")
        
        old_strategy = self._current_strategy
        self._current_strategy = name
        
        # Record strategy change
        change_record = {
            'timestamp': datetime.now(),
            'old_strategy': old_strategy,
            'new_strategy': name,
            'reason': 'manual_change'
        }
        self._strategy_history.append(change_record)
        
        self._logger.info(f"Changed execution strategy from '{old_strategy}' to '{name}'")
    
    def get_current_strategy(self) -> ExecutionStrategyConfig:
        """Get current execution strategy."""
        if not self._current_strategy:
            raise ValueError("No current strategy set")
        
        return self.get_strategy(self._current_strategy)
    
    def recommend_strategy(self, system_metrics: Dict[str, float], 
                         task_characteristics: Dict[str, Any]) -> str:
        """Recommend best strategy based on system metrics and task characteristics."""
        
        # Extract key metrics
        cpu_usage = system_metrics.get('cpu_usage', 0.5)
        memory_usage = system_metrics.get('memory_usage', 0.5)
        task_count = task_characteristics.get('task_count', 10)
        complexity_score = task_characteristics.get('complexity_score', 0.5)
        
        # Simple heuristic-based recommendation
        if cpu_usage > 0.8 or memory_usage > 0.8:
            return "sequential_fallback"
        elif cpu_usage < 0.3 and memory_usage < 0.3 and task_count > 20:
            return "aggressive_parallel"
        elif complexity_score > 0.8 or task_count > 50:
            return "adaptive"
        else:
            return "conservative_parallel"
    
    def auto_adjust_strategy(self, system_metrics: Dict[str, float], 
                           performance_metrics: Dict[str, Any]) -> bool:
        """Automatically adjust strategy based on metrics."""
        if not self._current_strategy:
            return False
        
        current_strategy = self.get_current_strategy()
        if not current_strategy.auto_optimization:
            return False
        
        # Check if strategy change is needed
        recommended_strategy = self.recommend_strategy(
            system_metrics, 
            performance_metrics.get('task_characteristics', {})
        )
        
        if recommended_strategy != self._current_strategy:
            # Check cooldown period
            if self._strategy_history:
                last_change = self._strategy_history[-1]['timestamp']
                cooldown = current_strategy.concurrency.cooldown_period
                if (datetime.now() - last_change).total_seconds() < cooldown:
                    return False
            
            # Apply strategy change
            old_strategy = self._current_strategy
            self._current_strategy = recommended_strategy
            
            # Record automatic change
            change_record = {
                'timestamp': datetime.now(),
                'old_strategy': old_strategy,
                'new_strategy': recommended_strategy,
                'reason': 'auto_optimization',
                'system_metrics': system_metrics,
                'performance_metrics': performance_metrics
            }
            self._strategy_history.append(change_record)
            
            self._logger.info(f"Auto-adjusted strategy from '{old_strategy}' to '{recommended_strategy}'")
            return True
        
        return False
    
    def update_performance_metrics(self, strategy_name: str, metrics: Dict[str, Any]) -> None:
        """Update performance metrics for a strategy."""
        if strategy_name not in self._performance_metrics:
            self._performance_metrics[strategy_name] = {
                'total_executions': 0,
                'successful_executions': 0,
                'average_duration': 0.0,
                'average_throughput': 0.0,
                'resource_efficiency': 0.0,
                'last_updated': datetime.now()
            }
        
        strategy_metrics = self._performance_metrics[strategy_name]
        
        # Update metrics using exponential moving average
        alpha = 0.1
        strategy_metrics['total_executions'] += 1
        
        if metrics.get('success', True):
            strategy_metrics['successful_executions'] += 1
        
        if 'duration' in metrics:
            strategy_metrics['average_duration'] = (
                alpha * metrics['duration'] + 
                (1 - alpha) * strategy_metrics['average_duration']
            )
        
        if 'throughput' in metrics:
            strategy_metrics['average_throughput'] = (
                alpha * metrics['throughput'] + 
                (1 - alpha) * strategy_metrics['average_throughput']
            )
        
        if 'resource_efficiency' in metrics:
            strategy_metrics['resource_efficiency'] = (
                alpha * metrics['resource_efficiency'] + 
                (1 - alpha) * strategy_metrics['resource_efficiency']
            )
        
        strategy_metrics['last_updated'] = datetime.now()
        
        self._logger.debug(f"Updated performance metrics for strategy '{strategy_name}'")
    
    def get_strategy_performance(self, strategy_name: str) -> Dict[str, Any]:
        """Get performance metrics for a strategy."""
        if strategy_name not in self._performance_metrics:
            return {}
        
        metrics = self._performance_metrics[strategy_name].copy()
        
        # Calculate success rate
        if metrics['total_executions'] > 0:
            metrics['success_rate'] = metrics['successful_executions'] / metrics['total_executions']
        else:
            metrics['success_rate'] = 0.0
        
        return metrics
    
    def get_all_strategies(self) -> Dict[str, ExecutionStrategyConfig]:
        """Get all registered strategies."""
        return self._strategies.copy()
    
    def get_strategy_summary(self) -> Dict[str, Any]:
        """Get summary of all strategies and their performance."""
        summary = {
            'total_strategies': len(self._strategies),
            'current_strategy': self._current_strategy,
            'strategy_changes': len(self._strategy_history),
            'strategies': {},
            'performance_summary': {}
        }
        
        # Strategy details
        for name, strategy in self._strategies.items():
            summary['strategies'][name] = {
                'description': strategy.description,
                'mode': strategy.mode.value,
                'max_workers': strategy.concurrency.max_workers,
                'auto_optimization': strategy.auto_optimization,
                'fallback_strategy': strategy.fallback_strategy
            }
        
        # Performance summary
        for name in self._strategies.keys():
            performance = self.get_strategy_performance(name)
            if performance:
                summary['performance_summary'][name] = {
                    'total_executions': performance['total_executions'],
                    'success_rate': performance['success_rate'],
                    'average_duration': performance['average_duration'],
                    'resource_efficiency': performance['resource_efficiency']
                }
        
        return summary
    
    def create_custom_strategy(self, name: str, base_strategy: str, 
                             overrides: Dict[str, Any]) -> ExecutionStrategyConfig:
        """Create a custom strategy based on an existing one with overrides."""
        if base_strategy not in self._strategies:
            raise ValueError(f"Base strategy '{base_strategy}' not found")
        
        base = self._strategies[base_strategy]
        
        # Create new strategy with overrides
        custom_strategy = ExecutionStrategyConfig(
            name=name,
            description=overrides.get('description', f"Custom strategy based on {base_strategy}"),
            mode=ExecutionMode(overrides.get('mode', base.mode.value)),
            concurrency=base.concurrency,
            parallel_execution=base.parallel_execution,
            resource_thresholds=base.resource_thresholds.copy(),
            fallback_strategy=overrides.get('fallback_strategy', base.fallback_strategy),
            monitoring_enabled=overrides.get('monitoring_enabled', base.monitoring_enabled),
            auto_optimization=overrides.get('auto_optimization', base.auto_optimization)
        )
        
        # Apply concurrency overrides
        if 'concurrency' in overrides:
            concurrency_overrides = overrides['concurrency']
            for key, value in concurrency_overrides.items():
                if hasattr(custom_strategy.concurrency, key):
                    setattr(custom_strategy.concurrency, key, value)
        
        # Apply parallel execution overrides
        if 'parallel_execution' in overrides:
            parallel_overrides = overrides['parallel_execution']
            for key, value in parallel_overrides.items():
                if hasattr(custom_strategy.parallel_execution, key):
                    setattr(custom_strategy.parallel_execution, key, value)
        
        self.register_strategy(custom_strategy)
        return custom_strategy


# Convenience functions
def create_execution_strategy_manager() -> ExecutionStrategyManager:
    """Factory function to create execution strategy manager."""
    return ExecutionStrategyManager()


def create_resource_threshold(resource_type: ResourceType, warning: float, 
                            critical: float, action: float, recovery: float) -> ResourceThresholdConfig:
    """Convenience function to create resource threshold configuration."""
    return ResourceThresholdConfig(
        resource_type=resource_type,
        warning_threshold=warning,
        critical_threshold=critical,
        action_threshold=action,
        recovery_threshold=recovery
    )