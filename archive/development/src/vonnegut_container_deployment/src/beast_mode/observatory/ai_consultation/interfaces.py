"""
Abstract interfaces for AI Consultation System

These interfaces define the contracts for all major components,
enabling dependency injection and testing.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncIterator
from datetime import datetime

from .models import (
    ConsultationQuery,
    ConsultationResult,
    DoctorStatus,
    QueuedQuery,
    QueueStatus,
    ObservatoryContext,
    BudgetStatus,
    CostAnalytics,
    ProcessingMode
)


class IDoctorStatusManager(ABC):
    """Interface for managing doctor availability and cost controls"""
    
    @abstractmethod
    async def get_status(self) -> DoctorStatus:
        """Get current doctor status"""
        pass
    
    @abstractmethod
    async def set_status(self, is_available: bool, reason: str) -> bool:
        """Set doctor availability status"""
        pass
    
    @abstractmethod
    async def check_budget_limits(self) -> BudgetStatus:
        """Check current budget status and limits"""
        pass
    
    @abstractmethod
    async def track_usage(self, tokens: int, cost: float) -> None:
        """Track token usage and cost"""
        pass
    
    @abstractmethod
    async def get_cost_analytics(self, days: int = 30) -> CostAnalytics:
        """Get cost analytics for specified period"""
        pass
    
    @abstractmethod
    async def reset_daily_budget(self) -> None:
        """Reset daily budget counters"""
        pass
    
    @abstractmethod
    async def reset_monthly_budget(self) -> None:
        """Reset monthly budget counters"""
        pass


class IConsultationRouter(ABC):
    """Interface for routing consultation requests"""
    
    @abstractmethod
    async def submit_query(self, query: ConsultationQuery) -> ConsultationResult:
        """Submit a query for processing"""
        pass
    
    @abstractmethod
    async def get_processing_mode(self) -> ProcessingMode:
        """Get current processing mode"""
        pass
    
    @abstractmethod
    async def handle_mode_transition(self, query: ConsultationQuery) -> None:
        """Handle transitions between processing modes"""
        pass


class IRealTimeChatEngine(ABC):
    """Interface for real-time chat consultation"""
    
    @abstractmethod
    async def start_session(self, user_id: str, context: ObservatoryContext) -> str:
        """Start a new chat session, returns session_id"""
        pass
    
    @abstractmethod
    async def process_message(self, session_id: str, message: str) -> AsyncIterator[str]:
        """Process a chat message and stream response"""
        pass
    
    @abstractmethod
    async def end_session(self, session_id: str) -> Dict[str, Any]:
        """End a chat session and return summary"""
        pass
    
    @abstractmethod
    async def get_session_cost(self, session_id: str) -> float:
        """Get current cost for a session"""
        pass
    
    @abstractmethod
    async def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        pass


class IBatchQueryProcessor(ABC):
    """Interface for batch query processing"""
    
    @abstractmethod
    async def queue_query(self, query: QueuedQuery) -> str:
        """Add query to processing queue, returns queue_id"""
        pass
    
    @abstractmethod
    async def process_batch(self, batch_size: int = 10) -> List[ConsultationResult]:
        """Process a batch of queued queries"""
        pass
    
    @abstractmethod
    async def get_queue_status(self) -> QueueStatus:
        """Get current queue status"""
        pass
    
    @abstractmethod
    async def retrieve_result(self, queue_id: str) -> Optional[ConsultationResult]:
        """Retrieve result for a queued query"""
        pass
    
    @abstractmethod
    async def cancel_query(self, queue_id: str) -> bool:
        """Cancel a queued query"""
        pass


class IObservatoryContextProvider(ABC):
    """Interface for providing Observatory monitoring context"""
    
    @abstractmethod
    async def get_current_context(self, user_id: str) -> ObservatoryContext:
        """Get current Observatory context for user"""
        pass
    
    @abstractmethod
    async def get_metric_context(self, metric_names: List[str], user_id: str) -> Dict[str, Any]:
        """Get context for specific metrics"""
        pass
    
    @abstractmethod
    async def get_alert_context(self, user_id: str) -> Dict[str, Any]:
        """Get current alert context"""
        pass
    
    @abstractmethod
    async def format_for_llm(self, context: ObservatoryContext) -> str:
        """Format context for LLM consumption"""
        pass
    
    @abstractmethod
    async def validate_permissions(self, user_id: str, context_type: str) -> bool:
        """Validate user permissions for context access"""
        pass


class IResultsStorageManager(ABC):
    """Interface for storing and retrieving consultation results"""
    
    @abstractmethod
    async def store_result(self, result: ConsultationResult) -> str:
        """Store consultation result, returns result_id"""
        pass
    
    @abstractmethod
    async def search_results(self, query: str, user_id: str, limit: int = 50) -> List[ConsultationResult]:
        """Search consultation results"""
        pass
    
    @abstractmethod
    async def get_user_history(self, user_id: str, limit: int = 100) -> List[ConsultationResult]:
        """Get consultation history for user"""
        pass
    
    @abstractmethod
    async def get_result_by_id(self, result_id: str) -> Optional[ConsultationResult]:
        """Get specific result by ID"""
        pass
    
    @abstractmethod
    async def cleanup_old_results(self, days: int = 90) -> int:
        """Clean up old results, returns count of deleted results"""
        pass
    
    @abstractmethod
    async def get_similar_queries(self, query_text: str, user_id: str, limit: int = 5) -> List[ConsultationResult]:
        """Find similar previous queries"""
        pass


class IEmailNotificationService(ABC):
    """Interface for email notification service"""
    
    @abstractmethod
    async def send_result_notification(self, email: str, result: ConsultationResult) -> bool:
        """Send result notification email"""
        pass
    
    @abstractmethod
    async def validate_email(self, email: str) -> bool:
        """Validate email format and deliverability"""
        pass
    
    @abstractmethod
    async def store_email_preference(self, user_id: str, email: str) -> None:
        """Store user email preference securely"""
        pass
    
    @abstractmethod
    async def remove_email_preference(self, user_id: str) -> None:
        """Remove user email preference"""
        pass
    
    @abstractmethod
    async def get_email_preference(self, user_id: str) -> Optional[str]:
        """Get user email preference"""
        pass
    
    @abstractmethod
    async def track_delivery(self, email: str, result_id: str, status: str) -> None:
        """Track email delivery status"""
        pass


class IFeatureFlagManager(ABC):
    """Interface for feature flag management"""
    
    @abstractmethod
    async def is_enabled(self, flag_name: str, user_id: Optional[str] = None) -> bool:
        """Check if feature flag is enabled"""
        pass
    
    @abstractmethod
    async def set_flag(self, flag_name: str, enabled: bool) -> None:
        """Set feature flag state"""
        pass
    
    @abstractmethod
    async def get_all_flags(self) -> Dict[str, bool]:
        """Get all feature flag states"""
        pass
    
    @abstractmethod
    async def get_user_flags(self, user_id: str) -> Dict[str, bool]:
        """Get feature flags for specific user"""
        pass


class ICircuitBreaker(ABC):
    """Interface for circuit breaker pattern"""
    
    @abstractmethod
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        pass
    
    @abstractmethod
    async def is_open(self) -> bool:
        """Check if circuit breaker is open"""
        pass
    
    @abstractmethod
    async def reset(self) -> None:
        """Reset circuit breaker to closed state"""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        pass


class IHealthChecker(ABC):
    """Interface for health checking"""
    
    @abstractmethod
    async def check_health(self) -> Dict[str, Any]:
        """Perform health check"""
        pass
    
    @abstractmethod
    async def check_readiness(self) -> Dict[str, Any]:
        """Check if service is ready to handle requests"""
        pass
    
    @abstractmethod
    async def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics"""
        pass