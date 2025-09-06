"""Data models for orchestration system."""

from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


class IsolationLevel(str, Enum):
    """Isolation level for instances."""

    BASIC = "basic"
    WORKSPACE = "workspace"
    CONTAINER = "container"
    VM = "vm"


class DistributionStrategy(str, Enum):
    """Task distribution strategy."""

    ROUND_ROBIN = "round_robin"
    LOAD_BALANCED = "load_balanced"
    DEPENDENCY_AWARE = "dependency_aware"
    CAPABILITY_BASED = "capability_based"


class IntegrationPolicy(str, Enum):
    """Integration policy for completed work."""

    IMMEDIATE = "immediate"
    BATCH = "batch"
    MANUAL = "manual"
    QUALITY_GATED = "quality_gated"


class TaskStatus(str, Enum):
    """Task execution status."""

    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class InstanceStatus(str, Enum):
    """Instance status."""

    STARTING = "starting"
    ACTIVE = "active"
    BUSY = "busy"
    IDLE = "idle"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class ResourceLimits(BaseModel):
    """Resource limits for instances."""

    max_cpu_percent: float = 80.0
    max_memory_mb: int = 4096
    max_disk_mb: int = 10240
    max_network_mbps: float = 100.0


class DeploymentTarget(BaseModel):
    """Deployment target configuration."""

    name: str
    type: str  # "local", "docker", "k8s", "cloud"
    endpoint: Optional[str] = None
    credentials: dict[str, Any] = Field(default_factory=dict)
    resource_limits: ResourceLimits = Field(default_factory=ResourceLimits)


class ProtocolConfig(BaseModel):
    """Communication protocol configuration."""

    protocol_type: str = "text"
    timeout_seconds: int = 30
    retry_attempts: int = 3
    batch_size: int = 10
    compression_enabled: bool = False


