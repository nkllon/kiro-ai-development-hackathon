#!/usr/bin/env python3
"""
Demo script showing the complete task processing workflow.

This demonstrates the integration between:
- Conversation state machine
- Task state machine  
- Multi-layered persistence
- Task processing with isolation
"""

import asyncio
import logging
from datetime import datetime
from unittest.mock import AsyncMock

from src.beast_mode.task_queue.models import (
    ConversationContext,
    TaskContext,
    PersistenceConfig,
    RedisConfig
)
from src.beast_mode.task_queue.persistence import StatePersistenceManager
from src.beast_mode.task_queue.task_processor import TaskProcessor, TaskWorkflowOrchestrator


async def demo_task_processing_workflow():
    """Demonstrate complete task processing workflow."""
    print("🚀 Claude Code Redis Task Queue Integration Demo")
    print("=" * 60)
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create mock Redis client
    mock_redis = AsyncMock()
    mock_redis.setex = AsyncMock(return_value=True)
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.xadd = AsyncMock(return_value=b"1234567890-0")
    mock_redis.expire = AsyncMock(return_value=True)
    mock_redis.xrevrange = AsyncMock(return_value=[])
    
    # Create persistence configuration
    persistence_config = PersistenceConfig(
        hot_storage_ttl_hours=1,
        warm_storage_ttl_days=7,
        cold_storage_ttl_days=30,
        checkpoint_storage_ttl_days=90,
        enable_compression=False,
        integrity_checking=True
    )
    
    # Initialize components
    persistence_manager = StatePersistenceManager(mock_redis, persistence_config)
    task_processor = TaskProcessor(persistence_manager)
    orchestrator = TaskWorkflowOrchestrator(task_processor)
    
    print(f"✅ Initialized task processing components")
    print(f"   - Persistence manager with {len(['hot', 'warm', 'cold', 'checkpoint'])} storage layers")
    print(f"   - Task processor with {len(task_processor.task_handlers)} default handlers")
    print(f"   - Workflow orchestrator with concurrency limit: {orchestrator.concurrent_limit}")
    print()
    
    # Create conversation context
    conversation = ConversationContext(
        conversation_id="demo-conversation-001"
    )
    
    print(f"📝 Created conversation context: {conversation.conversation_id}")
    print(f"   - Initial state: {conversation.current_state.name}")
    print(f"   - Session start: {conversation.session_start}")
    print()
    
    # Create sample tasks
    tasks = [
        TaskContext(
            task_id="task-001",
            task_type="code_generation",
            task_content="Generate a Python function to calculate fibonacci numbers",
            task_parameters={"language": "python", "function_name": "fibonacci"}
        ),
        TaskContext(
            task_id="task-002", 
            task_type="file_analysis",
            task_content="Analyze the generated fibonacci function for performance",
            task_parameters={"file_path": "fibonacci.py", "analysis_type": "performance"}
        ),
        TaskContext(
            task_id="task-003",
            task_type="testing",
            task_content="Create unit tests for the fibonacci function",
            task_parameters={"test_framework": "pytest", "coverage_target": 95}
        )
    ]
    
    print(f"📋 Created {len(tasks)} sample tasks:")
    for i, task in enumerate(tasks, 1):
        print(f"   {i}. {task.task_type}: {task.task_content[:50]}...")
    print()
    
    # Process tasks individually to show state transitions
    print("🔄 Processing tasks with full state machine integration...")
    print()
    
    for i, task in enumerate(tasks, 1):
        print(f"Task {i}/{len(tasks)}: {task.task_type} ({task.task_id})")
        print("-" * 50)
        
        start_time = datetime.now()
        
        # Process the task
        result = await task_processor.process_task_workflow(conversation, task)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds() * 1000
        
        # Display results
        status_emoji = "✅" if result.success else "❌"
        print(f"{status_emoji} Task completed: {result.success}")
        print(f"   - Execution time: {result.execution_time_ms:.2f}ms")
        print(f"   - Total processing time: {processing_time:.2f}ms")
        print(f"   - Final conversation state: {conversation.current_state.name}")
        
        if result.success and result.result_data:
            print(f"   - Result keys: {list(result.result_data.keys())}")
        elif not result.success:
            print(f"   - Error: {result.error_message}")
        
        print(f"   - Conversation turns: {len(conversation.conversation_turns)}")
        print(f"   - Completed tasks: {len(conversation.completed_tasks)}")
        print(f"   - State version: {conversation.state_version}")
        print()
    
    # Demonstrate batch processing
    print("🚀 Demonstrating batch processing...")
    print("-" * 50)
    
    # Create additional tasks for batch processing
    batch_tasks = [
        TaskContext(
            task_id=f"batch-task-{i:03d}",
            task_type="documentation",
            task_content=f"Generate documentation for module {i}",
            task_parameters={"format": "markdown", "module": f"module_{i}"}
        )
        for i in range(1, 4)
    ]
    
    batch_start_time = datetime.now()
    batch_results = await orchestrator.process_task_batch(conversation, batch_tasks)
    batch_end_time = datetime.now()
    batch_processing_time = (batch_end_time - batch_start_time).total_seconds() * 1000
    
    successful_tasks = sum(1 for result in batch_results if result.success)
    failed_tasks = len(batch_results) - successful_tasks
    
    print(f"✅ Batch processing completed:")
    print(f"   - Total tasks: {len(batch_tasks)}")
    print(f"   - Successful: {successful_tasks}")
    print(f"   - Failed: {failed_tasks}")
    print(f"   - Total processing time: {batch_processing_time:.2f}ms")
    print(f"   - Average time per task: {batch_processing_time/len(batch_tasks):.2f}ms")
    print()
    
    # Show final conversation state
    print("📊 Final Conversation State Summary")
    print("=" * 60)
    print(f"Conversation ID: {conversation.conversation_id}")
    print(f"Current State: {conversation.current_state.name}")
    print(f"State Version: {conversation.state_version}")
    print(f"Total Turns: {len(conversation.conversation_turns)}")
    print(f"Completed Tasks: {len(conversation.completed_tasks)}")
    print(f"Failed Tasks: {len(conversation.failed_tasks)}")
    print(f"Checkpoints Created: {len(conversation.checkpoints)}")
    print(f"Session Duration: {(datetime.now() - conversation.session_start).total_seconds():.2f}s")
    
    # Show workflow status
    workflow_status = await orchestrator.get_workflow_status()
    print(f"\nWorkflow Status:")
    print(f"Active Workflows: {workflow_status['active_workflows']}")
    print(f"Active Executions: {workflow_status['active_executions']}")
    print(f"Concurrent Limit: {workflow_status['concurrent_limit']}")
    
    print("\n🎉 Demo completed successfully!")
    print("   The task processing workflow demonstrates:")
    print("   ✅ Complete state machine integration")
    print("   ✅ Multi-layered persistence")
    print("   ✅ Task isolation and resource management")
    print("   ✅ Error handling and recovery")
    print("   ✅ Batch processing capabilities")
    print("   ✅ Comprehensive monitoring and observability")


if __name__ == "__main__":
    asyncio.run(demo_task_processing_workflow())