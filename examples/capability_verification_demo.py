#!/usr/bin/env python3
"""
Beast Mode Capability Verification System Demo

Demonstrates the complete capability verification workflow including:
- Capability testing and validation
- Trust scoring based on interactions
- Reputation tracking and display
- Capability recommendations for help requests
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.beast_mode.messaging.capability_verifier import (
    CapabilityVerifier, TrustLevel, VerificationStatus
)
from src.beast_mode.messaging.agent_registry import AgentRegistry
from src.beast_mode.messaging.help_system import HelpWantedSystem, CollaborationStatus
from src.beast_mode.messaging.models import BeastModeMessage, MessageType


class CapabilityVerificationDemo:
    """Demonstration of the capability verification system"""
    
    def __init__(self):
        self.agent_registry = AgentRegistry()
        self.help_system = HelpWantedSystem(self.agent_registry)
        self.verifier = CapabilityVerifier(self.agent_registry, self.help_system)
        
        # Demo agents
        self.demo_agents = [
            {
                "agent_id": "alice_python_expert",
                "capabilities": ["python", "testing", "debugging", "performance_optimization"],
                "specializations": ["web_development", "data_analysis"],
                "description": "Senior Python developer with 5+ years experience"
            },
            {
                "agent_id": "bob_devops_guru",
                "capabilities": ["docker", "kubernetes", "terraform", "gcp", "monitoring"],
                "specializations": ["infrastructure", "deployment", "scaling"],
                "description": "DevOps specialist focused on cloud infrastructure"
            },
            {
                "agent_id": "charlie_junior_dev",
                "capabilities": ["python", "testing", "documentation"],
                "specializations": ["learning", "code_review"],
                "description": "Junior developer eager to learn and contribute"
            },
            {
                "agent_id": "diana_security_expert",
                "capabilities": ["security", "penetration_testing", "compliance", "python"],
                "specializations": ["vulnerability_assessment", "secure_coding"],
                "description": "Security specialist with focus on application security"
            }
        ]
    
    def setup_demo_agents(self) -> None:
        """Register demo agents in the system"""
        print("🚀 Setting up demo agents...")
        
        for agent_data in self.demo_agents:
            discovery_message = BeastModeMessage(
                type=MessageType.AGENT_DISCOVERY,
                source=agent_data["agent_id"],
                payload={
                    "agent_capabilities": {
                        "agent_id": agent_data["agent_id"],
                        "capabilities": agent_data["capabilities"],
                        "availability": "ready_for_business",
                        "specializations": agent_data["specializations"]
                    },
                    "description": agent_data["description"]
                }
            )
            
            self.agent_registry.register_agent_discovery(discovery_message)
            print(f"   ✅ Registered {agent_data['agent_id']}")
        
        print(f"   📊 Total agents registered: {len(self.demo_agents)}")
        print()
    
    def demonstrate_capability_testing(self) -> None:
        """Demonstrate capability verification through testing"""
        print("🧪 Demonstrating Capability Testing...")
        
        # Test Alice's Python capability
        print("   Testing Alice's Python capability...")
        test = self.verifier.create_capability_test(
            agent_id="alice_python_expert",
            capability="python",
            test_type="interaction",
            test_description="Code review and optimization task",
            timeout_minutes=30,
            success_criteria={
                "code_quality": "good",
                "response_time": "<10s",
                "best_practices": True
            }
        )
        
        print(f"   📝 Created test {test.test_id}")
        
        # Start the test
        self.verifier.start_capability_test(test.test_id)
        print(f"   ▶️  Started test (status: {test.status})")
        
        # Simulate test completion
        time.sleep(0.1)  # Simulate test duration
        
        result_data = {
            "task_completed": True,
            "code_quality": "excellent",
            "response_time": 4.2,
            "best_practices_followed": True,
            "suggestions_provided": 3,
            "documentation_quality": "good"
        }
        
        performance_metrics = {
            "response_time": 4.2,
            "accuracy": 0.95,
            "completeness": 1.0,
            "efficiency": 0.9
        }
        
        self.verifier.complete_capability_test(
            test.test_id,
            success=True,
            result_data=result_data,
            performance_metrics=performance_metrics
        )
        
        print(f"   ✅ Test completed successfully (score: {test.success_score:.2f})")
        print(f"   📈 Performance: {performance_metrics}")
        print()
    
    def simulate_interaction_history(self) -> None:
        """Simulate interaction history for trust scoring"""
        print("📊 Simulating Interaction History...")
        
        # Define interaction scenarios for each agent
        interaction_scenarios = {
            "alice_python_expert": {
                "python": [(True, 2.5), (True, 3.0), (True, 2.8), (True, 3.2), (True, 2.9)],
                "testing": [(True, 4.0), (True, 3.5), (True, 4.2), (False, 6.0), (True, 3.8)],
                "debugging": [(True, 5.0), (True, 4.5), (True, 5.2)]
            },
            "bob_devops_guru": {
                "docker": [(True, 3.0), (True, 2.8), (True, 3.2)],
                "kubernetes": [(True, 8.0), (True, 7.5), (False, 12.0), (True, 8.2)],
                "terraform": [(True, 10.0), (True, 9.5)]
            },
            "charlie_junior_dev": {
                "python": [(True, 6.0), (False, 10.0), (True, 7.0), (True, 5.5)],
                "testing": [(False, 8.0), (True, 6.5), (True, 6.0)]
            },
            "diana_security_expert": {
                "security": [(True, 15.0), (True, 12.0), (True, 14.5)],
                "python": [(True, 4.0), (True, 3.8), (False, 7.0), (True, 4.2)]
            }
        }
        
        for agent_id, capabilities in interaction_scenarios.items():
            print(f"   🤖 Recording interactions for {agent_id}...")
            
            for capability, interactions in capabilities.items():
                for success, response_time in interactions:
                    self.verifier.record_interaction_result(
                        agent_id, capability, success, response_time
                    )
                
                # Get current trust score
                trust_key = (agent_id, capability)
                if trust_key in self.verifier.trust_scores:
                    trust_score = self.verifier.trust_scores[trust_key]
                    print(f"      {capability}: {trust_score.trust_level.value} "
                          f"(score: {trust_score.trust_score:.2f}, "
                          f"success: {trust_score.average_success_rate:.1%})")
        
        print()
    
    def demonstrate_collaboration_tracking(self) -> None:
        """Demonstrate collaboration-based trust scoring"""
        print("🤝 Demonstrating Collaboration Tracking...")
        
        # Create a help request
        help_request = self.help_system.create_help_request(
            requester_id="project_manager",
            required_capabilities=["python", "testing"],
            description="Need help setting up automated testing for Python project",
            urgency="normal"
        )
        
        print(f"   📢 Created help request: {help_request.description}")
        print(f"   🎯 Required capabilities: {help_request.required_capabilities}")
        
        # Simulate help response from Alice
        help_response_msg = BeastModeMessage(
            type=MessageType.HELP_RESPONSE,
            source="alice_python_expert",
            payload={
                "request_id": help_request.request_id,
                "matching_capabilities": ["python", "testing"],
                "confidence_score": 0.9,
                "availability": "ready_for_business",
                "message": "I can help with Python test automation setup"
            }
        )
        
        # Process the response
        self.help_system.process_help_response(help_response_msg)
        print(f"   💬 Alice responded with confidence: 0.9")
        
        # Accept the help and start collaboration
        response_id = help_request.responses[0].response_id
        collaboration = self.help_system.accept_help_response(help_request.request_id, response_id)
        
        print(f"   🚀 Started collaboration session: {collaboration.session_id}")
        print(f"   👥 Participants: {collaboration.requester_id} ↔ {collaboration.helper_id}")
        
        # Simulate successful collaboration
        collaboration.status = CollaborationStatus.COMPLETED
        collaboration.messages_exchanged = 15
        collaboration.success_metrics = {
            "task_completed": True,
            "quality_rating": 4.8,
            "time_efficiency": 0.9,
            "knowledge_transfer": True
        }
        
        # Record collaboration result
        self.verifier.record_collaboration_result(collaboration)
        
        print(f"   ✅ Collaboration completed successfully")
        print(f"   📊 Metrics: {collaboration.success_metrics}")
        print()
    
    def demonstrate_capability_recommendations(self) -> None:
        """Demonstrate capability recommendation system"""
        print("💡 Demonstrating Capability Recommendations...")
        
        # Request recommendations for different scenarios
        scenarios = [
            {
                "name": "Python Development Task",
                "capabilities": ["python", "testing"],
                "description": "Need help with Python development and testing"
            },
            {
                "name": "Infrastructure Deployment",
                "capabilities": ["docker", "kubernetes", "terraform"],
                "description": "Need help deploying application to Kubernetes"
            },
            {
                "name": "Security Review",
                "capabilities": ["security", "python"],
                "description": "Need security review of Python application"
            }
        ]
        
        for scenario in scenarios:
            print(f"   🎯 Scenario: {scenario['name']}")
            print(f"   📋 Required: {scenario['capabilities']}")
            
            recommendations = self.verifier.get_capability_recommendations(
                required_capabilities=scenario["capabilities"],
                min_trust_score=0.3,
                max_recommendations=3
            )
            
            if recommendations:
                print(f"   📊 Found {len(recommendations)} recommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"      {i}. {rec.agent_id} - {rec.capability}")
                    print(f"         Confidence: {rec.confidence:.2f} | Trust: {rec.trust_score:.2f}")
                    print(f"         Success Rate: {rec.estimated_success_rate:.1%}")
                    print(f"         Reason: {rec.recommendation_reason}")
                    if rec.risk_factors:
                        print(f"         Risks: {', '.join(rec.risk_factors)}")
            else:
                print("   ❌ No suitable recommendations found")
            
            print()
    
    def demonstrate_agent_reputation(self) -> None:
        """Demonstrate agent reputation tracking and display"""
        print("🏆 Demonstrating Agent Reputation System...")
        
        for agent_data in self.demo_agents:
            agent_id = agent_data["agent_id"]
            reputation = self.verifier.get_agent_reputation(agent_id)
            
            print(f"   👤 Agent: {agent_id}")
            print(f"   🎖️  Overall Trust: {reputation['overall_trust_level']} "
                  f"(score: {reputation['overall_trust_score']:.2f})")
            print(f"   📈 Success Rate: {reputation.get('overall_success_rate', 0):.1%}")
            print(f"   🔢 Total Interactions: {reputation['total_interactions']}")
            print(f"   💼 Capabilities: {len(reputation['capabilities'])}")
            
            # Show top capabilities
            if reputation['capabilities']:
                sorted_caps = sorted(
                    reputation['capabilities'].items(),
                    key=lambda x: x[1]['trust_score'],
                    reverse=True
                )
                
                print(f"   🌟 Top Capabilities:")
                for cap_name, cap_data in sorted_caps[:3]:
                    print(f"      • {cap_name}: {cap_data['trust_level']} "
                          f"({cap_data['trust_score']:.2f})")
            
            print(f"   📝 Summary: {reputation['reputation_summary']}")
            print()
    
    def display_system_statistics(self) -> None:
        """Display comprehensive system statistics"""
        print("📊 System Statistics...")
        
        # Verification system stats
        verification_stats = self.verifier.get_verification_stats()
        print(f"   🧪 Tests Created: {verification_stats['tests_created']}")
        print(f"   ✅ Tests Completed: {verification_stats['tests_completed']}")
        print(f"   📈 Tests Passed: {verification_stats['tests_passed']}")
        print(f"   📉 Tests Failed: {verification_stats['tests_failed']}")
        print(f"   🎯 Trust Scores: {verification_stats['total_trust_scores']}")
        print(f"   💡 Recommendations Generated: {verification_stats['recommendations_generated']}")
        
        # Trust level distribution
        trust_distribution = verification_stats['trust_level_distribution']
        print(f"   🏆 Trust Level Distribution:")
        for level, count in trust_distribution.items():
            if count > 0:
                print(f"      • {level}: {count}")
        
        # Agent registry stats
        registry_stats = self.agent_registry.get_registry_stats()
        print(f"   🤖 Active Agents: {registry_stats['active_agents']}")
        print(f"   🔍 Discovery Messages: {registry_stats['discovery_messages_processed']}")
        print(f"   🎯 Capability Matches: {registry_stats['capability_matches_found']}")
        
        # Help system stats
        help_stats = self.help_system.get_help_system_stats()
        print(f"   🆘 Help Requests: {help_stats['requests_created']}")
        print(f"   🤝 Collaborations Started: {help_stats['collaborations_started']}")
        print(f"   ✅ Collaborations Completed: {help_stats['collaborations_completed']}")
        
        print()
    
    def run_demo(self) -> None:
        """Run the complete capability verification demo"""
        print("=" * 60)
        print("🎯 Beast Mode Capability Verification System Demo")
        print("=" * 60)
        print()
        
        try:
            # Setup
            self.setup_demo_agents()
            
            # Demonstrate core features
            self.demonstrate_capability_testing()
            self.simulate_interaction_history()
            self.demonstrate_collaboration_tracking()
            self.demonstrate_capability_recommendations()
            self.demonstrate_agent_reputation()
            
            # Show final statistics
            self.display_system_statistics()
            
            print("=" * 60)
            print("✅ Demo completed successfully!")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Demo failed with error: {e}")
            raise


def main():
    """Run the capability verification demo"""
    demo = CapabilityVerificationDemo()
    demo.run_demo()


if __name__ == "__main__":
    main()