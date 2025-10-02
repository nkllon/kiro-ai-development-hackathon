"""
Attention Manager - Intelligent Focus Control and Progressive Disclosure
========================================================================

The Attention Manager provides intelligent focus control, event prioritization,
and progressive disclosure for optimal user attention management.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from .interfaces import (
    IAttentionPrioritizer, 
    IFocusController, 
    AttentionPriority,
    EngagementContext
)

logger = logging.getLogger(__name__)


@dataclass
class AttentionEvent:
    """Event requiring user attention."""
    event_id: str
    title: str
    description: str
    priority: AttentionPriority
    timestamp: datetime
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    attention_score: float = 0.0
    expires_at: Optional[datetime] = None


@dataclass
class FocusSession:
    """User focus session tracking."""
    session_id: str
    target: str
    priority: AttentionPriority
    start_time: datetime
    end_time: Optional[datetime] = None
    interruptions: int = 0
    effectiveness_score: float = 0.0


class AttentionPrioritizer(IAttentionPrioritizer):
    """Implementation of event prioritization by importance and urgency."""
    
    def __init__(self):
        self.priority_rules: Dict[str, Dict[str, Any]] = {
            "system_error": {"base_score": 0.9, "urgency_multiplier": 1.5},
            "user_interaction": {"base_score": 0.7, "urgency_multiplier": 1.2},
            "data_anomaly": {"base_score": 0.6, "urgency_multiplier": 1.0},
            "system_notification": {"base_score": 0.4, "urgency_multiplier": 0.8},
            "background_task": {"base_score": 0.2, "urgency_multiplier": 0.5}
        }
        
    async def prioritize_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize events by importance and urgency."""
        try:
            prioritized_events = []
            
            for event in events:
                # Calculate attention score
                attention_score = await self.calculate_attention_score(event)
                
                # Create prioritized event
                prioritized_event = event.copy()
                prioritized_event["attention_score"] = attention_score
                prioritized_event["calculated_priority"] = self._score_to_priority(attention_score)
                
                prioritized_events.append(prioritized_event)
            
            # Sort by attention score (highest first)
            prioritized_events.sort(key=lambda x: x["attention_score"], reverse=True)
            
            logger.info(f"Prioritized {len(prioritized_events)} events")
            return prioritized_events
            
        except Exception as e:
            logger.error(f"Event prioritization failed: {e}")
            return events  # Return original events if prioritization fails
    
    async def calculate_attention_score(self, event: Dict[str, Any]) -> float:
        """Calculate attention score for an event."""
        try:
            event_type = event.get("type", "unknown")
            timestamp = event.get("timestamp", datetime.now())
            
            # Get base score from rules
            rule = self.priority_rules.get(event_type, {"base_score": 0.5, "urgency_multiplier": 1.0})
            base_score = rule["base_score"]
            urgency_multiplier = rule["urgency_multiplier"]
            
            # Calculate time-based urgency
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            time_diff = (datetime.now() - timestamp).total_seconds()
            urgency_factor = max(0.1, 1.0 - (time_diff / 3600))  # Decay over 1 hour
            
            # Calculate final score
            attention_score = base_score * urgency_multiplier * urgency_factor
            
            # Apply additional factors
            if event.get("user_id"):
                attention_score *= 1.2  # User-specific events get boost
            
            if event.get("critical", False):
                attention_score *= 1.5  # Critical events get significant boost
            
            return min(1.0, attention_score)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"Attention score calculation failed: {e}")
            return 0.5  # Default score
    
    async def update_priority_rules(self, rules: Dict[str, Any]) -> bool:
        """Update priority calculation rules."""
        try:
            self.priority_rules.update(rules)
            logger.info(f"Priority rules updated: {len(rules)} rules")
            return True
        except Exception as e:
            logger.error(f"Priority rules update failed: {e}")
            return False
    
    def _score_to_priority(self, score: float) -> AttentionPriority:
        """Convert attention score to priority level."""
        if score >= 0.8:
            return AttentionPriority.CRITICAL
        elif score >= 0.6:
            return AttentionPriority.HIGH
        elif score >= 0.4:
            return AttentionPriority.MEDIUM
        else:
            return AttentionPriority.LOW


