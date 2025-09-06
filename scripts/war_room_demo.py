#!/usr/bin/env python3
"""
War Room Mode Demo

Launch the real-time DevOps dashboard server with simulated data.
"All hands on deck, show me everything"

Usage:
    python scripts/war_room_demo.py
    
Then open: http://localhost:8080
"""

import asyncio
import random
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from beast_mode.monitoring.war_room_server import WarRoomServer
from beast_mode.monitoring.events import Event, EventSeverity


async def simulate_events(server: WarRoomServer):
    """Simulate real-time events for the dashboard"""
    
    event_types = [
        ("test_execution", "Unit tests completed", EventSeverity.INFO),
        ("deployment", "Production deployment started", EventSeverity.INFO),
        ("hubris_prevention", "Emergency bypass attempt blocked", EventSeverity.WARNING),
        ("system_health", "CPU usage spike detected", EventSeverity.WARNING),
        ("security", "Unauthorized access attempt", EventSeverity.ERROR),
        ("mama_discovery", "Accountability chain activated", EventSeverity.WARNING),
        ("build_failure", "Build pipeline failed", EventSeverity.ERROR),
        ("recovery", "System auto-recovery initiated", EventSeverity.INFO)
    ]
    
    # Initial metrics
    await server.update_metrics({
        "test_pass_rate": 94.5,
        "system_health_score": 87.2,
        "deployment_status": "deploying"
    })
    
    await asyncio.sleep(3)
    
    for i in range(100):  # Simulate 100 events
        await asyncio.sleep(random.uniform(2, 8))  # Random intervals
        
        # Pick random event type
        event_type, message, severity = random.choice(event_types)
        
        # Create event
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            timestamp=datetime.now(),
            source="demo_simulator",
            data={"message": message, "simulation": True},
            severity=severity,
            tags=["demo", "simulation"]
        )
        
        # Publish event
        await server.publish_event(event)
        
        # Occasionally update metrics
        if i % 5 == 0:
            await server.update_metrics({
                "test_pass_rate": random.uniform(85, 98),
                "system_health_score": random.uniform(75, 95),
                "deployment_status": random.choice(["stable", "deploying", "rolling_back"])
            })
        
        # Occasionally create incidents
        if i % 15 == 0 and random.random() < 0.3:
            incident_titles = [
                "High CPU usage on production servers",
                "Database connection pool exhausted",
                "Hubris prevention system activated",
                "Deployment rollback required",
                "Security breach attempt detected"
            ]
            
            # This would normally be done via API call, but we'll simulate
            server.active_incidents.append({
                "id": str(uuid.uuid4()),
                "title": random.choice(incident_titles),
                "severity": random.choice(["low", "medium", "high"]),
                "status": "open",
                "created_at": datetime.now().isoformat(),
                "created_by": "system",
                "description": "Auto-generated incident from monitoring system"
            })
        
        print(f"📡 Event {i+1}: {message} ({severity.value})")


async def main():
    """Run the War Room demo"""
    print("🚨 Starting Beast Mode War Room Dashboard...")
    print("📡 Server will be available at: http://localhost:8080")
    print("🔥 Press Ctrl+C to stop")
    print()
    
    # Create server
    server = WarRoomServer(host="0.0.0.0", port=8080)
    
    try:
        # Start server and event simulation concurrently
        await asyncio.gather(
            server.start_server(),
            simulate_events(server)
        )
    except KeyboardInterrupt:
        print("\n🚨 War Room dashboard stopped. Stay safe out there!")


if __name__ == "__main__":
    asyncio.run(main())