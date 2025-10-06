#!/usr/bin/env python3
"""
LLM Selection Policies for DAG Orchestration
===========================================

Configurable LLM selection policies including cost-first, capability-first,
and balanced approaches with dynamic strategy selection.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class LLMSelectionStrategy(Enum):
    """LLM selection strategy types."""
    COST_FIRST = "cost_first"
    CAPABILITY_FIRST = "capability_first"
    BALANCED = "balanced"
    PERFORMANCE_FIRST = "performance_first"
    AVAILABILITY_FIRST = "availability_first"


@dataclass
class LLMProvider:
    """LLM provider information for selection."""
    name: str
    cost_per_token: float
    capability_score: float  # 0.0 to 1.0
    performance_score: float  # 0.0 to 1.0 (based on response time)
    availability_score: float  # 0.0 to 1.0 (based on uptime)
    subscription_model: bool = False
    max_tokens: int = 4096
    supports_streaming: bool = True
    supports_function_calling: bool = False
    last_used: Optional[datetime] = None
    success_rate: float = 1.0
    average_response_time: float = 1.0  # seconds


@dataclass
class TaskRequirements:
    """Requirements for task execution."""
    complexity_score: float  # 0.0 to 1.0
    max_cost: Optional[float] = None
    min_capability: float = 0.0
    max_response_time: Optional[float] = None
    requires_streaming: bool = False
    requires_function_calling: bool = False
    priority: int = 0  # Higher number = higher priority


@dataclass
class LLMSelectionResult:
    """Result of LLM selection process."""
    selected_provider: LLMProvider
    selection_rationale: str
    confidence_score: float  # 0.0 to 1.0
    estimated_cost: float
    estimated_time: float
    fallback_providers: List[LLMProvider] = field(default_factory=list)


class LLMSelectionPolicy(ABC):
    """Abstract base class for LLM selection policies."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self._logger = logging.getLogger(f"dag_orchestration.{self.__class__.__name__}")
    
    @abstractmethod
    def select_llm(self, providers: List[LLMProvider], 
                   requirements: TaskRequirements) -> LLMSelectionResult:
        """Select the best LLM provider based on policy."""
        pass
    
    def _calculate_cost_score(self, provider: LLMProvider, requirements: TaskRequirements) -> float:
        """Calculate cost score (higher is better for lower cost)."""
        if provider.subscription_model:
            return 1.0  # Subscription models get highest cost score
        
        # Normalize cost (assuming max cost per token of $0.01)
        max_cost = 0.01
        cost_score = 1.0 - min(provider.cost_per_token / max_cost, 1.0)
        
        # Apply cost constraint if specified
        if requirements.max_cost:
            estimated_cost = provider.cost_per_token * 1000  # Estimate for 1000 tokens
            if estimated_cost > requirements.max_cost:
                return 0.0  # Exceeds budget
        
        return cost_score
    
    def _calculate_capability_score(self, provider: LLMProvider, requirements: TaskRequirements) -> float:
        """Calculate capability score."""
        if provider.capability_score < requirements.min_capability:
            return 0.0  # Doesn't meet minimum capability
        
        capability_score = provider.capability_score
        
        # Apply feature requirements
        if requirements.requires_streaming and not provider.supports_streaming:
            capability_score *= 0.5
        
        if requirements.requires_function_calling and not provider.supports_function_calling:
            capability_score *= 0.3
        
        return capability_score
    
    def _calculate_performance_score(self, provider: LLMProvider, requirements: TaskRequirements) -> float:
        """Calculate performance score."""
        performance_score = provider.performance_score
        
        # Apply response time constraint if specified
        if requirements.max_response_time:
            if provider.average_response_time > requirements.max_response_time:
                return 0.0  # Too slow
        
        # Factor in success rate
        performance_score *= provider.success_rate
        
        return performance_score
    
    def _calculate_availability_score(self, provider: LLMProvider, requirements: TaskRequirements) -> float:
        """Calculate availability score."""
        return provider.availability_score


class CostFirstPolicy(LLMSelectionPolicy):
    """Policy that prioritizes cost optimization."""
    
    def __init__(self, cost_weight: float = 0.6, capability_weight: float = 0.3, performance_weight: float = 0.1):
        super().__init__("cost_first", "Prioritizes cost optimization while meeting capability requirements")
        self.cost_weight = cost_weight
        self.capability_weight = capability_weight
        self.performance_weight = performance_weight
    
    def select_llm(self, providers: List[LLMProvider], 
                   requirements: TaskRequirements) -> LLMSelectionResult:
        """Select LLM with cost-first strategy."""
        if not providers:
            raise ValueError("No LLM providers available")
        
        best_provider = None
        best_score = -1.0
        scores = []
        
        for provider in providers:
            cost_score = self._calculate_cost_score(provider, requirements)
            capability_score = self._calculate_capability_score(provider, requirements)
            performance_score = self._calculate_performance_score(provider, requirements)
            
            # Skip providers that don't meet minimum requirements
            if capability_score == 0.0 or performance_score == 0.0:
                continue
            
            # Calculate weighted score
            total_score = (
                cost_score * self.cost_weight +
                capability_score * self.capability_weight +
                performance_score * self.performance_weight
            )
            
            scores.append((provider, total_score, cost_score, capability_score, performance_score))
            
            if total_score > best_score:
                best_score = total_score
                best_provider = provider
        
        if best_provider is None:
            raise ValueError("No LLM providers meet the requirements")
        
        # Calculate estimated cost and time
        estimated_tokens = 1000 * (1 + requirements.complexity_score)  # Simple estimation
        estimated_cost = best_provider.cost_per_token * estimated_tokens if not best_provider.subscription_model else 0.0
        estimated_time = best_provider.average_response_time * (1 + requirements.complexity_score)
        
        # Create fallback list (sorted by score, excluding selected)
        fallback_providers = [p for p, s, _, _, _ in sorted(scores, key=lambda x: x[1], reverse=True) if p != best_provider][:3]
        
        return LLMSelectionResult(
            selected_provider=best_provider,
            selection_rationale=f"Selected based on cost-first policy (score: {best_score:.3f}). "
                              f"Cost optimization prioritized with {self.cost_weight:.1%} weight.",
            confidence_score=best_score,
            estimated_cost=estimated_cost,
            estimated_time=estimated_time,
            fallback_providers=fallback_providers
        )


class CapabilityFirstPolicy(LLMSelectionPolicy):
    """Policy that prioritizes capability and quality."""
    
    def __init__(self, capability_weight: float = 0.6, performance_weight: float = 0.3, cost_weight: float = 0.1):
        super().__init__("capability_first", "Prioritizes capability and quality over cost")
        self.capability_weight = capability_weight
        self.performance_weight = performance_weight
        self.cost_weight = cost_weight
    
    def select_llm(self, providers: List[LLMProvider], 
                   requirements: TaskRequirements) -> LLMSelectionResult:
        """Select LLM with capability-first strategy."""
        if not providers:
            raise ValueError("No LLM providers available")
        
        best_provider = None
        best_score = -1.0
        scores = []
        
        for provider in providers:
            cost_score = self._calculate_cost_score(provider, requirements)
            capability_score = self._calculate_capability_score(provider, requirements)
            performance_score = self._calculate_performance_score(provider, requirements)
            
            # Skip providers that don't meet minimum requirements
            if capability_score == 0.0 or performance_score == 0.0:
                continue
            
            # Calculate weighted score
            total_score = (
                capability_score * self.capability_weight +
                performance_score * self.performance_weight +
                cost_score * self.cost_weight
            )
            
            scores.append((provider, total_score, cost_score, capability_score, performance_score))
            
            if total_score > best_score:
                best_score = total_score
                best_provider = provider
        
        if best_provider is None:
            raise ValueError("No LLM providers meet the requirements")
        
        # Calculate estimated cost and time
        estimated_tokens = 1000 * (1 + requirements.complexity_score)
        estimated_cost = best_provider.cost_per_token * estimated_tokens if not best_provider.subscription_model else 0.0
        estimated_time = best_provider.average_response_time * (1 + requirements.complexity_score)
        
        # Create fallback list
        fallback_providers = [p for p, s, _, _, _ in sorted(scores, key=lambda x: x[1], reverse=True) if p != best_provider][:3]
        
        return LLMSelectionResult(
            selected_provider=best_provider,
            selection_rationale=f"Selected based on capability-first policy (score: {best_score:.3f}). "
                              f"Capability prioritized with {self.capability_weight:.1%} weight.",
            confidence_score=best_score,
            estimated_cost=estimated_cost,
            estimated_time=estimated_time,
            fallback_providers=fallback_providers
        )


