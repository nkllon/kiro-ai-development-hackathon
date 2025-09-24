"""
Unit tests for Observatory Core Engine.

Tests the central orchestrator functionality for the Beast Mode Coordination Observatory.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch

from src.beast_mode.observatory.core import ObservatoryCoreEngine, ObservatoryInsights
from src.beast_mode.observatory.models import (
    ObservatoryConfig,
    CoordinationEvent,
    CoordinationEventType,
    HealthScore,
)


class TestObservatoryCoreEngine:
    """Test ObservatoryCoreEngine functionality."""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return ObservatoryConfig()
    
    @pytest.fixture
    def observatory(self, config):
        """Create an Observatory instance for testing."""
        return ObservatoryCoreEngine(config)
    
    def test_observatory_initialization(self, observatory, config):
        """Test Observatory initialization."""
        assert observatory.module_id == "observatory_core"
        assert observatory._config == config
        assert observatory._running is False
        assert observatory._tasks == []
    
    @pytest.mark.asyncio
    async def test_start_observatory_success(self, observatory):
        """Test successful Observatory startup."""
        result = await observatory.start_observatory()
        
        assert result is True
        assert observatory._running is True
        assert len(observatory._tasks) > 0
        
        # Clean up
        await observatory.stop_observatory()
    
    @pytest.mark.asyncio
    async def test_start_observatory_already_running(self, observatory):
        """Test starting Observatory when already running."""
        # Start first time
        await observatory.start_observatory()
        
        # Try to start again
        result = await observatory.start_observatory()
        
        assert result is True  # Should succeed but not create duplicate tasks
        
        # Clean up
        await observatory.stop_observatory()
    
    @pytest.mark.asyncio
    async def test_start_observatory_invalid_config(self, config):
        """Test Observatory startup with invalid configuration."""
        config.redis_config.port = -1  # Invalid port
        observatory = ObservatoryCoreEngine(config)
        
        result = await observatory.start_observatory()
        
        assert result is False
        assert observatory._running is False
    
    @pytest.mark.asyncio
    async def test_stop_observatory(self, observatory):
        """Test Observatory shutdown."""
        # Start Observatory
        await observatory.start_observatory()
        assert observatory._running is True
        
        # Stop Observatory
        await observatory.stop_observatory()
        assert observatory._running is False
        assert len(observatory._tasks) == 0
    
    @pytest.mark.asyncio
    async def test_process_coordination_event(self, observatory):
        """Test processing coordination events."""
        event = CoordinationEvent(
            event_type=CoordinationEventType.TASK_COMPLETED,
            source_component="test_component",
            event_data={"task_id": "test-123"}
        )
        
        # Should not raise an exception
        await observatory.process_coordination_event(event)
    
    @pytest.mark.asyncio
    async def test_generate_real_time_insights(self, observatory):
        """Test generating real-time insights."""
        insights = await observatory.generate_real_time_insights()
        
        assert isinstance(insights, ObservatoryInsights)
        assert insights.timestamp is not None
        assert isinstance(insights.coordination_health, HealthScore)
    
    def test_get_health_status(self, observatory):
        """Test getting health status."""
        from src.rm_ddd.core.unified_reflective_module import ModuleHealth, ModuleStatus
        
        health = observatory.get_health_status()
        
        assert isinstance(health, ModuleHealth)
        assert health.module_id == "observatory_core"
        assert health.status == ModuleStatus.ERROR  # Not started yet
        assert health.health_score == 0.0
        assert len(health.issues) > 0
    
    @pytest.mark.asyncio
    async def test_get_health_status_running(self, observatory):
        """Test getting health status when running."""
        from src.rm_ddd.core.unified_reflective_module import ModuleHealth, ModuleStatus
        
        await observatory.start_observatory()
        
        health = observatory.get_health_status()
        
        assert isinstance(health, ModuleHealth)
        assert health.status == ModuleStatus.HEALTHY
        assert health.health_score == 1.0
        assert len(health.issues) == 0
        
        # Clean up
        await observatory.stop_observatory()
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, observatory):
        """Test getting Observatory metrics."""
        metrics = await observatory.get_metrics()
        
        assert isinstance(metrics, dict)
        assert "observatory_uptime_seconds" in metrics
        assert "events_processed_total" in metrics
        assert "insights_generated_total" in metrics
        assert "active_connections" in metrics
        assert "memory_usage_mb" in metrics
    
    def test_get_module_info(self, observatory):
        """Test getting module information."""
        info = observatory.get_module_info()
        
        assert isinstance(info, dict)
        assert info["module_id"] == "observatory_core"
        assert info["name"] == "Beast Mode Coordination Observatory"
        assert "version" in info
        assert "description" in info
        assert "config" in info
        
        config_info = info["config"]
        assert "redis_host" in config_info
        assert "websocket_port" in config_info
        assert "metrics_interval" in config_info
        assert "emoji_rain_enabled" in config_info
    
    @pytest.mark.asyncio
    async def test_monitoring_loop_cancellation(self, observatory):
        """Test that monitoring loop can be cancelled gracefully."""
        # Start Observatory
        await observatory.start_observatory()
        
        # Let it run briefly
        await asyncio.sleep(0.1)
        
        # Stop Observatory (should cancel monitoring loop)
        await observatory.stop_observatory()
        
        # All tasks should be completed or cancelled
        for task in observatory._tasks:
            assert task.done()


class TestObservatoryInsights:
    """Test ObservatoryInsights model."""
    
    def test_insights_creation(self):
        """Test creating Observatory insights."""
        insights = ObservatoryInsights()
        
        assert insights.timestamp is not None
        assert isinstance(insights.coordination_health, HealthScore)
        assert insights.cost_summary is not None
        assert insights.active_anomalies == []
        assert insights.recent_achievements == []
        assert insights.system_recommendations == []