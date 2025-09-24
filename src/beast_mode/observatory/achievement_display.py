"""
Achievement Display and Notification System

This module provides comprehensive display and notification capabilities for
the achievement tracking system, including progress visualization, leaderboards,
and real-time notifications.
"""

import asyncio
import json
import logging
import time
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, asdict

from .achievement_models import (
    AchievementDefinition,
    AchievementProgress,
    UnlockedAchievement,
    ParticipantProfile,
    AchievementRarity,
    AchievementCategory,
    CelebrationLevel
)


@dataclass
class NotificationConfig:
    """Configuration for achievement notifications."""
    notification_id: str
    enabled: bool = True
    show_progress: bool = True
    show_celebrations: bool = True
    auto_dismiss_ms: int = 5000
    sound_enabled: bool = True
    visual_style: str = "modern"  # modern, classic, minimal
    position: str = "top-right"  # top-left, top-right, bottom-left, bottom-right, center


@dataclass
class DisplayTheme:
    """Theme configuration for achievement displays."""
    theme_id: str
    name: str
    primary_color: str = "#4CAF50"
    secondary_color: str = "#FFC107"
    background_color: str = "#FFFFFF"
    text_color: str = "#333333"
    accent_color: str = "#FF5722"
    border_radius: int = 8
    shadow_enabled: bool = True
    animation_style: str = "smooth"  # smooth, bouncy, fade, slide


@dataclass
class ProgressVisualization:
    """Configuration for progress visualization."""
    viz_id: str
    chart_type: str  # bar, circular, line, radial
    show_percentage: bool = True
    show_milestones: bool = True
    color_gradient: bool = True
    animated: bool = True
    update_interval_ms: int = 500


