"""
LLM Integration Layer - Core Components for AI-Powered Engagement
================================================================

This module provides the foundational LLM integration components that power
all engagement engines with intelligent AI capabilities.
"""

from .orchestrator import (
    LLMOrchestrator,
    LLMProvider,
    LLMRequest,
    LLMResponse,
    ProviderConfig,
    RequestPriority
)

__version__ = "1.0.0"
__all__ = [
    "LLMOrchestrator",
    "LLMProvider", 
    "LLMRequest",
    "LLMResponse",
    "ProviderConfig",
    "RequestPriority"
]