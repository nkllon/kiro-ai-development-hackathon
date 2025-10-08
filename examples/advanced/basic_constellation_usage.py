#!/usr/bin/env python3
"""
Basic Constellation Orchestrator Usage Example.

This example demonstrates how to use the Constellation Orchestrator to execute
a DAG of AI prompts with dependency management.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from constellation_orchestrator import ConstellationOrchestrator, ConstellationConfig, TaskDefinition
from constellation_orchestrator.models.task_definition import TaskStatus
from constellation_orchestrator.observability.logging_config import setup_structured_logging


async def create_analysis_workflow() -> list[TaskDefinition]:
    """Create a realistic analysis workflow with dependencies."""
    
    tasks = [
        # Phase 1: Data Collection
        TaskDefinition(
            task_id="collect_requirements",
            prompt="""
            You are a business analyst. Please analyze the following scenario and provide requirements:
            
            Scenario: A company wants to build a new e-commerce platform.
            
            Please provide:
            1. 5 key functional requirements
            2. 3 key non-functional requirements
            3. Main user personas (2-3)
            
            Format your response as structured text.
            """,
            dependencies=[],
            timeout=60,
            category="analysis",
            priority=1,
            tags=["requirements", "business-analysis"]
        ),
        
        TaskDefinition(
            task_id="market_research",
            prompt="""
            You are a market researcher. Please provide a market analysis for e-commerce platforms:
            
            Please analyze:
            1. Current market trends in e-commerce
            2. Key competitors and their strengths
            3. Market opportunities and gaps
            4. Technology trends affecting e-commerce
            
            Provide a concise but comprehensive analysis.
            """,
            dependencies=[],
            timeout=60,
            category="research",
            priority=1,
            tags=["market-research", "competitive-analysis"]
        ),
        
        # Phase 2: Architecture Design (depends on requirements)
        TaskDefinition(
            task_id="system_architecture",
            prompt="""
            You are a system architect. Based on typical e-commerce requirements, design a system architecture.
            
            Please provide:
            1. High-level system architecture diagram (in text/ASCII)
            2. Key components and their responsibilities
            3. Technology stack recommendations
            4. Scalability considerations
            5. Security considerations
            
            Focus on modern, cloud-native architecture patterns.
            """,
            dependencies=["collect_requirements"],
            timeout=90,
            category="architecture",
            priority=2,
            tags=["architecture", "system-design"]
        ),
        
        TaskDefinition(
            task_id="database_design",
            prompt="""
            You are a database architect. Design a database schema for an e-commerce platform.
            
            Please provide:
            1. Entity-relationship diagram (in text format)
            2. Key entities and their attributes
            3. Relationships between entities
            4. Indexing strategy
            5. Data partitioning considerations
            
            Consider typical e-commerce entities: users, products, orders, payments, etc.
            """,
            dependencies=["collect_requirements"],
            timeout=90,
            category="database",
            priority=2,
            tags=["database", "data-modeling"]
        ),
        
        # Phase 3: Implementation Planning (depends on architecture)
        TaskDefinition(
            task_id="api_specification",
            prompt="""
            You are an API designer. Create API specifications for an e-commerce platform.
            
            Please provide:
            1. RESTful API endpoints for core functionality
            2. Request/response schemas (in JSON format)
            3. Authentication and authorization approach
            4. Error handling strategy
            5. API versioning strategy
            
            Focus on user management, product catalog, shopping cart, and order management.
            """,
            dependencies=["system_architecture", "database_design"],
            timeout=90,
            category="api-design",
            priority=3,
            tags=["api", "specification"]
        ),
        
        TaskDefinition(
            task_id="security_analysis",
            prompt="""
            You are a security architect. Perform a security analysis for the e-commerce platform.
            
            Please analyze:
            1. Key security threats and vulnerabilities
            2. Security controls and countermeasures
            3. Data protection and privacy considerations
            4. Compliance requirements (PCI DSS, GDPR)
            5. Security testing recommendations
            
            Provide actionable security recommendations.
            """,
            dependencies=["system_architecture", "api_specification"],
            timeout=90,
            category="security",
            priority=3,
            tags=["security", "compliance"]
        ),
        
        # Phase 4: Final Integration (depends on all previous phases)
        TaskDefinition(
            task_id="implementation_roadmap",
            prompt="""
            You are a project manager. Create an implementation roadmap for the e-commerce platform.
            
            Based on the analysis, architecture, and specifications, please provide:
            1. Development phases and milestones
            2. Resource requirements and team structure
            3. Timeline estimates for each phase
            4. Risk assessment and mitigation strategies
            5. Success criteria and KPIs
            
            Consider dependencies between different workstreams.
            """,
            dependencies=["api_specification", "security_analysis", "market_research"],
            timeout=120,
            category="planning",
            priority=4,
            tags=["roadmap", "project-management"]
        )
    ]
    
    return tasks


async def run_constellation_analysis():
    """Run the complete analysis workflow using Constellation Orchestrator."""
    
    print("🌟 Starting Constellation Orchestrator Analysis Workflow")
    print("=" * 60)
    
    # Setup logging
    setup_structured_logging(log_level="INFO", json_output=False)
    
    # Create configuration
    config = ConstellationConfig.load_from_env()
    print(f"📋 Configuration:")
    print(f"   - Max concurrent agents: {config.max_concurrent_agents}")
    print(f"   - Claude CLI path: {config.claude_cli_path}")
    print(f"   - Redis URL: {config.redis_url}")
    
    # Create orchestrator
    orchestrator = ConstellationOrchestrator(config)
    
    try:
        # Initialize orchestrator
        print("\n🔧 Initializing orchestrator...")
        success = await orchestrator.initialize()
        if not success:
            print("❌ Failed to initialize orchestrator")
            return False
        
        print("✅ Orchestrator initialized successfully")
        
        # Create analysis workflow
        print("\n📝 Creating analysis workflow...")
        tasks = await create_analysis_workflow()
        print(f"✅ Created {len(tasks)} tasks")
        
        # Load tasks into orchestrator
        print("\n📥 Loading tasks...")
        success = await orchestrator.load_tasks(tasks)
        if not success:
            print("❌ Failed to load tasks")
            return False
        
        # Validate DAG
        print("\n🔍 Validating DAG structure...")
        validation_result = await orchestrator.dag_manager.validate_dag()
        
        if not validation_result.is_valid:
            print("❌ DAG validation failed:")
            for error in validation_result.validation_errors:
                print(f"   - {error}")
            return False
        
        print("✅ DAG validation successful")
        print(f"   - Execution order: {' → '.join(validation_result.execution_order[:3])}...")
        
        # Get DAG statistics
        stats = orchestrator.dag_manager.get_dag_statistics()
        print(f"   - Total tasks: {stats['total_tasks']}")
        print(f"   - Root tasks: {stats['root_tasks']}")
        print(f"   - Max depth: {stats['max_depth']}")
        print(f"   - Critical path length: {stats['critical_path_length']}")
        
        # Start execution
        print("\n🚀 Starting execution...")
        execution_id = await orchestrator.start_execution("e_commerce_analysis")
        if not execution_id:
            print("❌ Failed to start execution")
            return False
        
        print(f"✅ Execution started: {execution_id}")
        
        # Monitor execution progress
        print("\n⏳ Monitoring execution progress...")
        print("   (This may take several minutes depending on task complexity)")
        
        last_completed = 0
        for i in range(600):  # Wait up to 10 minutes
            execution_state = await orchestrator.get_execution_state(execution_id)
            if not execution_state:
                print("❌ Could not get execution state")
                break
            
            # Show progress updates
            if execution_state.metrics.completed_tasks != last_completed:
                print(f"   📊 Progress: {execution_state.metrics.completed_tasks}/{execution_state.metrics.total_tasks} completed, "
                      f"{execution_state.metrics.failed_tasks} failed, {execution_state.metrics.running_tasks} running")
                
                # Show which tasks completed
                if execution_state.metrics.completed_tasks > last_completed:
                    completed_tasks = execution_state.get_tasks_by_status(TaskStatus.COMPLETED)
                    new_completed = completed_tasks[last_completed:]
                    for task_id in new_completed:
                        print(f"      ✅ {task_id}")
                
                last_completed = execution_state.metrics.completed_tasks
            
            # Check if execution is complete
            if execution_state.is_execution_complete():
                print(f"\n🎉 Execution completed!")
                print(f"   - Total tasks: {execution_state.metrics.total_tasks}")
                print(f"   - Completed: {execution_state.metrics.completed_tasks}")
                print(f"   - Failed: {execution_state.metrics.failed_tasks}")
                print(f"   - Success rate: {execution_state.metrics.get_success_rate():.1f}%")
                print(f"   - Average duration: {execution_state.metrics.average_task_duration:.2f}s")
                print(f"   - Tasks per minute: {execution_state.metrics.tasks_per_minute:.2f}")
                
                # Show failed tasks if any
                if execution_state.metrics.failed_tasks > 0:
                    failed_tasks = execution_state.get_failed_tasks()
                    print(f"\n❌ Failed tasks:")
                    for task_id in failed_tasks:
                        if task_id in execution_state.task_results:
                            result = execution_state.task_results[task_id]
                            print(f"   - {task_id}: {result.error}")
                
                break
            
            await asyncio.sleep(2)
        else:
            print("\n⚠️  Execution did not complete within timeout")
            execution_state = await orchestrator.get_execution_state(execution_id)
            if execution_state:
                print(f"   Final status: {execution_state.metrics.completed_tasks}/{execution_state.metrics.total_tasks} completed")
        
        return True
        
    except Exception as e:
        print(f"\n💥 Execution failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Shutdown orchestrator
        print("\n🔄 Shutting down orchestrator...")
        await orchestrator.shutdown()
        print("✅ Shutdown complete")


async def main():
    """Main function."""
    try:
        success = await run_constellation_analysis()
        if success:
            print("\n🎊 Analysis workflow completed successfully!")
            return 0
        else:
            print("\n❌ Analysis workflow failed")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️  Execution interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)