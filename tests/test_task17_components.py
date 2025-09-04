"""
Tests for Task 17: Operational Interfaces and Unknown Risk Mitigation Components
Tests CLI, operational dashboards, logging system, and unknown risk mitigation
"""

import pytest
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime

from src.beast_mode.cli.beast_mode_cli import (
    BeastModeCLI,
    CLICommand,
    CLIResult
)

from src.beast_mode.operations.operational_dashboard_manager import (
    OperationalDashboardManager,
    DashboardType,
    DashboardConfig,
    DashboardData
)

from src.beast_mode.operations.comprehensive_logging_system import (
    ComprehensiveLoggingSystem,
    LogLevel,
    AuditEvent,
    LogEntry
)

class TestBeastModeCLI:
    """Test Beast Mode CLI functionality"""
    
    @pytest.fixture
    def temp_project_root(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            
            # Create basic project structure
            (project_root / "src" / "beast_mode" / "core").mkdir(parents=True)
            (project_root / ".kiro" / "specs").mkdir(parents=True)
            
            yield project_root
            
    @pytest.fixture
    def beast_mode_cli(self, temp_project_root):
        return BeastModeCLI(str(temp_project_root))
        
    def test_cli_initialization(self, beast_mode_cli):
        """Test CLI initialization"""
        assert beast_mode_cli.module_name == "beast_mode_cli"
        assert beast_mode_cli.is_healthy()
        
        status = beast_mode_cli.get_module_status()
        assert "module_name" in status
        assert "status" in status
        assert "total_commands" in status
        
    def test_status_command(self, beast_mode_cli):
        """Test status command execution"""
        result = beast_mode_cli.execute_command(CLICommand.STATUS.value)
        
        assert isinstance(result, CLIResult)
        assert result.command == "status"
        assert result.success is True
        assert "Beast Mode Framework - Comprehensive Status" in result.output
        assert result.data is not None
        
    def test_health_command(self, beast_mode_cli):
        """Test health command execution"""
        result = beast_mode_cli.execute_command(CLICommand.HEALTH.value)
        
        assert isinstance(result, CLIResult)
        assert result.command == "health"
        assert result.success is True
        assert "Beast Mode Framework - Health Check" in result.output
        assert "Overall Health:" in result.output
        
    def test_validate_command(self, beast_mode_cli):
        """Test validation command execution"""
        # Test complete validation
        result = beast_mode_cli.execute_command(CLICommand.VALIDATE.value)
        
        assert isinstance(result, CLIResult)
        assert result.command == "validate"
        assert result.success is True
        assert "Complete Validation" in result.output
        
        # Test infrastructure validation only
        result = beast_mode_cli.execute_command(CLICommand.VALIDATE.value, ["infrastructure"])
        
        assert result.success is True
        assert "Infrastructure Validation" in result.output
        
    def test_pdca_command(self, beast_mode_cli):
        """Test PDCA command execution"""
        # Test complete PDCA cycle
        result = beast_mode_cli.execute_command(CLICommand.PDCA.value)
        
        assert isinstance(result, CLIResult)
        assert result.command == "pdca"
        assert result.success is True
        assert "PDCA Cycle" in result.output
        assert "PLAN Phase" in result.output
        assert "DO Phase" in result.output
        assert "CHECK Phase" in result.output
        assert "ACT Phase" in result.output
        
        # Test individual phases
        for phase in ["plan", "do", "check", "act"]:
            result = beast_mode_cli.execute_command(CLICommand.PDCA.value, [phase])
            assert result.success is True
            assert phase.upper() in result.output
            
    def test_orchestrate_command(self, beast_mode_cli):
        """Test orchestration command execution"""
        result = beast_mode_cli.execute_command(CLICommand.ORCHESTRATE.value)
        
        assert isinstance(result, CLIResult)
        assert result.command == "orchestrate"
        assert result.success is True
        assert "Tool Orchestration" in result.output
        assert "Decision Analytics" in result.output
        
    def test_metrics_command(self, beast_mode_cli):
        """Test metrics command execution"""
        # Test all metrics
        result = beast_mode_cli.execute_command(CLICommand.METRICS.value)
        
        assert isinstance(result, CLIResult)
        assert result.command == "metrics"
        assert result.success is True
        assert "Framework Metrics" in result.output
        
        # Test superiority metrics
        result = beast_mode_cli.execute_command(CLICommand.METRICS.value, ["superiority"])
        
        assert result.success is True
        assert "Superiority Metrics" in result.output
        
    def test_debug_command(self, beast_mode_cli):
        """Test debug command execution"""
        # Test system debug
        result = beast_mode_cli.execute_command(CLICommand.DEBUG.value)
        
        assert isinstance(result, CLIResult)
        assert result.command == "debug"
        assert result.success is True
        assert "Debug Information" in result.output
        
        # Test components debug
        result = beast_mode_cli.execute_command(CLICommand.DEBUG.value, ["components"])
        
        assert result.success is True
        assert "Integration Manager" in result.output
        
    def test_unknown_risks_command(self, beast_mode_cli):
        """Test unknown risks command execution"""
        # Test list all risks
        result = beast_mode_cli.execute_command(CLICommand.UNKNOWN_RISKS.value, ["list"])
        
        assert isinstance(result, CLIResult)
        assert result.command == "unknown-risks"
        assert result.success is True
        assert "Unknown Risk Mitigation" in result.output
        assert "UK-01" in result.output
        
        # Test risk status
        result = beast_mode_cli.execute_command(CLICommand.UNKNOWN_RISKS.value, ["status"])
        
        assert result.success is True
        assert "Risk Mitigation Summary" in result.output
        
        # Test specific risk
        result = beast_mode_cli.execute_command(CLICommand.UNKNOWN_RISKS.value, ["UK-01"])
        
        assert result.success is True
        assert "Project Registry Data Quality" in result.output
        
    def test_invalid_command(self, beast_mode_cli):
        """Test invalid command handling"""
        result = beast_mode_cli.execute_command("invalid_command")
        
        assert isinstance(result, CLIResult)
        assert result.success is False
        assert "Unknown command" in result.output
        
    def test_command_history_tracking(self, beast_mode_cli):
        """Test command history tracking"""
        # Execute several commands
        beast_mode_cli.execute_command(CLICommand.STATUS.value)
        beast_mode_cli.execute_command(CLICommand.HEALTH.value)
        beast_mode_cli.execute_command(CLICommand.STATUS.value)
        
        # Check history
        history = beast_mode_cli.get_command_history()
        assert len(history) == 3
        assert history[0]["command"] == "status"
        assert history[1]["command"] == "health"
        assert history[2]["command"] == "status"
        
        # Check metrics
        analytics = beast_mode_cli.get_cli_analytics()
        assert analytics["cli_metrics"]["total_commands"] == 3
        assert analytics["cli_metrics"]["most_used_command"] == "status"
        
    def test_cli_argument_parser(self, beast_mode_cli):
        """Test CLI argument parser creation"""
        parser = beast_mode_cli.create_parser()
        
        assert parser is not None
        assert parser.description is not None
        
        # Test parsing valid arguments
        args = parser.parse_args(["status"])
        assert args.command == "status"
        assert args.args == []

class TestOperationalDashboardManager:
    """Test operational dashboard functionality"""
    
    @pytest.fixture
    def temp_project_root(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
            
    @pytest.fixture
    def dashboard_manager(self, temp_project_root):
        return OperationalDashboardManager(str(temp_project_root))
        
    @pytest.fixture
    def sample_dashboard_config(self):
        return DashboardConfig(
            dashboard_id="test_dashboard",
            dashboard_type=DashboardType.HEALTH_MONITORING,
            title="Test Dashboard",
            description="Test dashboard for validation",
            refresh_interval_seconds=30
        )
        
    def test_dashboard_manager_initialization(self, dashboard_manager):
        """Test dashboard manager initialization"""
        assert dashboard_manager.module_name == "operational_dashboard_manager"
        assert dashboard_manager.is_healthy()
        
        status = dashboard_manager.get_module_status()
        assert "module_name" in status
        assert "total_dashboards" in status
        
        # Should have default dashboards
        assert dashboard_manager.dashboard_metrics['total_dashboards'] > 0
        
    def test_dashboard_creation(self, dashboard_manager, sample_dashboard_config):
        """Test dashboard creation"""
        result = dashboard_manager.create_dashboard(sample_dashboard_config)
        
        assert result["success"] is True
        assert result["dashboard_id"] == "test_dashboard"
        assert result["title"] == "Test Dashboard"
        
        # Verify dashboard is stored
        assert "test_dashboard" in dashboard_manager.dashboards
        
    def test_dashboard_data_update(self, dashboard_manager, sample_dashboard_config):
        """Test dashboard data updates"""
        # Create dashboard first
        dashboard_manager.create_dashboard(sample_dashboard_config)
        
        # Update data
        test_data = {"metric1": 100, "metric2": "healthy"}
        result = dashboard_manager.update_dashboard_data("test_dashboard", test_data)
        
        assert result["success"] is True
        assert result["dashboard_id"] == "test_dashboard"
        
        # Verify data is stored
        assert "test_dashboard" in dashboard_manager.dashboard_data
        assert dashboard_manager.dashboard_data["test_dashboard"].data == test_data
        
    def test_dashboard_data_retrieval(self, dashboard_manager, sample_dashboard_config):
        """Test dashboard data retrieval"""
        # Create dashboard and add data
        dashboard_manager.create_dashboard(sample_dashboard_config)
        test_data = {"status": "operational"}
        dashboard_manager.update_dashboard_data("test_dashboard", test_data)
        
        # Retrieve data
        result = dashboard_manager.get_dashboard_data("test_dashboard")
        
        assert "dashboard_id" in result
        assert result["title"] == "Test Dashboard"
        assert result["current_data"] == test_data
        
        # Test with history
        result_with_history = dashboard_manager.get_dashboard_data("test_dashboard", include_history=True)
        assert "history" in result_with_history
        
    def test_health_monitoring_dashboard_generation(self, dashboard_manager):
        """Test health monitoring dashboard generation"""
        result = dashboard_manager.generate_health_monitoring_dashboard()
        
        assert "overall_health" in result
        assert "components" in result
        assert "metrics" in result
        
        # Verify data structure
        assert "status" in result["overall_health"]
        assert "dashboard_manager" in result["components"]
        
    def test_superiority_metrics_dashboard_generation(self, dashboard_manager):
        """Test superiority metrics dashboard generation"""
        result = dashboard_manager.generate_superiority_metrics_dashboard()
        
        assert "systematic_vs_adhoc" in result
        assert "concrete_metrics" in result
        assert "evidence_strength" in result
        
        # Verify comparison data
        assert "tool_health_management" in result["systematic_vs_adhoc"]
        
    def test_performance_analytics_dashboard_generation(self, dashboard_manager):
        """Test performance analytics dashboard generation"""
        result = dashboard_manager.generate_performance_analytics_dashboard()
        
        assert "system_performance" in result
        assert "component_performance" in result
        assert "trends" in result
        
    def test_unknown_risks_dashboard_generation(self, dashboard_manager):
        """Test unknown risks dashboard generation"""
        result = dashboard_manager.generate_unknown_risks_dashboard()
        
        assert "risk_summary" in result
        assert "risk_details" in result
        assert "mitigation_effectiveness" in result
        
        # Verify risk data
        risk_summary = result["risk_summary"]
        assert "total_risks" in risk_summary
        assert "mitigated_risks" in risk_summary
        
    def test_dashboard_refresh_all(self, dashboard_manager):
        """Test refreshing all dashboards"""
        result = dashboard_manager.refresh_all_dashboards()
        
        assert result["success"] is True
        assert "dashboards_refreshed" in result
        assert "refresh_time_ms" in result
        
        # Should have refreshed default dashboards
        assert result["dashboards_refreshed"] > 0
        
    def test_dashboard_analytics(self, dashboard_manager):
        """Test dashboard analytics"""
        analytics = dashboard_manager.get_dashboard_analytics()
        
        assert "dashboard_metrics" in analytics
        assert "dashboard_summary" in analytics
        assert "data_statistics" in analytics
        assert "system_health" in analytics

class TestComprehensiveLoggingSystem:
    """Test comprehensive logging system functionality"""
    
    @pytest.fixture
    def temp_project_root(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
            
    @pytest.fixture
    def logging_system(self, temp_project_root):
        return ComprehensiveLoggingSystem(str(temp_project_root))
        
    def test_logging_system_initialization(self, logging_system):
        """Test logging system initialization"""
        assert logging_system.module_name == "comprehensive_logging_system"
        assert logging_system.is_healthy()
        
        status = logging_system.get_module_status()
        assert "module_name" in status
        assert "log_directory" in status
        
        # Verify log directory was created
        assert logging_system.log_directory.exists()
        
    def test_basic_logging(self, logging_system):
        """Test basic log entry creation"""
        correlation_id = logging_system.log(
            level=LogLevel.INFO,
            message="Test log message",
            component="test_component",
            operation="test_operation"
        )
        
        assert correlation_id is not None
        assert len(logging_system.log_entries) == 1
        
        log_entry = logging_system.log_entries[0]
        assert log_entry.level == LogLevel.INFO
        assert log_entry.message == "Test log message"
        assert log_entry.component == "test_component"
        assert log_entry.correlation_id == correlation_id
        
    def test_audit_logging(self, logging_system):
        """Test audit log creation"""
        correlation_id = logging_system.audit(
            event=AuditEvent.SYSTEM_START,
            component="test_system",
            operation="startup",
            metadata={"version": "1.0"}
        )
        
        assert correlation_id is not None
        assert len(logging_system.audit_trail) == 1
        
        audit_entry = logging_system.audit_trail[0]
        assert audit_entry.audit_event == AuditEvent.SYSTEM_START
        assert audit_entry.component == "test_system"
        
    def test_performance_logging(self, logging_system):
        """Test performance logging"""
        correlation_id = logging_system.performance_log(
            component="test_component",
            operation="test_operation",
            duration_ms=1500,
            metadata={"details": "test"}
        )
        
        assert correlation_id is not None
        
        # Find the performance log entry
        perf_logs = [log for log in logging_system.log_entries if log.performance_data is not None]
        assert len(perf_logs) == 1
        
        perf_log = perf_logs[0]
        assert perf_log.performance_data["duration_ms"] == 1500
        assert perf_log.performance_data["operation"] == "test_operation"
        
    def test_error_logging(self, logging_system):
        """Test error logging"""
        test_error = ValueError("Test error message")
        
        correlation_id = logging_system.error_log(
            component="test_component",
            operation="test_operation",
            error=test_error,
            metadata={"context": "test"}
        )
        
        assert correlation_id is not None
        
        # Find the error log entry
        error_logs = [log for log in logging_system.log_entries if log.level == LogLevel.ERROR]
        assert len(error_logs) == 1
        
        error_log = error_logs[0]
        assert error_log.error_details["error_type"] == "ValueError"
        assert error_log.error_details["error_message"] == "Test error message"
        
    def test_security_logging(self, logging_system):
        """Test security logging"""
        correlation_id = logging_system.security_log(
            event_type="unauthorized_access",
            component="security_system",
            details={"ip": "192.168.1.1", "user": "test_user"},
            severity="high"
        )
        
        assert correlation_id is not None
        assert logging_system.logging_metrics['security_events'] == 1
        
        # Find the security log entry
        security_logs = [log for log in logging_system.log_entries if log.audit_event == AuditEvent.SECURITY_EVENT]
        assert len(security_logs) == 1
        
    def test_correlation_context(self, logging_system):
        """Test correlation context management"""
        with logging_system.correlation_context("test-correlation-123", "test_operation") as correlation_id:
            assert correlation_id == "test-correlation-123"
            
            # Log within context
            logging_system.log(
                level=LogLevel.INFO,
                message="Test message in context",
                component="test_component"
            )
            
        # Verify correlation ID was used
        log_entry = logging_system.log_entries[0]
        assert log_entry.correlation_id == "test-correlation-123"
        
    def test_session_context(self, logging_system):
        """Test session context management"""
        with logging_system.session_context("session-123", "user-456"):
            logging_system.log(
                level=LogLevel.INFO,
                message="Test message in session",
                component="test_component"
            )
            
        # Verify session context was captured
        log_entry = logging_system.log_entries[0]
        assert log_entry.session_id == "session-123"
        assert log_entry.user_id == "user-456"
        
    def test_log_filtering(self, logging_system):
        """Test log filtering and retrieval"""
        # Create logs with different levels and components
        logging_system.log(LogLevel.INFO, "Info message", "component1")
        logging_system.log(LogLevel.ERROR, "Error message", "component1")
        logging_system.log(LogLevel.INFO, "Info message", "component2")
        
        # Test filtering by level
        error_logs = logging_system.get_logs(level=LogLevel.ERROR)
        assert len(error_logs) == 1
        assert error_logs[0].level == LogLevel.ERROR
        
        # Test filtering by component
        component1_logs = logging_system.get_logs(component="component1")
        assert len(component1_logs) == 2
        
    def test_performance_analytics(self, logging_system):
        """Test performance analytics generation"""
        # Add some performance logs
        logging_system.performance_log("comp1", "op1", 1000)
        logging_system.performance_log("comp1", "op2", 2000)
        logging_system.performance_log("comp2", "op1", 500)
        
        analytics = logging_system.get_performance_analytics()
        
        assert "total_performance_events" in analytics
        assert "average_duration_ms" in analytics
        assert analytics["total_performance_events"] == 3
        assert abs(analytics["average_duration_ms"] - 1166.67) < 0.01  # (1000+2000+500)/3 with tolerance
        
    def test_error_analytics(self, logging_system):
        """Test error analytics generation"""
        # Add some error logs
        logging_system.error_log("comp1", "op1", ValueError("Error 1"))
        logging_system.error_log("comp2", "op1", RuntimeError("Error 2"))
        logging_system.log(LogLevel.INFO, "Info message", "comp1")  # Non-error
        
        analytics = logging_system.get_error_analytics()
        
        assert "total_errors" in analytics
        assert "error_rate" in analytics
        assert "errors_by_component" in analytics
        assert analytics["total_errors"] == 2
        
    def test_logging_analytics(self, logging_system):
        """Test comprehensive logging analytics"""
        # Add various types of logs
        logging_system.log(LogLevel.INFO, "Info", "comp1")
        logging_system.audit(AuditEvent.SYSTEM_START, "comp1", "startup")
        logging_system.error_log("comp1", "op1", ValueError("Test error"))
        
        analytics = logging_system.get_logging_analytics()
        
        assert "logging_metrics" in analytics
        assert "performance_analytics" in analytics
        assert "error_analytics" in analytics
        assert "audit_summary" in analytics
        assert "system_health" in analytics
        
    def test_log_export(self, logging_system):
        """Test log export functionality"""
        # Add some logs
        logging_system.log(LogLevel.INFO, "Test message 1", "comp1")
        logging_system.log(LogLevel.ERROR, "Test message 2", "comp2")
        
        # Export logs
        exported_data = logging_system.export_logs(format="json")
        
        assert exported_data is not None
        
        # Parse exported JSON
        exported_logs = json.loads(exported_data)
        assert len(exported_logs) == 2
        assert exported_logs[0]["message"] == "Test message 1"
        assert exported_logs[1]["message"] == "Test message 2"

class TestTask17Integration:
    """Test integration between Task 17 components"""
    
    @pytest.fixture
    def temp_project_root(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            (project_root / "src" / "beast_mode").mkdir(parents=True)
            yield project_root
            
    def test_cli_dashboard_integration(self, temp_project_root):
        """Test CLI integration with dashboard manager"""
        cli = BeastModeCLI(str(temp_project_root))
        dashboard_manager = OperationalDashboardManager(str(temp_project_root))
        
        # CLI should be able to access dashboard functionality
        assert cli.is_healthy()
        assert dashboard_manager.is_healthy()
        
        # Test that CLI metrics command works
        result = cli.execute_command("metrics")
        assert result.success is True
        
    def test_cli_logging_integration(self, temp_project_root):
        """Test CLI integration with logging system"""
        cli = BeastModeCLI(str(temp_project_root))
        logging_system = ComprehensiveLoggingSystem(str(temp_project_root))
        
        # Both should be operational
        assert cli.is_healthy()
        assert logging_system.is_healthy()
        
        # CLI operations should be loggable
        with logging_system.correlation_context("cli-test"):
            result = cli.execute_command("status")
            assert result.success is True
            
    def test_dashboard_logging_integration(self, temp_project_root):
        """Test dashboard manager integration with logging"""
        # Create logging system first to ensure proper handler setup
        logging_system = ComprehensiveLoggingSystem(str(temp_project_root))
        dashboard_manager = OperationalDashboardManager(str(temp_project_root))
        
        # Dashboard operations should be loggable
        with logging_system.correlation_context("dashboard-test"):
            result = dashboard_manager.refresh_all_dashboards()
            assert result["success"] is True
            
        # Should have log entries
        assert len(logging_system.log_entries) > 0
        
    def test_unknown_risk_mitigation_coverage(self, temp_project_root):
        """Test that unknown risk mitigation covers all identified risks"""
        cli = BeastModeCLI(str(temp_project_root))
        
        # Get unknown risks status
        result = cli.execute_command("unknown-risks", ["status"])
        assert result.success is True
        
        # Verify comprehensive coverage
        assert "100%" in result.output  # Should show 100% coverage
        
        # Test specific risk details
        for risk_id in ["UK-01", "UK-02", "UK-03", "UK-06", "UK-09", "UK-17"]:
            result = cli.execute_command("unknown-risks", [risk_id])
            assert result.success is True
            assert risk_id in result.output

if __name__ == "__main__":
    pytest.main([__file__])