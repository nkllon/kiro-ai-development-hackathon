"""
Beast Mode Self-Refactoring - Execution Strategy
Provides local vs cloud execution strategy selection for parallel agents
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum
import logging


class ExecutionType(Enum):
    LOCAL = "local"
    CLOUD = "cloud"
    HYBRID = "hybrid"


@dataclass
class ExecutionStrategy:
    """Execution strategy configuration for parallel agent orchestration"""
    execution_type: ExecutionType
    max_concurrent_agents: int
    resource_allocation: Dict[str, Any]
    scaling_parameters: Dict[str, Any]
    branch_isolation_config: Dict[str, Any]


class ExecutionStrategySelector:
    """Selects optimal execution strategy based on task complexity and resources"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Predefined strategies
        self.local_strategy = ExecutionStrategy(
            execution_type=ExecutionType.LOCAL,
            max_concurrent_agents=1,  # Conservative for local execution
            resource_allocation={
                "memory_limit_mb": 2048,
                "cpu_cores": 2,
                "disk_space_mb": 1024
            },
            scaling_parameters={
                "batch_size": 1,
                "timeout_seconds": 300,
                "retry_attempts": 2
            },
            branch_isolation_config={
                "use_separate_branches": True,
                "cleanup_on_completion": True,
                "merge_strategy": "systematic_validation"
            }
        )
        
        self.cloud_strategy = ExecutionStrategy(
            execution_type=ExecutionType.CLOUD,
            max_concurrent_agents=4,  # Higher for cloud scaling
            resource_allocation={
                "memory_limit_mb": 8192,
                "cpu_cores": 8,
                "disk_space_mb": 4096
            },
            scaling_parameters={
                "batch_size": 4,
                "timeout_seconds": 600,
                "retry_attempts": 3,
                "auto_scale": True
            },
            branch_isolation_config={
                "use_separate_branches": True,
                "cleanup_on_completion": True,
                "merge_strategy": "systematic_validation"
            }
        )
    
    def select_strategy(self, task_count: int, complexity_score: float, 
                       local_resources_available: bool = True) -> ExecutionStrategy:
        """
        Select optimal execution strategy based on task characteristics
        
        Decision Logic:
        - Task Count <= 2 AND Local Resources Available → Local Execution (1 agent)
        - Task Count > 2 OR High Complexity → Cloud Execution (4 agents)
        - Local Resources Unavailable → Force Cloud Execution
        """
        
        self.logger.info(f"Selecting execution strategy: tasks={task_count}, complexity={complexity_score}, local_available={local_resources_available}")
        
        # Force cloud if local resources unavailable
        if not local_resources_available:
            self.logger.info("🌩️ Local resources unavailable - selecting cloud strategy")
            return self.cloud_strategy
        
        # Use local for small, simple tasks
        if task_count <= 2 and complexity_score < 0.5:
            self.logger.info("🏠 Selecting local execution strategy (1 agent)")
            return self.local_strategy
        
        # Use cloud for larger or complex tasks
        self.logger.info("🌩️ Selecting cloud execution strategy (4 agents)")
        return self.cloud_strategy
    
    def get_local_strategy(self) -> ExecutionStrategy:
        """Get the local execution strategy (1 agent)"""
        return self.local_strategy
    
    def get_cloud_strategy(self) -> ExecutionStrategy:
        """Get the cloud execution strategy (4 agents)"""
        return self.cloud_strategy