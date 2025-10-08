#!/usr/bin/env python3
"""
Test Redis Execution Tracking
=============================
Simple test to verify Redis tracking functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.execution_tracking.redis_execution_tracker import (
    RedisExecutionTracker, ExecutionStatus
)

async def test_redis_tracking():
    """Test Redis tracking functionality."""
    print("🧪 Testing Redis Execution Tracking")
    print("=" * 50)
    
    tracker = RedisExecutionTracker()
    
    # Test initialization
    print("1. Testing Redis connection...")
    if await tracker.initialize():
        print("✅ Redis connection successful")
    else:
        print("❌ Redis connection failed")
        return False
    
    # Test starting an execution
    print("\n2. Testing execution start...")
    try:
        execution_id = await tracker.start_execution(
            spec_name="test-specification",
            total_tasks=5,
            workflow_version="v2.0"
        )
        print(f"✅ Execution started: {execution_id}")
    except Exception as e:
        print(f"❌ Failed to start execution: {e}")
        return False
    
    # Test check-in
    print("\n3. Testing check-in...")
    try:
        success = await tracker.checkin_execution(
            execution_id,
            phase="Test Phase",
            progress_percentage=50.0,
            message="Testing check-in functionality"
        )
        if success:
            print("✅ Check-in successful")
        else:
            print("❌ Check-in failed")
    except Exception as e:
        print(f"❌ Check-in error: {e}")
    
    # Test status update
    print("\n4. Testing status update...")
    try:
        success = await tracker.update_execution_status(
            execution_id,
            ExecutionStatus.COMPLETED,
            efficiency_gain=75.0
        )
        if success:
            print("✅ Status update successful")
        else:
            print("❌ Status update failed")
    except Exception as e:
        print(f"❌ Status update error: {e}")
    
    # Test getting execution record
    print("\n5. Testing execution retrieval...")
    try:
        record = await tracker.get_execution_record(execution_id)
        if record:
            print(f"✅ Retrieved execution: {record.spec_name} - {record.status.value}")
        else:
            print("❌ Failed to retrieve execution")
    except Exception as e:
        print(f"❌ Retrieval error: {e}")
    
    # Test getting history
    print("\n6. Testing execution history...")
    try:
        history = await tracker.get_execution_history(limit=5)
        print(f"✅ Retrieved {len(history)} execution(s) from history")
        for record in history:
            print(f"   - {record.spec_name}: {record.status.value}")
    except Exception as e:
        print(f"❌ History retrieval error: {e}")
    
    print("\n🎉 Redis tracking test completed!")
    return True

if __name__ == "__main__":
    asyncio.run(test_redis_tracking())