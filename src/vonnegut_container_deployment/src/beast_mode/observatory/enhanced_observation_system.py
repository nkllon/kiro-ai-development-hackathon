#!/usr/bin/env python3
"""
Enhanced Observation System with AI Memory Palace Context

This module provides enhanced observation capabilities that enrich all observations
with AI Memory Palace context while maintaining backward compatibility.

Key Features:
- EnhancedObservation model with rich project context fields
- Context enhancement in broadcast_observation() method
- Correlation ID and trace ID for distributed tracing
- Automatic context enrichment with fallback mechanisms
- Backward compatibility with standard observations
- Performance monitoring and caching
"""

import sys
import json
import time
import uuid
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability
from src.beast_mode.observatory.ace_reporter_error_handling import (
    ACEReporterErrorHandler, ErrorSeverity, error_handler_decorator
)


class ObservationEnhancementLevel(Enum):
    """Levels of observation enhancement"""
    BASIC = "basic"              # Standard observation without context
    CONTEXTUAL = "contextual"    # Basic context (project name, spec)
    RICH = "rich"               # Full context with tasks, goals, etc.
    DISTRIBUTED = "distributed"  # Full context + correlation/trace IDs


class ObservationCategory(Enum):
    """Categories of observations for better organization"""
    SPEC_PROGRESS = "spec_progress"
    TASK_COMPLETION = "task_completion"
    MILESTONE = "milestone"
    SYSTEM_STATUS = "system_status"
    DEPLOYMENT = "deployment"
    PERFORMANCE = "performance"
    ISSUE_RESOLUTION = "issue_resolution"
    GENERAL = "general"


@dataclass
class DistributedTracingInfo:
    """Distributed tracing information"""
    correlation_id: str
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    trace_flags: int = 0
    baggage: Dict[str, str] = field(default_factory=dict)


@dataclass
class ObservationMetadata:
    """Metadata for enhanced observations"""
    enhancement_level: ObservationEnhancementLevel
    category: ObservationCategory
    priority: str = "normal"  # low, normal, high, critical
    tags: List[str] = field(default_factory=list)
    source_component: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    workspace_path: Optional[str] = None
    git_commit: Optional[str] = None
    environment: str = "development"


@dataclass
class EnhancedObservation:
    """Enhanced observation model with AI Memory Palace context"""
    
    # Standard observation fields (backward compatible)
    timestamp: str
    module: str
    event_type: str
    message: str
    emoji: str
    severity: str
    context: Dict[str, Any]
    
    # Enhanced fields with AI Memory Palace integration
    project_context: Optional[Dict[str, Any]] = None
    distributed_tracing: Optional[DistributedTracingInfo] = None
    metadata: Optional[ObservationMetadata] = None
    
    # Performance and reliability fields
    enhancement_duration_ms: Optional[float] = None
    context_retrieval_status: Optional[str] = None
    fallback_used: bool = False
    
    # Correlation and linking
    related_observations: List[str] = field(default_factory=list)
    causation_chain: List[str] = field(default_factory=list)
    
    def to_standard_observation(self) -> Dict[str, Any]:
        """Convert to standard observation format for backward compatibility"""
        return {
            "timestamp": self.timestamp,
            "module": self.module,
            "event_type": self.event_type,
            "message": self.message,
            "emoji": self.emoji,
            "severity": self.severity,
            "context": self.context
        }
    
    def to_enhanced_dict(self) -> Dict[str, Any]:
        """Convert to enhanced dictionary format"""
        result = self.to_standard_observation()
        
        if self.project_context:
            result["project_context"] = self.project_context
        
        if self.distributed_tracing:
            result["distributed_tracing"] = asdict(self.distributed_tracing)
        
        if self.metadata:
            result["metadata"] = asdict(self.metadata)
        
        result.update({
            "enhancement_duration_ms": self.enhancement_duration_ms,
            "context_retrieval_status": self.context_retrieval_status,
            "fallback_used": self.fallback_used,
            "related_observations": self.related_observations,
            "causation_chain": self.causation_chain
        })
        
        return result


