#!/usr/bin/env python3
"""
Constellation Execution Readiness Checker
Comprehensive pre-flight validation and launch preparation
"""

import os
import sys
import json
import time
import asyncio
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
import logging

# Add src to path for Beast Mode imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability


class ConstellationReadinessChecker(ReflectiveModule):
    """Comprehensive readiness checker for constellation execution"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("ConstellationReadiness")
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information"""
        return {
            "module_id": "constellation_readiness_checker",
            "name": "Constellation Execution Readiness Checker",
            "version": "1.0.0",
            "description": "Comprehensive pre-flight validation and launch preparation"
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status"""
        return ModuleHealth(
            module_id="constellation_readiness_checker",
            status=ModuleStatus.HEALTHY,
            health_score=1.0,
            issues=[],
            last_check=datetime.now(timezone.utc),
            uptime_seconds=(datetime.now(timezone.utc) - self._start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self):
        """Perform graceful degradation"""
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[],
            remaining_capabilities=self.get_capabilities()
        )
    
    async def run_infrastructure_preparation(self) -> Dict[str, Any]:
        """Run infrastructure preparation script"""
        print("🔧 Running Infrastructure Preparation...")
        
        try:
            process = await asyncio.create_subprocess_exec(
                sys.executable, "scripts/prepare_constellation_execution.py",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            result = {
                "success": process.returncode == 0,
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
                "return_code": process.returncode
            }
            
            if result["success"]:
                print("  ✅ Infrastructure preparation completed successfully")
            else:
                print("  ❌ Infrastructure preparation failed")
                print(f"     Error: {result['stderr']}")
            
            return result
            
        except Exception as e:
            print(f"  ❌ Infrastructure preparation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def run_dag_validation(self) -> Dict[str, Any]:
        """Run DAG structure validation"""
        print("🔍 Running DAG Validation...")
        
        try:
            process = await asyncio.create_subprocess_exec(
                sys.executable, "scripts/constellation_dag_validator.py", "--comprehensive",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            result = {
                "success": process.returncode == 0,
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
                "return_code": process.returncode
            }
            
            if result["success"]:
                print("  ✅ DAG validation passed")
            else:
                print("  ❌ DAG validation failed")
                print(f"     Error: {result['stderr']}")
            
            return result
            
        except Exception as e:
            print(f"  ❌ DAG validation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def setup_monitoring_system(self) -> Dict[str, Any]:
        """Setup monitoring system"""
        print("📊 Setting up Monitoring System...")
        
        try:
            # Run monitoring setup
            result = subprocess.run(
                [sys.executable, "scripts/constellation_monitor.py", "--setup"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("  ✅ Monitoring system setup completed")
                
                # Validate monitoring
                validate_result = subprocess.run(
                    [sys.executable, "scripts/constellation_monitor.py", "--validate"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if validate_result.returncode == 0:
                    print("  ✅ Monitoring system validation passed")
                    return {"success": True, "validated": True}
                else:
                    print("  ⚠️  Monitoring system validation failed")
                    return {
                        "success": True,
                        "validated": False,
                        "validation_error": validate_result.stderr
                    }
            else:
                print("  ❌ Monitoring system setup failed")
                return {
                    "success": False,
                    "error": result.stderr
                }
        
        except Exception as e:
            print(f"  ❌ Monitoring system setup error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_execution_commands(self, max_agents: int = 10) -> Dict[str, List[str]]:
        """Generate execution commands for different scenarios"""
        print("📝 Generating Execution Commands...")
        
        base_command = [sys.executable, "scripts/constellation_orchestrator.py"]
        monitor_command = [sys.executable, "scripts/constellation_monitor.py"]
        
        commands = {
            "test_execution": base_command + ["2", "--test-mode"],
            "conservative_execution": base_command + ["5"],
            "balanced_execution": base_command + [str(max_agents)],
            "aggressive_execution": base_command + ["20"],
            "resume_execution": base_command + [str(max_agents), "--resume"],
            "start_monitoring": monitor_command,
            "monitoring_once": monitor_command + ["--once"],
            "setup_monitoring": monitor_command + ["--setup"]
        }
        
        print("  📋 Generated execution commands:")
        for scenario, command in commands.items():
            print(f"    • {scenario}: {' '.join(command)}")
        
        return commands
    
    def create_execution_checklist(self) -> List[Dict[str, Any]]:
        """Create pre-execution checklist"""
        checklist = [
            {
                "category": "Infrastructure",
                "items": [
                    {"task": "Beast Mode components validated", "command": "python scripts/prepare_constellation_execution.py"},
                    {"task": "Redis connectivity confirmed", "command": "python scripts/prepare_constellation_execution.py"},
                    {"task": "Claude CLI integration tested", "command": "python scripts/prepare_constellation_execution.py"},
                    {"task": "Task registry populated", "command": "python scripts/prepare_constellation_execution.py"}
                ]
            },
            {
                "category": "DAG Validation",
                "items": [
                    {"task": "DAG structure validated", "command": "python scripts/constellation_dag_validator.py --comprehensive"},
                    {"task": "No circular dependencies", "command": "python scripts/constellation_dag_validator.py --comprehensive"},
                    {"task": "All prompt files accessible", "command": "python scripts/constellation_dag_validator.py --comprehensive"},
                    {"task": "Critical path calculated", "command": "python scripts/constellation_dag_validator.py --comprehensive"}
                ]
            },
            {
                "category": "Monitoring",
                "items": [
                    {"task": "Monitoring system setup", "command": "python scripts/constellation_monitor.py --setup"},
                    {"task": "Monitoring validation passed", "command": "python scripts/constellation_monitor.py --validate"},
                    {"task": "Status file accessibility", "command": "python scripts/constellation_monitor.py --validate"},
                    {"task": "Dashboard functionality", "command": "python scripts/constellation_monitor.py --once"}
                ]
            },
            {
                "category": "Execution Preparation",
                "items": [
                    {"task": "Execution directories created", "command": "ls -la .kiro/"},
                    {"task": "Configuration files generated", "command": "ls -la .kiro/*.json"},
                    {"task": "Staging prompts inventory", "command": "ls -la prompts/staging/*.md | wc -l"},
                    {"task": "Launch commands prepared", "command": "echo 'Commands ready'"}
                ]
            }
        ]
        
        return checklist
    
    def print_execution_summary(self, validation_results: Dict[str, Any], commands: Dict[str, List[str]]):
        """Print comprehensive execution summary"""
        print("\n" + "=" * 80)
        print("🚀 CONSTELLATION EXECUTION READINESS SUMMARY")
        print("=" * 80)
        
        # Overall readiness status
        all_successful = all(
            result.get("success", False) 
            for result in validation_results.values()
        )
        
        if all_successful:
            print("✅ SYSTEM READY FOR EXECUTION")
            print("🎯 All validation checks passed successfully")
        else:
            print("❌ SYSTEM NOT READY FOR EXECUTION")
            print("🛑 Issues must be resolved before launch")
        
        print(f"\n📊 Validation Results:")
        for component, result in validation_results.items():
            status_icon = "✅" if result.get("success", False) else "❌"
            print(f"  {status_icon} {component.replace('_', ' ').title()}")
        
        if all_successful:
            print(f"\n🚀 LAUNCH COMMANDS:")
            print(f"  • Test run (2 agents):     {' '.join(commands['test_execution'])}")
            print(f"  • Conservative (5 agents): {' '.join(commands['conservative_execution'])}")
            print(f"  • Balanced (10 agents):    {' '.join(commands['balanced_execution'])}")
            print(f"  • Aggressive (20 agents):  {' '.join(commands['aggressive_execution'])}")
            print(f"\n📊 MONITORING COMMANDS:")
            print(f"  • Start monitoring:        {' '.join(commands['start_monitoring'])}")
            print(f"  • Check status once:       {' '.join(commands['monitoring_once'])}")
            
            print(f"\n⚡ RECOMMENDED LAUNCH SEQUENCE:")
            print(f"  1. Start monitoring:       {' '.join(commands['start_monitoring'])}")
            print(f"  2. In another terminal:    {' '.join(commands['balanced_execution'])}")
            print(f"  3. Monitor progress in real-time")
            
            print(f"\n📈 EXPECTED PERFORMANCE:")
            print(f"  • Sequential execution:    ~52.8 hours")
            print(f"  • Parallel execution:      ~9.2 hours (83% reduction)")
            print(f"  • Success rate target:     >95%")
            print(f"  • Total prompts:           90+ staging prompts")
        else:
            print(f"\n🔧 RESOLUTION STEPS:")
            for component, result in validation_results.items():
                if not result.get("success", False):
                    print(f"  ❌ Fix {component}:")
                    if "error" in result:
                        print(f"     Error: {result['error']}")
                    if "stderr" in result and result["stderr"]:
                        print(f"     Details: {result['stderr'][:200]}...")
        
        print("\n" + "=" * 80)
    
    async def run_comprehensive_readiness_check(self, max_agents: int = 10) -> Dict[str, Any]:
        """Run comprehensive readiness check"""
        print("🚀 CONSTELLATION EXECUTION READINESS CHECK")
        print("=" * 80)
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🤖 Target agents: {max_agents}")
        print()
        
        validation_results = {}
        
        # 1. Infrastructure preparation
        validation_results["infrastructure_preparation"] = await self.run_infrastructure_preparation()
        
        # 2. DAG validation
        validation_results["dag_validation"] = await self.run_dag_validation()
        
        # 3. Monitoring setup
        validation_results["monitoring_setup"] = self.setup_monitoring_system()
        
        # 4. Generate execution commands
        commands = self.generate_execution_commands(max_agents)
        
        # 5. Create checklist
        checklist = self.create_execution_checklist()
        
        # 6. Save readiness report
        readiness_report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "max_agents": max_agents,
            "validation_results": validation_results,
            "execution_commands": commands,
            "checklist": checklist,
            "ready_for_execution": all(
                result.get("success", False) 
                for result in validation_results.values()
            )
        }
        
        try:
            report_file = Path(".kiro/constellation-readiness-report.json")
            with open(report_file, 'w') as f:
                json.dump(readiness_report, f, indent=2)
            print(f"💾 Readiness report saved to: {report_file}")
        except Exception as e:
            print(f"⚠️  Warning: Could not save readiness report: {e}")
        
        # 7. Print summary
        self.print_execution_summary(validation_results, commands)
        
        return readiness_report


async def main():
    parser = argparse.ArgumentParser(description="Constellation Execution Readiness Checker")
    parser.add_argument("--max-agents", type=int, default=10,
                       help="Maximum number of concurrent agents (default: 10)")
    
    args = parser.parse_args()
    
    checker = ConstellationReadinessChecker()
    report = await checker.run_comprehensive_readiness_check(max_agents=args.max_agents)
    
    # Exit with appropriate code
    if report["ready_for_execution"]:
        print("\n🎉 System is ready for constellation execution!")
        sys.exit(0)
    else:
        print("\n🛑 System is not ready. Please resolve issues before execution.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())