#!/usr/bin/env python3
"""
Example: LLM-Powered Code Review Workflow
Description: Demonstrates automated code review using LLM providers

This example shows how to create a comprehensive code review workflow
that uses LLM providers to analyze code quality, security, and best practices.
It demonstrates cost-aware LLM selection and parallel review processes.

Key concepts demonstrated:
- LLM task execution with cost management
- Multi-stage code review pipeline
- Parallel analysis with different LLM providers
- Cost optimization and budget management
- Integration with development workflows
"""

import sys
import time
from pathlib import Path
from typing import List, Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from dag_orchestration.core.dag_orchestrator import DAGOrchestrator
from dag_orchestration.core.task_definition import TaskDefinition
from dag_orchestration.execution.parallel_execution_engine import ParallelExecutionEngine
from dag_orchestration.execution.llm_orchestration_manager import LLMOrchestrationManager
from rm_ddd.core.dag_registry import DAGRegistry


def create_code_review_tasks(code_files: List[str], budget: float = 10.0) -> List[TaskDefinition]:
    """
    Create LLM-powered code review tasks.
    
    Args:
        code_files: List of code files to review
        budget: Budget limit for LLM usage
        
    Returns:
        List[TaskDefinition]: Code review tasks
    """
    
    tasks = []
    
    # Initial setup task
    tasks.append(TaskDefinition(
        id="setup-review",
        name="Setup Code Review Environment",
        description="Prepare environment for code review analysis",
        command="echo '🔧 Setting up code review environment...' && sleep 1",
        executor="shell",
        dependencies=[],
        timeout=30
    ))
    
    # Code analysis tasks (can run in parallel)
    for i, code_file in enumerate(code_files):
        
        # Static analysis task
        tasks.append(TaskDefinition(
            id=f"static-analysis-{i}",
            name=f"Static Analysis: {Path(code_file).name}",
            description=f"Perform static analysis on {code_file}",
            command=f"echo '🔍 Analyzing {code_file} for syntax and style issues...' && sleep 2",
            executor="shell",
            dependencies=["setup-review"],
            timeout=60
        ))
        
        # Security analysis with LLM
        tasks.append(TaskDefinition(
            id=f"security-review-{i}",
            name=f"Security Review: {Path(code_file).name}",
            description=f"LLM-powered security analysis of {code_file}",
            command=f"""
Analyze the following code file for security vulnerabilities and best practices:

File: {code_file}

Please review for:
1. SQL injection vulnerabilities
2. XSS vulnerabilities  
3. Authentication/authorization issues
4. Input validation problems
5. Cryptographic weaknesses
6. Information disclosure risks

Provide specific recommendations for each issue found.
            """.strip(),
            executor="llm",
            dependencies=[f"static-analysis-{i}"],
            timeout=300,
            resource_requirements={"cost_limit": budget * 0.3}  # 30% of budget per file
        ))
        
        # Code quality review with LLM
        tasks.append(TaskDefinition(
            id=f"quality-review-{i}",
            name=f"Quality Review: {Path(code_file).name}",
            description=f"LLM-powered code quality analysis of {code_file}",
            command=f"""
Review the following code file for quality and best practices:

File: {code_file}

Please analyze:
1. Code structure and organization
2. Naming conventions and clarity
3. Error handling patterns
4. Performance considerations
5. Maintainability and readability
6. Documentation quality
7. Test coverage adequacy

Provide actionable improvement suggestions with examples.
            """.strip(),
            executor="llm",
            dependencies=[f"static-analysis-{i}"],
            timeout=300,
            resource_requirements={"cost_limit": budget * 0.3}
        ))
        
        # Architecture review with LLM (for larger files)
        if Path(code_file).stat().st_size > 10000:  # Files larger than 10KB
            tasks.append(TaskDefinition(
                id=f"architecture-review-{i}",
                name=f"Architecture Review: {Path(code_file).name}",
                description=f"LLM-powered architecture analysis of {code_file}",
                command=f"""
Perform an architectural review of the following code file:

File: {code_file}

Focus on:
1. Design patterns usage
2. SOLID principles adherence
3. Coupling and cohesion
4. Scalability considerations
5. Integration patterns
6. Dependency management

Suggest architectural improvements and refactoring opportunities.
                """.strip(),
                executor="llm",
                dependencies=[f"static-analysis-{i}"],
                timeout=400,
                resource_requirements={"cost_limit": budget * 0.2}
            ))
    
    # Consolidation tasks
    security_deps = [f"security-review-{i}" for i in range(len(code_files))]
    quality_deps = [f"quality-review-{i}" for i in range(len(code_files))]
    architecture_deps = [f"architecture-review-{i}" for i in range(len(code_files)) 
                        if Path(code_files[i]).stat().st_size > 10000]
    
    # Consolidate security findings
    tasks.append(TaskDefinition(
        id="consolidate-security",
        name="Consolidate Security Findings",
        description="Consolidate security review findings across all files",
        command="""
Consolidate and prioritize the security findings from all file reviews:

1. Categorize findings by severity (Critical, High, Medium, Low)
2. Identify patterns across multiple files
3. Prioritize fixes based on risk and impact
4. Create actionable remediation plan
5. Suggest security best practices for the codebase

Generate a comprehensive security report with clear next steps.
        """.strip(),
        executor="llm",
        dependencies=security_deps,
        timeout=300,
        resource_requirements={"cost_limit": budget * 0.1}
    ))
    
    # Consolidate quality findings
    tasks.append(TaskDefinition(
        id="consolidate-quality",
        name="Consolidate Quality Findings", 
        description="Consolidate code quality findings across all files",
        command="""
Consolidate and summarize the code quality findings from all file reviews:

1. Identify common quality issues across files
2. Prioritize improvements by impact and effort
3. Suggest coding standards and guidelines
4. Recommend refactoring opportunities
5. Create quality improvement roadmap

Generate a comprehensive quality report with actionable recommendations.
        """.strip(),
        executor="llm",
        dependencies=quality_deps,
        timeout=300,
        resource_requirements={"cost_limit": budget * 0.1}
    ))
    
    # Generate final report
    final_deps = ["consolidate-security", "consolidate-quality"]
    if architecture_deps:
        tasks.append(TaskDefinition(
            id="consolidate-architecture",
            name="Consolidate Architecture Findings",
            description="Consolidate architectural review findings",
            command="""
Consolidate architectural findings and recommendations:

1. Identify architectural patterns and anti-patterns
2. Suggest system-wide improvements
3. Recommend design pattern applications
4. Create architectural evolution roadmap

Generate architectural improvement recommendations.
            """.strip(),
            executor="llm",
            dependencies=architecture_deps,
            timeout=300,
            resource_requirements={"cost_limit": budget * 0.05}
        ))
        final_deps.append("consolidate-architecture")
    
    # Final comprehensive report
    tasks.append(TaskDefinition(
        id="generate-final-report",
        name="Generate Final Code Review Report",
        description="Generate comprehensive code review report",
        command="""
Create a comprehensive code review report that includes:

1. Executive Summary
   - Overall code health assessment
   - Key findings and recommendations
   - Priority action items

2. Security Assessment
   - Critical security issues
   - Security best practices recommendations
   - Risk mitigation strategies

3. Quality Assessment  
   - Code quality metrics and trends
   - Maintainability recommendations
   - Technical debt analysis

4. Architecture Assessment (if applicable)
   - Architectural strengths and weaknesses
   - Design improvement opportunities
   - Scalability considerations

5. Action Plan
   - Prioritized list of improvements
   - Estimated effort and impact
   - Implementation timeline suggestions

Format as a professional report suitable for development teams and management.
        """.strip(),
        executor="llm",
        dependencies=final_deps,
        timeout=400,
        resource_requirements={"cost_limit": budget * 0.05}
    ))
    
    return tasks