class AchievementDisplay:
    """
    Comprehensive achievement display and notification system.

    Provides rich UI components for displaying achievement progress, unlocks,
    leaderboards, and real-time notifications with customizable themes and layouts.
    """

    def __init__(self,
                 achievement_tracker,
                 websocket_manager=None,
                 frontend_integration=None):
        self.achievement_tracker = achievement_tracker
        self.websocket_manager = websocket_manager
        self.frontend_integration = frontend_integration
        self.instance_id = f"display_{uuid.uuid4().hex[:8]}"
        self._logger = logging.getLogger(f"{__name__}.AchievementDisplay")

        # Display configuration
        self.notification_configs: Dict[str, NotificationConfig] = {}
        self.display_themes: Dict[str, DisplayTheme] = {}
        self.progress_visualizations: Dict[str, ProgressVisualization] = {}

        # Active notifications and displays
        self.active_notifications: List[Dict[str, Any]] = []
        self.display_subscribers: Dict[str, List[Callable]] = defaultdict(list)

        # Performance tracking
        self._notifications_sent = 0
        self._display_updates_sent = 0
        self._start_time = datetime.now()

        # Initialize defaults
        self._initialize_default_themes()
        self._initialize_default_configs()

        # Register with achievement tracker
        self.achievement_tracker.add_achievement_unlock_handler(self._handle_achievement_unlock)
        self.achievement_tracker.add_milestone_handler(self._handle_milestone_reached)
        self.achievement_tracker.add_celebration_handler(self._handle_celebration_event)

        self._logger.info(
            f"AchievementDisplay initialized",
            extra={
                "instance_id": self.instance_id,
                "themes": len(self.display_themes),
                "websocket_available": self.websocket_manager is not None
            }
        )

    def _initialize_default_themes(self):
        """Initialize default display themes."""

        # Modern theme
        self.register_theme(DisplayTheme(
            theme_id="modern",
            name="Modern",
            primary_color="#2196F3",
            secondary_color="#FFC107",
            background_color="#FFFFFF",
            text_color="#212121",
            accent_color="#FF5722",
            border_radius=12,
            shadow_enabled=True,
            animation_style="smooth"
        ))

        # Dark theme
        self.register_theme(DisplayTheme(
            theme_id="dark",
            name="Dark Mode",
            primary_color="#BB86FC",
            secondary_color="#03DAC6",
            background_color="#121212",
            text_color="#FFFFFF",
            accent_color="#CF6679",
            border_radius=8,
            shadow_enabled=True,
            animation_style="smooth"
        ))

        # Gaming theme
        self.register_theme(DisplayTheme(
            theme_id="gaming",
            name="Gaming",
            primary_color="#00FF41",
            secondary_color="#FFD700",
            background_color="#0D1B2A",
            text_color="#00FF41",
            accent_color="#FF6B35",
            border_radius=0,
            shadow_enabled=False,
            animation_style="bouncy"
        ))

        # Minimal theme
        self.register_theme(DisplayTheme(
            theme_id="minimal",
            name="Minimal",
            primary_color="#666666",
            secondary_color="#999999",
            background_color="#F8F9FA",
            text_color="#333333",
            accent_color="#007BFF",
            border_radius=4,
            shadow_enabled=False,
            animation_style="fade"
        ))

    def _initialize_default_configs(self):
        """Initialize default notification configurations."""

        # Default notification config
        self.register_notification_config(NotificationConfig(
            notification_id="default",
            enabled=True,
            show_progress=True,
            show_celebrations=True,
            auto_dismiss_ms=5000,
            sound_enabled=True,
            visual_style="modern",
            position="top-right"
        ))

        # Minimal notifications
        self.register_notification_config(NotificationConfig(
            notification_id="minimal",
            enabled=True,
            show_progress=False,
            show_celebrations=False,
            auto_dismiss_ms=3000,
            sound_enabled=False,
            visual_style="minimal",
            position="bottom-right"
        ))

        # Gaming style notifications
        self.register_notification_config(NotificationConfig(
            notification_id="gaming",
            enabled=True,
            show_progress=True,
            show_celebrations=True,
            auto_dismiss_ms=7000,
            sound_enabled=True,
            visual_style="gaming",
            position="center"
        ))

    def register_theme(self, theme: DisplayTheme):
        """Register a display theme."""
        self.display_themes[theme.theme_id] = theme
        self._logger.debug(f"Registered display theme: {theme.name}")

    def register_notification_config(self, config: NotificationConfig):
        """Register a notification configuration."""
        self.notification_configs[config.notification_id] = config
        self._logger.debug(f"Registered notification config: {config.notification_id}")

    async def _handle_achievement_unlock(self, participant_id: str, achievement: AchievementDefinition, unlock_record: UnlockedAchievement):
        """Handle achievement unlock notifications."""
        try:
            notification_data = {
                "type": "achievement_unlock",
                "participant_id": participant_id,
                "achievement": {
                    "id": achievement.id,
                    "name": achievement.name,
                    "description": achievement.description,
                    "rarity": achievement.rarity.value,
                    "category": achievement.category.name,
                    "points": achievement.points,
                    "icon": achievement.icon,
                    "unlock_message": achievement.unlock_message
                },
                "unlock_timestamp": unlock_record.unlocked_at.isoformat(),
                "points_awarded": unlock_record.points_awarded,
                "celebration_level": achievement.celebration_level.value
            }

            await self._send_notification(notification_data)

            # Update displays
            await self._update_participant_displays(participant_id)
            await self._update_leaderboard_displays()

        except Exception as e:
            self._logger.error(f"Error handling achievement unlock notification: {e}")

    async def _handle_milestone_reached(self, participant_id: str, milestone_def, event):
        """Handle milestone reached notifications."""
        try:
            notification_data = {
                "type": "milestone_reached",
                "participant_id": participant_id,
                "milestone": {
                    "id": milestone_def.milestone_id,
                    "name": milestone_def.name,
                    "description": milestone_def.description,
                    "threshold_value": milestone_def.threshold_value,
                    "metric_name": milestone_def.metric_name
                },
                "timestamp": datetime.now().isoformat(),
                "event_context": event.context if hasattr(event, 'context') else {}
            }

            await self._send_notification(notification_data)

        except Exception as e:
            self._logger.error(f"Error handling milestone notification: {e}")

    async def _handle_celebration_event(self, celebration_data):
        """Handle celebration event notifications."""
        try:
            notification_data = {
                "type": "celebration",
                "celebration_data": celebration_data,
                "timestamp": datetime.now().isoformat()
            }

            await self._send_notification(notification_data)

        except Exception as e:
            self._logger.error(f"Error handling celebration notification: {e}")

    async def _send_notification(self, notification_data: Dict[str, Any]):
        """Send notification to all connected clients."""
        try:
            # Add notification ID and metadata
            notification_data.update({
                "notification_id": str(uuid.uuid4()),
                "sent_at": datetime.now().isoformat(),
                "display_config": self.notification_configs.get("default", {})
            })

            # Add to active notifications
            self.active_notifications.append(notification_data)

            # Send via websocket
            if self.websocket_manager:
                message = {
                    "type": "achievement_notification",
                    "data": notification_data
                }
                await self.websocket_manager.broadcast_message(json.dumps(message))

            # Send to frontend integration
            if self.frontend_integration:
                await self.frontend_integration.show_notification(notification_data)

            self._notifications_sent += 1

            self._logger.debug(
                f"Sent notification",
                extra={
                    "notification_type": notification_data["type"],
                    "notification_id": notification_data["notification_id"]
                }
            )

        except Exception as e:
            self._logger.error(f"Error sending notification: {e}")

    async def get_participant_dashboard(self, participant_id: str, theme_id: str = "modern") -> Dict[str, Any]:
        """Generate comprehensive participant dashboard data."""
        try:
            # Get participant stats
            stats = self.achievement_tracker.get_participant_stats(participant_id)
            if not stats:
                return {"error": "Participant not found"}

            profile = stats["profile"]
            theme = self.display_themes.get(theme_id, self.display_themes["modern"])

            # Get achievement progress
            progress_data = await self._get_achievement_progress_data(participant_id)

            # Get recent activity
            recent_activity = await self._get_recent_activity(participant_id, limit=10)

            # Generate dashboard
            dashboard = {
                "participant_id": participant_id,
                "theme": asdict(theme),
                "profile_summary": {
                    "name": profile.name or f"Participant {participant_id}",
                    "total_points": profile.total_points,
                    "current_level": profile.current_level,
                    "achievements_count": len(profile.achievements_unlocked),
                    "coordination_score": profile.coordination_score,
                    "systematic_practice_score": profile.systematic_practice_score,
                    "collaboration_score": profile.collaboration_score,
                    "joined_at": profile.joined_at.isoformat() if profile.joined_at else None,
                    "last_active": profile.last_active_at.isoformat() if profile.last_active_at else None
                },
                "achievement_progress": progress_data,
                "recent_achievements": stats["recent_achievements"],
                "achievements_by_category": stats["achievements_by_category"],
                "achievements_by_rarity": stats["achievements_by_rarity"],
                "recent_activity": recent_activity,
                "next_level_progress": self._calculate_next_level_progress(profile.total_points),
                "generated_at": datetime.now().isoformat()
            }

            return dashboard

        except Exception as e:
            self._logger.error(f"Error generating participant dashboard: {e}")
            return {"error": str(e)}

    async def _get_achievement_progress_data(self, participant_id: str) -> List[Dict[str, Any]]:
        """Get detailed achievement progress data for display."""
        progress_data = []

        participant_progress = self.achievement_tracker.participant_progress.get(participant_id, {})

        for achievement_id, progress in participant_progress.items():
            achievement_def = self.achievement_tracker.achievement_definitions.get(achievement_id)
            if not achievement_def:
                continue

            progress_item = {
                "achievement_id": achievement_id,
                "name": achievement_def.name,
                "description": achievement_def.description,
                "category": achievement_def.category.name,
                "rarity": achievement_def.rarity.value,
                "points": achievement_def.points,
                "icon": achievement_def.icon,
                "progress_percentage": progress.progress_percentage,
                "is_completed": progress.is_completed,
                "current_progress": progress.current_progress,
                "first_progress_at": progress.first_progress_at.isoformat() if progress.first_progress_at else None,
                "last_updated_at": progress.last_updated_at.isoformat() if progress.last_updated_at else None,
                "requirements": achievement_def.requirements,
                "unlock_message": achievement_def.unlock_message
            }

            # Add completion info if completed
            if progress.is_completed and progress.completion_times:
                progress_item["completed_at"] = progress.completion_times[-1].isoformat()

            progress_data.append(progress_item)

        # Sort by progress percentage (descending) and then by points
        progress_data.sort(key=lambda x: (x["progress_percentage"], x["points"]), reverse=True)

        return progress_data

    async def _get_recent_activity(self, participant_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent coordination activity for participant."""
        recent_events = []

        # Get recent coordination events from tracker
        for event in reversed(self.achievement_tracker.coordination_events):
            if event.participant_id == participant_id:
                recent_events.append({
                    "event_id": event.event_id,
                    "event_type": event.event_type,
                    "timestamp": event.timestamp.isoformat(),
                    "coordination_quality": event.coordination_quality,
                    "systematic_score": event.systematic_score,
                    "collaboration_score": event.collaboration_score,
                    "context": event.context
                })

                if len(recent_events) >= limit:
                    break

        return recent_events

    def _calculate_next_level_progress(self, total_points: int) -> Dict[str, Any]:
        """Calculate progress toward next level."""
        current_level = self.achievement_tracker._calculate_level(total_points)
        next_level = current_level + 1

        # Calculate points needed for next level
        # Using same formula as in achievement_tracker: level = floor(sqrt(points / 100))
        # So points = (level^2) * 100
        next_level_points = (next_level ** 2) * 100
        current_level_points = (current_level ** 2) * 100

        points_for_next_level = next_level_points - total_points
        points_in_current_level = total_points - current_level_points
        points_needed_for_level = next_level_points - current_level_points

        progress_percentage = (points_in_current_level / points_needed_for_level) * 100 if points_needed_for_level > 0 else 0

        return {
            "current_level": current_level,
            "next_level": next_level,
            "current_points": total_points,
            "points_for_next_level": points_for_next_level,
            "progress_percentage": min(100.0, progress_percentage)
        }

    async def get_leaderboard(self,
                            category: Optional[str] = None,
                            time_period: str = "all_time",
                            limit: int = 10,
                            theme_id: str = "modern") -> Dict[str, Any]:
        """Generate leaderboard display data."""
        try:
            # Get base leaderboard data
            leaderboard_data = self.achievement_tracker.get_leaderboard(limit=limit * 2)  # Get more for filtering

            theme = self.display_themes.get(theme_id, self.display_themes["modern"])

            # Filter by category if specified
            if category:
                filtered_data = []
                for participant in leaderboard_data:
                    participant_id = participant["participant_id"]
                    unlocked = self.achievement_tracker.unlocked_achievements.get(participant_id, [])

                    category_achievements = 0
                    for unlock in unlocked:
                        achievement_def = self.achievement_tracker.achievement_definitions.get(unlock.achievement_id)
                        if achievement_def and achievement_def.category.name == category:
                            category_achievements += 1

                    if category_achievements > 0:
                        participant["category_achievements"] = category_achievements
                        filtered_data.append(participant)

                # Re-sort by category achievements
                filtered_data.sort(key=lambda x: x["category_achievements"], reverse=True)
                leaderboard_data = filtered_data[:limit]

            # Apply time period filtering for recent achievements
            if time_period != "all_time":
                time_periods = {
                    "today": 1,
                    "week": 7,
                    "month": 30
                }

                days = time_periods.get(time_period, 7)
                cutoff_date = datetime.now() - timedelta(days=days)

                # Filter and re-score based on recent activity
                recent_leaderboard = []
                for participant in leaderboard_data:
                    participant_id = participant["participant_id"]
                    unlocked = self.achievement_tracker.unlocked_achievements.get(participant_id, [])

                    recent_points = sum(
                        unlock.points_awarded for unlock in unlocked
                        if unlock.unlocked_at >= cutoff_date
                    )

                    if recent_points > 0:
                        participant = participant.copy()
                        participant["recent_points"] = recent_points
                        recent_leaderboard.append(participant)

                recent_leaderboard.sort(key=lambda x: x["recent_points"], reverse=True)
                leaderboard_data = recent_leaderboard[:limit]

            # Enhance with additional display data
            enhanced_leaderboard = []
            for rank, participant in enumerate(leaderboard_data, 1):
                participant_id = participant["participant_id"]

                # Get recent achievement for participant
                unlocked = self.achievement_tracker.unlocked_achievements.get(participant_id, [])
                recent_achievement = None
                if unlocked:
                    latest_unlock = max(unlocked, key=lambda x: x.unlocked_at)
                    achievement_def = self.achievement_tracker.achievement_definitions.get(latest_unlock.achievement_id)
                    if achievement_def:
                        recent_achievement = {
                            "name": achievement_def.name,
                            "rarity": achievement_def.rarity.value,
                            "unlocked_at": latest_unlock.unlocked_at.isoformat()
                        }

                enhanced_participant = {
                    "rank": rank,
                    "participant_id": participant_id,
                    "name": participant.get("name") or f"Participant {participant_id}",
                    "total_points": participant["total_points"],
                    "current_level": participant["current_level"],
                    "achievements_count": participant["achievements_count"],
                    "coordination_score": participant["coordination_score"],
                    "recent_achievement": recent_achievement,
                    "recent_points": participant.get("recent_points", 0)
                }

                enhanced_leaderboard.append(enhanced_participant)

            return {
                "leaderboard": enhanced_leaderboard,
                "category": category,
                "time_period": time_period,
                "total_participants": len(self.achievement_tracker.participant_profiles),
                "theme": asdict(theme),
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            self._logger.error(f"Error generating leaderboard: {e}")
            return {"error": str(e)}

    async def get_achievement_gallery(self,
                                    category: Optional[str] = None,
                                    rarity: Optional[str] = None,
                                    theme_id: str = "modern") -> Dict[str, Any]:
        """Generate achievement gallery display data."""
        try:
            theme = self.display_themes.get(theme_id, self.display_themes["modern"])

            # Get all achievement definitions
            achievements = list(self.achievement_tracker.achievement_definitions.values())

            # Apply filters
            if category:
                achievements = [a for a in achievements if a.category.name == category]

            if rarity:
                achievements = [a for a in achievements if a.rarity.value == rarity]

            # Calculate unlock statistics
            gallery_items = []
            for achievement in achievements:
                # Count how many participants have unlocked this
                unlock_count = 0
                total_participants = len(self.achievement_tracker.participant_profiles)

                for participant_unlocks in self.achievement_tracker.unlocked_achievements.values():
                    if any(unlock.achievement_id == achievement.id for unlock in participant_unlocks):
                        unlock_count += 1

                unlock_rate = (unlock_count / total_participants * 100) if total_participants > 0 else 0

                gallery_item = {
                    "id": achievement.id,
                    "name": achievement.name,
                    "description": achievement.description,
                    "category": achievement.category.name,
                    "rarity": achievement.rarity.value,
                    "points": achievement.points,
                    "icon": achievement.icon,
                    "unlock_message": achievement.unlock_message,
                    "requirements": achievement.requirements,
                    "unlock_count": unlock_count,
                    "unlock_rate_percentage": unlock_rate,
                    "celebration_level": achievement.celebration_level.value,
                    "is_repeatable": achievement.is_repeatable,
                    "prerequisite_achievements": achievement.prerequisite_achievements
                }

                gallery_items.append(gallery_item)

            # Sort by rarity and then by points
            rarity_order = {"legendary": 5, "epic": 4, "rare": 3, "uncommon": 2, "common": 1}
            gallery_items.sort(
                key=lambda x: (rarity_order.get(x["rarity"], 0), x["points"]),
                reverse=True
            )

            return {
                "achievements": gallery_items,
                "filters": {
                    "category": category,
                    "rarity": rarity
                },
                "statistics": {
                    "total_achievements": len(gallery_items),
                    "categories": list(set(item["category"] for item in gallery_items)),
                    "rarities": list(set(item["rarity"] for item in gallery_items))
                },
                "theme": asdict(theme),
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            self._logger.error(f"Error generating achievement gallery: {e}")
            return {"error": str(e)}

    async def _update_participant_displays(self, participant_id: str):
        """Update displays for a specific participant."""
        try:
            # Notify subscribers
            subscribers = self.display_subscribers.get("participant_update", [])
            for callback in subscribers:
                try:
                    await callback(participant_id)
                except Exception as e:
                    self._logger.error(f"Error in display subscriber callback: {e}")

            # Send websocket update
            if self.websocket_manager:
                message = {
                    "type": "participant_display_update",
                    "participant_id": participant_id,
                    "timestamp": datetime.now().isoformat()
                }
                await self.websocket_manager.send_to_participant(participant_id, json.dumps(message))

            self._display_updates_sent += 1

        except Exception as e:
            self._logger.error(f"Error updating participant displays: {e}")

    async def _update_leaderboard_displays(self):
        """Update leaderboard displays."""
        try:
            # Notify subscribers
            subscribers = self.display_subscribers.get("leaderboard_update", [])
            for callback in subscribers:
                try:
                    await callback()
                except Exception as e:
                    self._logger.error(f"Error in leaderboard subscriber callback: {e}")

            # Send websocket update
            if self.websocket_manager:
                message = {
                    "type": "leaderboard_update",
                    "timestamp": datetime.now().isoformat()
                }
                await self.websocket_manager.broadcast_message(json.dumps(message))

            self._display_updates_sent += 1

        except Exception as e:
            self._logger.error(f"Error updating leaderboard displays: {e}")

    def subscribe_to_display_updates(self, update_type: str, callback: Callable):
        """Subscribe to display update events."""
        self.display_subscribers[update_type].append(callback)
        self._logger.debug(f"Added subscriber for {update_type} updates")

    def get_display_stats(self) -> Dict[str, Any]:
        """Get display system statistics."""
        uptime_hours = (datetime.now() - self._start_time).total_seconds() / 3600

        return {
            "instance_id": self.instance_id,
            "notifications_sent": self._notifications_sent,
            "display_updates_sent": self._display_updates_sent,
            "active_notifications": len(self.active_notifications),
            "registered_themes": len(self.display_themes),
            "notification_configs": len(self.notification_configs),
            "display_subscribers": sum(len(subs) for subs in self.display_subscribers.values()),
            "uptime_hours": uptime_hours,
            "notifications_per_hour": self._notifications_sent / uptime_hours if uptime_hours > 0 else 0,
            "websocket_integration": self.websocket_manager is not None,
            "frontend_integration": self.frontend_integration is not None
        }