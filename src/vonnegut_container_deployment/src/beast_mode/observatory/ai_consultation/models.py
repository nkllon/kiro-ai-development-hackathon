"""
Core data models for AI Consultation System

These models define the data structures used throughout the AI consultation
system with proper validation and backward compatibility.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


class ProcessingMode(str, Enum):
    """Processing mode for AI consultations"""
    REAL_TIME = "real_time"
    QUEUE = "queue"


class QueryPriority(str, Enum):
    """Priority levels for queued queries"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class DoctorStatusReason(str, Enum):
    """Reasons for doctor status changes"""
    MANUAL = "manual"
    BUDGET_LIMIT = "budget_limit"
    COST_THRESHOLD = "cost_threshold"
    SYSTEM_ERROR = "system_error"
    MAINTENANCE = "maintenance"


class Alert(BaseModel):
    """Observatory alert model"""
    id: str
    name: str
    severity: str
    status: str
    timestamp: datetime
    message: str
    tags: Dict[str, str] = Field(default_factory=dict)


class Event(BaseModel):
    """Observatory event model"""
    id: str
    type: str
    timestamp: datetime
    source: str
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SystemHealth(BaseModel):
    """Observatory system health model"""
    overall_status: str
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_status: str
    service_count: int
    healthy_services: int
    timestamp: datetime


class UserPermissions(BaseModel):
    """User permissions for Observatory data access"""
    user_id: str
    can_view_metrics: bool = True
    can_view_alerts: bool = True
    can_view_events: bool = True
    can_view_system_health: bool = True
    accessible_namespaces: List[str] = Field(default_factory=list)
    accessible_services: List[str] = Field(default_factory=list)


