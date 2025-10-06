"""Main Constellation Orchestrator implementation."""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import structlog

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from .config import ConstellationConfig
from ..models.task_definition import TaskDefinition
from ..models.execution_state import ExecutionState, ExecutionResult
from ..dag.dag_manager import DAGManager
from ..execution.execution_manager import ExecutionManager
from ..status.status_manager import StatusManager
from ..agents.agent_manager import AgentManager


class ConstellationOrchestrator(ReflectiveModule):
    """
    Main orchestrator for DAG-based AI prompt execution.
    
    Provides systematic orchestration of 90+ AI prompts with comprehensive
    dependency management, multi-agent coordination, and Beast Mode observability.
    """
    
    def __init__(self, config: Optional[ConstellationConfig] = None):
        """Initialize the Constellation Orchestrator."""
        super().__init__()
        
        self.config = config or ConstellationConfig.load_from_env()
        self.logger = structlog.get_logger(__name__)
        
        # Generate unique orchestrator instance ID
        self.instance_id = str(uuid.uuid4())
        
        # Initialize components (will be created in initialize())
        self.dag_manager: Optional[DAGManager] = None
        self.execution_manager: Optional[ExecutionManager] = None
        self.status_manager: Optional[StatusManager] = None
        self.agent_manager: Optional[AgentManager] = None
        
        # Execution state
        self.current_execution_id: Optional[str] = None
        self.is_initialized = False
        
        self.logger.info(
            "constellation_orchestrator_created",
            instance_id=self.instance_id,
            config=self.config.to_dict()
        )
    
    async def initialize(self) -> bool:
        """Initialize all orchestrator components."""
        try:
            self.logger.info("constellation_orchestrator_initializing", instance_id=self.instance_id)
            
            # Initialize components in dependency order
            self.status_manager = StatusManager(self.config)
            await self.status_manager.initialize()
            
            self.agent_manager = AgentManager(self.config)
            await self.agent_manager.initialize()
            
            self.dag_manager = DAGManager(self.config)
            await self.dag_manager.initialize()
            
            self.execution_manager = ExecutionManager(
                self.config, 
                self.agent_manager, 
                self.status_manager
            )
            await self.execution_manager.initialize()
            
            # Components are initialized and will be checked in health_check method
            
            self.is_initialized = True
            
            self.logger.info(
                "constellation_orchestrator_initialized",
                instance_id=self.instance_id,
                components_initialized=4
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                "constellation_orchestrator_initialization_failed",
                instance_id=self.instance_id,
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    async def load_tasks(self, task_definitions: List[TaskDefinition]) -> bool:
        """Load task definitions and validate DAG structure."""
        if not self.is_initialized:
            raise RuntimeError("Orchestrator not initialized. Call initialize() first.")
        
        try:
            self.logger.info(
                "constellation_loading_tasks",
                instance_id=self.instance_id,
                task_count=len(task_definitions)
            )
            
            # Load tasks into DAG manager
            success = await self.dag_manager.load_tasks(task_definitions)
            if not success:
                self.logger.error("constellation_task_loading_failed", instance_id=self.instance_id)
                return False
            
            # Validate DAG structure
            validation_result = await self.dag_manager.validate_dag()
            if not validation_result.is_valid:
                self.logger.error(
                    "constellation_dag_validation_failed",
                    instance_id=self.instance_id,
                    cycles=validation_result.cycles,
                    orphaned_tasks=validation_result.orphaned_tasks
                )
                return False
            
            self.logger.info(
                "constellation_tasks_loaded_successfully",
                instance_id=self.instance_id,
                task_count=len(task_definitions),
                execution_order_length=len(validation_result.execution_order)
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                "constellation_task_loading_error",
                instance_id=self.instance_id,
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    async def start_execution(self, execution_name: Optional[str] = None) -> Optional[str]:
        """Start DAG execution and return execution ID."""
        if not self.is_initialized:
            raise RuntimeError("Orchestrator not initialized. Call initialize() first.")
        
        if not self.dag_manager.has_tasks():
            raise RuntimeError("No tasks loaded. Call load_tasks() first.")
        
        try:
            # Generate execution ID
            execution_id = f"constellation_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            if execution_name:
                execution_id = f"{execution_name}_{execution_id}"
            
            self.current_execution_id = execution_id
            
            self.logger.info(
                "constellation_execution_starting",
                instance_id=self.instance_id,
                execution_id=execution_id
            )
            
            # Initialize execution state
            task_count = self.dag_manager.get_task_count()
            success = await self.status_manager.initialize_execution(execution_id, task_count)
            if not success:
                self.logger.error(
                    "constellation_execution_initialization_failed",
                    instance_id=self.instance_id,
                    execution_id=execution_id
                )
                return None
            
            # Add task definitions to execution manager
            task_definitions = [self.dag_manager.get_task_by_id(task_id) for task_id in self.dag_manager.tasks.keys()]
            self.execution_manager.add_task_definitions([t for t in task_definitions if t is not None])
            
            # Start execution in background
            asyncio.create_task(self._execute_dag(execution_id))
            
            self.logger.info(
                "constellation_execution_started",
                instance_id=self.instance_id,
                execution_id=execution_id,
                task_count=task_count
            )
            
            return execution_id
            
        except Exception as e:
            self.logger.error(
                "constellation_execution_start_error",
                instance_id=self.instance_id,
                error=str(e),
                error_type=type(e).__name__
            )
            return None
    
    async def _execute_dag(self, execution_id: str) -> None:
        """Execute DAG tasks with dependency management."""
        try:
            self.logger.info(
                "constellation_dag_execution_starting",
                instance_id=self.instance_id,
                execution_id=execution_id
            )
            
            completed_tasks = set()
            
            while True:
                # Get ready tasks
                ready_tasks = await self.dag_manager.get_ready_tasks(completed_tasks)
                
                if not ready_tasks:
                    # Check if all tasks are completed
                    total_tasks = self.dag_manager.get_task_count()
                    if len(completed_tasks) >= total_tasks:
                        self.logger.info(
                            "constellation_dag_execution_completed",
                            instance_id=self.instance_id,
                            execution_id=execution_id,
                            completed_tasks=len(completed_tasks)
                        )
                        break
                    else:
                        # Wait for running tasks to complete
                        await asyncio.sleep(1)
                        continue
                
                # Execute ready tasks in parallel
                self.logger.info(
                    "constellation_executing_ready_tasks",
                    instance_id=self.instance_id,
                    execution_id=execution_id,
                    ready_task_count=len(ready_tasks)
                )
                
                # Get task definitions for ready tasks
                ready_task_definitions = []
                for task_id in ready_tasks:
                    task_def = self.dag_manager.get_task_by_id(task_id)
                    if task_def:
                        ready_task_definitions.append(task_def)
                
                # Execute tasks
                results = []
                for task_def in ready_task_definitions:
                    result = await self.execution_manager.execute_task(task_def.task_id, task_def)
                    results.append(result)
                
                # Process results
                for result in results:
                    if result.status.value in ['completed', 'failed']:
                        completed_tasks.add(result.task_id)
                        
                        # Update status
                        await self.status_manager.update_task_status(
                            result.task_id, 
                            result.status, 
                            result
                        )
                        
                        self.logger.info(
                            "constellation_task_completed",
                            instance_id=self.instance_id,
                            execution_id=execution_id,
                            task_id=result.task_id,
                            status=result.status.value,
                            duration=result.duration
                        )
            
            # Mark execution as completed
            await self.status_manager.complete_execution(execution_id)
            
        except Exception as e:
            self.logger.error(
                "constellation_dag_execution_error",
                instance_id=self.instance_id,
                execution_id=execution_id,
                error=str(e),
                error_type=type(e).__name__
            )
            
            # Mark execution as failed
            await self.status_manager.fail_execution(execution_id, str(e))
    
    async def get_execution_state(self, execution_id: Optional[str] = None) -> Optional[ExecutionState]:
        """Get current execution state."""
        if not self.is_initialized:
            return None
        
        target_execution_id = execution_id or self.current_execution_id
        if not target_execution_id:
            return None
        
        return await self.status_manager.get_execution_state(target_execution_id)
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for all components."""
        health_status = super().health_check()
        
        if not self.is_initialized:
            health_status.update({
                'status': 'not_initialized',
                'components_initialized': 0
            })
            return health_status
        
        # Add orchestrator-specific health metrics
        try:
            agent_status = await self.agent_manager.get_agent_status()
            
            health_status.update({
                'instance_id': self.instance_id,
                'is_initialized': self.is_initialized,
                'current_execution_id': self.current_execution_id,
                'available_agents': len([a for a in agent_status.values() if a == 'available']),
                'total_agents': len(agent_status),
                'components_healthy': all([
                    await self.dag_manager.health_check(),
                    await self.execution_manager.health_check(),
                    await self.status_manager.health_check(),
                    await self.agent_manager.health_check()
                ])
            })
            
        except Exception as e:
            health_status.update({
                'status': 'unhealthy',
                'error': str(e)
            })
        
        return health_status
    
    async def shutdown(self) -> None:
        """Graceful shutdown of all components."""
        try:
            self.logger.info(
                "constellation_orchestrator_shutting_down",
                instance_id=self.instance_id
            )
            
            if self.execution_manager:
                await self.execution_manager.shutdown()
            
            if self.agent_manager:
                await self.agent_manager.shutdown()
            
            if self.status_manager:
                await self.status_manager.shutdown()
            
            if self.dag_manager:
                await self.dag_manager.shutdown()
            
            self.is_initialized = False
            
            self.logger.info(
                "constellation_orchestrator_shutdown_complete",
                instance_id=self.instance_id
            )
            
        except Exception as e:
            self.logger.error(
                "constellation_orchestrator_shutdown_error",
                instance_id=self.instance_id,
                error=str(e),
                error_type=type(e).__name__
            )
    
    # ReflectiveModule abstract method implementations
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            'module_name': 'ConstellationOrchestrator',
            'version': '0.1.0',
            'description': 'DAG-based AI prompt execution orchestrator',
            'instance_id': self.instance_id,
            'is_initialized': self.is_initialized,
            'current_execution_id': self.current_execution_id
        }
    
    def get_capabilities(self) -> List[Any]:
        """Get orchestrator capabilities."""
        # Import here to avoid circular imports
        from src.rm_ddd.core.unified_reflective_module import ModuleCapability
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.API_INTEGRATION,
            ModuleCapability.MONITORING
        ]
    
    async def get_health_status(self) -> Any:
        """Get detailed health status."""
        from src.rm_ddd.core.unified_reflective_module import ModuleHealth, ModuleStatus
        
        health_data = await self.health_check()
        
        # Determine status based on health data
        if not self.is_initialized:
            status = ModuleStatus.ERROR
            health_score = 0.0
            issues = ["Not initialized"]
        elif health_data.get('components_healthy', False):
            status = ModuleStatus.HEALTHY
            health_score = 1.0
            issues = []
        else:
            status = ModuleStatus.WARNING
            health_score = 0.5
            issues = ["Some components unhealthy"]
        
        return ModuleHealth(
            module_id=self.instance_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.utcnow(),
            uptime_seconds=(datetime.utcnow() - self._start_time).total_seconds() if hasattr(self, '_start_time') else 0.0,
            error_count=getattr(self, '_error_count', 0),
            warning_count=getattr(self, '_warning_count', 0)
        )
    
    async def graceful_degradation(self, error: Exception = None) -> Any:
        """Handle graceful degradation on errors."""
        self.logger.error(
            "constellation_orchestrator_graceful_degradation",
            instance_id=self.instance_id,
            error=str(error),
            error_type=type(error).__name__
        )
        
        # Attempt to save current state
        degradation_actions = []
        
        try:
            if self.current_execution_id and self.status_manager:
                await self.status_manager.fail_execution(
                    self.current_execution_id, 
                    f"Graceful degradation triggered: {str(error)}"
                )
                degradation_actions.append("execution_state_saved")
        except Exception as save_error:
            self.logger.error(
                "constellation_orchestrator_degradation_save_failed",
                instance_id=self.instance_id,
                error=str(save_error)
            )
        
        # Cancel running tasks
        try:
            if self.execution_manager:
                cancelled_count = await self.execution_manager.cancel_all_tasks()
                degradation_actions.append(f"cancelled_{cancelled_count}_tasks")
        except Exception as cancel_error:
            self.logger.error(
                "constellation_orchestrator_degradation_cancel_failed",
                instance_id=self.instance_id,
                error=str(cancel_error)
            )
        
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult, ModuleCapability
        
        # Determine remaining capabilities after degradation
        remaining_capabilities = []
        degraded_capabilities = [ModuleCapability.CORE_FUNCTIONALITY]
        
        if self.status_manager and await self.status_manager.health_check():
            remaining_capabilities.append(ModuleCapability.MONITORING)
        else:
            degraded_capabilities.append(ModuleCapability.MONITORING)
        
        return GracefulDegradationResult(
            success=len(degradation_actions) > 0,
            degraded_capabilities=degraded_capabilities,
            remaining_capabilities=remaining_capabilities,
            error_message=str(error) if error else None
        )