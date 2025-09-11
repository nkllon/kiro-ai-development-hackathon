#!/usr/bin/env python3
"""
Beast Mode Collaboration Scheduler Demo

Demonstrates the collaboration scheduling system functionality including:
- Office hours management
- Collaboration session scheduling
- Asynchronous collaboration handling
- Pattern recognition and optimization
"""

import asyncio
import logging
from datetime import datetime, time, timedelta
from typing import List, Dict, Any

from src.beast_mode.messaging.bus_client import BeastModeBusClient
from src.beast_mode.messaging.collaboration_scheduler import (
    CollaborationType,
    OfficeHoursPattern,
    CollaborationStatus
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CollaborationSchedulerDemo:
    """Demonstration of collaboration scheduler functionality"""
    
    def __init__(self):
        self.agents: Dict[str, BeastModeBusClient] = {}
        self.demo_results: List[str] = []
    
    async def setup_agents(self) -> None:
        """Set up demo agents with different capabilities"""
        logger.info("Setting up demo agents...")
        
        # Agent 1: Python expert with testing focus
        agent1 = BeastModeBusClient(
            redis_url="redis://localhost:6379",
            agent_id="python_expert",
            capabilities=["python", "testing", "code_review", "debugging"]
        )
        
        # Agent 2: AI/ML specialist
        agent2 = BeastModeBusClient(
            redis_url="redis://localhost:6379",
            agent_id="ml_specialist",
            capabilities=["python", "machine_learning", "data_science", "tensorflow"]
        )
        
        # Agent 3: DevOps engineer
        agent3 = BeastModeBusClient(
            redis_url="redis://localhost:6379",
            agent_id="devops_engineer",
            capabilities=["docker", "kubernetes", "ci_cd", "monitoring"]
        )
        
        # Mock Redis connections for demo
        from unittest.mock import AsyncMock
        for agent in [agent1, agent2, agent3]:
            agent.client = AsyncMock()
            agent.client.publish = AsyncMock()
            agent.is_connected = True
        
        self.agents = {
            "python_expert": agent1,
            "ml_specialist": agent2,
            "devops_engineer": agent3
        }
        
        self.demo_results.append("✓ Set up 3 demo agents with different capabilities")
    
    async def demo_office_hours_management(self) -> None:
        """Demonstrate office hours management"""
        logger.info("Demonstrating office hours management...")
        
        # Set different office hours for each agent
        
        # Python expert: Daily 9-5
        python_expert = self.agents["python_expert"]
        await python_expert.announce_office_hours(
            pattern=OfficeHoursPattern.DAILY,
            start_time=time(9, 0),
            end_time=time(17, 0),
            description="Available for Python development and testing collaboration",
            capabilities_focus=["python", "testing", "code_review"]
        )
        
        # ML specialist: Weekdays 10-6
        ml_specialist = self.agents["ml_specialist"]
        await ml_specialist.announce_office_hours(
            pattern=OfficeHoursPattern.WEEKDAYS,
            start_time=time(10, 0),
            end_time=time(18, 0),
            description="ML/AI consultation and model development",
            capabilities_focus=["machine_learning", "data_science"]
        )
        
        # DevOps engineer: Custom schedule (Mon, Wed, Fri)
        devops_engineer = self.agents["devops_engineer"]
        await devops_engineer.announce_office_hours(
            pattern=OfficeHoursPattern.CUSTOM,
            start_time=time(8, 0),
            end_time=time(16, 0),
            days_of_week={0, 2, 4},  # Monday, Wednesday, Friday
            description="Infrastructure and deployment support",
            capabilities_focus=["docker", "kubernetes", "ci_cd"]
        )
        
        self.demo_results.append("✓ Set up office hours for all agents")
        
        # Check availability
        current_time = datetime(2024, 1, 3, 14, 0)  # Wednesday 2 PM
        
        for agent_id, agent in self.agents.items():
            available = agent.is_agent_available_for_collaboration(agent_id, current_time)
            status = "Available" if available else "Unavailable"
            self.demo_results.append(f"  - {agent_id}: {status} at {current_time.strftime('%A %I:%M %p')}")
        
        # Find next available slots
        logger.info("Finding next available collaboration slots...")
        for agent_id, agent in self.agents.items():
            next_slot = agent.get_next_available_collaboration_slot(agent_id, 30)
            if next_slot:
                self.demo_results.append(f"  - {agent_id}: Next 30-min slot at {next_slot.strftime('%A %I:%M %p')}")
    
    async def demo_collaboration_scheduling(self) -> None:
        """Demonstrate collaboration session scheduling"""
        logger.info("Demonstrating collaboration scheduling...")
        
        python_expert = self.agents["python_expert"]
        
        # Schedule collaboration with ML specialist
        try:
            request_id = await python_expert.request_collaboration(
                target_agents=["ml_specialist"],
                topic="ML model testing strategy",
                collaboration_type=CollaborationType.SCHEDULED_SESSION,
                scheduled_start=datetime(2024, 1, 3, 15, 0),  # Wednesday 3 PM
                duration_minutes=60,
                description="Discuss testing strategies for ML models in production",
                required_capabilities=["machine_learning", "testing"]
            )
            
            self.demo_results.append(f"✓ Scheduled collaboration session (Request ID: {request_id[:8]}...)")
            
            # Get the created session
            sessions = list(python_expert.collaboration_scheduler.sessions.values())
            if sessions:
                session = sessions[-1]  # Get the most recent session
                self.demo_results.append(f"  - Session ID: {session.session_id[:8]}...")
                self.demo_results.append(f"  - Topic: {session.topic}")
                self.demo_results.append(f"  - Participants: {', '.join(session.participants)}")
                self.demo_results.append(f"  - Scheduled: {session.scheduled_start.strftime('%A %I:%M %p')}")
                self.demo_results.append(f"  - Duration: {(session.scheduled_end - session.scheduled_start).total_seconds() / 60:.0f} minutes")
                
                return session.session_id
        
        except Exception as e:
            self.demo_results.append(f"✗ Failed to schedule collaboration: {e}")
            return None
    
    async def demo_collaboration_workflow(self, session_id: str) -> None:
        """Demonstrate complete collaboration workflow"""
        logger.info("Demonstrating collaboration workflow...")
        
        python_expert = self.agents["python_expert"]
        ml_specialist = self.agents["ml_specialist"]
        
        # Simulate ML specialist responding positively
        from src.beast_mode.messaging.models import BeastModeMessage, MessageType
        
        response_message = BeastModeMessage(
            type=MessageType.COLLABORATION_RESPONSE,
            source="ml_specialist",
            payload={
                "request_id": session_id,
                "available": True,
                "agent_capabilities": {
                    "agent_id": "ml_specialist",
                    "capabilities": ["python", "machine_learning", "data_science", "tensorflow"],
                    "availability": "ready_for_business"
                }
            }
        )
        
        await python_expert._handle_collaboration_response(response_message)
        self.demo_results.append("✓ ML specialist responded positively to collaboration request")
        
        # Start the collaboration session
        success = await python_expert.start_collaboration_session(session_id)
        if success:
            self.demo_results.append("✓ Started collaboration session")
            
            # Simulate some collaboration activity
            session = python_expert.collaboration_scheduler.get_session(session_id)
            if session:
                session.collaboration_data.update({
                    'topics_discussed': [
                        'Unit testing for ML models',
                        'Integration testing strategies',
                        'Performance testing approaches'
                    ],
                    'decisions_made': [
                        'Use pytest for unit tests',
                        'Implement model validation pipeline',
                        'Set up automated performance benchmarks'
                    ],
                    'action_items': [
                        'Create test framework template',
                        'Document testing best practices',
                        'Schedule follow-up session'
                    ]
                })
                
                self.demo_results.append("✓ Collaboration in progress - knowledge being exchanged")
                
                # Simulate collaboration completion
                await asyncio.sleep(0.1)  # Brief pause for realism
                
                success_metrics = {
                    "outcome": "successful",
                    "knowledge_shared": True,
                    "action_items_created": 3,
                    "follow_up_needed": True,
                    "satisfaction_score": 9.2
                }
                
                success = await python_expert.end_collaboration_session(
                    session_id,
                    success=True,
                    success_metrics=success_metrics
                )
                
                if success:
                    self.demo_results.append("✓ Successfully completed collaboration session")
                    self.demo_results.append(f"  - Satisfaction score: {success_metrics['satisfaction_score']}/10")
                    self.demo_results.append(f"  - Action items created: {success_metrics['action_items_created']}")
                    self.demo_results.append(f"  - Follow-up needed: {success_metrics['follow_up_needed']}")
    
    async def demo_asynchronous_collaboration(self) -> None:
        """Demonstrate asynchronous collaboration handling"""
        logger.info("Demonstrating asynchronous collaboration...")
        
        python_expert = self.agents["python_expert"]
        
        # Queue collaboration for an "offline" agent
        queue_id = python_expert.collaboration_scheduler.queue_offline_collaboration(
            target_agent="offline_agent",
            collaboration_type="code_review",
            data={
                "topic": "Review async/await patterns",
                "description": "Need expert review of asynchronous code patterns",
                "priority": "high",
                "estimated_duration": 45
            },
            priority=2
        )
        
        self.demo_results.append(f"✓ Queued offline collaboration (Queue ID: {queue_id[:8]}...)")
        
        # Simulate agent coming online and processing queue
        queued_requests = python_expert.collaboration_scheduler.process_offline_collaboration_queue("offline_agent")
        
        if queued_requests:
            request = queued_requests[0]
            self.demo_results.append("✓ Processed offline collaboration queue")
            self.demo_results.append(f"  - Found {len(queued_requests)} queued request(s)")
            self.demo_results.append(f"  - Topic: {request['data']['topic']}")
            self.demo_results.append(f"  - Priority: {request['priority']}")
            self.demo_results.append(f"  - Queued by: {request['requester']}")
    
    async def demo_pattern_recognition(self) -> None:
        """Demonstrate collaboration pattern recognition"""
        logger.info("Demonstrating pattern recognition...")
        
        python_expert = self.agents["python_expert"]
        
        # Create multiple completed sessions to simulate patterns
        from src.beast_mode.messaging.collaboration_scheduler import CollaborationSession
        
        # Simulate recurring weekly sessions with ML specialist
        base_time = datetime.now() - timedelta(days=21)  # 3 weeks ago
        
        for week in range(3):
            session_time = base_time + timedelta(weeks=week)
            
            session = CollaborationSession(
                organizer_id="python_expert",
                participants=["python_expert", "ml_specialist"],
                topic=f"Weekly ML/Testing sync - Week {week + 1}",
                session_type=CollaborationType.KNOWLEDGE_EXCHANGE,
                scheduled_start=session_time,
                scheduled_end=session_time + timedelta(minutes=45),
                actual_start=session_time,
                actual_end=session_time + timedelta(minutes=42),
                status=CollaborationStatus.COMPLETED,
                required_capabilities=["machine_learning", "testing"],
                success_metrics={
                    "success": True,
                    "satisfaction_score": 8.5 + (week * 0.3),  # Improving over time
                    "knowledge_shared": True
                }
            )
            
            python_expert.collaboration_scheduler.sessions[session.session_id] = session
        
        # Trigger pattern analysis
        python_expert.collaboration_scheduler._analyze_collaboration_patterns()
        
        self.demo_results.append("✓ Created collaboration history for pattern analysis")
        
        # Get recommendations based on patterns
        recommendations = python_expert.get_collaboration_recommendations()
        
        if recommendations:
            self.demo_results.append(f"✓ Generated {len(recommendations)} collaboration recommendation(s)")
            
            for i, rec in enumerate(recommendations[:2]):  # Show first 2 recommendations
                self.demo_results.append(f"  Recommendation {i + 1}:")
                self.demo_results.append(f"    - Participants: {', '.join(rec['participants'])}")
                self.demo_results.append(f"    - Success probability: {rec['success_probability']:.1%}")
                self.demo_results.append(f"    - Suggested duration: {rec['suggested_duration']:.0f} minutes")
                self.demo_results.append(f"    - Common topics: {', '.join(rec['common_topics'][:2])}")
                self.demo_results.append(f"    - Confidence: {rec['confidence']:.1%}")
        else:
            self.demo_results.append("✓ Pattern analysis complete (insufficient data for recommendations)")
    
    async def demo_collaboration_statistics(self) -> None:
        """Demonstrate collaboration statistics and monitoring"""
        logger.info("Demonstrating collaboration statistics...")
        
        # Collect statistics from all agents
        all_stats = {}
        
        for agent_id, agent in self.agents.items():
            stats = agent.get_collaboration_stats()
            all_stats[agent_id] = stats
        
        self.demo_results.append("✓ Collected collaboration statistics")
        
        # Display aggregated statistics
        total_sessions = sum(stats['total_sessions'] for stats in all_stats.values())
        total_successful = sum(stats['successful_sessions'] for stats in all_stats.values())
        
        self.demo_results.append(f"  - Total sessions across all agents: {total_sessions}")
        self.demo_results.append(f"  - Successful sessions: {total_successful}")
        
        if total_sessions > 0:
            success_rate = (total_successful / total_sessions) * 100
            self.demo_results.append(f"  - Overall success rate: {success_rate:.1f}%")
        
        # Show per-agent statistics
        for agent_id, stats in all_stats.items():
            if stats['total_sessions'] > 0:
                self.demo_results.append(f"  - {agent_id}:")
                self.demo_results.append(f"    • Sessions: {stats['total_sessions']}")
                self.demo_results.append(f"    • Success rate: {(stats['successful_sessions']/stats['total_sessions']*100):.1f}%")
                self.demo_results.append(f"    • Avg duration: {stats['average_duration']:.1f} minutes")
                self.demo_results.append(f"    • Active sessions: {stats['active_sessions']}")
    
    async def demo_collaboration_callbacks(self) -> None:
        """Demonstrate collaboration event callbacks"""
        logger.info("Demonstrating collaboration callbacks...")
        
        python_expert = self.agents["python_expert"]
        
        # Set up event tracking
        events_captured = []
        
        def on_collaboration_response(agent_id: str, payload: Dict[str, Any]) -> None:
            events_captured.append(f"Response from {agent_id}: {'Available' if payload.get('available') else 'Unavailable'}")
        
        def on_collaboration_start(session_id: str, payload: Dict[str, Any]) -> None:
            events_captured.append(f"Session started: {payload.get('topic', 'Unknown topic')}")
        
        def on_collaboration_end(session_id: str, success: bool, metrics: Dict[str, Any]) -> None:
            outcome = "successful" if success else "unsuccessful"
            events_captured.append(f"Session ended: {outcome} (score: {metrics.get('satisfaction_score', 'N/A')})")
        
        # Register callbacks
        python_expert.set_collaboration_callback('on_collaboration_response', on_collaboration_response)
        python_expert.set_collaboration_callback('on_collaboration_start', on_collaboration_start)
        python_expert.set_collaboration_callback('on_collaboration_end', on_collaboration_end)
        
        self.demo_results.append("✓ Set up collaboration event callbacks")
        
        # Simulate some events
        from src.beast_mode.messaging.models import BeastModeMessage, MessageType
        
        # Simulate response event
        response_msg = BeastModeMessage(
            type=MessageType.COLLABORATION_RESPONSE,
            source="callback_test_agent",
            payload={
                "request_id": "test123",
                "available": True,
                "agent_capabilities": {
                    "agent_id": "callback_test_agent",
                    "capabilities": ["python"],
                    "availability": "ready_for_business"
                }
            }
        )
        
        await python_expert._handle_collaboration_response(response_msg)
        
        # Display captured events
        if events_captured:
            self.demo_results.append(f"✓ Captured {len(events_captured)} collaboration event(s)")
            for event in events_captured:
                self.demo_results.append(f"  - {event}")
    
    async def cleanup_agents(self) -> None:
        """Clean up demo agents"""
        logger.info("Cleaning up demo agents...")
        
        for agent in self.agents.values():
            if hasattr(agent, 'collaboration_scheduler'):
                agent.collaboration_scheduler.stop_background_tasks()
        
        self.demo_results.append("✓ Cleaned up all demo agents")
    
    def print_demo_results(self) -> None:
        """Print demo results summary"""
        print("\n" + "="*60)
        print("BEAST MODE COLLABORATION SCHEDULER DEMO RESULTS")
        print("="*60)
        
        for result in self.demo_results:
            print(result)
        
        print("\n" + "="*60)
        print("Demo completed successfully!")
        print("="*60)


async def main():
    """Run the collaboration scheduler demo"""
    demo = CollaborationSchedulerDemo()
    
    try:
        # Run all demo scenarios
        await demo.setup_agents()
        await demo.demo_office_hours_management()
        
        session_id = await demo.demo_collaboration_scheduling()
        if session_id:
            await demo.demo_collaboration_workflow(session_id)
        
        await demo.demo_asynchronous_collaboration()
        await demo.demo_pattern_recognition()
        await demo.demo_collaboration_statistics()
        await demo.demo_collaboration_callbacks()
        
    except Exception as e:
        logger.error(f"Demo error: {e}")
        demo.demo_results.append(f"✗ Demo error: {e}")
    
    finally:
        await demo.cleanup_agents()
        demo.print_demo_results()


if __name__ == "__main__":
    asyncio.run(main())