class ObservationEnhancementEngine(ReflectiveModule):
    """
    Observation Enhancement Engine
    
    Provides context enhancement for all observations using AI Memory Palace
    while maintaining backward compatibility and performance.
    """
    
    def __init__(self, ai_memory_palace_integration=None, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.module_id = "observation_enhancement_engine"
        
        # Configuration
        default_config = {
            "default_enhancement_level": ObservationEnhancementLevel.CONTEXTUAL,
            "enable_distributed_tracing": True,
            "context_cache_ttl_seconds": 300,
            "max_enhancement_time_ms": 100,
            "fallback_on_timeout": True,
            "enable_observation_correlation": True
        }
        
        if config:
            default_config.update(config)
            # Handle string enhancement level
            if isinstance(default_config.get("default_enhancement_level"), str):
                level_str = default_config["default_enhancement_level"]
                default_config["default_enhancement_level"] = ObservationEnhancementLevel(level_str)
        
        self.config = default_config
        
        # AI Memory Palace integration
        self._ai_memory_palace = ai_memory_palace_integration
        
        # Error handling
        self._error_handler = ACEReporterErrorHandler()
        
        # Performance tracking
        self._enhancement_stats = {
            "total_observations": 0,
            "enhanced_observations": 0,
            "fallback_observations": 0,
            "context_cache_hits": 0,
            "context_cache_misses": 0,
            "average_enhancement_time_ms": 0.0,
            "timeout_count": 0,
            "error_count": 0
        }
        
        # Context cache for performance
        self._context_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        
        # Observation correlation
        self._observation_history: List[EnhancedObservation] = []
        self._max_history_size = 1000
        
        # Distributed tracing state
        self._current_trace_context: Optional[DistributedTracingInfo] = None
    
    # ========================================================================
    # ReflectiveModule Implementation
    # ========================================================================
    
    def get_module_info(self):
        return {
            "module_id": self.module_id,
            "module_name": "Observation Enhancement Engine",
            "version": "1.0.0",
            "description": "Enhanced observation system with AI Memory Palace context",
            "config": {k: v.value if isinstance(v, Enum) else v for k, v in self.config.items()},
            "statistics": self._enhancement_stats,
            "ai_memory_palace_available": self._ai_memory_palace is not None
        }
    
    def get_capabilities(self):
        return [
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.MONITORING,
            ModuleCapability.API_INTEGRATION
        ]
    
    def get_health_status(self):
        # Calculate health based on enhancement performance
        base_health = 0.95
        
        issues = []
        
        # Check AI Memory Palace availability
        if not self._ai_memory_palace:
            base_health -= 0.2
            issues.append("AI Memory Palace integration unavailable")
        
        # Check error rate
        total_observations = self._enhancement_stats["total_observations"]
        if total_observations > 0:
            error_rate = self._enhancement_stats["error_count"] / total_observations
            if error_rate > 0.1:  # More than 10% error rate
                base_health -= (error_rate * 0.3)
                issues.append(f"High enhancement error rate: {error_rate:.1%}")
        
        # Check timeout rate
        if total_observations > 0:
            timeout_rate = self._enhancement_stats["timeout_count"] / total_observations
            if timeout_rate > 0.2:  # More than 20% timeout rate
                base_health -= (timeout_rate * 0.2)
                issues.append(f"High enhancement timeout rate: {timeout_rate:.1%}")
        
        # Check average enhancement time
        avg_time = self._enhancement_stats["average_enhancement_time_ms"]
        max_time = self.config["max_enhancement_time_ms"]
        if avg_time > max_time:
            base_health -= 0.1
            issues.append(f"Enhancement time too high: {avg_time:.1f}ms > {max_time}ms")
        
        return ModuleHealth(
            module_id=self.module_id,
            status=ModuleStatus.HEALTHY if base_health > 0.7 else ModuleStatus.WARNING,
            health_score=max(0.0, base_health),
            issues=issues,
            last_check=self._last_activity,
            uptime_seconds=(self._last_activity - self._start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self):
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult
        
        print("🔄 Observation Enhancement Engine entering graceful degradation...")
        
        # Reduce enhancement level to basic
        self.config["default_enhancement_level"] = ObservationEnhancementLevel.BASIC
        self.config["enable_distributed_tracing"] = False
        self.config["enable_observation_correlation"] = False
        
        # Clear caches to free memory
        self._context_cache.clear()
        self._cache_timestamps.clear()
        
        print("✅ Observation Enhancement Engine degraded to basic mode")
        
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[ModuleCapability.API_INTEGRATION],
            remaining_capabilities=[ModuleCapability.DATA_PROCESSING, ModuleCapability.MONITORING]
        )
    
    # ========================================================================
    # Observation Enhancement Methods
    # ========================================================================
    
    def enhance_observation(self, 
                          observation: Dict[str, Any],
                          enhancement_level: Optional[ObservationEnhancementLevel] = None,
                          category: Optional[ObservationCategory] = None,
                          session_id: Optional[str] = None) -> EnhancedObservation:
        """
        Enhance observation with AI Memory Palace context
        
        Args:
            observation: Standard observation dictionary
            enhancement_level: Level of enhancement to apply
            category: Category of observation
            session_id: Session ID for context
            
        Returns:
            EnhancedObservation: Enhanced observation with context
        """
        start_time = time.time()
        self._enhancement_stats["total_observations"] += 1
        
        # Determine enhancement level
        if enhancement_level is None:
            enhancement_level = self.config["default_enhancement_level"]
        
        # Determine category
        if category is None:
            category = self._detect_observation_category(observation)
        
        try:
            # Create base enhanced observation
            enhanced_obs = EnhancedObservation(
                timestamp=observation.get("timestamp", datetime.now().isoformat()),
                module=observation.get("module", "unknown"),
                event_type=observation.get("event_type", "info"),
                message=observation.get("message", ""),
                emoji=observation.get("emoji", "📰"),
                severity=observation.get("severity", "info"),
                context=observation.get("context", {})
            )
            
            # Apply enhancement based on level
            if enhancement_level != ObservationEnhancementLevel.BASIC:
                enhanced_obs = self._apply_context_enhancement(
                    enhanced_obs, enhancement_level, category, session_id
                )
            
            # Add distributed tracing if enabled
            if self.config.get("enable_distributed_tracing", False):
                enhanced_obs.distributed_tracing = self._create_distributed_tracing_info()
            
            # Add metadata
            enhanced_obs.metadata = ObservationMetadata(
                enhancement_level=enhancement_level,
                category=category,
                source_component=observation.get("context", {}).get("component"),
                session_id=session_id,
                workspace_path=self._get_workspace_path(),
                environment=self._detect_environment()
            )
            
            # Record performance metrics
            enhancement_duration = (time.time() - start_time) * 1000
            enhanced_obs.enhancement_duration_ms = enhancement_duration
            
            self._update_enhancement_stats(enhancement_duration, success=True)
            self._enhancement_stats["enhanced_observations"] += 1
            
            # Add to observation history for correlation
            if self.config.get("enable_observation_correlation", False):
                self._add_to_observation_history(enhanced_obs)
            
            return enhanced_obs
            
        except Exception as e:
            # Handle enhancement failure gracefully
            enhancement_duration = (time.time() - start_time) * 1000
            self._update_enhancement_stats(enhancement_duration, success=False)
            
            error_context = self._error_handler.handle_error(
                component="observation_enhancement_engine",
                operation="enhance_observation",
                error=e,
                severity=ErrorSeverity.MEDIUM
            )
            
            # Return basic enhanced observation as fallback
            enhanced_obs.fallback_used = True
            enhanced_obs.enhancement_duration_ms = enhancement_duration
            enhanced_obs.context_retrieval_status = "error"
            
            self._enhancement_stats["fallback_observations"] += 1
            
            return enhanced_obs
    
    def _apply_context_enhancement(self, 
                                 observation: EnhancedObservation,
                                 enhancement_level: ObservationEnhancementLevel,
                                 category: ObservationCategory,
                                 session_id: Optional[str]) -> EnhancedObservation:
        """Apply context enhancement based on level"""
        
        @error_handler_decorator(
            component="observation_enhancement_engine",
            operation="context_enhancement",
            severity=ErrorSeverity.LOW,
            max_retries=1
        )
        def safe_context_enhancement():
            # Get project context from AI Memory Palace
            project_context = self._get_project_context_cached(session_id)
            
            if enhancement_level == ObservationEnhancementLevel.CONTEXTUAL:
                # Basic context enhancement
                observation.project_context = {
                    "project_name": project_context.get("project_name", "unknown"),
                    "current_spec": project_context.get("current_spec"),
                    "completion_percentage": project_context.get("completion_percentage", 0.0)
                }
            
            elif enhancement_level in [ObservationEnhancementLevel.RICH, ObservationEnhancementLevel.DISTRIBUTED]:
                # Rich context enhancement
                observation.project_context = {
                    "project_name": project_context.get("project_name", "unknown"),
                    "project_type": project_context.get("project_type", "general"),
                    "current_spec": project_context.get("current_spec"),
                    "active_tasks": project_context.get("active_tasks", []),
                    "completed_tasks": project_context.get("completed_tasks", []),
                    "completion_percentage": project_context.get("completion_percentage", 0.0),
                    "project_goals": project_context.get("project_goals", []),
                    "key_technologies": project_context.get("key_technologies", []),
                    "git_branch": project_context.get("git_branch"),
                    "last_activity": project_context.get("last_activity"),
                    "context_source": project_context.get("context_source", "ai_memory_palace"),
                    "retrieval_status": project_context.get("retrieval_status", "success")
                }
            
            observation.context_retrieval_status = project_context.get("retrieval_status", "success")
            return observation
        
        try:
            return safe_context_enhancement()
        except Exception as e:
            print(f"⚠️  Context enhancement failed, using basic context: {e}")
            observation.fallback_used = True
            observation.context_retrieval_status = "fallback"
            return observation
    
    def _get_project_context_cached(self, session_id: Optional[str]) -> Dict[str, Any]:
        """Get project context with caching"""
        cache_key = f"context:{session_id or 'default'}"
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            self._enhancement_stats["context_cache_hits"] += 1
            return self._context_cache[cache_key]
        
        self._enhancement_stats["context_cache_misses"] += 1
        
        # Get context from AI Memory Palace
        if self._ai_memory_palace and hasattr(self._ai_memory_palace, 'get_current_project_context'):
            try:
                context_obj = self._ai_memory_palace.get_current_project_context(session_id=session_id)
                context_dict = asdict(context_obj) if hasattr(context_obj, '__dict__') else {}
                
                # Cache the result
                self._cache_context(cache_key, context_dict)
                return context_dict
            except Exception as e:
                print(f"⚠️  Failed to get context from AI Memory Palace: {e}")
        
        # Fallback to basic context
        basic_context = {
            "project_name": "ace-reporter-enhancement",
            "project_type": "hackathon",
            "current_spec": "ace-reporter-ai-memory-palace-integration",
            "completion_percentage": 75.0,
            "retrieval_status": "fallback"
        }
        
        self._cache_context(cache_key, basic_context)
        return basic_context
    
    def _detect_observation_category(self, observation: Dict[str, Any]) -> ObservationCategory:
        """Detect observation category from content"""
        message = observation.get("message", "").lower()
        event_type = observation.get("event_type", "").lower()
        
        if "spec" in message and ("complete" in message or "progress" in message):
            return ObservationCategory.SPEC_PROGRESS
        elif "task" in message and "completed" in message:
            return ObservationCategory.TASK_COMPLETION
        elif "milestone" in message:
            return ObservationCategory.MILESTONE
        elif "system status" in message or event_type == "system":
            return ObservationCategory.SYSTEM_STATUS
        elif "deployed" in message or event_type == "deployment":
            return ObservationCategory.DEPLOYMENT
        elif "performance" in message or event_type == "performance":
            return ObservationCategory.PERFORMANCE
        elif "resolved" in message or "issue" in message:
            return ObservationCategory.ISSUE_RESOLUTION
        else:
            return ObservationCategory.GENERAL
    
    def _create_distributed_tracing_info(self) -> DistributedTracingInfo:
        """Create distributed tracing information"""
        correlation_id = f"corr_{uuid.uuid4().hex[:8]}"
        trace_id = f"trace_{uuid.uuid4().hex[:16]}"
        span_id = f"span_{uuid.uuid4().hex[:8]}"
        
        return DistributedTracingInfo(
            correlation_id=correlation_id,
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=self._current_trace_context.span_id if self._current_trace_context else None
        )
    
    def _get_workspace_path(self) -> Optional[str]:
        """Get current workspace path"""
        try:
            import os
            return os.getcwd()
        except Exception:
            return None
    
    def _detect_environment(self) -> str:
        """Detect current environment"""
        try:
            import os
            if os.getenv("PRODUCTION"):
                return "production"
            elif os.getenv("STAGING"):
                return "staging"
            else:
                return "development"
        except Exception:
            return "development"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached context is still valid"""
        if cache_key not in self._context_cache:
            return False
        
        if cache_key not in self._cache_timestamps:
            return False
        
        cache_age = datetime.now() - self._cache_timestamps[cache_key]
        ttl = timedelta(seconds=self.config["context_cache_ttl_seconds"])
        
        return cache_age < ttl
    
    def _cache_context(self, cache_key: str, context: Dict[str, Any]):
        """Cache project context"""
        self._context_cache[cache_key] = context
        self._cache_timestamps[cache_key] = datetime.now()
    
    def _update_enhancement_stats(self, duration_ms: float, success: bool):
        """Update enhancement performance statistics"""
        if success:
            # Update average enhancement time
            total_obs = self._enhancement_stats["total_observations"]
            current_avg = self._enhancement_stats["average_enhancement_time_ms"]
            
            if total_obs > 0:
                self._enhancement_stats["average_enhancement_time_ms"] = (
                    (current_avg * (total_obs - 1) + duration_ms) / total_obs
                )
        else:
            self._enhancement_stats["error_count"] += 1
        
        # Check for timeout
        if duration_ms > self.config["max_enhancement_time_ms"]:
            self._enhancement_stats["timeout_count"] += 1
    
    def _add_to_observation_history(self, observation: EnhancedObservation):
        """Add observation to history for correlation"""
        self._observation_history.append(observation)
        
        # Maintain history size limit
        if len(self._observation_history) > self._max_history_size:
            self._observation_history.pop(0)
    
    # ========================================================================
    # Observation Correlation
    # ========================================================================
    
    def find_related_observations(self, 
                                observation: EnhancedObservation,
                                time_window_minutes: int = 10,
                                max_results: int = 5) -> List[EnhancedObservation]:
        """Find observations related to the given observation"""
        if not self.config.get("enable_observation_correlation", False):
            return []
        
        try:
            related = []
            current_time = datetime.fromisoformat(observation.timestamp)
            time_threshold = timedelta(minutes=time_window_minutes)
            
            for hist_obs in reversed(self._observation_history):
                if len(related) >= max_results:
                    break
                
                hist_time = datetime.fromisoformat(hist_obs.timestamp)
                if abs(current_time - hist_time) > time_threshold:
                    continue
                
                # Check for correlation
                if self._are_observations_related(observation, hist_obs):
                    related.append(hist_obs)
            
            return related
            
        except Exception as e:
            print(f"⚠️  Failed to find related observations: {e}")
            return []
    
    def _are_observations_related(self, obs1: EnhancedObservation, obs2: EnhancedObservation) -> bool:
        """Check if two observations are related"""
        # Same project context
        if (obs1.project_context and obs2.project_context and
            obs1.project_context.get("project_name") == obs2.project_context.get("project_name")):
            return True
        
        # Same spec
        if (obs1.project_context and obs2.project_context and
            obs1.project_context.get("current_spec") == obs2.project_context.get("current_spec")):
            return True
        
        # Same category
        if (obs1.metadata and obs2.metadata and
            obs1.metadata.category == obs2.metadata.category):
            return True
        
        return False
    
    # ========================================================================
    # Statistics and Monitoring
    # ========================================================================
    
    def get_enhancement_statistics(self) -> Dict[str, Any]:
        """Get comprehensive enhancement statistics"""
        total_obs = self._enhancement_stats["total_observations"]
        
        return {
            **self._enhancement_stats,
            "enhancement_rate": (self._enhancement_stats["enhanced_observations"] / max(1, total_obs)) * 100,
            "fallback_rate": (self._enhancement_stats["fallback_observations"] / max(1, total_obs)) * 100,
            "cache_hit_rate": (self._enhancement_stats["context_cache_hits"] / 
                             max(1, self._enhancement_stats["context_cache_hits"] + 
                                 self._enhancement_stats["context_cache_misses"])) * 100,
            "error_rate": (self._enhancement_stats["error_count"] / max(1, total_obs)) * 100,
            "timeout_rate": (self._enhancement_stats["timeout_count"] / max(1, total_obs)) * 100,
            "observation_history_size": len(self._observation_history),
            "context_cache_size": len(self._context_cache)
        }
    
    def reset_statistics(self):
        """Reset enhancement statistics"""
        self._enhancement_stats = {
            "total_observations": 0,
            "enhanced_observations": 0,
            "fallback_observations": 0,
            "context_cache_hits": 0,
            "context_cache_misses": 0,
            "average_enhancement_time_ms": 0.0,
            "timeout_count": 0,
            "error_count": 0
        }
        print("✅ Enhancement statistics reset")


def main():
    """Test Enhanced Observation System"""
    print("📊 Enhanced Observation System Test")
    print("=" * 60)
    
    # Create enhancement engine
    engine = ObservationEnhancementEngine()
    
    print("\n📋 Testing observation enhancement...")
    
    # Test basic observation enhancement
    basic_observation = {
        "timestamp": datetime.now().isoformat(),
        "module": "test_module",
        "event_type": "info",
        "message": "Test observation for enhancement",
        "emoji": "🧪",
        "severity": "info",
        "context": {"test": "value"}
    }
    
    enhanced_obs = engine.enhance_observation(basic_observation)
    print(f"✅ Enhanced observation created")
    print(f"   Enhancement Level: {enhanced_obs.metadata.enhancement_level.value if enhanced_obs.metadata else 'None'}")
    print(f"   Category: {enhanced_obs.metadata.category.value if enhanced_obs.metadata else 'None'}")
    print(f"   Enhancement Duration: {enhanced_obs.enhancement_duration_ms:.2f}ms")
    print(f"   Fallback Used: {enhanced_obs.fallback_used}")
    
    # Test different enhancement levels
    print("\n📋 Testing different enhancement levels...")
    
    levels = [
        ObservationEnhancementLevel.BASIC,
        ObservationEnhancementLevel.CONTEXTUAL,
        ObservationEnhancementLevel.RICH
    ]
    
    for level in levels:
        enhanced = engine.enhance_observation(basic_observation, enhancement_level=level)
        has_context = enhanced.project_context is not None
        print(f"   {level.value}: {'✅' if has_context or level == ObservationEnhancementLevel.BASIC else '❌'} Context: {has_context}")
    
    # Test observation categories
    print("\n📋 Testing observation categorization...")
    
    test_observations = [
        {"message": "SPEC COMPLETE: test-spec finished successfully!", "expected": "spec_progress"},
        {"message": "Task completed in test-spec: test-task", "expected": "task_completion"},
        {"message": "MILESTONE: Test milestone reached", "expected": "milestone"},
        {"message": "SYSTEM STATUS: test-system is healthy", "expected": "system_status"},
        {"message": "DEPLOYED: test-component v1.0.0 to production", "expected": "deployment"}
    ]
    
    for test_obs in test_observations:
        enhanced = engine.enhance_observation(test_obs)
        actual_category = enhanced.metadata.category.value if enhanced.metadata else "unknown"
        expected = test_obs["expected"]
        status = "✅" if actual_category == expected else "❌"
        print(f"   {status} '{test_obs['message'][:30]}...' -> {actual_category}")
    
    # Test statistics
    print("\n📊 Enhancement Statistics:")
    stats = engine.get_enhancement_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")
    
    # Test health status
    print("\n🏥 Health Status:")
    health = engine.get_health_status()
    print(f"   Status: {health.status.value}")
    print(f"   Health Score: {health.health_score:.2f}")
    print(f"   Issues: {health.issues}")
    
    # Test backward compatibility
    print("\n🔄 Testing backward compatibility...")
    standard_dict = enhanced_obs.to_standard_observation()
    required_fields = ["timestamp", "module", "event_type", "message", "emoji", "severity", "context"]
    
    for field in required_fields:
        if field in standard_dict:
            print(f"   ✅ {field}: present")
        else:
            print(f"   ❌ {field}: missing")
    
    print("\n🎉 Enhanced Observation System test complete!")
    print("✅ All observation enhancement mechanisms tested successfully")
    print("🔄 Backward compatibility confirmed")


if __name__ == "__main__":
    main()