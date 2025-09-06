"""
Beast Mode Billing Interfaces

Core interfaces and data structures for unified billing and cost tracking.
Follows Beast Mode's Reflective Module (RM) pattern for systematic integration.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum


class BillingProviderType(Enum):
    """Types of billing providers"""
    LLM = "llm"
    GCP = "gcp"
    AWS = "aws"
    AZURE = "azure"
    OTHER = "other"


class BudgetStatus(Enum):
    """Budget status indicators"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    EXCEEDED = "exceeded"


@dataclass
class BillingMetrics:
    """Base billing metrics structure"""
    provider_type: BillingProviderType
    provider_name: str
    total_cost_usd: float
    daily_cost_usd: float
    hourly_burn_rate: float
    cost_breakdown: Dict[str, float]
    usage_metrics: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'provider_type': self.provider_type.value,
            'provider_name': self.provider_name,
            'total_cost_usd': self.total_cost_usd,
            'daily_cost_usd': self.daily_cost_usd,
            'hourly_burn_rate': self.hourly_burn_rate,
            'cost_breakdown': self.cost_breakdown,
            'usage_metrics': self.usage_metrics,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class CostAttribution:
    """Cost attribution to development activities"""
    feature_name: Optional[str] = None
    branch_name: Optional[str] = None
    team_name: Optional[str] = None
    project_id: Optional[str] = None
    tags: Dict[str, str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}


@dataclass
class UnifiedFinancialMetrics:
    """Unified financial metrics across all billing providers"""
    total_cost_usd: float
    daily_cost_usd: float
    hourly_burn_rate: float
    budget_limit_usd: float
    budget_remaining_usd: float
    budget_status: BudgetStatus
    cost_by_provider: Dict[str, float]
    cost_by_category: Dict[str, float]
    provider_metrics: List[BillingMetrics]
    cost_attribution: Optional[CostAttribution]
    timestamp: datetime
    
    @property
    def budget_utilization_percent(self) -> float:
        """Calculate budget utilization percentage"""
        if self.budget_limit_usd <= 0:
            return 0.0
        return (self.total_cost_usd / self.budget_limit_usd) * 100
    
    def get_provider_cost(self, provider_type: BillingProviderType) -> float:
        """Get cost for specific provider type"""
        return self.cost_by_provider.get(provider_type.value, 0.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'total_cost_usd': self.total_cost_usd,
            'daily_cost_usd': self.daily_cost_usd,
            'hourly_burn_rate': self.hourly_burn_rate,
            'budget_limit_usd': self.budget_limit_usd,
            'budget_remaining_usd': self.budget_remaining_usd,
            'budget_status': self.budget_status.value,
            'budget_utilization_percent': self.budget_utilization_percent,
            'cost_by_provider': self.cost_by_provider,
            'cost_by_category': self.cost_by_category,
            'provider_metrics': [m.to_dict() for m in self.provider_metrics],
            'cost_attribution': self.cost_attribution.__dict__ if self.cost_attribution else None,
            'timestamp': self.timestamp.isoformat()
        }


class BillingProvider(ABC):
    """
    Abstract base class for billing providers
    
    Follows Beast Mode's Reflective Module (RM) pattern for systematic integration
    """
    
    @abstractmethod
    async def collect_billing_metrics(self) -> BillingMetrics:
        """Collect billing metrics from the provider"""
        pass
    
    @abstractmethod
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for RM pattern compliance"""
        pass
    
    @abstractmethod
    def get_configuration_schema(self) -> Dict[str, Any]:
        """Get configuration schema for the provider"""
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Validate provider credentials"""
        pass
    
    @abstractmethod
    def get_cost_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get cost optimization recommendations"""
        pass


class BillingAggregator(ABC):
    """
    Abstract base class for billing aggregation and unified metrics
    """
    
    @abstractmethod
    async def aggregate_metrics(self, provider_metrics: List[BillingMetrics]) -> UnifiedFinancialMetrics:
        """Aggregate metrics from multiple providers"""
        pass
    
    @abstractmethod
    def calculate_cost_attribution(self, metrics: UnifiedFinancialMetrics) -> CostAttribution:
        """Calculate cost attribution to development activities"""
        pass
    
    @abstractmethod
    def check_budget_status(self, total_cost: float, budget_limit: float) -> BudgetStatus:
        """Check budget status and return appropriate enum"""
        pass


# Health monitoring interfaces for RM pattern compliance
@dataclass
class HealthStatus:
    """Health status for RM pattern"""
    is_healthy: bool
    status_message: str
    last_check: datetime
    metrics: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'is_healthy': self.is_healthy,
            'status_message': self.status_message,
            'last_check': self.last_check.isoformat(),
            'metrics': self.metrics
        }


class ReflectiveModule(ABC):
    """
    Base class for Beast Mode Reflective Module (RM) pattern
    All billing components should inherit from this
    """
    
    @abstractmethod
    def get_health_status(self) -> HealthStatus:
        """Get current health status"""
        pass
    
    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """Get operational metrics"""
        pass
    
    @abstractmethod
    def get_configuration(self) -> Dict[str, Any]:
        """Get current configuration"""
        pass