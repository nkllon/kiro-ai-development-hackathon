#!/usr/bin/env python3
"""
Run Third Wave Parallel Module Fixing - Execute third wave of specialized agents
================================================================================

This script runs the third wave of specialized agents in parallel to fix
remaining missing modules and achieve 50%+ test collection success.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Execute third wave of parallel module fixing agents
"""

import os
import sys
import subprocess
import threading
import time
import json
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class AgentExecution:
    """Agent execution result."""
    agent_name: str
    success: bool
    modules_fixed: int
    duration: float
    output: str
    error: str = ""

class ThirdWaveParallelFixingRunner:
    """Runs third wave of module fixing agents in parallel."""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.agents = [
            "scripts/agent_import_resolver_fixer.py",
            "scripts/agent_syntax_fixer.py",
            "scripts/comprehensive_module_fixer.py"
        ]
        self.results = []
    
    def run_agent(self, agent_script: str) -> AgentExecution:
        """Run a single agent script."""
        start_time = datetime.now()
        agent_name = Path(agent_script).stem
        
        print(f"🚀 Starting {agent_name}...")
        
        try:
            result = subprocess.run([
                'python3', agent_script
            ], capture_output=True, text=True, timeout=300)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Parse JSON output if available
            modules_fixed = 0
            if result.stdout:
                try:
                    output_data = json.loads(result.stdout)
                    modules_fixed = output_data.get('modules_fixed', 0)
                except:
                    # Fallback: count success indicators
                    modules_fixed = result.stdout.count('✅')
            
            success = result.returncode == 0
            
            return AgentExecution(
                agent_name=agent_name,
                success=success,
                modules_fixed=modules_fixed,
                duration=duration,
                output=result.stdout,
                error=result.stderr
            )
            
        except subprocess.TimeoutExpired:
            return AgentExecution(
                agent_name=agent_name,
                success=False,
                modules_fixed=0,
                duration=300.0,
                output="",
                error="Agent timed out after 300 seconds"
            )
        except Exception as e:
            return AgentExecution(
                agent_name=agent_name,
                success=False,
                modules_fixed=0,
                duration=(datetime.now() - start_time).total_seconds(),
                output="",
                error=str(e)
            )
    
    def run_third_wave_agents(self) -> List[AgentExecution]:
        """Run third wave of agents in parallel."""
        print("🚀 STARTING THIRD WAVE PARALLEL MODULE FIXING")
        print("=" * 70)
        
        results = []
        
        with ThreadPoolExecutor(max_workers=len(self.agents)) as executor:
            # Submit all agent tasks
            future_to_agent = {
                executor.submit(self.run_agent, agent): agent 
                for agent in self.agents
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_agent):
                agent = future_to_agent[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    status = "✅ SUCCESS" if result.success else "❌ FAILED"
                    print(f"{status} {result.agent_name}: {result.modules_fixed} modules fixed in {result.duration:.2f}s")
                    
                except Exception as e:
                    print(f"❌ Agent {agent} failed with exception: {e}")
                    results.append(AgentExecution(
                        agent_name=Path(agent).stem,
                        success=False,
                        modules_fixed=0,
                        duration=0.0,
                        output="",
                        error=str(e)
                    ))
        
        self.results = results
        return results
    
    def validate_results(self) -> Dict[str, int]:
        """Validate the results by running test collection."""
        print("🔍 Validating third wave execution results...")
        
        try:
            # Run test collection to check improvement
            result = subprocess.run([
                'python3', '-m', 'pytest', 'tests/unit/beast_mode/', '--collect-only'
            ], capture_output=True, text=True, timeout=300)
            
            # Parse results
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'collected' in line and 'errors' in line:
                        parts = line.split()
                        collected = int(parts[1]) if len(parts) > 1 else 0
                        errors = int(parts[4]) if len(parts) > 4 else 0
                        return {
                            'tests_collected': collected,
                            'errors_remaining': errors,
                            'collection_success': True
                        }
            else:
                error_count = result.stderr.count('ERROR')
                return {
                    'tests_collected': 0,
                    'errors_remaining': error_count,
                    'collection_success': False
                }
        
        except Exception as e:
            print(f"⚠️  Error validating results: {e}")
            return {
                'tests_collected': 0,
                'errors_remaining': 0,
                'collection_success': False
            }
    
    def generate_third_wave_report(self, validation_stats: Dict[str, int]) -> str:
        """Generate comprehensive third wave execution report."""
        total_modules_fixed = sum(r.modules_fixed for r in self.results)
        successful_agents = sum(1 for r in self.results if r.success)
        total_duration = max(r.duration for r in self.results) if self.results else 0
        
        report = f"""
🚀 THIRD WAVE PARALLEL MODULE FIXING REPORT
==========================================

📊 THIRD WAVE EXECUTION STATISTICS:
• Total Agents Deployed: {len(self.results)}
• Successful Agents: {successful_agents} ({successful_agents/len(self.results)*100:.1f}%)
• Total Modules Fixed: {total_modules_fixed}
• Total Execution Duration: {total_duration:.2f} seconds

🔍 VALIDATION RESULTS:
• Tests Collected: {validation_stats.get('tests_collected', 0)}
• Errors Remaining: {validation_stats.get('errors_remaining', 0)}
• Collection Success: {'✅' if validation_stats.get('collection_success') else '❌'}

📋 AGENT RESULTS:
"""
        
        for result in self.results:
            status = "✅" if result.success else "❌"
            report += f"{status} {result.agent_name}: {result.modules_fixed} modules ({result.duration:.2f}s)\n"
            if result.error:
                report += f"   Error: {result.error[:100]}...\n"
        
        report += f"""
🎯 PERFORMANCE METRICS:
• Average Agent Duration: {sum(r.duration for r in self.results)/len(self.results):.2f}s
• Modules Fixed per Second: {total_modules_fixed/total_duration:.2f}
• Parallel Efficiency: {successful_agents/len(self.results)*100:.1f}%

📈 IMPROVEMENT ASSESSMENT:
"""
        
        # Compare with previous baseline (124 errors, 41 tests)
        previous_errors = 124
        previous_tests = 41
        
        if validation_stats.get('tests_collected', 0) > previous_tests:
            improvement = validation_stats['tests_collected'] - previous_tests
            report += f"• Test Collection Improved: +{improvement} tests now collecting\n"
        
        if validation_stats.get('errors_remaining', 124) < previous_errors:
            improvement = previous_errors - validation_stats['errors_remaining']
            report += f"• Errors Reduced: -{improvement} errors resolved\n"
        
        report += f"""
🔄 CUMULATIVE PROGRESS:
• Wave 1 + Wave 2 + Wave 3 Total Modules Fixed: {total_modules_fixed + 208}
• Cumulative Test Collection Improvement: {validation_stats.get('tests_collected', 0) - 0} tests
• Cumulative Error Reduction: {124 - validation_stats.get('errors_remaining', 124)} errors
"""
        
        # Check if we achieved our target
        target_tests = 82  # 50% of 165 total tests
        if validation_stats.get('tests_collected', 0) >= target_tests:
            report += f"""
🎉 TARGET ACHIEVED:
• 50%+ Test Collection Success Rate: {validation_stats.get('tests_collected', 0)}/{165} tests
• Mission Accomplished: Third wave deployment successful!
"""
        else:
            remaining_to_target = target_tests - validation_stats.get('tests_collected', 0)
            report += f"""
🎯 PROGRESS TOWARD TARGET:
• Current: {validation_stats.get('tests_collected', 0)}/{165} tests ({validation_stats.get('tests_collected', 0)/165*100:.1f}%)
• Target: 82/{165} tests (50.0%)
• Remaining to Target: {remaining_to_target} tests
"""
        
        return report

def main():
    """Main execution function."""
    runner = ThirdWaveParallelFixingRunner()
    
    print("🚀 STARTING THIRD WAVE PARALLEL MODULE FIXING")
    print("=" * 70)
    
    # Run third wave agents
    results = runner.run_third_wave_agents()
    
    # Validate results
    validation_stats = runner.validate_results()
    
    # Generate report
    report = runner.generate_third_wave_report(validation_stats)
    print(report)
    
    # Save report
    with open("third_wave_parallel_fixing_report.txt", "w") as f:
        f.write(report)
    
    print("📄 Report saved to third_wave_parallel_fixing_report.txt")
    
    # Return success if any agents succeeded
    success = any(r.success for r in results)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
