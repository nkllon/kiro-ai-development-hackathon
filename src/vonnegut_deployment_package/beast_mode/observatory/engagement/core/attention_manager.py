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
    IProgressiveDisclosure,
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


class ProgressiveDisclosure(IProgressiveDisclosure):
    """Implementation of progressive information disclosure."""
    
    def __init__(self):
        self.disclosed_information: Dict[str, Dict[str, Any]] = {}
        self.disclosure_rules: Dict[str, Dict[str, Any]] = {
            "default": {
                "max_level": 3,
                "auto_reveal_threshold": 0.7,
                "hide_after_seconds": 300
            }
        }
        
    async def reveal_information(self, information_id: str, level: int) -> Dict[str, Any]:
        """Reveal information at specified detail level."""
        try:
            # Get disclosure rules for this information type
            info_type = information_id.split('_')[0] if '_' in information_id else 'default'
            rules = self.disclosure_rules.get(info_type, self.disclosure_rules['default'])
            
            # Validate level
            max_level = rules.get('max_level', 3)
            level = min(level, max_level)
            
            # Create or update disclosure record
            if information_id not in self.disclosed_information:
                self.disclosed_information[information_id] = {
                    "current_level": 0,
                    "max_level_reached": 0,
                    "reveal_count": 0,
                    "first_revealed": datetime.now(),
                    "last_revealed": datetime.now(),
                    "auto_hide_at": None
                }
            
            disclosure = self.disclosed_information[information_id]
            disclosure["current_level"] = level
            disclosure["max_level_reached"] = max(disclosure["max_level_reached"], level)
            disclosure["reveal_count"] += 1
            disclosure["last_revealed"] = datetime.now()
            
            # Set auto-hide timer if configured
            hide_after = rules.get('hide_after_seconds')
            if hide_after:
                disclosure["auto_hide_at"] = datetime.now() + timedelta(seconds=hide_after)
            
            logger.info(f"Information revealed: {information_id} at level {level}")
            
            return {
                "information_id": information_id,
                "level": level,
                "max_level": max_level,
                "revealed": True,
                "auto_hide_at": disclosure["auto_hide_at"].isoformat() if disclosure["auto_hide_at"] else None
            }
            
        except Exception as e:
            logger.error(f"Information revelation failed: {e}")
            return {"information_id": information_id, "revealed": False, "error": str(e)}
    
    async def hide_information(self, information_id: str) -> bool:
        """Hide previously revealed information."""
        try:
            if information_id in self.disclosed_information:
                self.disclosed_information[information_id]["current_level"] = 0
                self.disclosed_information[information_id]["auto_hide_at"] = None
                logger.info(f"Information hidden: {information_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Information hiding failed: {e}")
            return False
    
    async def get_disclosure_level(self, information_id: str) -> int:
        """Get current disclosure level for information."""
        try:
            if information_id in self.disclosed_information:
                return self.disclosed_information[information_id]["current_level"]
            return 0
        except Exception as e:
            logger.error(f"Get disclosure level failed: {e}")
            return 0
    
    async def set_disclosure_rules(self, rules: Dict[str, Any]) -> bool:
        """Set rules for progressive disclosure."""
        try:
            self.disclosure_rules.update(rules)
            logger.info(f"Disclosure rules updated: {len(rules)} rules")
            return True
        except Exception as e:
            logger.error(f"Disclosure rules update failed: {e}")
            return False
    
    async def cleanup_expired_disclosures(self) -> int:
        """Clean up expired auto-hide disclosures."""
        try:
            now = datetime.now()
            expired_count = 0
            
            for info_id, disclosure in list(self.disclosed_information.items()):
                if disclosure.get("auto_hide_at") and now > disclosure["auto_hide_at"]:
                    await self.hide_information(info_id)
                    expired_count += 1
            
            return expired_count
        except Exception as e:
            logger.error(f"Disclosure cleanup failed: {e}")
            return 0


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
        self.progressive_disclosure = ProgressiveDisclosure()
        
        # State management
        self.is_initialized = False
        self.attention_events: List[AttentionEvent] = []
        self.attention_budget = 1.0  # Available attention capacity
        
        logger.info("Attention Manager initialized")
    
    async def initialize(self, observatory_core=None) -> bool:
        """Initialize the Attention Manager with Observatory integration."""
        try:
            # Store Observatory core reference for event integration
            self.observatory_core = observatory_core
            
            # Initialize with Observatory-specific priority rules
            observatory_priority_rules = {
                "engagement_drop": {"base_score": 0.8, "urgency_multiplier": 1.3},
                "performance_issue": {"base_score": 0.7, "urgency_multiplier": 1.4},
                # Observatory coordination event types
                "TASK_COMPLETED": {"base_score": 0.3, "urgency_multiplier": 0.8},
                "TASK_FAILED": {"base_score": 0.8, "urgency_multiplier": 1.4},
                "QUEUE_HEALTH_CHANGE": {"base_score": 0.6, "urgency_multiplier": 1.2},
                "API_CALL_SUCCESS": {"base_score": 0.2, "urgency_multiplier": 0.6},
                "API_CALL_FAILURE": {"base_score": 0.7, "urgency_multiplier": 1.3},
                "COST_THRESHOLD_REACHED": {"base_score": 0.9, "urgency_multiplier": 1.5},
                "ANOMALY_DETECTED": {"base_score": 0.9, "urgency_multiplier": 1.6},
                "ACHIEVEMENT_UNLOCKED": {"base_score": 0.4, "urgency_multiplier": 0.9},
                "COORDINATION_MILESTONE": {"base_score": 0.5, "urgency_multiplier": 1.0},
                "SYSTEM_HEALTH_CHANGE": {"base_score": 0.8, "urgency_multiplier": 1.4}
            }
            await self.attention_prioritizer.update_priority_rules(observatory_priority_rules)
            
            # Set up Observatory-specific disclosure rules
            observatory_disclosure_rules = {
                "system_alert": {"max_level": 2, "auto_reveal_threshold": 0.8, "hide_after_seconds": 180},
                "user_notification": {"max_level": 3, "auto_reveal_threshold": 0.6, "hide_after_seconds": 300},
                "performance_metric": {"max_level": 4, "auto_reveal_threshold": 0.5, "hide_after_seconds": 600},
                "coordination_event": {"max_level": 3, "auto_reveal_threshold": 0.7, "hide_after_seconds": 240},
                "cost_alert": {"max_level": 2, "auto_reveal_threshold": 0.9, "hide_after_seconds": 120},
                "anomaly_alert": {"max_level": 4, "auto_reveal_threshold": 0.9, "hide_after_seconds": 300}
            }
            await self.progressive_disclosure.set_disclosure_rules(observatory_disclosure_rules)
            
            # Initialize attention budget management for Observatory events
            self.observatory_event_budget = 1.0
            self.event_type_weights = {
                "CRITICAL": 0.4,
                "HIGH": 0.3,
                "MEDIUM": 0.2,
                "LOW": 0.1
            }
            
            self.is_initialized = True
            logger.info("Attention Manager initialization complete with Observatory integration")
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
    
    async def reveal_information(self, information_id: str, level: int = 1) -> Dict[str, Any]:
        """Reveal information with progressive disclosure."""
        return await self.progressive_disclosure.reveal_information(information_id, level)
    
    async def hide_information(self, information_id: str) -> bool:
        """Hide previously revealed information."""
        return await self.progressive_disclosure.hide_information(information_id)
    
    async def get_disclosure_level(self, information_id: str) -> int:
        """Get current disclosure level for information."""
        return await self.progressive_disclosure.get_disclosure_level(information_id)
    
    async def set_disclosure_rules(self, rules: Dict[str, Any]) -> bool:
        """Set rules for progressive disclosure."""
        return await self.progressive_disclosure.set_disclosure_rules(rules)
    
    async def prioritize_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize events by importance and urgency."""
        return await self.attention_prioritizer.prioritize_events(events)
    
    async def set_focus(self, target: str, priority: AttentionPriority) -> bool:
        """Set user focus to specific target."""
        return await self.focus_controller.set_focus(target, priority)
    
    async def clear_focus(self) -> bool:
        """Clear current focus."""
        return await self.focus_controller.clear_focus()
    
    async def get_focus_history(self) -> List[Dict[str, Any]]:
        """Get history of focus changes."""
        return await self.focus_controller.get_focus_history()
    
    async def process_observatory_event(self, coordination_event) -> Dict[str, Any]:
        """Process Observatory coordination events for attention management."""
        try:
            # Convert Observatory coordination event to attention event
            event_data = {
                "id": coordination_event.event_id,
                "type": coordination_event.event_type.name,
                "title": f"{coordination_event.event_type.name.replace('_', ' ').title()}",
                "description": f"Event from {coordination_event.source_component}",
                "timestamp": coordination_event.timestamp.isoformat(),
                "source": coordination_event.source_component,
                "metadata": {
                    "correlation_id": coordination_event.correlation_id,
                    "user_id": coordination_event.user_id,
                    "event_data": coordination_event.event_data
                }
            }
            
            # Add criticality based on event type
            critical_events = ["ANOMALY_DETECTED", "COST_THRESHOLD_REACHED", "SYSTEM_HEALTH_CHANGE", "TASK_FAILED"]
            event_data["critical"] = coordination_event.event_type.name in critical_events
            
            # Process through attention system
            result = await self.process_attention_event(event_data)
            
            # Update Observatory-specific attention budget
            await self._update_observatory_attention_budget(coordination_event.event_type.name)
            
            # Auto-reveal information for high-priority events
            if result.get("attention_score", 0) >= 0.7:
                disclosure_level = 2 if result.get("attention_score", 0) >= 0.9 else 1
                await self.reveal_information(
                    f"coordination_event_{coordination_event.event_id}",
                    disclosure_level
                )
            
            logger.info(f"Processed Observatory event: {coordination_event.event_type.name} with attention score {result.get('attention_score', 0):.2f}")
            
            return {
                **result,
                "observatory_event_id": coordination_event.event_id,
                "event_type": coordination_event.event_type.name,
                "observatory_budget_remaining": self.observatory_event_budget
            }
            
        except Exception as e:
            logger.error(f"Observatory event processing failed: {e}")
            return {"error": str(e), "observatory_event_id": getattr(coordination_event, 'event_id', 'unknown')}
    
    async def get_observatory_event_priorities(self) -> Dict[str, Dict[str, Any]]:
        """Get priority scoring for Observatory coordination event types."""
        try:
            event_priorities = {}
            
            # Get current priority rules
            for event_type, rules in self.attention_prioritizer.priority_rules.items():
                if event_type.isupper():  # Observatory event types are uppercase
                    priority_level = AttentionPriority.LOW
                    if rules["base_score"] >= 0.8:
                        priority_level = AttentionPriority.CRITICAL
                    elif rules["base_score"] >= 0.6:
                        priority_level = AttentionPriority.HIGH
                    elif rules["base_score"] >= 0.4:
                        priority_level = AttentionPriority.MEDIUM
                    
                    event_priorities[event_type] = {
                        "base_score": rules["base_score"],
                        "urgency_multiplier": rules["urgency_multiplier"],
                        "priority_level": priority_level.name,
                        "attention_weight": self.event_type_weights.get(priority_level.name, 0.1),
                        "auto_focus": rules["base_score"] >= 0.7
                    }
            
            return event_priorities
            
        except Exception as e:
            logger.error(f"Failed to get Observatory event priorities: {e}")
            return {}
    
    async def update_observatory_event_priorities(self, priority_updates: Dict[str, Dict[str, Any]]) -> bool:
        """Update priority scoring for specific Observatory event types."""
        try:
            # Validate and apply priority updates
            valid_updates = {}
            for event_type, updates in priority_updates.items():
                if event_type.isupper() and isinstance(updates, dict):
                    if "base_score" in updates and 0.0 <= updates["base_score"] <= 1.0:
                        valid_updates[event_type] = {
                            "base_score": updates["base_score"],
                            "urgency_multiplier": updates.get("urgency_multiplier", 1.0)
                        }
            
            if valid_updates:
                await self.attention_prioritizer.update_priority_rules(valid_updates)
                logger.info(f"Updated Observatory event priorities: {list(valid_updates.keys())}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Observatory event priority update failed: {e}")
            return False
    
    async def _update_observatory_attention_budget(self, event_type: str) -> None:
        """Update attention budget based on Observatory event processing."""
        try:
            # Get event priority level
            rules = self.attention_prioritizer.priority_rules.get(event_type, {"base_score": 0.5})
            base_score = rules["base_score"]
            
            # Calculate budget impact
            if base_score >= 0.8:  # Critical events
                budget_impact = 0.3
            elif base_score >= 0.6:  # High priority events
                budget_impact = 0.2
            elif base_score >= 0.4:  # Medium priority events
                budget_impact = 0.1
            else:  # Low priority events
                budget_impact = 0.05
            
            # Apply budget impact
            self.observatory_event_budget = max(0.0, self.observatory_event_budget - budget_impact)
            
            # Budget recovery over time (simplified)
            if self.observatory_event_budget < 1.0:
                recovery_rate = 0.05  # 5% recovery per event processing cycle
                self.observatory_event_budget = min(1.0, self.observatory_event_budget + recovery_rate)
            
        except Exception as e:
            logger.error(f"Observatory attention budget update failed: {e}")
    
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
            
            # Progressive disclosure metrics
            disclosed_count = len([d for d in self.progressive_disclosure.disclosed_information.values() if d["current_level"] > 0])
            total_disclosures = len(self.progressive_disclosure.disclosed_information)
            
            # Observatory-specific metrics
            observatory_events = len([e for e in self.attention_events if e.source.startswith("observatory") or e.metadata.get("event_data")])
            critical_observatory_events = len([
                e for e in self.attention_events 
                if e.priority == AttentionPriority.CRITICAL and (e.source.startswith("observatory") or e.metadata.get("event_data"))
            ])
            
            return {
                "total_events": total_events,
                "high_priority_events": high_priority_events,
                "attention_budget": self.attention_budget,
                "observatory_attention_budget": getattr(self, 'observatory_event_budget', 1.0),
                "current_focus": (
                    {
                        "target": self.focus_controller.current_focus.target,
                        "priority": self.focus_controller.current_focus.priority.name,
                        "duration_seconds": (datetime.now() - self.focus_controller.current_focus.start_time).total_seconds()
                    } if self.focus_controller.current_focus else None
                ),
                "focus_sessions_today": len(focus_history),
                "average_focus_duration": avg_focus_duration,
                "attention_effectiveness": await self._calculate_attention_effectiveness(),
                "disclosed_information_count": disclosed_count,
                "total_information_items": total_disclosures,
                "observatory_events_processed": observatory_events,
                "critical_observatory_events": critical_observatory_events,
                "observatory_integration_active": hasattr(self, 'observatory_core') and self.observatory_core is not None
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
        capabilities = [
            "event_prioritization",
            "focus_management",
            "attention_budgeting",
            "progressive_disclosure",
            "information_revelation",
            "attention_analytics"
        ]
        
        # Add Observatory-specific capabilities if integrated
        if hasattr(self, 'observatory_core') and self.observatory_core is not None:
            capabilities.extend([
                "observatory_event_processing",
                "coordination_event_prioritization",
                "observatory_attention_budgeting",
                "system_event_focus_control"
            ])
        
        return capabilities
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get Attention Manager health status."""
        disclosed_count = len([d for d in self.progressive_disclosure.disclosed_information.values() if d["current_level"] > 0])
        observatory_events = len([e for e in self.attention_events if e.source.startswith("observatory") or e.metadata.get("event_data")])
        
        health_status = {
            "status": "healthy" if self.is_initialized else "initializing",
            "attention_events": len(self.attention_events),
            "attention_budget": self.attention_budget,
            "current_focus": self.focus_controller.current_focus.target if self.focus_controller.current_focus else None,
            "focus_sessions": len(self.focus_controller.focus_history),
            "disclosed_information": disclosed_count,
            "disclosure_rules": len(self.progressive_disclosure.disclosure_rules)
        }
        
        # Add Observatory-specific health metrics if integrated
        if hasattr(self, 'observatory_core') and self.observatory_core is not None:
            health_status.update({
                "observatory_integration": "active",
                "observatory_events_processed": observatory_events,
                "observatory_attention_budget": getattr(self, 'observatory_event_budget', 1.0),
                "observatory_priority_rules": len([
                    rule for rule in self.attention_prioritizer.priority_rules.keys() 
                    if rule.isupper()
                ])
            })
        else:
            health_status["observatory_integration"] = "inactive"
        
        return health_status
    
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
            
            # Hide all disclosed information to reduce cognitive load
            hidden_count = 0
            for info_id in list(self.progressive_disclosure.disclosed_information.keys()):
                # Synchronously hide information during degradation
                self.progressive_disclosure.disclosed_information.pop(info_id, None)
                hidden_count += 1
            degradation_actions.append(f"Hidden {hidden_count} disclosed information items")
            
            # Simplify priority rules to basic levels
            basic_rules = {
                "system_error": {"base_score": 0.9, "urgency_multiplier": 1.0},
                "user_interaction": {"base_score": 0.5, "urgency_multiplier": 1.0},
                "default": {"base_score": 0.3, "urgency_multiplier": 1.0}
            }
            
            # Keep only critical Observatory event types in degraded mode
            if hasattr(self, 'observatory_core') and self.observatory_core is not None:
                basic_rules.update({
                    "ANOMALY_DETECTED": {"base_score": 0.9, "urgency_multiplier": 1.0},
                    "COST_THRESHOLD_REACHED": {"base_score": 0.9, "urgency_multiplier": 1.0},
                    "SYSTEM_HEALTH_CHANGE": {"base_score": 0.8, "urgency_multiplier": 1.0},
                    "TASK_FAILED": {"base_score": 0.7, "urgency_multiplier": 1.0}
                })
                degradation_actions.append("Simplified priority rules with critical Observatory events only")
            else:
                degradation_actions.append("Simplified priority rules")
            
            self.attention_prioritizer.priority_rules = basic_rules
            
            # Reset Observatory attention budget if integrated
            if hasattr(self, 'observatory_event_budget'):
                self.observatory_event_budget = 1.0
                degradation_actions.append("Reset Observatory attention budget")
            
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