class FocusController(IFocusController):
    """Implementation of user attention flow management."""
    
    def __init__(self):
        self.current_focus: Optional[FocusSession] = None
        self.focus_history: List[FocusSession] = []
        self.focus_queue: List[Dict[str, Any]] = []
        
    async def set_focus(self, target: str, priority: AttentionPriority) -> bool:
        """Set user focus to specific target."""
        try:
            # End current focus session if exists
            if self.current_focus and not self.current_focus.end_time:
                await self._end_focus_session()
            
            # Start new focus session
            session_id = f"focus_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.current_focus = FocusSession(
                session_id=session_id,
                target=target,
                priority=priority,
                start_time=datetime.now()
            )
            
            logger.info(f"Focus set to: {target} (priority: {priority.name})")
            return True
            
        except Exception as e:
            logger.error(f"Set focus failed: {e}")
            return False
    
    async def clear_focus(self) -> bool:
        """Clear current focus."""
        try:
            if self.current_focus:
                await self._end_focus_session()
                logger.info("Focus cleared")
                return True
            return False
        except Exception as e:
            logger.error(f"Clear focus failed: {e}")
            return False
    
    async def get_focus_history(self) -> List[Dict[str, Any]]:
        """Get history of focus changes."""
        try:
            history = []
            for session in self.focus_history[-20:]:  # Last 20 sessions
                history.append({
                    "session_id": session.session_id,
                    "target": session.target,
                    "priority": session.priority.name,
                    "start_time": session.start_time.isoformat(),
                    "end_time": session.end_time.isoformat() if session.end_time else None,
                    "duration_seconds": (
                        (session.end_time - session.start_time).total_seconds()
                        if session.end_time else None
                    ),
                    "interruptions": session.interruptions,
                    "effectiveness_score": session.effectiveness_score
                })
            return history
        except Exception as e:
            logger.error(f"Get focus history failed: {e}")
            return []
    
    async def _end_focus_session(self) -> None:
        """End the current focus session."""
        if self.current_focus:
            self.current_focus.end_time = datetime.now()
            self.current_focus.effectiveness_score = await self._calculate_effectiveness()
            self.focus_history.append(self.current_focus)
            self.current_focus = None
    
    async def _calculate_effectiveness(self) -> float:
        """Calculate focus session effectiveness."""
        if not self.current_focus:
            return 0.0
        
        # Simple effectiveness calculation based on duration and interruptions
        duration = (datetime.now() - self.current_focus.start_time).total_seconds()
        interruption_penalty = self.current_focus.interruptions * 0.1
        
        # Effectiveness decreases with interruptions, increases with duration (up to a point)
        base_effectiveness = min(1.0, duration / 1800)  # 30 minutes = 100%
        effectiveness = max(0.0, base_effectiveness - interruption_penalty)
        
        return effectiveness