class ObservatoryContext(BaseModel):
    """Observatory monitoring context for AI consultations"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    system_status: str  # "healthy", "degraded", "unhealthy"
    active_alerts: int = Field(default=0, ge=0)
    critical_alerts: int = Field(default=0, ge=0)
    metrics_summary: Dict[str, Any] = Field(default_factory=dict)
    alerts_summary: Dict[str, Any] = Field(default_factory=dict)
    formatted_context: str = Field(default="")  # LLM-optimized context
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class ConsultationQuery(BaseModel):
    """A query submitted for AI consultation"""
    query_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    query_text: str = Field(..., min_length=1, max_length=10000)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    context_snapshot: Optional[ObservatoryContext] = None
    email_notification: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')
    priority: QueryPriority = QueryPriority.NORMAL
    processing_mode: Optional[ProcessingMode] = None
    session_id: Optional[str] = None
    
    @field_validator('query_text')
    @classmethod
    def validate_query_text(cls, v):
        """Validate and sanitize query text"""
        if not v or not v.strip():
            raise ValueError("Query text cannot be empty")
        # Basic sanitization - remove potential script tags
        sanitized = v.replace('<script', '&lt;script').replace('</script>', '&lt;/script&gt;')
        return sanitized.strip()
    
    @field_validator('email_notification')
    @classmethod
    def validate_email(cls, v):
        """Validate email format if provided"""
        if v is not None and v.strip():
            # Basic email validation - more comprehensive validation in service layer
            if '@' not in v or '.' not in v.split('@')[-1]:
                raise ValueError("Invalid email format")
            return v.strip().lower()
        return None
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class ConsultationResult(BaseModel):
    """Result of an AI consultation"""
    result_id: str = Field(default_factory=lambda: str(uuid4()))
    query_id: str
    query: ConsultationQuery
    response: str
    processing_mode: ProcessingMode
    cost: float = Field(ge=0)
    tokens_used: int = Field(ge=0)
    processing_time: float = Field(ge=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    error_message: Optional[str] = None
    retry_count: int = Field(default=0, ge=0)
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class DoctorStatus(BaseModel):
    """Current status of the AI consultation system"""
    is_available: bool
    reason: DoctorStatusReason
    cost_budget_remaining: float = Field(ge=0)
    daily_usage: float = Field(default=0, ge=0)
    monthly_usage: float = Field(default=0, ge=0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    next_budget_reset: Optional[datetime] = None
    active_sessions: int = Field(default=0, ge=0)
    queue_length: int = Field(default=0, ge=0)
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class QueuedQuery(BaseModel):
    """A query in the processing queue"""
    queue_id: str = Field(default_factory=lambda: str(uuid4()))
    query: ConsultationQuery
    queued_at: datetime = Field(default_factory=datetime.utcnow)
    priority: QueryPriority = QueryPriority.NORMAL
    estimated_cost: float = Field(default=0, ge=0)
    retry_count: int = Field(default=0, ge=0)
    max_retries: int = Field(default=3, ge=0)
    processing_started_at: Optional[datetime] = None
    
    @property
    def is_expired(self) -> bool:
        """Check if query has been in queue too long"""
        max_age = timedelta(hours=24)  # Queries expire after 24 hours
        return datetime.utcnow() - self.queued_at > max_age
    
    @property
    def can_retry(self) -> bool:
        """Check if query can be retried"""
        return self.retry_count < self.max_retries
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class QueueStatus(BaseModel):
    """Current status of the query queue"""
    total_queued: int = Field(ge=0)
    processing: int = Field(ge=0)
    estimated_wait_time: timedelta
    estimated_batch_cost: float = Field(ge=0)
    queue_capacity: int = Field(default=1000, ge=0)
    last_processed: Optional[datetime] = None
    
    @property
    def is_full(self) -> bool:
        """Check if queue is at capacity"""
        return self.total_queued >= self.queue_capacity
    
    @property
    def utilization_percent(self) -> float:
        """Calculate queue utilization percentage"""
        return (self.total_queued / self.queue_capacity) * 100 if self.queue_capacity > 0 else 0
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            timedelta: lambda v: v.total_seconds()
        }
    )


class BudgetStatus(BaseModel):
    """Budget and cost tracking information"""
    daily_budget: float = Field(ge=0)
    monthly_budget: float = Field(ge=0)
    daily_spent: float = Field(default=0, ge=0)
    monthly_spent: float = Field(default=0, ge=0)
    daily_remaining: float = Field(ge=0)
    monthly_remaining: float = Field(ge=0)
    cost_per_token: float = Field(default=0.0001, gt=0)
    last_reset: datetime = Field(default_factory=datetime.utcnow)
    
    @model_validator(mode='before')
    @classmethod
    def calculate_remaining(cls, values):
        """Calculate remaining budget amounts"""
        if isinstance(values, dict):
            values['daily_remaining'] = max(0, values.get('daily_budget', 0) - values.get('daily_spent', 0))
            values['monthly_remaining'] = max(0, values.get('monthly_budget', 0) - values.get('monthly_spent', 0))
        return values
    
    @property
    def is_daily_budget_exceeded(self) -> bool:
        """Check if daily budget is exceeded"""
        return self.daily_spent >= self.daily_budget
    
    @property
    def is_monthly_budget_exceeded(self) -> bool:
        """Check if monthly budget is exceeded"""
        return self.monthly_spent >= self.monthly_budget
    
    @property
    def daily_utilization_percent(self) -> float:
        """Calculate daily budget utilization percentage"""
        return (self.daily_spent / self.daily_budget) * 100 if self.daily_budget > 0 else 0
    
    @property
    def monthly_utilization_percent(self) -> float:
        """Calculate monthly budget utilization percentage"""
        return (self.monthly_spent / self.monthly_budget) * 100 if self.monthly_budget > 0 else 0
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class BudgetStatus(BaseModel):
    """Current budget status and limits"""
    daily_budget: float = Field(ge=0)
    monthly_budget: float = Field(ge=0)
    daily_spent: float = Field(default=0, ge=0)
    monthly_spent: float = Field(default=0, ge=0)
    daily_remaining: float = Field(ge=0)
    monthly_remaining: float = Field(ge=0)
    daily_percentage: float = Field(ge=0, le=2)  # Allow over 100% for overruns
    monthly_percentage: float = Field(ge=0, le=2)
    daily_exhausted: bool = Field(default=False)
    monthly_exhausted: bool = Field(default=False)
    daily_warning: bool = Field(default=False)  # Above warning threshold
    monthly_warning: bool = Field(default=False)
    daily_critical: bool = Field(default=False)  # Above critical threshold
    monthly_critical: bool = Field(default=False)
    cost_per_token: float = Field(ge=0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class CostAnalytics(BaseModel):
    """Cost analytics and insights"""
    period_days: int = Field(ge=1)
    total_cost: float = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)
    total_queries: int = Field(default=0, ge=0)
    avg_cost_per_query: float = Field(default=0, ge=0)
    avg_cost_per_token: float = Field(default=0, ge=0)
    daily_costs: List[float] = Field(default_factory=list)
    cost_trend_percentage: float = Field(default=0)  # Percentage change in recent period
    budget_utilization_daily: float = Field(default=0, ge=0, le=1)
    budget_utilization_monthly: float = Field(default=0, ge=0, le=1)
    projected_monthly_cost: float = Field(default=0, ge=0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )