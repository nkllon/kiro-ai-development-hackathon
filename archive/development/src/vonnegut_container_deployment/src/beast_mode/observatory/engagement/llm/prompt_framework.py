"""
Prompt Engineering Framework - Template-based Construction and Context Injection
===============================================================================

The Prompt Engineering Framework provides systematic prompt construction,
context injection, versioning, and A/B testing capabilities for LLM interactions.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
from abc import ABC, abstractmethod

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule

logger = logging.getLogger(__name__)


class PromptType(Enum):
    """Types of prompts for different engagement engines."""
    ATTENTION_PRIORITIZATION = "attention_prioritization"
    ANIMATION_SELECTION = "animation_selection"
    PERSONALITY_ANALYSIS = "personality_analysis"
    INTERACTION_INTENT = "interaction_intent"
    PATTERN_RECOGNITION = "pattern_recognition"
    CONTEXT_ANALYSIS = "context_analysis"
    GENERAL = "general"


class ContextType(Enum):
    """Types of context that can be injected into prompts."""
    SYSTEM_STATE = "system_state"
    USER_BEHAVIOR = "user_behavior"
    OBSERVATORY_METRICS = "observatory_metrics"
    ENGAGEMENT_HISTORY = "engagement_history"
    PERFORMANCE_DATA = "performance_data"
    ALERT_CONTEXT = "alert_context"


@dataclass
class PromptTemplate:
    """Template for constructing prompts."""
    template_id: str
    prompt_type: PromptType
    version: str
    system_prompt: str
    user_prompt_template: str
    required_context: List[ContextType]
    optional_context: List[ContextType] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    active: bool = True


@dataclass
class ContextData:
    """Context data for prompt injection."""
    context_type: ContextType
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    quality_score: float = 1.0
    source: str = "unknown"


@dataclass
class ConstructedPrompt:
    """Fully constructed prompt ready for LLM."""
    prompt_id: str
    template_id: str
    system_prompt: str
    user_prompt: str
    context_used: List[ContextType]
    parameters: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class ContextProvider(ABC):
    """Abstract interface for context providers."""
    
    @abstractmethod
    async def get_context(self, context_type: ContextType, **kwargs) -> Optional[ContextData]:
        """Get context data of specified type."""
        pass
    
    @abstractmethod
    async def get_available_contexts(self) -> List[ContextType]:
        """Get list of available context types."""
        pass


class SystemStateContextProvider(ContextProvider):
    """Provides system state context."""
    
    def __init__(self):
        self.cached_context: Dict[str, ContextData] = {}
        self.cache_ttl = 60.0  # 1 minute
    
    async def get_context(self, context_type: ContextType, **kwargs) -> Optional[ContextData]:
        """Get system state context."""
        if context_type != ContextType.SYSTEM_STATE:
            return None
        
        # Check cache
        cache_key = "system_state"
        if cache_key in self.cached_context:
            cached = self.cached_context[cache_key]
            if (datetime.now() - cached.timestamp).total_seconds() < self.cache_ttl:
                return cached
        
        # Generate fresh system state context
        context_data = {
            "system_cpu": 45,
            "system_memory": 62,
            "cpu_usage": 0.45,
            "memory_usage": 0.62,
            "active_users": 3,
            "dashboard_load": "moderate",
            "alert_count": 2,
            "system_health": "good",
            "performance_score": 0.85,
            "performance_budget": 16.67,
            "gpu_available": True,
            "available_actions": ["drill_down", "filter", "export", "alert"],
            "data_context": "performance_monitoring_dashboard",
            "performance_state": "normal",
            "last_update": datetime.now().isoformat()
        }
        
        context = ContextData(
            context_type=ContextType.SYSTEM_STATE,
            data=context_data,
            quality_score=0.95,
            source="system_monitor"
        )
        
        self.cached_context[cache_key] = context
        return context
    
    async def get_available_contexts(self) -> List[ContextType]:
        """Get available context types."""
        return [ContextType.SYSTEM_STATE]


class UserBehaviorContextProvider(ContextProvider):
    """Provides user behavior context."""
    
    def __init__(self):
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def get_context(self, context_type: ContextType, **kwargs) -> Optional[ContextData]:
        """Get user behavior context."""
        if context_type != ContextType.USER_BEHAVIOR:
            return None
        
        user_id = kwargs.get("user_id", "anonymous")
        
        # Mock user behavior data
        context_data = {
            "user_id": user_id,
            "session_duration": 30,  # 30 minutes
            "interaction_count": 45,
            "preferred_views": ["detailed", "charts"],
            "engagement_level": "high",
            "attention_level": "high",
            "visual_complexity": "medium",
            "attention_patterns": ["morning_active", "detail_oriented"],
            "accessibility_needs": ["keyboard_navigation"],
            "user_experience": "advanced",
            "preferred_interactions": ["keyboard", "detailed_views"],
            "current_focus": "performance_monitoring",
            "last_interaction": datetime.now().isoformat()
        }
        
        return ContextData(
            context_type=ContextType.USER_BEHAVIOR,
            data=context_data,
            quality_score=0.88,
            source="behavior_tracker"
        )
    
    async def get_available_contexts(self) -> List[ContextType]:
        """Get available context types."""
        return [ContextType.USER_BEHAVIOR]


class ObservatoryMetricsContextProvider(ContextProvider):
    """Provides Observatory-specific metrics context."""
    
    async def get_context(self, context_type: ContextType, **kwargs) -> Optional[ContextData]:
        """Get Observatory metrics context."""
        if context_type != ContextType.OBSERVATORY_METRICS:
            return None
        
        # Mock Observatory metrics
        context_data = {
            "active_dashboards": 5,
            "total_metrics": 127,
            "alert_states": {
                "critical": 1,
                "warning": 3,
                "info": 8
            },
            "data_freshness": 0.95,
            "query_performance": {
                "avg_response_time": 0.245,
                "success_rate": 0.998
            },
            "user_activity": {
                "active_sessions": 3,
                "recent_interactions": 23
            },
            "system_load": {
                "cpu": 0.34,
                "memory": 0.67,
                "network": 0.12
            }
        }
        
        return ContextData(
            context_type=ContextType.OBSERVATORY_METRICS,
            data=context_data,
            quality_score=0.92,
            source="observatory_api"
        )
    
    async def get_available_contexts(self) -> List[ContextType]:
        """Get available context types."""
        return [ContextType.OBSERVATORY_METRICS]


class PromptTemplateManager:
    """Manages prompt templates and versioning."""
    
    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self.template_versions: Dict[str, List[str]] = {}  # template_name -> [version_ids]
        self.ab_tests: Dict[str, Dict[str, Any]] = {}
        
        # Initialize default templates
        asyncio.create_task(self._initialize_default_templates())
    
    async def _initialize_default_templates(self) -> None:
        """Initialize default prompt templates."""
        
        # Attention Prioritization Template
        attention_template = PromptTemplate(
            template_id="attention_priority_v1",
            prompt_type=PromptType.ATTENTION_PRIORITIZATION,
            version="1.0",
            system_prompt="""You are an intelligent attention management system for a live dashboard. 
Your role is to analyze events and determine their priority for user attention based on context, impact, and urgency.
Always respond with valid JSON containing priority, reasoning, confidence, and recommendations.""",
            user_prompt_template="""Analyze this event for attention priority:

Event: {event_description}
Event Type: {event_type}
Timestamp: {timestamp}

System Context:
- CPU Usage: {system_cpu}%
- Memory Usage: {system_memory}%
- Active Users: {active_users}
- Current Alerts: {alert_count}

User Context:
- Session Duration: {session_duration} minutes
- Interaction Count: {interaction_count}
- Engagement Level: {engagement_level}

Determine the priority level (low, medium, high, critical) and provide reasoning.""",
            required_context=[ContextType.SYSTEM_STATE, ContextType.USER_BEHAVIOR],
            parameters={
                "max_tokens": 300,
                "temperature": 0.3
            }
        )
        
        # Animation Selection Template
        animation_template = PromptTemplate(
            template_id="animation_select_v1",
            prompt_type=PromptType.ANIMATION_SELECTION,
            version="1.0",
            system_prompt="""You are an intelligent animation system for data visualization. 
Your role is to select appropriate animations based on data characteristics, user attention patterns, and system performance.
Always respond with valid JSON containing animation_type, intensity, duration, and reasoning.""",
            user_prompt_template="""Select appropriate animation for this data update:

Data Characteristics:
- Data Type: {data_type}
- Change Magnitude: {change_magnitude}
- Update Frequency: {update_frequency}
- Data Importance: {data_importance}

System Performance:
- CPU Usage: {system_cpu}%
- GPU Available: {gpu_available}
- Performance Budget: {performance_budget}ms

User Context:
- Attention Level: {attention_level}
- Preferred Complexity: {visual_complexity}
- Accessibility Needs: {accessibility_needs}