class AttentionManager(ReflectiveModule):
    """
    Main Attention Manager that provides intelligent focus control
    and progressive disclosure for optimal user attention management.
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "attention_manager"
        
        # Core components
        self.attention_prioritizer = AttentionPrioritizer()
        self.focus_controller = FocusController()
        
        # State management
        self.is_initialized = False
        self.attention_events: List[AttentionEvent] = []
        self.attention_budget = 1.0  # Available attention capacity
        
        logger.info("Attention Manager initialized")
    
    async def initialize(self) -> bool:
        """Initialize the Attention Manager."""
        try:
            # Initialize with default priority rules
            default_rules = {
                "engagement_drop": {"base_score": 0.8, "urgency_multiplier": 1.3},
                "performance_issue": {"base_score": 0.7, "urgency_multiplier": 1.4}
            }
            await self.attention_prioritizer.update_priority_rules(default_rules)
            
            self.is_initialized = True
            logger.info("Attention Manager initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Attention Manager initialization failed: {e}")
            return False
    
    async def process_attention_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process a new attention event."""
        try:
            # Calculate attention score
            attention_score = await self.attention_prioritizer.calculate_attention_score(event)
            
            # Create attention event
            attention_event = AttentionEvent(
                event_id=event.get("id", f"event_{datetime.now().strftime('%H%M%S')}"),
                title=event.get("title", "Attention Event"),
                description=event.get("description", ""),
                priority=self.attention_prioritizer._score_to_priority(attention_score),
                timestamp=datetime.now(),
                source=event.get("source", "unknown"),
                metadata=event.get("metadata", {}),
                attention_score=attention_score
            )
            
            # Add to attention events
            self.attention_events.append(attention_event)
            
            # Manage attention budget
            await self._manage_attention_budget()
            
            # Determine if focus should be set
            if attention_score >= 0.7 and self.attention_budget > 0.3:
                await self.focus_controller.set_focus(
                    attention_event.event_id, 
                    attention_event.priority
                )
            
            return {
                "event_id": attention_event.event_id,
                "attention_score": attention_score,
                "priority": attention_event.priority.name,
                "focus_set": attention_score >= 0.7,
                "attention_budget_remaining": self.attention_budget
            }
            
        except Exception as e:
            logger.error(f"Attention event processing failed: {e}")
            return {"error": str(e)}
    
    async def get_attention_analytics(self) -> Dict[str, Any]:
        """Get attention management analytics."""
        try:
            # Calculate attention metrics
            total_events = len(self.attention_events)
            high_priority_events = len([e for e in self.attention_events if e.priority in [AttentionPriority.HIGH, AttentionPriority.CRITICAL]])
            
            focus_history = await self.focus_controller.get_focus_history()
            avg_focus_duration = 0.0
            if focus_history:
                durations = [h["duration_seconds"] for h in focus_history if h["duration_seconds"]]
                avg_focus_duration = sum(durations) / len(durations) if durations else 0.0
            
            return {
                "total_events": total_events,
                "high_priority_events": high_priority_events,
                "attention_budget": self.attention_budget,
                "current_focus": (
                    {
                        "target": self.focus_controller.current_focus.target,
                        "priority": self.focus_controller.current_focus.priority.name,
                        "duration_seconds": (datetime.now() - self.focus_controller.current_focus.start_time).total_seconds()
                    } if self.focus_controller.current_focus else None
                ),
                "focus_sessions_today": len(focus_history),
                "average_focus_duration": avg_focus_duration,
                "attention_effectiveness": await self._calculate_attention_effectiveness()
            }
            
        except Exception as e:
            logger.error(f"Failed to get attention analytics: {e}")
            return {"error": str(e)}
    
    async def _manage_attention_budget(self) -> None:
        """Manage available attention budget."""
        try:
            # Simple attention budget management
            # Budget decreases with high-priority events, recovers over time
            high_priority_count = len([e for e in self.attention_events[-10:] if e.priority in [AttentionPriority.HIGH, AttentionPriority.CRITICAL]])
            
            # Decrease budget based on recent high-priority events
            budget_decrease = high_priority_count * 0.1
            self.attention_budget = max(0.0, 1.0 - budget_decrease)
            
            # Budget recovery (simplified)
            if high_priority_count == 0:
                self.attention_budget = min(1.0, self.attention_budget + 0.1)
                
        except Exception as e:
            logger.error(f"Attention budget management failed: {e}")
    
    async def _calculate_attention_effectiveness(self) -> float:
        """Calculate overall attention management effectiveness."""
        try:
            focus_history = await self.focus_controller.get_focus_history()
            if not focus_history:
                return 0.5  # Default
            
            # Calculate based on focus session effectiveness
            effectiveness_scores = [h["effectiveness_score"] for h in focus_history[-10:]]
            return sum(effectiveness_scores) / len(effectiveness_scores) if effectiveness_scores else 0.5
            
        except Exception as e:
            logger.error(f"Attention effectiveness calculation failed: {e}")
            return 0.5
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List[str]:
        """Get Attention Manager capabilities."""
        return [
            "event_prioritization",
            "focus_management",
            "attention_budgeting",
            "progressive_disclosure",
            "attention_analytics"
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get Attention Manager health status."""
        return {
            "status": "healthy" if self.is_initialized else "initializing",
            "attention_events": len(self.attention_events),
            "attention_budget": self.attention_budget,
            "current_focus": self.focus_controller.current_focus.target if self.focus_controller.current_focus else None,
            "focus_sessions": len(self.focus_controller.focus_history)
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get Attention Manager module information."""
        return {
            "module_id": self.module_id,
            "name": "Attention Manager",
            "version": "1.0.0",
            "description": "Intelligent focus control and progressive disclosure for optimal attention management"
        }
    
    def graceful_degradation(self) -> Dict[str, Any]:
        """Perform graceful degradation to basic attention management."""
        try:
            degradation_actions = []
            
            # Clear current focus to reduce processing
            if self.focus_controller.current_focus:
                asyncio.create_task(self.focus_controller.clear_focus())
                degradation_actions.append("Cleared current focus")
            
            # Reset attention budget to maximum
            self.attention_budget = 1.0
            degradation_actions.append("Reset attention budget to maximum")
            
            # Clear non-critical attention events
            critical_events = [
                event for event in self.attention_events 
                if event.priority == AttentionPriority.CRITICAL
            ]
            cleared_count = len(self.attention_events) - len(critical_events)
            self.attention_events = critical_events
            degradation_actions.append(f"Cleared {cleared_count} non-critical attention events")
            
            # Simplify priority rules to basic levels
            self.attention_prioritizer.priority_rules = {
                "system_error": {"base_score": 0.9, "urgency_multiplier": 1.0},
                "user_interaction": {"base_score": 0.5, "urgency_multiplier": 1.0},
                "default": {"base_score": 0.3, "urgency_multiplier": 1.0}
            }
            degradation_actions.append("Simplified priority rules")
            
            return {
                "status": "degraded",
                "actions_taken": degradation_actions,
                "active_events": len(self.attention_events),
                "functionality_level": "basic_prioritization_only",
                "recovery_possible": True
            }
        except Exception as e:
            return {
                "status": "degradation_failed",
                "error": str(e),
                "functionality_level": "unknown",
                "recovery_possible": False
            }