class BalancedPolicy(LLMSelectionPolicy):
    """Policy that balances cost, capability, and performance."""
    
    def __init__(self, cost_weight: float = 0.33, capability_weight: float = 0.33, 
                 performance_weight: float = 0.34):
        super().__init__("balanced", "Balances cost, capability, and performance considerations")
        self.cost_weight = cost_weight
        self.capability_weight = capability_weight
        self.performance_weight = performance_weight
    
    def select_llm(self, providers: List[LLMProvider], 
                   requirements: TaskRequirements) -> LLMSelectionResult:
        """Select LLM with balanced strategy."""
        if not providers:
            raise ValueError("No LLM providers available")
        
        best_provider = None
        best_score = -1.0
        scores = []
        
        for provider in providers:
            cost_score = self._calculate_cost_score(provider, requirements)
            capability_score = self._calculate_capability_score(provider, requirements)
            performance_score = self._calculate_performance_score(provider, requirements)
            availability_score = self._calculate_availability_score(provider, requirements)
            
            # Skip providers that don't meet minimum requirements
            if capability_score == 0.0 or performance_score == 0.0:
                continue
            
            # Calculate weighted score with availability factor
            total_score = (
                cost_score * self.cost_weight +
                capability_score * self.capability_weight +
                performance_score * self.performance_weight
            ) * availability_score  # Multiply by availability as a factor
            
            scores.append((provider, total_score, cost_score, capability_score, performance_score))
            
            if total_score > best_score:
                best_score = total_score
                best_provider = provider
        
        if best_provider is None:
            raise ValueError("No LLM providers meet the requirements")
        
        # Calculate estimated cost and time
        estimated_tokens = 1000 * (1 + requirements.complexity_score)
        estimated_cost = best_provider.cost_per_token * estimated_tokens if not best_provider.subscription_model else 0.0
        estimated_time = best_provider.average_response_time * (1 + requirements.complexity_score)
        
        # Create fallback list
        fallback_providers = [p for p, s, _, _, _ in sorted(scores, key=lambda x: x[1], reverse=True) if p != best_provider][:3]
        
        return LLMSelectionResult(
            selected_provider=best_provider,
            selection_rationale=f"Selected based on balanced policy (score: {best_score:.3f}). "
                              f"Equal weighting of cost ({self.cost_weight:.1%}), "
                              f"capability ({self.capability_weight:.1%}), and "
                              f"performance ({self.performance_weight:.1%}).",
            confidence_score=best_score,
            estimated_cost=estimated_cost,
            estimated_time=estimated_time,
            fallback_providers=fallback_providers
        )