def monitor_llm_costs(llm_manager: LLMOrchestrationManager, budget: float):
    """Monitor LLM costs during execution."""
    
    print("💰 LLM Cost Monitoring")
    print("-" * 25)
    
    while True:
        try:
            cost_summary = llm_manager.get_cost_summary()
            
            print(f"💳 Current cost: ${cost_summary.total_cost:.2f}")
            print(f"💰 Budget remaining: ${cost_summary.budget_remaining:.2f}")
            print(f"📊 Usage by provider: {cost_summary.cost_by_provider}")
            
            # Alert if approaching budget limit
            if cost_summary.budget_remaining < budget * 0.2:  # Less than 20% remaining
                print("⚠️  WARNING: Approaching budget limit!")
            
            if cost_summary.budget_remaining <= 0:
                print("🛑 BUDGET EXCEEDED: Stopping execution")
                break
                
            time.sleep(10)  # Check every 10 seconds
            
        except Exception as e:
            print(f"⚠️  Cost monitoring error: {e}")
            break


def main():
    """Main execution function."""
    
    print("🚀 Example: LLM-Powered Code Review Workflow")
    print("=" * 50)
    print("Demonstrates automated code review using LLM providers")
    print()
    
    # Configuration
    code_files = [
        "src/dag_orchestration/core/dag_orchestrator.py",
        "src/dag_orchestration/execution/parallel_execution_engine.py", 
        "src/dag_orchestration/execution/llm_orchestration_manager.py"
    ]
    
    # Filter to existing files only
    existing_files = [f for f in code_files if Path(f).exists()]
    if not existing_files:
        print("⚠️  No code files found for review. Using simulated files.")
        existing_files = ["example_file_1.py", "example_file_2.py"]
    
    budget = 5.0  # $5 budget for this review
    
    try:
        # Create orchestrator with LLM support
        print("🔧 Initializing LLM-powered code review orchestrator...")
        
        dag_registry = DAGRegistry()
        execution_engine = ParallelExecutionEngine(max_workers=4)
        llm_manager = LLMOrchestrationManager(
            cost_budget=budget,
            preferred_providers=["cursor", "kiro"]  # Prefer subscription models
        )
        
        orchestrator = DAGOrchestrator(
            dag_registry=dag_registry,
            execution_engine=execution_engine,
            llm_manager=llm_manager
        )
        
        # Check LLM availability
        available_llms = list(llm_manager.available_llms.keys())
        if not available_llms:
            print("❌ No LLM providers available")
            print("💡 Install LLM CLI tools (cursor, claude, kiro) to run this example")
            return False
        
        print(f"🤖 Available LLMs: {available_llms}")
        print(f"💰 Budget: ${budget}")
        
        # Create code review tasks
        print(f"📝 Creating code review tasks for {len(existing_files)} files...")
        tasks = create_code_review_tasks(existing_files, budget)
        print(f"✅ Created {len(tasks)} review tasks")
        
        # Show task breakdown
        print(f"\n📋 Task Breakdown:")
        llm_tasks = [t for t in tasks if t.executor == "llm"]
        shell_tasks = [t for t in tasks if t.executor == "shell"]
        print(f"   LLM tasks: {len(llm_tasks)}")
        print(f"   Shell tasks: {len(shell_tasks)}")
        
        # Validate DAG structure
        print("\n🔍 Validating code review workflow...")
        validation = orchestrator.validate_dag(tasks)
        
        if not validation.is_valid:
            print("❌ Workflow validation failed:")
            for error in validation.errors:
                print(f"   • {error}")
            return False
        
        print("✅ Workflow validation passed")
        
        # Show execution plan
        print(f"\n📊 Execution Plan:")
        print(f"   Total tasks: {len(tasks)}")
        print(f"   Estimated LLM cost: ${budget}")
        print(f"   Parallel execution groups:")
        
        # Group tasks by dependency level for display
        dependency_levels = {}
        for task in tasks:
            level = len(task.dependencies)
            if level not in dependency_levels:
                dependency_levels[level] = []
            dependency_levels[level].append(task.name)
        
        for level, level_tasks in sorted(dependency_levels.items()):
            print(f"     Level {level}: {len(level_tasks)} tasks")
        
        # Execute code review workflow
        print(f"\n🎯 Executing code review workflow...")
        
        # Start cost monitoring in background
        import threading
        cost_monitor = threading.Thread(
            target=monitor_llm_costs, 
            args=(llm_manager, budget)
        )
        cost_monitor.daemon = True
        cost_monitor.start()
        
        start_time = time.time()
        result = orchestrator.execute_dag(tasks)
        execution_time = time.time() - start_time
        
        # Report results
        print(f"\n📊 Code Review Results:")
        print("=" * 30)
        print(f"   Status: {result.status}")
        print(f"   Total tasks: {result.total_tasks}")
        print(f"   Completed: {len(result.completed_tasks)}")
        print(f"   Failed: {len(result.failed_tasks)}")
        print(f"   Execution time: {execution_time:.2f}s")
        
        # Show cost summary
        cost_summary = llm_manager.get_cost_summary()
        print(f"\n💰 Cost Summary:")
        print(f"   Total cost: ${cost_summary.total_cost:.2f}")
        print(f"   Budget used: {(cost_summary.total_cost/budget)*100:.1f}%")
        print(f"   Cost by provider: {cost_summary.cost_by_provider}")
        
        # Show LLM task results
        llm_results = [r for r in result.completed_tasks if 'llm' in r.task_id or 'review' in r.task_id]
        if llm_results:
            print(f"\n🤖 LLM Review Results:")
            for task_result in llm_results:
                print(f"   ✅ {task_result.task_id}: {task_result.duration:.1f}s")
                if hasattr(task_result, 'cost') and task_result.cost > 0:
                    print(f"      Cost: ${task_result.cost:.3f}")
        
        if result.failed_tasks:
            print(f"\n❌ Failed Tasks:")
            for task_result in result.failed_tasks:
                print(f"   • {task_result.task_id}: {task_result.error}")
        
        # Success determination
        success = result.status == "COMPLETED" and len(result.failed_tasks) == 0
        
        if success:
            print(f"\n🎉 Code review workflow completed successfully!")
            print(f"💡 Generated comprehensive review covering security, quality, and architecture")
            print(f"💰 Stayed within budget: ${cost_summary.total_cost:.2f} / ${budget}")
        else:
            print(f"\n🛑 Code review workflow failed")
            print(f"💡 Check failed tasks and LLM provider availability")
        
        return success
        
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)