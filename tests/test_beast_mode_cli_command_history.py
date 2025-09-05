"""
Unit tests for BeastModeCLI command history functionality
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from pathlib import Path

from src.beast_mode.cli.beast_mode_cli import BeastModeCLI, CLIResult


class TestBeastModeCLICommandHistory:
    """Test BeastModeCLI command history functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create a temporary directory for testing
        self.test_project_root = "/tmp/test_beast_mode"
        
        # Mock the dependencies to avoid initialization issues
        with patch('src.beast_mode.cli.beast_mode_cli.InfrastructureIntegrationManager'), \
             patch('src.beast_mode.cli.beast_mode_cli.SelfConsistencyValidator'), \
             patch('src.beast_mode.cli.beast_mode_cli.ToolOrchestrationEngine'), \
             patch('pathlib.Path.exists', return_value=True):
            
            self.cli = BeastModeCLI(self.test_project_root)
    
    def test_cli_has_command_history_attribute(self):
        """Test that BeastModeCLI has command_history attribute"""
        assert hasattr(self.cli, 'command_history')
        assert isinstance(self.cli.command_history, list)
        assert len(self.cli.command_history) == 0  # Initially empty
    
    def test_get_command_history_method_exists(self):
        """Test that get_command_history method exists and works"""
        assert hasattr(self.cli, 'get_command_history')
        assert callable(self.cli.get_command_history)
        
        # Should return a copy of command history
        history = self.cli.get_command_history()
        assert isinstance(history, list)
        assert history == []
        
        # Verify it's a copy (not the same object)
        assert history is not self.cli.command_history
    
    def test_record_command_method_exists(self):
        """Test that _record_command method exists and works"""
        assert hasattr(self.cli, '_record_command')
        assert callable(self.cli._record_command)
        
        # Record a command
        self.cli._record_command("test_command", ["arg1", "arg2"], True, 100)
        
        # Check that it was recorded
        history = self.cli.get_command_history()
        assert len(history) == 1
        
        command_entry = history[0]
        assert command_entry["command"] == "test_command"
        assert command_entry["args"] == ["arg1", "arg2"]
        assert command_entry["success"] is True
        assert command_entry["execution_time_ms"] == 100
        assert isinstance(command_entry["timestamp"], datetime)
    
    def test_record_command_with_defaults(self):
        """Test _record_command with default parameters"""
        self.cli._record_command("simple_command")
        
        history = self.cli.get_command_history()
        assert len(history) == 1
        
        command_entry = history[0]
        assert command_entry["command"] == "simple_command"
        assert command_entry["args"] == []
        assert command_entry["success"] is True
        assert command_entry["execution_time_ms"] == 0
    
    def test_command_history_limit(self):
        """Test that command history is limited to 100 entries"""
        # Add 150 commands
        for i in range(150):
            self.cli._record_command(f"command_{i}")
        
        # Should only keep the last 100
        history = self.cli.get_command_history()
        assert len(history) == 100
        
        # Should have commands 50-149 (the last 100)
        assert history[0]["command"] == "command_50"
        assert history[-1]["command"] == "command_149"
    
    def test_command_history_tracking_in_execute_command(self):
        """Test that execute_command records commands in history"""
        # Mock the command execution methods
        mock_result = CLIResult(
            command="status",
            success=True,
            output="Mock status output",
            execution_time_ms=50
        )
        
        with patch.object(self.cli, '_execute_status_command', return_value=mock_result):
            result = self.cli.execute_command("status", ["--verbose"])
        
        # Check that command was recorded in history
        history = self.cli.get_command_history()
        assert len(history) == 1
        
        command_entry = history[0]
        assert command_entry["command"] == "status"
        assert command_entry["args"] == ["--verbose"]
        assert command_entry["success"] is True
        assert command_entry["execution_time_ms"] >= 0  # Should have execution time recorded
    
    def test_failed_command_recorded_in_history(self):
        """Test that failed commands are recorded in history"""
        # Mock a command that raises an exception
        with patch.object(self.cli, '_execute_status_command', side_effect=Exception("Test error")):
            result = self.cli.execute_command("status")
        
        # Check that failed command was recorded
        history = self.cli.get_command_history()
        assert len(history) == 1
        
        command_entry = history[0]
        assert command_entry["command"] == "status"
        assert command_entry["success"] is False
        assert command_entry["execution_time_ms"] >= 0
        
        # Check that the result indicates failure
        assert result.success is False
        assert "Command execution failed" in result.output
    
    def test_multiple_commands_in_history(self):
        """Test tracking multiple commands in history"""
        # Mock different command results
        status_result = CLIResult("status", True, "Status OK", 30)
        health_result = CLIResult("health", True, "Health OK", 45)
        
        with patch.object(self.cli, '_execute_status_command', return_value=status_result), \
             patch.object(self.cli, '_execute_health_command', return_value=health_result):
            
            self.cli.execute_command("status")
            self.cli.execute_command("health", ["--detailed"])
        
        # Check history
        history = self.cli.get_command_history()
        assert len(history) == 2
        
        # First command
        assert history[0]["command"] == "status"
        assert history[0]["args"] == []
        assert history[0]["success"] is True
        
        # Second command
        assert history[1]["command"] == "health"
        assert history[1]["args"] == ["--detailed"]
        assert history[1]["success"] is True
    
    def test_command_history_immutability(self):
        """Test that returned command history cannot modify internal state"""
        self.cli._record_command("test_command")
        
        # Get history and try to modify it
        history = self.cli.get_command_history()
        history.append({"command": "malicious", "args": []})
        
        # Internal history should be unchanged
        internal_history = self.cli.get_command_history()
        assert len(internal_history) == 1
        assert internal_history[0]["command"] == "test_command"
    
    def test_most_used_command_tracking(self):
        """Test that most used command is tracked correctly"""
        # Record multiple commands with different frequencies
        self.cli._record_command("status")
        self.cli._record_command("health")
        self.cli._record_command("status")
        self.cli._record_command("validate")
        self.cli._record_command("status")
        
        # Status should be the most used command (3 times)
        assert self.cli.cli_metrics['most_used_command'] == "status"
    
    def test_command_history_in_health_indicators(self):
        """Test that command history size is included in health indicators"""
        # Add some commands
        self.cli._record_command("command1")
        self.cli._record_command("command2")
        self.cli._record_command("command3")
        
        health_indicators = self.cli.get_health_indicators()
        
        # Check that command history metrics are included
        assert "operational_metrics" in health_indicators
        operational_metrics = health_indicators["operational_metrics"]
        
        assert "command_history_size" in operational_metrics
        assert operational_metrics["command_history_size"] == 3
        
        assert "recent_commands" in operational_metrics
        assert operational_metrics["recent_commands"] == 3  # All 3 are recent