class AdaptiveLLMSelector(ReflectiveModule):
    """
    Adaptive LLM selector that can switch between policies based on context.
    
    Features:
    - Multiple selection policies
    - Dynamic policy switching
    - Learning from selection outcomes
    - Provider performance tracking
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "AdaptiveLLMSelector"
        self._logger = logging.getLogger(f"dag_orchestration.{self.__class__.__name__}")
        
        # Initialize policies
        self._policies: Dict[str, LLMSelectionPolicy] = {
            "cost_first": CostFirstPolicy(),
            "capability_first": CapabilityFirstPolicy(),
            "balanced": BalancedPolicy()
        }
        
        # Provider tracking
        self._providers: Dict[str, LLMProvider] = {}
        self._selection_history: List[Dict[str, Any]] = []
        
        # Configuration
        self._default_policy = "balanced"
        self._learning_enabled = True
        
        self._logger.info("AdaptiveLLMSelector initialized with policies: " + 
                         ", ".join(self._policies.keys()))
    
    def register_provider(self, provider: LLMProvider) -> None:
        """Register an LLM provider."""
        self._providers[provider.name] = provider
        self._logger.info(f"Registered LLM provider: {provider.name}")
    
    def update_provider_performance(self, provider_name: str, 
                                  response_time: float, success: bool) -> None:
        """Update provider performance metrics."""
        if provider_name not in self._providers:
            return
        
        provider = self._providers[provider_name]
        
        # Update average response time (exponential moving average)
        alpha = 0.1
        provider.average_response_time = (
            alpha * response_time + (1 - alpha) * provider.average_response_time
        )
        
        # Update success rate (exponential moving average)
        success_value = 1.0 if success else 0.0
        provider.success_rate = (
            alpha * success_value + (1 - alpha) * provider.success_rate
        )
        
        # Update last used timestamp
        provider.last_used = datetime.now()
        
        self._logger.debug(f"Updated performance for {provider_name}: "
                          f"response_time={response_time:.2f}s, success={success}")
    
    def select_llm(self, requirements: TaskRequirements, 
                   policy_name: Optional[str] = None) -> LLMSelectionResult:
        """Select LLM using specified or default policy."""
        with self.trace_operation("select_llm", 
                                requirements=requirements, 
                                policy_name=policy_name) as trace:
            
            # Use specified policy or default
            policy_name = policy_name or self._default_policy
            
            if policy_name not in self._policies:
                raise ValueError(f"Unknown policy: {policy_name}")
            
            policy = self._policies[policy_name]
            providers = list(self._providers.values())
            
            if not providers:
                raise ValueError("No LLM providers registered")
            
            # Select LLM using policy
            result = policy.select_llm(providers, requirements)
            
            # Record selection for learning
            selection_record = {
                'timestamp': datetime.now(),
                'policy_used': policy_name,
                'selected_provider': result.selected_provider.name,
                'requirements': requirements,
                'confidence_score': result.confidence_score,
                'estimated_cost': result.estimated_cost,
                'estimated_time': result.estimated_time
            }
            self._selection_history.append(selection_record)
            
            # Keep only last 1000 selections
            if len(self._selection_history) > 1000:
                self._selection_history = self._selection_history[-1000:]
            
            trace.output_result = {
                'selected_provider': result.selected_provider.name,
                'policy_used': policy_name,
                'confidence_score': result.confidence_score,
                'estimated_cost': result.estimated_cost
            }
            
            self._logger.info(f"Selected LLM '{result.selected_provider.name}' "
                            f"using '{policy_name}' policy (confidence: {result.confidence_score:.3f})")
            
            return result
    
    def get_provider_statistics(self) -> Dict[str, Any]:
        """Get statistics for all registered providers."""
        stats = {}
        
        for name, provider in self._providers.items():
            stats[name] = {
                'cost_per_token': provider.cost_per_token,
                'capability_score': provider.capability_score,
                'performance_score': provider.performance_score,
                'availability_score': provider.availability_score,
                'subscription_model': provider.subscription_model,
                'success_rate': provider.success_rate,
                'average_response_time': provider.average_response_time,
                'last_used': provider.last_used.isoformat() if provider.last_used else None
            }
        
        return stats
    
    def get_selection_statistics(self) -> Dict[str, Any]:
        """Get selection statistics and patterns."""
        if not self._selection_history:
            return {'total_selections': 0}
        
        # Calculate statistics
        total_selections = len(self._selection_history)
        policy_usage = {}
        provider_usage = {}
        
        for record in self._selection_history:
            policy = record['policy_used']
            provider = record['selected_provider']
            
            policy_usage[policy] = policy_usage.get(policy, 0) + 1
            provider_usage[provider] = provider_usage.get(provider, 0) + 1
        
        # Calculate averages
        avg_confidence = sum(r['confidence_score'] for r in self._selection_history) / total_selections
        avg_cost = sum(r['estimated_cost'] for r in self._selection_history) / total_selections
        avg_time = sum(r['estimated_time'] for r in self._selection_history) / total_selections
        
        return {
            'total_selections': total_selections,
            'policy_usage': policy_usage,
            'provider_usage': provider_usage,
            'average_confidence': avg_confidence,
            'average_estimated_cost': avg_cost,
            'average_estimated_time': avg_time,
            'recent_selections': self._selection_history[-10:]  # Last 10 selections
        }
    
    def recommend_policy(self, requirements: TaskRequirements) -> str:
        """Recommend best policy based on requirements and history."""
        # Simple heuristic-based recommendation
        if requirements.max_cost and requirements.max_cost < 1.0:
            return "cost_first"
        elif requirements.complexity_score > 0.8 or requirements.min_capability > 0.7:
            return "capability_first"
        else:
            return "balanced"
    
    def set_default_policy(self, policy_name: str) -> None:
        """Set default selection policy."""
        if policy_name not in self._policies:
            raise ValueError(f"Unknown policy: {policy_name}")
        
        self._default_policy = policy_name
        self._logger.info(f"Set default policy to: {policy_name}")


# Convenience functions
def create_adaptive_llm_selector() -> AdaptiveLLMSelector:
    """Factory function to create adaptive LLM selector."""
    return AdaptiveLLMSelector()


def create_default_providers() -> List[LLMProvider]:
    """Create default LLM provider configurations."""
    return [
        LLMProvider(
            name="cursor",
            cost_per_token=0.0,  # Subscription model
            capability_score=0.8,
            performance_score=0.9,
            availability_score=0.95,
            subscription_model=True,
            supports_streaming=True,
            supports_function_calling=True
        ),
        LLMProvider(
            name="claude",
            cost_per_token=0.008,
            capability_score=0.95,
            performance_score=0.85,
            availability_score=0.98,
            subscription_model=False,
            supports_streaming=True,
            supports_function_calling=True
        ),
        LLMProvider(
            name="kiro",
            cost_per_token=0.0,  # Internal system
            capability_score=0.7,
            performance_score=0.8,
            availability_score=1.0,
            subscription_model=True,
            supports_streaming=True,
            supports_function_calling=False
        )
    ]