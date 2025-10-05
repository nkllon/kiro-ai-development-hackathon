"""
Achievement Tracking System for Beast Mode Observatory

This module implements the core achievement tracking system that monitors coordination
patterns, detects milestones, and manages the gamification layer for systematic practices.
"""

import asyncio
import logging
import time
import uuid
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set, Callable, Tuple
import json

from .achievement_models import (
    AchievementDefinition,
    AchievementProgress,
    UnlockedAchievement,
    CoordinationEvent,
    AchievementStats,
    CelebrationEffect,
    MilestoneDefinition,
    ParticipantProfile,
    AchievementType,
    AchievementCategory,
    AchievementRarity,
    CelebrationLevel
)


class AchievementTracker:
    """
    Core achievement tracking system for monitoring coordination patterns and milestones.

    Features:
    - Real-time coordination pattern monitoring
    - Achievement detection and unlock system
    - Progress tracking and history
    - Milestone detection for systematic practices
    - Celebration trigger integration
    - Gamification statistics and leaderboards
    """

    def __init__(self, storage_backend=None, emoji_rain_integration=None):
        self.storage_backend = storage_backend
        self.emoji_rain_integration = emoji_rain_integration
        self.instance_id = f"achievement_tracker_{uuid.uuid4().hex[:8]}"
        self._logger = logging.getLogger(f"{__name__}.AchievementTracker")

        # Achievement definitions registry
        self.achievement_definitions: Dict[str, AchievementDefinition] = {}
        self.milestone_definitions: Dict[str, MilestoneDefinition] = {}

        # Runtime tracking state
        self.participant_progress: Dict[str, Dict[str, AchievementProgress]] = defaultdict(dict)
        self.unlocked_achievements: Dict[str, List[UnlockedAchievement]] = defaultdict(list)
        self.participant_profiles: Dict[str, ParticipantProfile] = {}
        self.coordination_events: deque = deque(maxlen=10000)  # Recent events buffer

        # Event handlers
        self.achievement_unlock_handlers: List[Callable] = []
        self.milestone_handlers: List[Callable] = []
        self.celebration_handlers: List[Callable] = []

        # Performance tracking
        self._event_processing_times = deque(maxlen=1000)
        self._total_events_processed = 0
        self._last_stats_update = datetime.now()

        # Initialize with default achievements
        self._initialize_default_achievements()

        self._logger.info(
            f"AchievementTracker initialized",
            extra={
                "instance_id": self.instance_id,
                "default_achievements": len(self.achievement_definitions),
                "default_milestones": len(self.milestone_definitions)
            }
        )

    def _initialize_default_achievements(self):
        """Initialize system with default coordination achievements."""

        # Daily coordination achievements
        self.register_achievement(AchievementDefinition(
            id="daily_coordinator",
            name="Daily Coordinator",
            description="Complete coordinated activities for 5 consecutive days",
            achievement_type=AchievementType.CONSISTENCY,
            category=AchievementCategory.DAILY,
            rarity=AchievementRarity.COMMON,
            celebration_level=CelebrationLevel.NORMAL,
            requirements={
                "consecutive_days": 5,
                "min_coordination_score": 0.7
            },
            rewards={"points": 100, "emoji_burst": "🌟"},
            points=100,
            unlock_message="Consistency is the foundation of great coordination! 🌟",
            is_repeatable=True,
            cooldown_hours=24
        ))

        self.register_achievement(AchievementDefinition(
            id="systematic_practitioner",
            name="Systematic Practitioner",
            description="Demonstrate systematic approach in 10 coordination events",
            achievement_type=AchievementType.SYSTEMATIC_PRACTICE,
            category=AchievementCategory.PERSONAL,
            rarity=AchievementRarity.UNCOMMON,
            celebration_level=CelebrationLevel.ENHANCED,
            requirements={
                "systematic_events": 10,
                "min_systematic_score": 0.8
            },
            rewards={"points": 250, "title": "Systematic Coordinator"},
            points=250,
            unlock_message="Your systematic approach is making coordination effortless! 🔧⚡"
        ))

        self.register_achievement(AchievementDefinition(
            id="collaboration_champion",
            name="Collaboration Champion",
            description="Excel in team coordination activities with high collaboration scores",
            achievement_type=AchievementType.COLLABORATION,
            category=AchievementCategory.TEAM,
            rarity=AchievementRarity.RARE,
            celebration_level=CelebrationLevel.SPECTACULAR,
            requirements={
                "team_events": 20,
                "min_collaboration_score": 0.9,
                "team_size_min": 3
            },
            rewards={"points": 500, "badge": "collaboration_champion"},
            points=500,
            unlock_message="Your collaboration skills inspire everyone around you! 🤝✨"
        ))

        self.register_achievement(AchievementDefinition(
            id="innovation_catalyst",
            name="Innovation Catalyst",
            description="Introduce creative solutions that improve coordination patterns",
            achievement_type=AchievementType.INNOVATION,
            category=AchievementCategory.SYSTEM,
            rarity=AchievementRarity.EPIC,
            celebration_level=CelebrationLevel.SPECTACULAR,
            requirements={
                "innovative_solutions": 5,
                "adoption_rate": 0.75,
                "impact_score": 0.8
            },
            rewards={"points": 1000, "special_effects": "innovation_burst"},
            points=1000,
            unlock_message="Your innovations are transforming how teams coordinate! 💡🚀"
        ))

        self.register_achievement(AchievementDefinition(
            id="coordination_legend",
            name="Coordination Legend",
            description="Achieve mastery across all coordination dimensions",
            achievement_type=AchievementType.COORDINATION_MASTERY,
            category=AchievementCategory.SYSTEM,
            rarity=AchievementRarity.LEGENDARY,
            celebration_level=CelebrationLevel.SPECTACULAR,
            requirements={
                "mastery_score": 0.95,
                "total_events": 100,
                "consistency_days": 30,
                "team_impact": 0.9
            },
            rewards={"points": 2500, "legendary_status": True},
            points=2500,
            prerequisite_achievements=["systematic_practitioner", "collaboration_champion"],
            unlock_message="You have achieved legendary status in coordination mastery! 👑🌟"
        ))

        # Initialize default milestones
        self.register_milestone(MilestoneDefinition(
            milestone_id="weekly_coordination_goal",
            name="Weekly Coordination Goal",
            description="Maintain average coordination score above 0.8 for a week",
            threshold_value=0.8,
            metric_name="coordination_score",
            evaluation_period_days=7,
            celebration_effect=CelebrationEffect(
                effect_id="weekly_goal_celebration",
                effect_type="emoji_burst",
                duration_ms=2000,
                emoji_patterns=["🎯", "⭐", "🏆"]
            )
        ))

        self.register_milestone(MilestoneDefinition(
            milestone_id="systematic_streak",
            name="Systematic Streak",
            description="Achieve systematic practice score above 0.85 for 14 days",
            threshold_value=0.85,
            metric_name="systematic_practice_score",
            evaluation_period_days=14,
            celebration_effect=CelebrationEffect(
                effect_id="systematic_streak_celebration",
                effect_type="rainbow_effect",
                duration_ms=3000,
                emoji_patterns=["🔧", "⚡", "🌈", "✨"]
            )
        ))

    def register_achievement(self, achievement: AchievementDefinition):
        """Register a new achievement definition."""
        self.achievement_definitions[achievement.id] = achievement
        self._logger.info(f"Registered achievement: {achievement.name} ({achievement.id})")

    def register_milestone(self, milestone: MilestoneDefinition):
        """Register a new milestone definition."""
        self.milestone_definitions[milestone.milestone_id] = milestone
        self._logger.info(f"Registered milestone: {milestone.name} ({milestone.milestone_id})")

    async def track_coordination_event(self, event: CoordinationEvent) -> Dict[str, Any]:
        """
        Track a coordination event and check for achievement progress.

        Args:
            event: CoordinationEvent to process

        Returns:
            Dict containing processing results and any triggered achievements
        """
        processing_start = time.time()
        result = {
            "event_processed": True,
            "achievements_unlocked": [],
            "milestones_reached": [],
            "progress_updates": [],
            "celebrations_triggered": []
        }

        try:
            # Store event
            self.coordination_events.append(event)
            self._total_events_processed += 1

            # Initialize participant if needed
            participant_id = event.participant_id
            if participant_id and participant_id not in self.participant_profiles:
                await self._initialize_participant(participant_id)

            # Process achievement progress
            progress_updates = await self._process_achievement_progress(event)
            result["progress_updates"] = progress_updates

            # Check for achievement unlocks
            unlocked_achievements = await self._check_achievement_unlocks(event)
            result["achievements_unlocked"] = unlocked_achievements

            # Check milestones
            milestones_reached = await self._check_milestones(event)
            result["milestones_reached"] = milestones_reached

            # Trigger celebrations
            celebrations = await self._trigger_celebrations(unlocked_achievements, milestones_reached)
            result["celebrations_triggered"] = celebrations

            # Update participant profile
            if participant_id:
                await self._update_participant_profile(participant_id, event)

            processing_time = (time.time() - processing_start) * 1000
            self._event_processing_times.append(processing_time)

            self._logger.debug(
                f"Processed coordination event",
                extra={
                    "event_id": event.event_id,
                    "participant_id": participant_id,
                    "processing_time_ms": processing_time,
                    "achievements_unlocked": len(unlocked_achievements),
                    "milestones_reached": len(milestones_reached)
                }
            )

            return result

        except Exception as e:
            self._logger.error(f"Error processing coordination event {event.event_id}: {e}")
            result["event_processed"] = False
            result["error"] = str(e)
            return result

    async def _initialize_participant(self, participant_id: str):
        """Initialize a new participant profile."""
        profile = ParticipantProfile(
            participant_id=participant_id,
            joined_at=datetime.now(),
            last_active_at=datetime.now()
        )
        self.participant_profiles[participant_id] = profile

        # Initialize progress tracking for all achievements
        for achievement_id in self.achievement_definitions:
            if participant_id not in self.participant_progress:
                self.participant_progress[participant_id] = {}

            self.participant_progress[participant_id][achievement_id] = AchievementProgress(
                achievement_id=achievement_id
            )

        self._logger.info(f"Initialized participant profile: {participant_id}")

    async def _process_achievement_progress(self, event: CoordinationEvent) -> List[Dict[str, Any]]:
        """Process progress updates for all applicable achievements."""
        updates = []
        participant_id = event.participant_id

        if not participant_id:
            return updates

        for achievement_id, achievement_def in self.achievement_definitions.items():
            progress = self.participant_progress[participant_id].get(achievement_id)
            if not progress or progress.is_completed:
                continue

            # Update progress based on event
            progress_update = await self._update_achievement_progress(achievement_def, progress, event)
            if progress_update:
                updates.append(progress_update)

        return updates

    async def _update_achievement_progress(self,
                                        achievement: AchievementDefinition,
                                        progress: AchievementProgress,
                                        event: CoordinationEvent) -> Optional[Dict[str, Any]]:
        """Update progress for a specific achievement."""
        updated = False

        # Initialize progress tracking if first time
        if not progress.first_progress_at:
            progress.first_progress_at = event.timestamp

        # Update based on achievement type
        if achievement.achievement_type == AchievementType.CONSISTENCY:
            updated = await self._update_consistency_progress(achievement, progress, event)
        elif achievement.achievement_type == AchievementType.SYSTEMATIC_PRACTICE:
            updated = await self._update_systematic_progress(achievement, progress, event)
        elif achievement.achievement_type == AchievementType.COLLABORATION:
            updated = await self._update_collaboration_progress(achievement, progress, event)
        elif achievement.achievement_type == AchievementType.COORDINATION_MASTERY:
            updated = await self._update_mastery_progress(achievement, progress, event)
        elif achievement.achievement_type == AchievementType.INNOVATION:
            updated = await self._update_innovation_progress(achievement, progress, event)

        if updated:
            progress.last_updated_at = event.timestamp
            # Calculate progress percentage
            progress.progress_percentage = self._calculate_progress_percentage(achievement, progress)

            return {
                "achievement_id": achievement.id,
                "progress_percentage": progress.progress_percentage,
                "current_progress": dict(progress.current_progress),
                "updated_at": progress.last_updated_at.isoformat()
            }

        return None

    async def _update_consistency_progress(self,
                                        achievement: AchievementDefinition,
                                        progress: AchievementProgress,
                                        event: CoordinationEvent) -> bool:
        """Update progress for consistency-type achievements."""
        required_days = achievement.requirements.get("consecutive_days", 5)
        min_score = achievement.requirements.get("min_coordination_score", 0.7)

        if event.coordination_quality and event.coordination_quality >= min_score:
            # Track daily coordination activities
            event_date = event.timestamp.date()

            if "daily_scores" not in progress.current_progress:
                progress.current_progress["daily_scores"] = {}

            # Update daily score (keep highest for the day)
            date_str = event_date.isoformat()
            current_daily_score = progress.current_progress["daily_scores"].get(date_str, 0.0)
            progress.current_progress["daily_scores"][date_str] = max(current_daily_score, event.coordination_quality)

            # Calculate consecutive days
            progress.current_progress["consecutive_days"] = self._calculate_consecutive_days(
                progress.current_progress["daily_scores"], min_score
            )

            return True

        return False

    async def _update_systematic_progress(self,
                                        achievement: AchievementDefinition,
                                        progress: AchievementProgress,
                                        event: CoordinationEvent) -> bool:
        """Update progress for systematic practice achievements."""
        required_events = achievement.requirements.get("systematic_events", 10)
        min_score = achievement.requirements.get("min_systematic_score", 0.8)

        if event.systematic_score and event.systematic_score >= min_score:
            if "systematic_events" not in progress.current_progress:
                progress.current_progress["systematic_events"] = 0

            progress.current_progress["systematic_events"] += 1
            return True

        return False

    async def _update_collaboration_progress(self,
                                          achievement: AchievementDefinition,
                                          progress: AchievementProgress,
                                          event: CoordinationEvent) -> bool:
        """Update progress for collaboration achievements."""
        required_events = achievement.requirements.get("team_events", 20)
        min_score = achievement.requirements.get("min_collaboration_score", 0.9)
        min_team_size = achievement.requirements.get("team_size_min", 3)

        team_size = event.context.get("team_size", 1)

        if (event.collaboration_score and event.collaboration_score >= min_score and
            team_size >= min_team_size):

            if "team_events" not in progress.current_progress:
                progress.current_progress["team_events"] = 0

            progress.current_progress["team_events"] += 1
            return True

        return False

    async def _update_mastery_progress(self,
                                     achievement: AchievementDefinition,
                                     progress: AchievementProgress,
                                     event: CoordinationEvent) -> bool:
        """Update progress for coordination mastery achievements."""
        # Complex mastery tracking combining multiple metrics
        if not all(score is not None for score in [event.coordination_quality, event.systematic_score, event.collaboration_score]):
            return False

        # Track various mastery metrics
        if "total_events" not in progress.current_progress:
            progress.current_progress["total_events"] = 0
        if "score_sum" not in progress.current_progress:
            progress.current_progress["score_sum"] = 0.0
        if "high_quality_events" not in progress.current_progress:
            progress.current_progress["high_quality_events"] = 0

        progress.current_progress["total_events"] += 1

        # Calculate composite score
        composite_score = (event.coordination_quality + event.systematic_score + event.collaboration_score) / 3
        progress.current_progress["score_sum"] += composite_score

        if composite_score >= 0.9:
            progress.current_progress["high_quality_events"] += 1

        # Calculate average mastery score
        progress.current_progress["mastery_score"] = (
            progress.current_progress["score_sum"] / progress.current_progress["total_events"]
        )

        return True

    async def _update_innovation_progress(self,
                                        achievement: AchievementDefinition,
                                        progress: AchievementProgress,
                                        event: CoordinationEvent) -> bool:
        """Update progress for innovation achievements."""
        # Check if event represents an innovative solution
        is_innovative = event.context.get("innovative_solution", False)
        adoption_rate = event.context.get("adoption_rate", 0.0)
        impact_score = event.context.get("impact_score", 0.0)

        if is_innovative and impact_score > 0:
            if "innovative_solutions" not in progress.current_progress:
                progress.current_progress["innovative_solutions"] = 0
            if "total_adoption_rate" not in progress.current_progress:
                progress.current_progress["total_adoption_rate"] = 0.0
            if "total_impact_score" not in progress.current_progress:
                progress.current_progress["total_impact_score"] = 0.0

            progress.current_progress["innovative_solutions"] += 1
            progress.current_progress["total_adoption_rate"] += adoption_rate
            progress.current_progress["total_impact_score"] += impact_score

            # Calculate averages
            solutions_count = progress.current_progress["innovative_solutions"]
            progress.current_progress["avg_adoption_rate"] = (
                progress.current_progress["total_adoption_rate"] / solutions_count
            )
            progress.current_progress["avg_impact_score"] = (
                progress.current_progress["total_impact_score"] / solutions_count
            )

            return True

        return False

    def _calculate_consecutive_days(self, daily_scores: Dict[str, float], min_score: float) -> int:
        """Calculate consecutive days with minimum coordination score."""
        if not daily_scores:
            return 0

        # Get sorted dates
        sorted_dates = sorted([datetime.fromisoformat(date).date() for date in daily_scores.keys()])

        consecutive_days = 0
        current_streak = 0

        for i, date in enumerate(sorted_dates):
            date_str = date.isoformat()
            score = daily_scores.get(date_str, 0.0)

            if score >= min_score:
                # Check if this date continues the streak
                if i == 0 or (date - sorted_dates[i-1]).days == 1:
                    current_streak += 1
                    consecutive_days = max(consecutive_days, current_streak)
                else:
                    current_streak = 1
            else:
                current_streak = 0

        return consecutive_days

    def _calculate_progress_percentage(self, achievement: AchievementDefinition, progress: AchievementProgress) -> float:
        """Calculate completion percentage for an achievement."""
        if progress.is_completed:
            return 100.0

        reqs = achievement.requirements
        current = progress.current_progress

        if achievement.achievement_type == AchievementType.CONSISTENCY:
            required = reqs.get("consecutive_days", 5)
            actual = current.get("consecutive_days", 0)
            return min(100.0, (actual / required) * 100.0)

        elif achievement.achievement_type == AchievementType.SYSTEMATIC_PRACTICE:
            required = reqs.get("systematic_events", 10)
            actual = current.get("systematic_events", 0)
            return min(100.0, (actual / required) * 100.0)

        elif achievement.achievement_type == AchievementType.COLLABORATION:
            required = reqs.get("team_events", 20)
            actual = current.get("team_events", 0)
            return min(100.0, (actual / required) * 100.0)

        elif achievement.achievement_type == AchievementType.COORDINATION_MASTERY:
            # Complex calculation based on multiple requirements
            mastery_score = current.get("mastery_score", 0.0)
            total_events = current.get("total_events", 0)

            required_score = reqs.get("mastery_score", 0.95)
            required_events = reqs.get("total_events", 100)

            score_progress = (mastery_score / required_score) * 50
            events_progress = (total_events / required_events) * 50

            return min(100.0, score_progress + events_progress)

        elif achievement.achievement_type == AchievementType.INNOVATION:
            required_solutions = reqs.get("innovative_solutions", 5)
            actual_solutions = current.get("innovative_solutions", 0)

            base_progress = (actual_solutions / required_solutions) * 70

            # Additional progress from quality metrics
            adoption_rate = current.get("avg_adoption_rate", 0.0)
            impact_score = current.get("avg_impact_score", 0.0)

            required_adoption = reqs.get("adoption_rate", 0.75)
            required_impact = reqs.get("impact_score", 0.8)

            quality_progress = ((adoption_rate / required_adoption) + (impact_score / required_impact)) * 15

            return min(100.0, base_progress + quality_progress)

        return 0.0

    async def _check_achievement_unlocks(self, event: CoordinationEvent) -> List[Dict[str, Any]]:
        """Check if any achievements should be unlocked."""
        unlocked = []
        participant_id = event.participant_id

        if not participant_id:
            return unlocked

        for achievement_id, achievement_def in self.achievement_definitions.items():
            progress = self.participant_progress[participant_id].get(achievement_id)

            if not progress or progress.is_completed:
                continue

            # Check if achievement can be unlocked now
            if await self._is_achievement_complete(achievement_def, progress, participant_id):
                unlock_record = await self._unlock_achievement(participant_id, achievement_def, event)
                if unlock_record:
                    unlocked.append({
                        "achievement_id": achievement_id,
                        "achievement_name": achievement_def.name,
                        "unlock_message": achievement_def.unlock_message,
                        "points_awarded": achievement_def.points,
                        "rarity": achievement_def.rarity.value,
                        "celebration_level": achievement_def.celebration_level.value
                    })

        return unlocked

    async def _is_achievement_complete(self,
                                     achievement: AchievementDefinition,
                                     progress: AchievementProgress,
                                     participant_id: str) -> bool:
        """Check if achievement requirements are met."""
        current = progress.current_progress
        reqs = achievement.requirements

        # Check prerequisite achievements
        if achievement.prerequisite_achievements:
            participant_unlocked = [ua.achievement_id for ua in self.unlocked_achievements[participant_id]]
            for prereq in achievement.prerequisite_achievements:
                if prereq not in participant_unlocked:
                    return False

        # Check cooldown for repeatable achievements
        if achievement.is_repeatable and achievement.cooldown_hours:
            last_unlock = None
            for unlock in self.unlocked_achievements[participant_id]:
                if unlock.achievement_id == achievement.id:
                    last_unlock = unlock.unlocked_at
                    break

            if last_unlock and (datetime.now() - last_unlock).total_seconds() < achievement.cooldown_hours * 3600:
                return False

        # Check specific requirements based on achievement type
        if achievement.achievement_type == AchievementType.CONSISTENCY:
            required_days = reqs.get("consecutive_days", 5)
            actual_days = current.get("consecutive_days", 0)
            return actual_days >= required_days

        elif achievement.achievement_type == AchievementType.SYSTEMATIC_PRACTICE:
            required_events = reqs.get("systematic_events", 10)
            actual_events = current.get("systematic_events", 0)
            return actual_events >= required_events

        elif achievement.achievement_type == AchievementType.COLLABORATION:
            required_events = reqs.get("team_events", 20)
            actual_events = current.get("team_events", 0)
            return actual_events >= required_events

        elif achievement.achievement_type == AchievementType.COORDINATION_MASTERY:
            mastery_score = current.get("mastery_score", 0.0)
            total_events = current.get("total_events", 0)

            required_score = reqs.get("mastery_score", 0.95)
            required_events = reqs.get("total_events", 100)

            return mastery_score >= required_score and total_events >= required_events

        elif achievement.achievement_type == AchievementType.INNOVATION:
            solutions = current.get("innovative_solutions", 0)
            adoption_rate = current.get("avg_adoption_rate", 0.0)
            impact_score = current.get("avg_impact_score", 0.0)

            required_solutions = reqs.get("innovative_solutions", 5)
            required_adoption = reqs.get("adoption_rate", 0.75)
            required_impact = reqs.get("impact_score", 0.8)

            return (solutions >= required_solutions and
                   adoption_rate >= required_adoption and
                   impact_score >= required_impact)

        return False

    async def _unlock_achievement(self,
                                participant_id: str,
                                achievement: AchievementDefinition,
                                trigger_event: CoordinationEvent) -> Optional[UnlockedAchievement]:
        """Unlock an achievement for a participant."""
        try:
            unlock_record = UnlockedAchievement(
                achievement_id=achievement.id,
                unlocked_at=datetime.now(),
                unlock_context={
                    "trigger_event_id": trigger_event.event_id,
                    "trigger_event_type": trigger_event.event_type,
                    "achievement_rarity": achievement.rarity.value,
                    "points_awarded": achievement.points
                },
                points_awarded=achievement.points
            )

            # Record unlock
            self.unlocked_achievements[participant_id].append(unlock_record)

            # Mark progress as completed
            progress = self.participant_progress[participant_id][achievement.id]
            progress.is_completed = True
            progress.completion_times.append(unlock_record.unlocked_at)

            # Update participant profile
            profile = self.participant_profiles[participant_id]
            profile.total_points += achievement.points
            profile.achievements_unlocked.append(achievement.id)
            profile.current_level = self._calculate_level(profile.total_points)

            # Trigger unlock handlers
            for handler in self.achievement_unlock_handlers:
                try:
                    await handler(participant_id, achievement, unlock_record)
                except Exception as e:
                    self._logger.error(f"Error in achievement unlock handler: {e}")

            self._logger.info(
                f"Achievement unlocked: {achievement.name} for {participant_id}",
                extra={
                    "achievement_id": achievement.id,
                    "participant_id": participant_id,
                    "points_awarded": achievement.points,
                    "rarity": achievement.rarity.value
                }
            )

            return unlock_record

        except Exception as e:
            self._logger.error(f"Error unlocking achievement {achievement.id} for {participant_id}: {e}")
            return None

    async def _check_milestones(self, event: CoordinationEvent) -> List[Dict[str, Any]]:
        """Check if any milestones have been reached."""
        milestones_reached = []
        participant_id = event.participant_id

        if not participant_id:
            return milestones_reached

        for milestone_id, milestone_def in self.milestone_definitions.items():
            if await self._evaluate_milestone(milestone_def, participant_id, event):
                milestones_reached.append({
                    "milestone_id": milestone_id,
                    "milestone_name": milestone_def.name,
                    "threshold_value": milestone_def.threshold_value,
                    "metric_name": milestone_def.metric_name,
                    "celebration_effect": milestone_def.celebration_effect
                })

                # Trigger milestone handlers
                for handler in self.milestone_handlers:
                    try:
                        await handler(participant_id, milestone_def, event)
                    except Exception as e:
                        self._logger.error(f"Error in milestone handler: {e}")

        return milestones_reached

    async def _evaluate_milestone(self,
                                milestone: MilestoneDefinition,
                                participant_id: str,
                                event: CoordinationEvent) -> bool:
        """Evaluate if a milestone threshold has been reached."""
        try:
            # Get participant's recent events for evaluation period
            cutoff_date = datetime.now() - timedelta(days=milestone.evaluation_period_days)

            participant_events = [
                e for e in self.coordination_events
                if (e.participant_id == participant_id and
                    e.timestamp >= cutoff_date)
            ]

            if not participant_events:
                return False

            # Calculate metric based on milestone definition
            if milestone.metric_name == "coordination_score":
                scores = [e.coordination_quality for e in participant_events if e.coordination_quality is not None]
                if scores:
                    avg_score = sum(scores) / len(scores)
                    return avg_score >= milestone.threshold_value

            elif milestone.metric_name == "systematic_practice_score":
                scores = [e.systematic_score for e in participant_events if e.systematic_score is not None]
                if scores:
                    avg_score = sum(scores) / len(scores)
                    return avg_score >= milestone.threshold_value

            elif milestone.metric_name == "collaboration_score":
                scores = [e.collaboration_score for e in participant_events if e.collaboration_score is not None]
                if scores:
                    avg_score = sum(scores) / len(scores)
                    return avg_score >= milestone.threshold_value

            return False

        except Exception as e:
            self._logger.error(f"Error evaluating milestone {milestone.milestone_id}: {e}")
            return False

    async def _trigger_celebrations(self,
                                  unlocked_achievements: List[Dict[str, Any]],
                                  milestones_reached: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Trigger celebration effects for achievements and milestones."""
        celebrations = []

        try:
            # Handle achievement celebrations
            for achievement_data in unlocked_achievements:
                celebration_level = achievement_data.get("celebration_level", "normal")

                celebration_effect = await self._create_achievement_celebration(
                    achievement_data, celebration_level
                )

                if celebration_effect:
                    celebrations.append(celebration_effect)

                    # Trigger emoji rain integration if available
                    if self.emoji_rain_integration:
                        await self._trigger_emoji_rain_celebration(achievement_data, celebration_effect)

            # Handle milestone celebrations
            for milestone_data in milestones_reached:
                celebration_effect = milestone_data.get("celebration_effect")

                if celebration_effect:
                    milestone_celebration = {
                        "type": "milestone_celebration",
                        "milestone_id": milestone_data["milestone_id"],
                        "milestone_name": milestone_data["milestone_name"],
                        "effect": celebration_effect
                    }
                    celebrations.append(milestone_celebration)

                    # Trigger emoji rain for milestones
                    if self.emoji_rain_integration:
                        await self._trigger_milestone_emoji_rain(milestone_data, celebration_effect)

            # Trigger celebration handlers
            for celebration in celebrations:
                for handler in self.celebration_handlers:
                    try:
                        await handler(celebration)
                    except Exception as e:
                        self._logger.error(f"Error in celebration handler: {e}")

            return celebrations

        except Exception as e:
            self._logger.error(f"Error triggering celebrations: {e}")
            return []

    async def _create_achievement_celebration(self,
                                           achievement_data: Dict[str, Any],
                                           celebration_level: str) -> Optional[Dict[str, Any]]:
        """Create celebration effect for an achievement."""
        rarity = achievement_data.get("rarity", "common")

        # Define celebration parameters based on level and rarity
        celebration_configs = {
            "subtle": {"duration_ms": 1500, "intensity": 0.5},
            "normal": {"duration_ms": 2500, "intensity": 0.7},
            "enhanced": {"duration_ms": 3500, "intensity": 0.9},
            "spectacular": {"duration_ms": 5000, "intensity": 1.0}
        }

        rarity_emojis = {
            "common": ["⭐", "🌟"],
            "uncommon": ["⭐", "🌟", "✨"],
            "rare": ["🏆", "🌟", "✨", "💫"],
            "epic": ["🏆", "🎉", "🌟", "✨", "💫", "🎊"],
            "legendary": ["👑", "🏆", "🎉", "🌟", "✨", "💫", "🎊", "🚀"]
        }

        config = celebration_configs.get(celebration_level, celebration_configs["normal"])
        emojis = rarity_emojis.get(rarity, rarity_emojis["common"])

        return {
            "type": "achievement_celebration",
            "achievement_id": achievement_data["achievement_id"],
            "achievement_name": achievement_data["achievement_name"],
            "duration_ms": config["duration_ms"],
            "intensity": config["intensity"],
            "emoji_patterns": emojis,
            "celebration_level": celebration_level,
            "rarity": rarity,
            "unlock_message": achievement_data.get("unlock_message", "Achievement unlocked!")
        }

    async def _trigger_emoji_rain_celebration(self,
                                            achievement_data: Dict[str, Any],
                                            celebration_effect: Dict[str, Any]):
        """Trigger emoji rain integration for achievement celebrations."""
        if not self.emoji_rain_integration:
            return

        try:
            emoji_patterns = celebration_effect.get("emoji_patterns", ["🌟"])
            duration_ms = celebration_effect.get("duration_ms", 2500)
            intensity = celebration_effect.get("intensity", 0.7)

            # Trigger emoji rain with achievement-specific patterns
            await self.emoji_rain_integration.trigger_celebration_rain(
                emoji_patterns=emoji_patterns,
                duration_ms=duration_ms,
                intensity=intensity,
                message=achievement_data.get("unlock_message", "Achievement unlocked!"),
                celebration_type="achievement"
            )

        except Exception as e:
            self._logger.error(f"Error triggering emoji rain for achievement: {e}")

    async def _trigger_milestone_emoji_rain(self,
                                          milestone_data: Dict[str, Any],
                                          celebration_effect):
        """Trigger emoji rain integration for milestone celebrations."""
        if not self.emoji_rain_integration:
            return

        try:
            if hasattr(celebration_effect, 'emoji_patterns'):
                emoji_patterns = celebration_effect.emoji_patterns
                duration_ms = celebration_effect.duration_ms
                intensity = celebration_effect.intensity
            else:
                # Handle dict-like celebration effect
                emoji_patterns = celebration_effect.get("emoji_patterns", ["🎯"])
                duration_ms = celebration_effect.get("duration_ms", 2000)
                intensity = celebration_effect.get("intensity", 0.8)

            await self.emoji_rain_integration.trigger_celebration_rain(
                emoji_patterns=emoji_patterns,
                duration_ms=duration_ms,
                intensity=intensity,
                message=f"Milestone reached: {milestone_data['milestone_name']}!",
                celebration_type="milestone"
            )

        except Exception as e:
            self._logger.error(f"Error triggering emoji rain for milestone: {e}")

    async def _update_participant_profile(self, participant_id: str, event: CoordinationEvent):
        """Update participant profile based on coordination event."""
        profile = self.participant_profiles.get(participant_id)
        if not profile:
            return

        profile.last_active_at = event.timestamp

        # Update coordination scores with exponential moving average
        alpha = 0.1  # Smoothing factor

        if event.coordination_quality is not None:
            if profile.coordination_score == 0.0:
                profile.coordination_score = event.coordination_quality
            else:
                profile.coordination_score = (
                    alpha * event.coordination_quality +
                    (1 - alpha) * profile.coordination_score
                )

        if event.systematic_score is not None:
            if profile.systematic_practice_score == 0.0:
                profile.systematic_practice_score = event.systematic_score
            else:
                profile.systematic_practice_score = (
                    alpha * event.systematic_score +
                    (1 - alpha) * profile.systematic_practice_score
                )

        if event.collaboration_score is not None:
            if profile.collaboration_score == 0.0:
                profile.collaboration_score = event.collaboration_score
            else:
                profile.collaboration_score = (
                    alpha * event.collaboration_score +
                    (1 - alpha) * profile.collaboration_score
                )

    def _calculate_level(self, total_points: int) -> int:
        """Calculate participant level based on total points."""
        # Exponential level progression: level = floor(sqrt(points / 100))
        import math
        return max(1, int(math.sqrt(total_points / 100)))

    # Event Handler Registration
    def add_achievement_unlock_handler(self, handler: Callable):
        """Add handler for achievement unlock events."""
        self.achievement_unlock_handlers.append(handler)

    def add_milestone_handler(self, handler: Callable):
        """Add handler for milestone events."""
        self.milestone_handlers.append(handler)

    def add_celebration_handler(self, handler: Callable):
        """Add handler for celebration events."""
        self.celebration_handlers.append(handler)

    # Query and Statistics Methods
    def get_participant_stats(self, participant_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive statistics for a participant."""
        profile = self.participant_profiles.get(participant_id)
        if not profile:
            return None

        unlocked = self.unlocked_achievements.get(participant_id, [])

        # Calculate achievement breakdown by category and rarity
        achievements_by_category = defaultdict(int)
        achievements_by_rarity = defaultdict(int)

        for unlock in unlocked:
            achievement_def = self.achievement_definitions.get(unlock.achievement_id)
            if achievement_def:
                achievements_by_category[achievement_def.category.name] += 1
                achievements_by_rarity[achievement_def.rarity.value] += 1

        return {
            "participant_id": participant_id,
            "profile": profile,
            "total_achievements": len(unlocked),
            "total_points": profile.total_points,
            "current_level": profile.current_level,
            "coordination_score": profile.coordination_score,
            "systematic_practice_score": profile.systematic_practice_score,
            "collaboration_score": profile.collaboration_score,
            "achievements_by_category": dict(achievements_by_category),
            "achievements_by_rarity": dict(achievements_by_rarity),
            "recent_achievements": [
                {
                    "achievement_id": unlock.achievement_id,
                    "achievement_name": self.achievement_definitions[unlock.achievement_id].name,
                    "unlocked_at": unlock.unlocked_at.isoformat(),
                    "points_awarded": unlock.points_awarded
                }
                for unlock in sorted(unlocked, key=lambda x: x.unlocked_at, reverse=True)[:5]
            ]
        }

    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get leaderboard of top participants."""
        participants = []

        for participant_id, profile in self.participant_profiles.items():
            participants.append({
                "participant_id": participant_id,
                "name": profile.name,
                "total_points": profile.total_points,
                "current_level": profile.current_level,
                "achievements_count": len(profile.achievements_unlocked),
                "coordination_score": profile.coordination_score,
                "systematic_practice_score": profile.systematic_practice_score,
                "collaboration_score": profile.collaboration_score
            })

        # Sort by total points (descending) and return top participants
        return sorted(participants, key=lambda x: x["total_points"], reverse=True)[:limit]

    def get_system_stats(self) -> AchievementStats:
        """Get comprehensive system statistics."""
        total_unlocked = sum(len(unlocks) for unlocks in self.unlocked_achievements.values())

        # Calculate completion rate
        total_possible = len(self.achievement_definitions) * len(self.participant_profiles)
        completion_rate = (total_unlocked / total_possible * 100) if total_possible > 0 else 0.0

        # Get achievements by rarity and category
        achievements_by_rarity = defaultdict(int)
        achievements_by_category = defaultdict(int)

        total_points = 0
        last_achievement = None
        last_unlock_time = None

        for participant_unlocks in self.unlocked_achievements.values():
            for unlock in participant_unlocks:
                total_points += unlock.points_awarded

                achievement_def = self.achievement_definitions.get(unlock.achievement_id)
                if achievement_def:
                    achievements_by_rarity[achievement_def.rarity.value] += 1
                    achievements_by_category[achievement_def.category.name] += 1

                if last_unlock_time is None or unlock.unlocked_at > last_unlock_time:
                    last_unlock_time = unlock.unlocked_at
                    last_achievement = unlock.achievement_id

        return AchievementStats(
            total_achievements_defined=len(self.achievement_definitions),
            total_achievements_unlocked=total_unlocked,
            total_points_earned=total_points,
            completion_rate=completion_rate,
            last_achievement_unlocked=last_achievement,
            last_unlock_timestamp=last_unlock_time,
            achievements_by_rarity=dict(achievements_by_rarity),
            achievements_by_category=dict(achievements_by_category)
        )

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the achievement tracker."""
        avg_processing_time = 0.0
        if self._event_processing_times:
            avg_processing_time = sum(self._event_processing_times) / len(self._event_processing_times)

        return {
            "instance_id": self.instance_id,
            "total_events_processed": self._total_events_processed,
            "average_processing_time_ms": avg_processing_time,
            "achievement_definitions_count": len(self.achievement_definitions),
            "milestone_definitions_count": len(self.milestone_definitions),
            "active_participants": len(self.participant_profiles),
            "events_buffer_size": len(self.coordination_events),
            "uptime_hours": (datetime.now() - self._last_stats_update).total_seconds() / 3600
        }