Recommend animation type, intensity (0.0-1.0), and duration.""",
            required_context=[ContextType.SYSTEM_STATE, ContextType.USER_BEHAVIOR],
            parameters={
                "max_tokens": 250,
                "temperature": 0.4
            }
        )
        
        # Personality Analysis Template
        personality_template = PromptTemplate(
            template_id="personality_analysis_v1",
            prompt_type=PromptType.PERSONALITY_ANALYSIS,
            version="1.0",
            system_prompt="""You are an intelligent personality system for adaptive dashboard behavior. 
Your role is to analyze system events and user context to recommend appropriate personality states and transitions.
Always respond with valid JSON containing personality_state, energy_level, transition_recommended, and reasoning.""",
            user_prompt_template="""Analyze the current situation for personality adaptation:

System Events:
{system_events}

Team Context:
- Active Users: {active_users}
- Stress Indicators: {stress_indicators}
- Collaboration Level: {collaboration_level}

Current Personality:
- State: {current_personality}
- Energy Level: {current_energy}
- Duration: {personality_duration} minutes

Observatory Metrics:
- Alert Count: {alert_count}
- System Health: {system_health}
- Performance Score: {performance_score}

Recommend personality state (professional, friendly, energetic, calm, focused, celebratory) and energy level (0.0-1.0).""",
            required_context=[ContextType.SYSTEM_STATE, ContextType.OBSERVATORY_METRICS],
            parameters={
                "max_tokens": 300,
                "temperature": 0.5
            }
        )
        
        # Interaction Intent Template
        interaction_template = PromptTemplate(
            template_id="interaction_intent_v1",
            prompt_type=PromptType.INTERACTION_INTENT,
            version="1.0",
            system_prompt="""You are an intelligent interaction system that analyzes user interactions to understand intent and provide appropriate responses.
Always respond with valid JSON containing intent, confidence, suggested_response, and accessibility_considerations.""",
            user_prompt_template="""Analyze this user interaction for intent:

Interaction Details:
- Type: {interaction_type}
- Target: {target_element}
- Context: {interaction_context}
- Sequence: {interaction_sequence}

User Profile:
- Experience Level: {user_experience}
- Preferred Interactions: {preferred_interactions}
- Accessibility Needs: {accessibility_needs}
- Current Focus: {current_focus}

System State:
- Available Actions: {available_actions}
- Data Context: {data_context}
- Performance State: {performance_state}

