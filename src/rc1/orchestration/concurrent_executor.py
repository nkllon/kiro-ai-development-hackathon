"""
Concurrent Executor - Orchestrate independent agent execution
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from ..agents.base_agent import BaseAgent, AgentResult


@dataclass
class ExecutionSummary:
    """Summary of concurrent execution"""
    total_agents: int
    successful_agents: int
    failed_agents: int
    total_execution_time_ms: float
    start_time: datetime
    end_time: datetime
    agent_results: List[AgentResult]
    overall_success_rate: float


class ConcurrentExecutor:
    """Orchestrate independent agent execution with concurrency"""
    
    def __init__(self, agents: List[BaseAgent]):
        self.agents = agents
        self.execution_results: List[AgentResult] = []
        self.execution_summary: Optional[ExecutionSummary] = None
    
    async def execute_all_agents(self) -> List[AgentResult]:
        """Execute all agents concurrently"""
        start_time = datetime.now()
        
        try:
            # Create tasks for all agents
            tasks = []
            for agent in self.agents:
                task = asyncio.create_task(agent.execute_async())
                tasks.append(task)
            
            # Execute all agents concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    # Create error result for failed agent
                    error_result = AgentResult(
                        agent_name=self.agents[i].name,
                        success=False,
                        execution_time_ms=0.0,
                        start_time=start_time,
                        end_time=datetime.now(),
                        data={},
                        metrics={},
                        errors=[str(result)],
                        warnings=[]
                    )
                    processed_results.append(error_result)
                else:
                    processed_results.append(result)
            
            self.execution_results = processed_results
            
            # Generate execution summary
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds() * 1000
            
            successful_count = sum(1 for r in processed_results if r.success)
            failed_count = len(processed_results) - successful_count
            
            self.execution_summary = ExecutionSummary(
                total_agents=len(self.agents),
                successful_agents=successful_count,
                failed_agents=failed_count,
                total_execution_time_ms=total_time,
                start_time=start_time,
                end_time=end_time,
                agent_results=processed_results,
                overall_success_rate=(successful_count / len(processed_results)) * 100 if processed_results else 0.0
            )
            
            return processed_results
            
        except Exception as e:
            # Create summary even if execution fails
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds() * 1000
            
            self.execution_summary = ExecutionSummary(
                total_agents=len(self.agents),
                successful_agents=0,
                failed_agents=len(self.agents),
                total_execution_time_ms=total_time,
                start_time=start_time,
                end_time=end_time,
                agent_results=[],
                overall_success_rate=0.0
            )
            
            raise e
    
    def execute_all_agents_sync(self) -> List[AgentResult]:
        """Execute all agents synchronously (fallback)"""
        start_time = datetime.now()
        results = []
        
        for agent in self.agents:
            try:
                result = agent.execute()
                results.append(result)
            except Exception as e:
                # Create error result
                error_result = AgentResult(
                    agent_name=agent.name,
                    success=False,
                    execution_time_ms=0.0,
                    start_time=start_time,
                    end_time=datetime.now(),
                    data={},
                    metrics={},
                    errors=[str(e)],
                    warnings=[]
                )
                results.append(error_result)
        
        self.execution_results = results
        
        # Generate summary
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() * 1000
        
        successful_count = sum(1 for r in results if r.success)
        failed_count = len(results) - successful_count
        
        self.execution_summary = ExecutionSummary(
            total_agents=len(self.agents),
            successful_agents=successful_count,
            failed_agents=failed_count,
            total_execution_time_ms=total_time,
            start_time=start_time,
            end_time=end_time,
            agent_results=results,
            overall_success_rate=(successful_count / len(results)) * 100 if results else 0.0
        )
        
        return results
    
    def get_execution_summary(self) -> Optional[ExecutionSummary]:
        """Get execution summary"""
        return self.execution_summary
    
    def get_agent_results(self) -> List[AgentResult]:
        """Get all agent results"""
        return self.execution_results
    
    def get_successful_results(self) -> List[AgentResult]:
        """Get only successful agent results"""
        return [result for result in self.execution_results if result.success]
    
    def get_failed_results(self) -> List[AgentResult]:
        """Get only failed agent results"""
        return [result for result in self.execution_results if not result.success]
    
    def export_results(self, output_path: str) -> bool:
        """Export execution results to file"""
        try:
            import json
            
            export_data = {
                "execution_summary": asdict(self.execution_summary) if self.execution_summary else None,
                "agent_results": [asdict(result) for result in self.execution_results],
                "export_timestamp": datetime.now().isoformat()
            }
            
            # Convert datetime objects to strings
            if export_data["execution_summary"]:
                summary = export_data["execution_summary"]
                summary["start_time"] = summary["start_time"].isoformat() if isinstance(summary["start_time"], datetime) else summary["start_time"]
                summary["end_time"] = summary["end_time"].isoformat() if isinstance(summary["end_time"], datetime) else summary["end_time"]
            
            for result in export_data["agent_results"]:
                result["start_time"] = result["start_time"].isoformat() if isinstance(result["start_time"], datetime) else result["start_time"]
                result["end_time"] = result["end_time"].isoformat() if isinstance(result["end_time"], datetime) else result["end_time"]
            
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error exporting results: {e}")
            return False
    
    def print_execution_summary(self) -> None:
        """Print execution summary to console"""
        if not self.execution_summary:
            print("No execution summary available")
            return
        
        summary = self.execution_summary
        
        print("🚀 Concurrent Agent Execution Summary")
        print("=" * 50)
        print(f"📊 Total Agents: {summary.total_agents}")
        print(f"✅ Successful: {summary.successful_agents}")
        print(f"❌ Failed: {summary.failed_agents}")
        print(f"⏱️  Total Time: {summary.total_execution_time_ms:.2f}ms")
        print(f"📈 Success Rate: {summary.overall_success_rate:.1f}%")
        print(f"🕐 Start Time: {summary.start_time.isoformat()}")
        print(f"🕐 End Time: {summary.end_time.isoformat()}")
        
        if summary.failed_agents > 0:
            print("\n❌ Failed Agents:")
            for result in self.get_failed_results():
                print(f"  - {result.agent_name}: {', '.join(result.errors[:2])}")
        
        if summary.successful_agents > 0:
            print("\n✅ Successful Agents:")
            for result in self.get_successful_results():
                print(f"  - {result.agent_name}: {result.execution_time_ms:.2f}ms")