class TestBeastModeCLIIntegration:
    """Integration tests for BeastModeCLI command history"""
    
    def setup_method(self):
        """Set up test fixtures"""
        with patch('src.beast_mode.cli.beast_mode_cli.InfrastructureIntegrationManager'), \
             patch('src.beast_mode.cli.beast_mode_cli.SelfConsistencyValidator'), \
             patch('src.beast_mode.cli.beast_mode_cli.ToolOrchestrationEngine'), \
             patch('pathlib.Path.exists', return_value=True):
            
            self.cli = BeastModeCLI("/tmp/test")
    
    def test_command_history_persistence_across_operations(self):
        """Test that command history persists across multiple operations"""
        # Mock successful operations
        with patch.object(self.cli, '_execute_status_command', 
                         return_value=CLIResult("status", True, "OK", 10)), \
             patch.object(self.cli, '_execute_health_command',
                         return_value=CLIResult("health", True, "Healthy", 15)):
            
            # Execute multiple commands
            self.cli.execute_command("status")
            self.cli.execute_command("health")
            
            # Check that both are in history
            history = self.cli.get_command_history()
            assert len(history) == 2
            
            # Execute more commands
            self.cli.execute_command("status", ["--verbose"])
            
            # History should now have 3 commands
            history = self.cli.get_command_history()
            assert len(history) == 3
            
            # Verify order (chronological)
            assert history[0]["command"] == "status"
            assert history[0]["args"] == []
            assert history[1]["command"] == "health"
            assert history[2]["command"] == "status"
            assert history[2]["args"] == ["--verbose"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])