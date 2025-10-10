"""
AI Consultation System for Observatory Dashboard

This module provides cost-controlled, queue-based AI consultation features
integrated into the Observatory monitoring dashboard.

The "Doctor Is In/Out" system provides:
- Real-time AI chat when "Doctor Is In"
- Queue-based processing when "Doctor Is Out"
- Cost monitoring and budget controls
- Observatory context integration
- Optional email notifications
"""

from .models import (
    ProcessingMode, QueryPriority, DoctorStatusReason,
    ConsultationQuery, ConsultationResult, DoctorStatus, QueuedQuery, 
    BudgetStatus, CostAnalytics, ObservatoryContext
)
from .exceptions import (
    ConsultationError, ValidationError, ProcessingError,
    CostLimitExceededError, QueueFullError, ContextUnavailableError
)
from .interfaces import (
    ConsultationServiceInterface, ContextProviderInterface, 
    NotificationServiceInterface
)
from .feature_flags import feature_flags, FeatureFlag
from .circuit_breaker import CircuitBreaker, with_circuit_breaker
from .health_checker import HealthChecker, ComponentHealth, SystemHealth
from .visual_regression import VisualRegressionTester, RegressionResult, RegressionSeverity
from .doctor_status_manager import (
    DoctorStatusManager, StatusTransition, StatusChangeEvent,
    status_manager, get_doctor_status, initialize_status_manager, cleanup_status_manager
)
from .database import DatabaseManager, initialize_database, cleanup_database
from .status_broadcaster import (
    StatusBroadcaster, BroadcastChannel, WebSocketMessage, ClientConnection,
    status_broadcaster, initialize_broadcaster, cleanup_broadcaster
)
from .status_persistence import (
    StatusPersistence, status_persistence, initialize_persistence, cleanup_persistence
)
from .observatory_context_provider import (
    ObservatoryContextProvider, MetricData, AlertData, SystemStatus, DataSensitivity, MetricType,
    observatory_context_provider, get_observatory_context, initialize_context_provider, cleanup_context_provider
)
from .security_manager import (
    SecurityManager, PermissionLevel, ResourceType, UserPermissions, SecurityContext,
    security_manager, authenticate_user, validate_session, check_permission,
    initialize_security_manager, cleanup_security_manager
)
from .consultation_router import (
    ConsultationRouter, RoutingDecision, RoutingReason, RoutingContext, RoutingResult,
    get_consultation_router, route_consultation_request
)
from .request_processor import (
    RequestProcessor, ProcessingStage, ContextInjectionMode, ProcessedRequest,
    get_request_processor, process_consultation_request
)
from .realtime_chat_engine import (
    RealTimeChatEngine, ChatSession, ChatMessage, ChatSessionState, 
    MessageType, ChatMessageRole, get_chat_engine
)
from .llm_service import (
    LLMService, LLMProvider, LLMModel, LLMRequest, LLMResponse, LLMUsage, LLMCost,
    get_llm_service
)
from .query_queue import (
    QueryQueue, QueuedQuery, QueueStatus, get_query_queue
)

__version__ = "0.1.0"
__all__ = [
    # Models
    "ProcessingMode", "QueryPriority", "DoctorStatusReason", "RegressionSeverity",
    "ConsultationQuery", "ConsultationResult", "DoctorStatus", "QueuedQuery", 
    "BudgetStatus", "CostAnalytics", "ObservatoryContext",
    
    # Exceptions
    "ConsultationError", "ValidationError", "ProcessingError",
    "CostLimitExceededError", "QueueFullError", "ContextUnavailableError",
    
    # Interfaces
    "ConsultationServiceInterface", "ContextProviderInterface", 
    "NotificationServiceInterface",
    
    # Feature Management
    "feature_flags", "FeatureFlag",
    
    # Infrastructure
    "CircuitBreaker", "with_circuit_breaker",
    "HealthChecker", "ComponentHealth", "SystemHealth",
    "VisualRegressionTester", "RegressionResult",
    
    # Status Management
    "DoctorStatusManager", "StatusTransition", "StatusChangeEvent",
    "status_manager", "get_doctor_status", "initialize_status_manager", "cleanup_status_manager",
    
    # Database
    "DatabaseManager", "initialize_database", "cleanup_database",
    
    # Broadcasting & Persistence
    "StatusBroadcaster", "BroadcastChannel", "WebSocketMessage", "ClientConnection",
    "status_broadcaster", "initialize_broadcaster", "cleanup_broadcaster",
    "StatusPersistence", "status_persistence", "initialize_persistence", "cleanup_persistence",
    
    # Observatory Context
    "ObservatoryContextProvider", "MetricData", "AlertData", "SystemStatus", "DataSensitivity", "MetricType",
    "observatory_context_provider", "get_observatory_context", "initialize_context_provider", "cleanup_context_provider",
    
    # Security & Permissions
    "SecurityManager", "PermissionLevel", "ResourceType", "UserPermissions", "SecurityContext",
    "security_manager", "authenticate_user", "validate_session", "check_permission",
    "initialize_security_manager", "cleanup_security_manager",
    
    # Consultation Routing
    "ConsultationRouter", "RoutingDecision", "RoutingReason", "RoutingContext", "RoutingResult",
    "get_consultation_router", "route_consultation_request",
    
    # Request Processing
    "RequestProcessor", "ProcessingStage", "ContextInjectionMode", "ProcessedRequest",
    "get_request_processor", "process_consultation_request",
    
    # Real-Time Chat
    "RealTimeChatEngine", "ChatSession", "ChatMessage", "ChatSessionState", 
    "MessageType", "ChatMessageRole", "get_chat_engine",
    
    # LLM Service
    "LLMService", "LLMProvider", "LLMModel", "LLMRequest", "LLMResponse", "LLMUsage", "LLMCost",
    "get_llm_service",
    
    # Query Queue
    "QueryQueue", "QueuedQuery", "QueueStatus", "get_query_queue",
]