Determine the user's intent and suggest appropriate response actions.""",
            required_context=[ContextType.USER_BEHAVIOR, ContextType.SYSTEM_STATE],
            parameters={
                "max_tokens": 350,
                "temperature": 0.3
            }
        )
        
        # Pattern Recognition Template
        pattern_template = PromptTemplate(
            template_id="pattern_recognition_v1",
            prompt_type=PromptType.PATTERN_RECOGNITION,
            version="1.0",
            system_prompt="""You are an intelligent pattern recognition system that analyzes user behavior and system data to identify meaningful patterns and optimization opportunities.
Always respond with valid JSON containing patterns_detected, user_type, optimization_opportunities, and confidence.""",
            user_prompt_template="""Analyze these patterns for insights:

User Behavior Data:
{behavior_data}

Engagement History:
{engagement_history}

System Performance:
{performance_data}

Time Patterns:
{time_patterns}

Identify behavioral patterns, classify user type, and suggest optimization opportunities.""",
            required_context=[ContextType.USER_BEHAVIOR, ContextType.ENGAGEMENT_HISTORY, ContextType.PERFORMANCE_DATA],
            optional_context=[ContextType.SYSTEM_STATE],
            parameters={
                "max_tokens": 400,
                "temperature": 0.4
            }
        )
        
        # Store templates
        templates = [
            attention_template,
            animation_template,
            personality_template,
            interaction_template,
            pattern_template
        ]
        
        for template in templates:
            await self.add_template(template)
    
    async def add_template(self, template: PromptTemplate) -> bool:
        """Add a new prompt template."""
        try:
            self.templates[template.template_id] = template
            
            # Track versions
            base_name = template.template_id.rsplit('_v', 1)[0]
            if base_name not in self.template_versions:
                self.template_versions[base_name] = []
            self.template_versions[base_name].append(template.template_id)
            
            logger.info(f"Added prompt template: {template.template_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add template {template.template_id}: {e}")
            return False
    
    async def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Get a prompt template by ID."""
        return self.templates.get(template_id)
    
    async def get_templates_by_type(self, prompt_type: PromptType) -> List[PromptTemplate]:
        """Get all templates of a specific type."""
        return [
            template for template in self.templates.values()
            if template.prompt_type == prompt_type and template.active
        ]
    
    async def get_latest_template(self, base_name: str) -> Optional[PromptTemplate]:
        """Get the latest version of a template."""
        if base_name not in self.template_versions:
            return None
        
        versions = self.template_versions[base_name]
        if not versions:
            return None
        
        # Sort by version and get latest
        latest_id = sorted(versions)[-1]
        return self.templates.get(latest_id)


class PromptConstructor:
    """Constructs prompts from templates and context."""
    
    def __init__(self):
        self.context_providers: Dict[ContextType, ContextProvider] = {}
        self.construction_cache: Dict[str, ConstructedPrompt] = {}
        self.cache_ttl = 300.0  # 5 minutes
    
    def register_context_provider(self, context_type: ContextType, provider: ContextProvider) -> None:
        """Register a context provider."""
        self.context_providers[context_type] = provider
        logger.info(f"Registered context provider for: {context_type.value}")
    
    async def construct_prompt(
        self, 
        template: PromptTemplate, 
        parameters: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> ConstructedPrompt:
        """Construct a prompt from template and context."""
        try:
            prompt_id = f"{template.template_id}_{hashlib.md5(json.dumps(parameters, sort_keys=True).encode()).hexdigest()[:8]}"
            
            # Check cache
            if prompt_id in self.construction_cache:
                cached = self.construction_cache[prompt_id]
                if (datetime.now() - cached.created_at).total_seconds() < self.cache_ttl:
                    return cached
            
            # Gather required context
            context_data = {}
            context_used = []
            
            for context_type in template.required_context:
                if context_type in self.context_providers:
                    context = await self.context_providers[context_type].get_context(
                        context_type, 
                        user_id=user_id,
                        **parameters
                    )
                    if context:
                        context_data.update(context.data)
                        context_used.append(context_type)
                    else:
                        logger.warning(f"Failed to get required context: {context_type.value}")
                else:
                    logger.warning(f"No provider for required context: {context_type.value}")
            
            # Gather optional context
            for context_type in template.optional_context:
                if context_type in self.context_providers:
                    context = await self.context_providers[context_type].get_context(
                        context_type,
                        user_id=user_id,
                        **parameters
                    )
                    if context:
                        context_data.update(context.data)
                        context_used.append(context_type)
            
            # Merge parameters with context data
            all_parameters = {**context_data, **parameters}
            
            # Construct user prompt
            try:
                user_prompt = template.user_prompt_template.format(**all_parameters)
            except KeyError as e:
                logger.error(f"Missing parameter for template {template.template_id}: {e}")
                # Fill missing parameters with defaults
                missing_params = {str(e).strip("'"): "N/A"}
                all_parameters.update(missing_params)
                user_prompt = template.user_prompt_template.format(**all_parameters)
            
            constructed = ConstructedPrompt(
                prompt_id=prompt_id,
                template_id=template.template_id,
                system_prompt=template.system_prompt,
                user_prompt=user_prompt,
                context_used=context_used,
                parameters=all_parameters,
                metadata={
                    "template_version": template.version,
                    "prompt_type": template.prompt_type.value,
                    "context_quality": 0.9  # Simplified quality score
                }
            )
            
            # Cache the result
            self.construction_cache[prompt_id] = constructed
            
            return constructed
            
        except Exception as e:
            logger.error(f"Failed to construct prompt from template {template.template_id}: {e}")
            raise


class PromptEngineering(ReflectiveModule):
    """
    Main Prompt Engineering Framework that provides template-based prompt construction,
    context injection, versioning, and A/B testing capabilities.
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "prompt_engineering"
        
        # Core components
        self.template_manager = PromptTemplateManager()
        self.prompt_constructor = PromptConstructor()
        
        # State management
        self.is_initialized = False
        self.construction_stats: Dict[str, int] = {}
        
        logger.info("Prompt Engineering Framework initialized")
    
    async def initialize(self) -> bool:
        """Initialize the Prompt Engineering Framework."""
        try:
            # Register default context providers
            self.prompt_constructor.register_context_provider(
                ContextType.SYSTEM_STATE, 
                SystemStateContextProvider()
            )
            self.prompt_constructor.register_context_provider(
                ContextType.USER_BEHAVIOR, 
                UserBehaviorContextProvider()
            )
            self.prompt_constructor.register_context_provider(
                ContextType.OBSERVATORY_METRICS, 
                ObservatoryMetricsContextProvider()
            )
            
            # Wait for default templates to be initialized
            await asyncio.sleep(0.1)
            
            self.is_initialized = True
            logger.info("Prompt Engineering Framework initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Prompt Engineering Framework initialization failed: {e}")
            return False
    
    async def create_prompt(
        self, 
        prompt_type: PromptType, 
        parameters: Dict[str, Any],
        user_id: Optional[str] = None,
        template_version: Optional[str] = None
    ) -> ConstructedPrompt:
        """Create a prompt for the specified type and parameters."""
        try:
            if not self.is_initialized:
                raise Exception("Prompt Engineering Framework not initialized")
            
            # Get appropriate template
            if template_version:
                template = await self.template_manager.get_template(template_version)
            else:
                templates = await self.template_manager.get_templates_by_type(prompt_type)
                template = templates[0] if templates else None
            
            if not template:
                raise Exception(f"No template found for prompt type: {prompt_type.value}")
            
            # Construct prompt
            constructed = await self.prompt_constructor.construct_prompt(
                template, 
                parameters, 
                user_id
            )
            
            # Update stats
            self.construction_stats[prompt_type.value] = self.construction_stats.get(prompt_type.value, 0) + 1
            
            return constructed
            
        except Exception as e:
            logger.error(f"Failed to create prompt: {e}")
            raise
    
    async def get_framework_status(self) -> Dict[str, Any]:
        """Get comprehensive framework status."""
        try:
            template_count = len(self.template_manager.templates)
            active_templates = sum(1 for t in self.template_manager.templates.values() if t.active)
            
            context_providers = list(self.prompt_constructor.context_providers.keys())
            
            return {
                "initialized": self.is_initialized,
                "templates": {
                    "total": template_count,
                    "active": active_templates,
                    "by_type": {
                        pt.value: len(await self.template_manager.get_templates_by_type(pt))
                        for pt in PromptType
                    }
                },
                "context_providers": [cp.value for cp in context_providers],
                "construction_stats": self.construction_stats,
                "cache_size": len(self.prompt_constructor.construction_cache)
            }
            
        except Exception as e:
            logger.error(f"Failed to get framework status: {e}")
            return {"error": str(e)}
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List[str]:
        """Get Prompt Engineering Framework capabilities."""
        return [
            "template_based_construction",
            "context_injection",
            "prompt_versioning",
            "ab_testing_support",
            "intelligent_caching"
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get Prompt Engineering Framework health status."""
        return {
            "status": "healthy" if self.is_initialized else "initializing",
            "templates": len(self.template_manager.templates),
            "context_providers": len(self.prompt_constructor.context_providers),
            "constructions": sum(self.construction_stats.values())
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get Prompt Engineering Framework module information."""
        return {
            "module_id": self.module_id,
            "name": "Prompt Engineering Framework",
            "version": "1.0.0",
            "description": "Template-based prompt construction with context injection and versioning"
        }
    
    def graceful_degradation(self) -> Dict[str, Any]:
        """Perform graceful degradation to basic functionality."""
        try:
            degradation_actions = []
            
            # Clear construction cache to save memory
            if self.prompt_constructor.construction_cache:
                cache_size = len(self.prompt_constructor.construction_cache)
                self.prompt_constructor.construction_cache.clear()
                degradation_actions.append(f"Cleared {cache_size} cached prompts")
            
            # Disable optional context providers
            optional_contexts = [ContextType.ENGAGEMENT_HISTORY, ContextType.PERFORMANCE_DATA]
            removed_providers = []
            for context_type in optional_contexts:
                if context_type in self.prompt_constructor.context_providers:
                    del self.prompt_constructor.context_providers[context_type]
                    removed_providers.append(context_type.value)
            
            if removed_providers:
                degradation_actions.append(f"Disabled optional context providers: {removed_providers}")
            
            # Keep only essential templates
            essential_types = [PromptType.ATTENTION_PRIORITIZATION, PromptType.GENERAL]
            templates_to_remove = []
            for template_id, template in self.template_manager.templates.items():
                if template.prompt_type not in essential_types:
                    templates_to_remove.append(template_id)
            
            for template_id in templates_to_remove:
                del self.template_manager.templates[template_id]
            
            if templates_to_remove:
                degradation_actions.append(f"Removed {len(templates_to_remove)} non-essential templates")
            
            return {
                "status": "degraded",
                "actions_taken": degradation_actions,
                "active_templates": len(self.template_manager.templates),
                "active_providers": len(self.prompt_constructor.context_providers),
                "functionality_level": "essential_prompts_only",
                "recovery_possible": True
            }
        except Exception as e:
            return {
                "status": "degradation_failed",
                "error": str(e),
                "functionality_level": "unknown",
                "recovery_possible": False
            }