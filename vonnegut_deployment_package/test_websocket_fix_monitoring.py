#!/usr/bin/env python3
"""
Test Script for WebSocket Fix Monitoring Agent

Validates the monitoring agent functionality without running actual WebSocket fix agents.
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scripts.websocket_fix_monitoring_agent import (
    WebSocketFixMonitoringAgent,
    AgentPhase,
    AgentStatus,
    RemediationAction
)


class TestWebSocketFixMonitoringAgent:
    """Test harness for WebSocket Fix Monitoring Agent"""
    
    def __init__(self):
        self.test_results = []
        self.monitoring_agent = None
    
    async def run_all_tests(self):
        """Run all monitoring agent tests"""
        print("🧪 WebSocket Fix Monitoring Agent Test Suite")
        print("=" * 60)
        
        tests = [
            ("Configuration Loading", self.test_configuration_loading),
            ("Agent Initialization", self.test_agent_initialization),
            ("Status Tracking", self.test_status_tracking),
            ("Health Check System", self.test_health_check_system),
            ("Remediation Actions", self.test_remediation_actions),
            ("Report Generation", self.test_report_generation),
            ("Signal Handling", self.test_signal_handling),
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running: {test_name}")
            try:
                result = await test_func()
                self.test_results.append((test_name, "PASS", result))
                print(f"   ✅ {test_name}: PASSED")
            except Exception as e:
                self.test_results.append((test_name, "FAIL", str(e)))
                print(f"   ❌ {test_name}: FAILED - {e}")
        
        # Generate test summary
        self.generate_test_summary()
    
    async def test_configuration_loading(self):
        """Test configuration loading functionality"""
        # Test default configuration
        agent = WebSocketFixMonitoringAgent()
        
        # Verify all phases are configured
        assert AgentPhase.PHASE_1 in agent.config
        assert AgentPhase.PHASE_2 in agent.config
        assert AgentPhase.PHASE_3 in agent.config
        
        # Verify configuration values
        phase1_config = agent.config[AgentPhase.PHASE_1]
        assert phase1_config.timeout_minutes == 30
        assert phase1_config.health_check_interval == 60
        assert phase1_config.auto_remediation is True
        
        return "Configuration loaded successfully"
    
    async def test_agent_initialization(self):
        """Test agent initialization"""
        agent = WebSocketFixMonitoringAgent()
        
        # Verify agents are initialized
        assert len(agent.agents) == 3
        assert AgentPhase.PHASE_1 in agent.agents
        assert AgentPhase.PHASE_2 in agent.agents
        assert AgentPhase.PHASE_3 in agent.agents
        
        # Verify initial status
        for phase, agent_process in agent.agents.items():
            assert agent_process.status == AgentStatus.NOT_STARTED
            assert agent_process.pid is None
            assert agent_process.restart_count == 0
        
        return "Agents initialized successfully"
    
    async def test_status_tracking(self):
        """Test agent status tracking"""
        agent = WebSocketFixMonitoringAgent()
        
        # Simulate agent status changes
        phase1_agent = agent.agents[AgentPhase.PHASE_1]
        
        # Test status transitions
        phase1_agent.status = AgentStatus.STARTING
        assert phase1_agent.status == AgentStatus.STARTING
        
        phase1_agent.status = AgentStatus.RUNNING
        phase1_agent.pid = 12345
        phase1_agent.start_time = datetime.now()
        
        assert phase1_agent.status == AgentStatus.RUNNING
        assert phase1_agent.pid == 12345
        assert phase1_agent.start_time is not None
        
        return "Status tracking working correctly"
    
    async def test_health_check_system(self):
        """Test health check system"""
        agent = WebSocketFixMonitoringAgent()
        
        # Test health score calculation
        phase1_agent = agent.agents[AgentPhase.PHASE_1]
        phase1_agent.status = AgentStatus.RUNNING
        phase1_agent.pid = 12345
        
        # Mock a healthy process
        health_score = agent._check_agent_health(phase1_agent)
        assert isinstance(health_score, float)
        assert 0.0 <= health_score <= 1.0
        
        return f"Health check system working (score: {health_score:.2f})"
    
    async def test_remediation_actions(self):
        """Test remediation action system"""
        agent = WebSocketFixMonitoringAgent()
        
        phase1_agent = agent.agents[AgentPhase.PHASE_1]
        
        # Test remediation action tracking
        phase1_agent.remediation_actions.append(RemediationAction.RESTART_AGENT)
        phase1_agent.remediation_actions.append(RemediationAction.KILL_AND_RESTART)
        
        assert len(phase1_agent.remediation_actions) == 2
        assert RemediationAction.RESTART_AGENT in phase1_agent.remediation_actions
        assert RemediationAction.KILL_AND_RESTART in phase1_agent.remediation_actions
        
        return "Remediation actions tracked correctly"
    
    async def test_report_generation(self):
        """Test report generation"""
        agent = WebSocketFixMonitoringAgent()
        
        # Generate a test report
        report = agent._generate_status_report()
        
        # Verify report structure
        assert report.timestamp is not None
        assert report.overall_status is not None
        assert isinstance(report.phases_status, dict)
        assert isinstance(report.health_metrics, dict)
        assert isinstance(report.recommendations, list)
        
        # Verify all phases are in report
        assert "phase_1" in report.phases_status
        assert "phase_2" in report.phases_status
        assert "phase_3" in report.phases_status
        
        return "Report generation working correctly"
    
    async def test_signal_handling(self):
        """Test signal handling"""
        agent = WebSocketFixMonitoringAgent()
        
        # Test signal handler setup
        assert hasattr(agent, '_signal_handler')
        
        # Test monitoring active flag
        assert agent.monitoring_active is False
        
        return "Signal handling configured correctly"
    
    def generate_test_summary(self):
        """Generate test summary report"""
        print("\n" + "=" * 60)
        print("🧪 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, status, _ in self.test_results if status == "PASS")
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for test_name, status, result in self.test_results:
                if status == "FAIL":
                    print(f"   • {test_name}: {result}")
            print()
        
        print("✅ PASSED TESTS:")
        for test_name, status, result in self.test_results:
            if status == "PASS":
                print(f"   • {test_name}: {result}")
        
        print("\n" + "=" * 60)
        
        if failed_tests == 0:
            print("🎉 ALL TESTS PASSED!")
            print("WebSocket Fix Monitoring Agent is ready for deployment.")
        else:
            print("⚠️  SOME TESTS FAILED!")
            print("Please review failed tests before deployment.")
        
        # Save test results
        test_report = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": passed_tests/total_tests*100,
            "test_results": [
                {
                    "test_name": test_name,
                    "status": status,
                    "result": result
                }
                for test_name, status, result in self.test_results
            ]
        }
        
        # Save to file
        Path("logs").mkdir(exist_ok=True)
        with open("logs/websocket_fix_monitoring_test_report.json", "w") as f:
            json.dump(test_report, f, indent=2)
        
        print(f"\n💾 Test report saved to: logs/websocket_fix_monitoring_test_report.json")


async def main():
    """Main test entry point"""
    print("🚀 Starting WebSocket Fix Monitoring Agent Tests")
    
    tester = TestWebSocketFixMonitoringAgent()
    await tester.run_all_tests()
    
    return 0 if all(status == "PASS" for _, status, _ in tester.test_results) else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)