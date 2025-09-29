"""
Unit tests for TunnelDiagnostics module.

Tests comprehensive tunnel connectivity diagnostics including process health,
configuration validation, WebSocket connectivity, edge connectivity, and performance metrics.
"""

import asyncio
import json
import pytest
import tempfile
import yaml
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, mock_open

from src.beast_mode.observatory.tunnel.diagnostics import TunnelDiagnostics


class TestTunnelDiagnostics:
    """Test cases for TunnelDiagnostics class."""
    
    @pytest.fixture
    def diagnostics(self):
        """Create TunnelDiagnostics instance for testing."""
        return TunnelDiagnostics()
    
    @pytest.fixture
    def temp_config_file(self):
        """Create temporary configuration file for testing."""
        config_data = {
            "tunnel": "test-tunnel",
            "ingress": [
                {
                    "hostname": "test.example.com",
                    "service": ""  # Empty string enables WebSocket
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f)
            return f.name
    
    def test_initialization(self, diagnostics):
        """Test TunnelDiagnostics initialization."""
        assert diagnostics.module_id == "tunnel_diagnostics"
        assert diagnostics.config_path == Path("cloudflared-config.yml")
        assert diagnostics._diagnostic_count == 0
        assert diagnostics._successful_diagnostics == 0
        assert diagnostics._failed_diagnostics == 0
    
    def test_initialization_with_custom_config(self):
        """Test initialization with custom config path."""
        custom_path = "/custom/path/config.yml"
        diagnostics = TunnelDiagnostics(custom_path)
        assert diagnostics.config_path == Path(custom_path)
    
    @pytest.mark.asyncio
    async def test_run_comprehensive_diagnostics_success(self, diagnostics, temp_config_file):
        """Test successful comprehensive diagnostics run."""
        diagnostics.config_path = Path(temp_config_file)
        
        with patch.object(diagnostics, '_check_cloudflared_process') as mock_process, \
             patch.object(diagnostics, '_validate_tunnel_config') as mock_config, \
             patch.object(diagnostics, '_test_websocket_connectivity') as mock_websocket, \
             patch.object(diagnostics, '_test_edge_connectivity') as mock_edge, \
             patch.object(diagnostics, '_collect_performance_metrics') as mock_perf:
            
            # Mock successful results
            mock_process.return_value = {"status": "healthy", "is_running": True}
            mock_config.return_value = {"status": "healthy", "websocket_enabled": True}
            mock_websocket.return_value = {"status": "healthy", "websocket_upgrade_successful": True}
            mock_edge.return_value = {"status": "healthy", "connectivity_ratio": 1.0}
            mock_perf.return_value = {"status": "healthy", "memory_usage_percent": 50}
            
            results = await diagnostics.run_comprehensive_diagnostics()
            
            # Verify results structure
            assert "timestamp" in results
            assert "tunnel_id" in results
            assert "diagnostics" in results
            assert "health_assessment" in results
            assert "recommendations" in results
            
            # Verify all diagnostic tests were run
            diagnostics_section = results["diagnostics"]
            assert "process_health" in diagnostics_section
            assert "config_validation" in diagnostics_section
            assert "websocket_connectivity" in diagnostics_section
            assert "edge_connectivity" in diagnostics_section
            assert "performance_metrics" in diagnostics_section
            
            # Verify tracking metrics updated
            assert diagnostics._diagnostic_count == 1
            assert diagnostics._successful_diagnostics == 1
            assert diagnostics._failed_diagnostics == 0
    
    @pytest.mark.asyncio
    async def test_run_comprehensive_diagnostics_failure(self, diagnostics):
        """Test comprehensive diagnostics with failure."""
        with patch.object(diagnostics, '_check_cloudflared_process') as mock_process:
            mock_process.side_effect = Exception("Test error")
            
            results = await diagnostics.run_comprehensive_diagnostics()
            
            # Verify error handling
            assert "error" in results
            assert results["status"] == "failed"
            assert diagnostics._failed_diagnostics == 1
    
    @pytest.mark.asyncio
    async def test_check_cloudflared_process_running(self, diagnostics):
        """Test cloudflared process check when running."""
        with patch('subprocess.run') as mock_run:
            # Mock successful pgrep
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="12345\n67890\n"
            )
            
            result = await diagnostics._check_cloudflared_process()
            
            assert result["status"] == "healthy"
            assert result["is_running"] is True
            assert result["process_count"] == 2
    
    @pytest.mark.asyncio
    async def test_check_cloudflared_process_not_running(self, diagnostics):
        """Test cloudflared process check when not running."""
        with patch('subprocess.run') as mock_run:
            # Mock failed pgrep
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout=""
            )
            
            result = await diagnostics._check_cloudflared_process()
            
            assert result["status"] == "error"
            assert result["is_running"] is False
            assert result["process_count"] == 0
    
    @pytest.mark.asyncio
    async def test_check_cloudflared_process_timeout(self, diagnostics):
        """Test cloudflared process check with timeout."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("pgrep", 10)
            
            result = await diagnostics._check_cloudflared_process()
            
            assert result["status"] == "error"
            assert result["is_running"] is False
            assert "timeout" in result["error"]
    
    @pytest.mark.asyncio
    async def test_validate_tunnel_config_success(self, diagnostics, temp_config_file):
        """Test successful tunnel configuration validation."""
        diagnostics.config_path = Path(temp_config_file)
        
        result = await diagnostics._validate_tunnel_config()
        
        assert result["status"] == "healthy"
        assert result["config_exists"] is True
        assert result["yaml_valid"] is True
        assert result["websocket_enabled"] is True
        assert result["missing_fields"] == []
    
    @pytest.mark.asyncio
    async def test_validate_tunnel_config_missing_file(self, diagnostics):
        """Test tunnel configuration validation with missing file."""
        diagnostics.config_path = Path("/nonexistent/config.yml")
        
        result = await diagnostics._validate_tunnel_config()
        
        assert result["status"] == "error"
        assert result["config_exists"] is False
        assert "not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_validate_tunnel_config_invalid_yaml(self, diagnostics):
        """Test tunnel configuration validation with invalid YAML."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            f.flush()
            diagnostics.config_path = Path(f.name)
        
        result = await diagnostics._validate_tunnel_config()
        
        assert result["status"] == "error"
        assert result["config_exists"] is True
        assert result["yaml_valid"] is False
        assert "YAML parsing error" in result["error"]
    
    def test_check_websocket_config_enabled(self, diagnostics):
        """Test WebSocket configuration check when enabled."""
        config_data = {
            "ingress": [
                {"service": ""},  # Empty string enables WebSocket
                {"service": "websocket://localhost:8080"}
            ]
        }
        
        result = diagnostics._check_websocket_config(config_data)
        assert result is True
    
    def test_check_websocket_config_disabled(self, diagnostics):
        """Test WebSocket configuration check when disabled."""
        config_data = {
            "ingress": [
                {"service": "http://localhost:8080"}
            ]
        }
        
        result = diagnostics._check_websocket_config(config_data)
        assert result is False
    
    def test_check_websocket_config_invalid_structure(self, diagnostics):
        """Test WebSocket configuration check with invalid structure."""
        config_data = {"ingress": "not_a_list"}
        
        result = diagnostics._check_websocket_config(config_data)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_test_websocket_connectivity_success(self, diagnostics):
        """Test WebSocket connectivity test success."""
        result = await diagnostics._test_websocket_connectivity()
        
        assert result["status"] == "healthy"
        assert result["websocket_upgrade_successful"] is True
        assert "latency_ms" in result
        assert result["protocol_version"] == "13"
    
    @pytest.mark.asyncio
    async def test_test_edge_connectivity_success(self, diagnostics):
        """Test edge connectivity test success."""
        with patch('subprocess.run') as mock_run:
            # Mock successful ping
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="PING 1.1.1.1: 56 data bytes\n64 bytes from 1.1.1.1: icmp_seq=0 ttl=57 time=10.123 ms"
            )
            
            result = await diagnostics._test_edge_connectivity()
            
            assert result["status"] == "healthy"
            assert result["connectivity_ratio"] == 1.0
            assert result["reachable_servers"] == 2
            assert result["total_servers"] == 2
            assert "edge_results" in result
    
    @pytest.mark.asyncio
    async def test_test_edge_connectivity_partial_failure(self, diagnostics):
        """Test edge connectivity test with partial failure."""
        with patch('subprocess.run') as mock_run:
            # Mock one successful, one failed ping
            def side_effect(*args, **kwargs):
                if "1.1.1.1" in args[0]:
                    return MagicMock(returncode=0, stdout="success")
                else:
                    return MagicMock(returncode=1, stderr="failed")
            
            mock_run.side_effect = side_effect
            
            result = await diagnostics._test_edge_connectivity()
            
            assert result["status"] == "warning"
            assert result["connectivity_ratio"] == 0.5
            assert result["reachable_servers"] == 1
            assert result["total_servers"] == 2
    
    @pytest.mark.asyncio
    async def test_collect_performance_metrics_success(self, diagnostics):
        """Test performance metrics collection success."""
        with patch('psutil.net_io_counters') as mock_net, \
             patch('psutil.virtual_memory') as mock_mem, \
             patch('psutil.cpu_percent') as mock_cpu:
            
            # Mock system metrics
            mock_net.return_value = MagicMock(bytes_sent=1000, bytes_recv=2000)
            mock_mem.return_value = MagicMock(percent=50.0, available=1024*1024*1024)
            mock_cpu.return_value = 25.0
            
            result = await diagnostics._collect_performance_metrics()
            
            assert result["status"] == "healthy"
            assert result["network_bytes_sent"] == 1000
            assert result["network_bytes_recv"] == 2000
            assert result["memory_usage_percent"] == 50.0
            assert result["memory_available_mb"] == 1024
            assert result["cpu_usage_percent"] == 25.0
    
    @pytest.mark.asyncio
    async def test_collect_performance_metrics_failure(self, diagnostics):
        """Test performance metrics collection failure."""
        with patch('psutil.net_io_counters') as mock_net:
            mock_net.side_effect = Exception("psutil error")
            
            result = await diagnostics._collect_performance_metrics()
            
            assert result["status"] == "warning"
            assert "Performance metrics collection failed" in result["error"]
    
    def test_assess_overall_health_healthy(self, diagnostics):
        """Test overall health assessment when healthy."""
        diagnostics_data = {
            "process_health": {"status": "healthy"},
            "config_validation": {"status": "healthy"},
            "websocket_connectivity": {"status": "healthy"},
            "edge_connectivity": {"status": "healthy"},
            "performance_metrics": {"status": "healthy"}
        }
        
        result = diagnostics._assess_overall_health(diagnostics_data)
        
        assert result["status"] == "healthy"
        assert result["health_score"] == 1.0
        assert result["critical_issues"] == []
        assert result["warnings"] == []
    
    def test_assess_overall_health_warning(self, diagnostics):
        """Test overall health assessment with warnings."""
        diagnostics_data = {
            "process_health": {"status": "healthy"},
            "config_validation": {"status": "warning", "error": "Config warning"},
            "websocket_connectivity": {"status": "healthy"},
            "edge_connectivity": {"status": "healthy"},
            "performance_metrics": {"status": "healthy"}
        }
        
        result = diagnostics._assess_overall_health(diagnostics_data)
        
        assert result["status"] == "warning"
        assert result["health_score"] == 0.7
        assert len(result["warnings"]) == 1
        assert "Config warning" in result["warnings"][0]
    
    def test_assess_overall_health_error(self, diagnostics):
        """Test overall health assessment with errors."""
        diagnostics_data = {
            "process_health": {"status": "error", "error": "Process error"},
            "config_validation": {"status": "healthy"},
            "websocket_connectivity": {"status": "healthy"},
            "edge_connectivity": {"status": "healthy"},
            "performance_metrics": {"status": "healthy"}
        }
        
        result = diagnostics._assess_overall_health(diagnostics_data)
        
        assert result["status"] == "error"
        assert result["health_score"] == 0.0
        assert len(result["critical_issues"]) == 1
        assert "Process error" in result["critical_issues"][0]
    
    def test_generate_recommendations_no_issues(self, diagnostics):
        """Test recommendation generation with no issues."""
        diagnostics_data = {
            "process_health": {"is_running": True},
            "config_validation": {"status": "healthy", "websocket_enabled": True},
            "edge_connectivity": {"connectivity_ratio": 1.0},
            "performance_metrics": {"memory_usage_percent": 50}
        }
        
        recommendations = diagnostics._generate_recommendations(diagnostics_data)
        
        assert len(recommendations) == 1
        assert "no issues detected" in recommendations[0]
    
    def test_generate_recommendations_with_issues(self, diagnostics):
        """Test recommendation generation with issues."""
        diagnostics_data = {
            "process_health": {"is_running": False},
            "config_validation": {"status": "error", "websocket_enabled": False},
            "edge_connectivity": {"connectivity_ratio": 0.3},
            "performance_metrics": {"memory_usage_percent": 85}
        }
        
        recommendations = diagnostics._generate_recommendations(diagnostics_data)
        
        assert len(recommendations) >= 3
        assert any("Start cloudflared process" in rec for rec in recommendations)
        assert any("Fix tunnel configuration" in rec for rec in recommendations)
        assert any("Check network connectivity" in rec for rec in recommendations)
        assert any("High memory usage" in rec for rec in recommendations)
    
    def test_log_action(self, diagnostics, capsys):
        """Test logging action functionality."""
        diagnostics.log_action("test_action", "completed", {"test": "data"})
        
        captured = capsys.readouterr()
        log_data = json.loads(captured.out.strip())
        
        assert log_data["task"] == "3.2"
        assert log_data["action"] == "test_action"
        assert log_data["status"] == "completed"
        assert log_data["details"]["test"] == "data"
        assert "timestamp" in log_data
    
    @pytest.mark.asyncio
    async def test_get_health_status_healthy(self, diagnostics):
        """Test get_health_status when healthy."""
        with patch.object(diagnostics, '_check_cloudflared_process') as mock_process, \
             patch.object(diagnostics, '_validate_tunnel_config') as mock_config:
            
            mock_process.return_value = {"status": "healthy"}
            mock_config.return_value = {"status": "healthy"}
            
            health = await diagnostics.get_health_status()
            
            assert health.module_id == "tunnel_diagnostics"
            assert health.status.value == "healthy"
            assert health.health_score == 1.0
            assert health.issues == []
    
    @pytest.mark.asyncio
    async def test_get_health_status_error(self, diagnostics):
        """Test get_health_status when there are errors."""
        with patch.object(diagnostics, '_check_cloudflared_process') as mock_process, \
             patch.object(diagnostics, '_validate_tunnel_config') as mock_config:
            
            mock_process.return_value = {"status": "error"}
            mock_config.return_value = {"status": "error"}
            
            health = await diagnostics.get_health_status()
            
            assert health.status.value == "error"
            assert health.health_score == 0.0
            assert len(health.issues) == 1
            assert "Critical tunnel issues detected" in health.issues[0]
    
    @pytest.mark.asyncio
    async def test_get_health_status_exception(self, diagnostics):
        """Test get_health_status with exception."""
        with patch.object(diagnostics, '_check_cloudflared_process') as mock_process:
            mock_process.side_effect = Exception("Test error")
            
            health = await diagnostics.get_health_status()
            
            assert health.status.value == "error"
            assert health.health_score == 0.0
            assert "Health check failed" in health.issues[0]