class Task(BaseModel):
    """Task representation for distributed execution."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    description: str
    requirements: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    estimated_duration: timedelta = Field(default=timedelta(minutes=30))
    complexity_score: float = Field(default=1.0, ge=0.1, le=10.0)
    required_capabilities: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    parameters: dict[str, Any] = Field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    assigned_instance: Optional[str] = None
    start_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None
    result: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None


class PeacockTheme(BaseModel):
    """Peacock color theme for IDE instances."""

    color_name: str
    primary_color: str
    accent_color: str
    theme_id: str = Field(default_factory=lambda: str(uuid4()))


class WorktreeInfo(BaseModel):
    """Git worktree information."""

    workspace_path: Path
    branch_name: str
    worktree_id: str = Field(default_factory=lambda: str(uuid4()))
    creation_timestamp: datetime = Field(default_factory=datetime.now)
    shared_git_dir: Path
    is_detached: bool = False


class KiroInstance(BaseModel):
    """Kiro instance configuration and state."""

    instance_id: str = Field(default_factory=lambda: f"kiro-{uuid4().hex[:8]}")
    branch_name: str
    workspace_path: Path
    source_repository: str
    resource_allocation: ResourceLimits = Field(default_factory=ResourceLimits)
    task_assignments: list[str] = Field(default_factory=list)
    communication_endpoint: str
    isolation_level: IsolationLevel = IsolationLevel.WORKSPACE
    peacock_theme: PeacockTheme
    visual_identifier: str
    status: InstanceStatus = InstanceStatus.STARTING
    start_time: datetime = Field(default_factory=datetime.now)
    last_heartbeat: Optional[datetime] = None
    worktree_info: Optional[WorktreeInfo] = None
    process_id: Optional[int] = None
    performance_metrics: dict[str, Any] = Field(default_factory=dict)


class SwarmConfig(BaseModel):
    """Configuration for distributed Beast Mode swarm."""

    instance_count: int = Field(default=3, ge=1, le=50)
    resource_limits: ResourceLimits = Field(default_factory=ResourceLimits)
    deployment_targets: list[DeploymentTarget] = Field(default_factory=list)
    task_distribution_strategy: DistributionStrategy = DistributionStrategy.DEPENDENCY_AWARE
    communication_protocol: ProtocolConfig = Field(default_factory=ProtocolConfig)
    integration_policy: IntegrationPolicy = IntegrationPolicy.QUALITY_GATED
    auto_scaling_enabled: bool = True
    max_instances: int = Field(default=10, ge=1, le=100)
    min_instances: int = Field(default=1, ge=1)
    scaling_threshold_cpu: float = Field(default=70.0, ge=10.0, le=95.0)
    scaling_threshold_memory: float = Field(default=80.0, ge=10.0, le=95.0)
    health_check_interval: int = Field(default=30, ge=5, le=300)  # seconds
    task_timeout: int = Field(default=3600, ge=60)  # seconds
    enable_visual_identification: bool = True

    @model_validator(mode='after')
    def validate_instance_limits(self) -> 'SwarmConfig':
        """Validate that min_instances <= max_instances."""
        if self.min_instances > self.max_instances:
            raise ValueError(f"min_instances ({self.min_instances}) must be <= max_instances ({self.max_instances})")
        return self


class SwarmMetrics(BaseModel):
    """Performance metrics for swarm operations."""

    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    active_instances: int = 0
    average_task_duration: float = 0.0
    total_execution_time: float = 0.0
    resource_utilization: dict[str, float] = Field(default_factory=dict)
    throughput_tasks_per_hour: float = 0.0
    error_rate: float = 0.0
    last_updated: datetime = Field(default_factory=datetime.now)


class IntegrationStatus(BaseModel):
    """Status of work integration."""

    pending_integrations: int = 0
    successful_integrations: int = 0
    failed_integrations: int = 0
    conflicts_detected: int = 0
    last_integration: Optional[datetime] = None
    integration_queue: list[str] = Field(default_factory=list)


class SwarmState(BaseModel):
    """Current state of distributed Beast Mode swarm."""

    swarm_id: str = Field(default_factory=lambda: f"swarm-{uuid4().hex[:8]}")
    instances: dict[str, KiroInstance] = Field(default_factory=dict)
    task_assignments: dict[str, list[str]] = Field(default_factory=dict)
    execution_status: dict[str, TaskStatus] = Field(default_factory=dict)
    communication_log: list[dict[str, Any]] = Field(default_factory=list)
    performance_metrics: SwarmMetrics = Field(default_factory=SwarmMetrics)
    integration_status: IntegrationStatus = Field(default_factory=IntegrationStatus)
    start_time: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    config: SwarmConfig
    status: str = "initializing"  # initializing, active, scaling, stopping, stopped, error


class DistributionPlan(BaseModel):
    """Task distribution plan for swarm execution."""

    plan_id: str = Field(default_factory=lambda: str(uuid4()))
    total_tasks: int
    instance_assignments: dict[str, list[str]] = Field(default_factory=dict)
    dependency_groups: list[list[str]] = Field(default_factory=list)
    estimated_completion_time: timedelta
    resource_requirements: dict[str, ResourceLimits] = Field(default_factory=dict)
    parallel_execution_groups: list[list[str]] = Field(default_factory=list)
    critical_path: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    strategy_used: DistributionStrategy


class InstanceFailure(BaseModel):
    """Instance failure information."""

    instance_id: str
    failure_type: str  # "crash", "timeout", "resource", "communication"
    failure_time: datetime = Field(default_factory=datetime.now)
    error_message: str
    stack_trace: Optional[str] = None
    affected_tasks: list[str] = Field(default_factory=list)
    recovery_attempts: int = 0
    is_recoverable: bool = True
    context: dict[str, Any] = Field(default_factory=dict)


class RecoveryPlan(BaseModel):
    """Recovery plan for failed instances."""

    plan_id: str = Field(default_factory=lambda: str(uuid4()))
    failed_instance: str
    recovery_strategy: str  # "restart", "reassign", "scale_up", "manual"
    task_reassignments: dict[str, str] = Field(default_factory=dict)
    estimated_recovery_time: timedelta
    required_actions: list[str] = Field(default_factory=list)
    rollback_plan: Optional[dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.now)


class IntegrationReport(BaseModel):
    """Report of integration results."""

    report_id: str = Field(default_factory=lambda: str(uuid4()))
    integration_batch: list[str] = Field(default_factory=list)
    successful_integrations: list[str] = Field(default_factory=list)
    failed_integrations: list[str] = Field(default_factory=list)
    conflicts_resolved: list[str] = Field(default_factory=list)
    conflicts_remaining: list[str] = Field(default_factory=list)
    quality_gate_results: dict[str, bool] = Field(default_factory=dict)
    integration_time: timedelta
    created_at: datetime = Field(default_factory=datetime.now)
    summary: str = ""