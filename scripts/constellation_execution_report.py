#!/usr/bin/env python3
"""
Constellation Execution Report Generator
Generates comprehensive reports from constellation execution results
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# Add src to path for Beast Mode imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability


class ConstellationReportGenerator(ReflectiveModule):
    """Generates comprehensive reports from constellation execution"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("ConstellationReportGenerator")
        self.status_file = Path(".kiro/execution-status.json")
        self.logs_dir = Path(".kiro/execution-logs")
        self.reports_dir = Path("reports/constellation-execution")
        
        # Ensure reports directory exists
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information"""
        return {
            "module_id": "constellation_report_generator",
            "name": "Constellation Execution Report Generator",
            "version": "1.0.0",
            "description": "Generates comprehensive reports from constellation execution results"
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status"""
        return ModuleHealth(
            module_id="constellation_report_generator",
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
    
    def load_execution_status(self) -> Optional[Dict]:
        """Load execution status"""
        if not self.status_file.exists():
            return None
        
        try:
            with open(self.status_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load execution status: {e}")
            return None
    
    def analyze_execution_performance(self, status: Dict) -> Dict[str, Any]:
        """Analyze execution performance metrics"""
        if not status or "prompts" not in status:
            return {}
        
        prompts = status["prompts"]
        
        # Basic counts
        total_tasks = len(prompts)
        completed = [p for p in prompts.values() if p["status"] == "completed"]
        failed = [p for p in prompts.values() if p["status"] == "failed"]
        
        # Duration analysis
        completed_with_duration = [p for p in completed if p.get("duration_min")]
        
        if completed_with_duration:
            durations = [p["duration_min"] for p in completed_with_duration]
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            total_execution_time = sum(durations)
        else:
            avg_duration = min_duration = max_duration = total_execution_time = 0
        
        # Calculate theoretical sequential time
        estimated_sequential_time = sum(
            p.get("estimated_minutes", 60) for p in prompts.values()
        ) / 60  # Convert to hours
        
        actual_parallel_time = total_execution_time / 60  # Convert to hours
        time_savings = estimated_sequential_time - actual_parallel_time
        efficiency_gain = (time_savings / estimated_sequential_time * 100) if estimated_sequential_time > 0 else 0
        
        # Success rate
        finished_tasks = len(completed) + len(failed)
        success_rate = (len(completed) / finished_tasks * 100) if finished_tasks > 0 else 0
        
        # Execution timeline
        started_at = status.get("started_at")
        completed_at = status.get("completed_at")
        wall_clock_time = 0
        
        if started_at and completed_at:
            try:
                start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                wall_clock_time = (end_time - start_time).total_seconds() / 3600  # Hours
            except Exception:
                pass
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": len(completed),
            "failed_tasks": len(failed),
            "success_rate_percent": success_rate,
            "average_task_duration_minutes": avg_duration,
            "min_task_duration_minutes": min_duration,
            "max_task_duration_minutes": max_duration,
            "total_execution_time_hours": total_execution_time / 60,
            "estimated_sequential_time_hours": estimated_sequential_time,
            "time_savings_hours": time_savings,
            "efficiency_gain_percent": efficiency_gain,
            "wall_clock_time_hours": wall_clock_time,
            "parallelization_factor": estimated_sequential_time / wall_clock_time if wall_clock_time > 0 else 0
        }
    
    def analyze_phase_performance(self, status: Dict) -> Dict[str, Dict]:
        """Analyze performance by execution phase"""
        if not status or "prompts" not in status:
            return {}
        
        phases = {
            "Phase 1: Discovery": {"tasks": [], "completed": 0, "failed": 0, "total_duration": 0},
            "Phase 2: Requirements": {"tasks": [], "completed": 0, "failed": 0, "total_duration": 0},
            "Phase 3: Design": {"tasks": [], "completed": 0, "failed": 0, "total_duration": 0},
            "Phase 4: Tasks": {"tasks": [], "completed": 0, "failed": 0, "total_duration": 0},
            "Phase 5: Consolidation": {"tasks": [], "completed": 0, "failed": 0, "total_duration": 0},
            "Other": {"tasks": [], "completed": 0, "failed": 0, "total_duration": 0}
        }
        
        for task_name, task_data in status["prompts"].items():
            # Determine phase
            if task_name.startswith("phase-1"):
                phase = "Phase 1: Discovery"
            elif task_name.startswith("phase-2"):
                phase = "Phase 2: Requirements"
            elif task_name.startswith("phase-3"):
                phase = "Phase 3: Design"
            elif task_name.startswith("phase-4"):
                phase = "Phase 4: Tasks"
            elif task_name.startswith("phase-5"):
                phase = "Phase 5: Consolidation"
            else:
                phase = "Other"
            
            phases[phase]["tasks"].append(task_name)
            
            if task_data["status"] == "completed":
                phases[phase]["completed"] += 1
                if task_data.get("duration_min"):
                    phases[phase]["total_duration"] += task_data["duration_min"]
            elif task_data["status"] == "failed":
                phases[phase]["failed"] += 1
        
        # Calculate phase metrics
        for phase_name, phase_data in phases.items():
            total_tasks = len(phase_data["tasks"])
            completed = phase_data["completed"]
            
            phase_data.update({
                "total_tasks": total_tasks,
                "completion_rate_percent": (completed / total_tasks * 100) if total_tasks > 0 else 0,
                "average_task_duration_minutes": (
                    phase_data["total_duration"] / completed if completed > 0 else 0
                ),
                "total_duration_hours": phase_data["total_duration"] / 60
            })
        
        return phases
    
    def identify_performance_insights(self, performance: Dict, phases: Dict) -> List[str]:
        """Identify key performance insights"""
        insights = []
        
        # Overall performance insights
        if performance.get("success_rate_percent", 0) >= 95:
            insights.append("✅ Excellent success rate achieved (≥95%)")
        elif performance.get("success_rate_percent", 0) >= 85:
            insights.append("⚠️ Good success rate, but room for improvement")
        else:
            insights.append("❌ Low success rate indicates systematic issues")
        
        # Efficiency insights
        efficiency = performance.get("efficiency_gain_percent", 0)
        if efficiency >= 80:
            insights.append(f"🚀 Outstanding parallelization efficiency ({efficiency:.1f}% time savings)")
        elif efficiency >= 60:
            insights.append(f"📈 Good parallelization efficiency ({efficiency:.1f}% time savings)")
        else:
            insights.append(f"⚠️ Limited parallelization benefits ({efficiency:.1f}% time savings)")
        
        # Duration insights
        avg_duration = performance.get("average_task_duration_minutes", 0)
        if avg_duration > 0:
            if avg_duration < 30:
                insights.append("⚡ Tasks completed quickly on average")
            elif avg_duration > 90:
                insights.append("🐌 Tasks took longer than expected on average")
        
        # Phase-specific insights
        for phase_name, phase_data in phases.items():
            if phase_data["total_tasks"] == 0:
                continue
            
            completion_rate = phase_data["completion_rate_percent"]
            if completion_rate < 80:
                insights.append(f"⚠️ {phase_name} had lower completion rate ({completion_rate:.1f}%)")
        
        # Resource utilization insights
        parallelization = performance.get("parallelization_factor", 0)
        if parallelization > 5:
            insights.append(f"🔥 Excellent resource utilization (x{parallelization:.1f} speedup)")
        elif parallelization > 3:
            insights.append(f"📊 Good resource utilization (x{parallelization:.1f} speedup)")
        
        return insights
    
    def generate_failure_analysis(self, status: Dict) -> Dict[str, Any]:
        """Generate analysis of failed tasks"""
        if not status or "prompts" not in status:
            return {}
        
        failed_tasks = [
            (name, data) for name, data in status["prompts"].items()
            if data["status"] == "failed"
        ]
        
        if not failed_tasks:
            return {"total_failures": 0, "failure_patterns": [], "recommendations": []}
        
        # Analyze failure patterns
        failure_patterns = {}
        phase_failures = {}
        
        for task_name, task_data in failed_tasks:
            error = task_data.get("error", "Unknown error")
            
            # Categorize error
            if "timeout" in error.lower():
                category = "Timeout"
            elif "connection" in error.lower() or "network" in error.lower():
                category = "Network"
            elif "permission" in error.lower() or "access" in error.lower():
                category = "Permission"
            elif "file not found" in error.lower() or "no such file" in error.lower():
                category = "File System"
            else:
                category = "Other"
            
            if category not in failure_patterns:
                failure_patterns[category] = []
            failure_patterns[category].append({"task": task_name, "error": error})
            
            # Phase analysis
            if task_name.startswith("phase-"):
                phase = task_name.split("-")[1]
                if phase not in phase_failures:
                    phase_failures[phase] = 0
                phase_failures[phase] += 1
        
        # Generate recommendations
        recommendations = []
        
        if "Timeout" in failure_patterns:
            recommendations.append("Consider increasing task timeout limits")
        
        if "Network" in failure_patterns:
            recommendations.append("Check network connectivity and API rate limits")
        
        if "Permission" in failure_patterns:
            recommendations.append("Verify file system permissions and access rights")
        
        if "File System" in failure_patterns:
            recommendations.append("Ensure all required files are present and accessible")
        
        if len(failed_tasks) > len(status["prompts"]) * 0.1:  # >10% failure rate
            recommendations.append("High failure rate suggests systematic issues - review infrastructure")
        
        return {
            "total_failures": len(failed_tasks),
            "failure_patterns": failure_patterns,
            "phase_failures": phase_failures,
            "recommendations": recommendations,
            "failed_tasks": [{"task": name, "error": data.get("error", "Unknown")} for name, data in failed_tasks]
        }
    
    def generate_html_report(self, analysis: Dict) -> str:
        """Generate HTML report"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Constellation Execution Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #f8f9fa; border-radius: 3px; }}
        .success {{ color: #28a745; }}
        .warning {{ color: #ffc107; }}
        .error {{ color: #dc3545; }}
        .insight {{ margin: 5px 0; padding: 8px; background: #e9ecef; border-radius: 3px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌟 Constellation Execution Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Execution ID: {analysis.get('execution_id', 'Unknown')}</p>
    </div>
    
    <div class="section">
        <h2>📊 Executive Summary</h2>
        <div class="metric">
            <strong>Total Tasks:</strong> {analysis['performance']['total_tasks']}
        </div>
        <div class="metric">
            <strong>Success Rate:</strong> {analysis['performance']['success_rate_percent']:.1f}%
        </div>
        <div class="metric">
            <strong>Time Savings:</strong> {analysis['performance']['efficiency_gain_percent']:.1f}%
        </div>
        <div class="metric">
            <strong>Execution Time:</strong> {analysis['performance']['wall_clock_time_hours']:.1f}h
        </div>
    </div>
    
    <div class="section">
        <h2>🎯 Key Insights</h2>
        {''.join(f'<div class="insight">{insight}</div>' for insight in analysis['insights'])}
    </div>
    
    <div class="section">
        <h2>📈 Performance Metrics</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Completed Tasks</td><td>{analysis['performance']['completed_tasks']}</td></tr>
            <tr><td>Failed Tasks</td><td>{analysis['performance']['failed_tasks']}</td></tr>
            <tr><td>Average Task Duration</td><td>{analysis['performance']['average_task_duration_minutes']:.1f} minutes</td></tr>
            <tr><td>Total Execution Time</td><td>{analysis['performance']['total_execution_time_hours']:.1f} hours</td></tr>
            <tr><td>Estimated Sequential Time</td><td>{analysis['performance']['estimated_sequential_time_hours']:.1f} hours</td></tr>
            <tr><td>Parallelization Factor</td><td>{analysis['performance']['parallelization_factor']:.1f}x</td></tr>
        </table>
    </div>
    
    <div class="section">
        <h2>🎭 Phase Analysis</h2>
        <table>
            <tr><th>Phase</th><th>Tasks</th><th>Completed</th><th>Completion Rate</th><th>Duration</th></tr>
        """
        
        for phase_name, phase_data in analysis['phases'].items():
            if phase_data['total_tasks'] > 0:
                html += f"""
            <tr>
                <td>{phase_name}</td>
                <td>{phase_data['total_tasks']}</td>
                <td>{phase_data['completed']}</td>
                <td>{phase_data['completion_rate_percent']:.1f}%</td>
                <td>{phase_data['total_duration_hours']:.1f}h</td>
            </tr>
                """
        
        html += """
        </table>
    </div>
        """
        
        if analysis['failures']['total_failures'] > 0:
            html += f"""
    <div class="section">
        <h2>❌ Failure Analysis</h2>
        <p><strong>Total Failures:</strong> {analysis['failures']['total_failures']}</p>
        
        <h3>Failure Patterns:</h3>
        <ul>
            """
            
            for pattern, failures in analysis['failures']['failure_patterns'].items():
                html += f"<li><strong>{pattern}:</strong> {len(failures)} failures</li>"
            
            html += """
        </ul>
        
        <h3>Recommendations:</h3>
        <ul>
            """
            
            for rec in analysis['failures']['recommendations']:
                html += f"<li>{rec}</li>"
            
            html += """
        </ul>
    </div>
            """
        
        html += """
</body>
</html>
        """
        
        return html
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive execution report"""
        print("📊 Generating Constellation Execution Report...")
        
        # Load execution status
        status = self.load_execution_status()
        if not status:
            print("❌ No execution status found")
            return {}
        
        print(f"📋 Analyzing execution: {status.get('execution_id', 'Unknown')}")
        
        # Perform analysis
        performance = self.analyze_execution_performance(status)
        phases = self.analyze_phase_performance(status)
        failures = self.generate_failure_analysis(status)
        insights = self.identify_performance_insights(performance, phases)
        
        analysis = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "execution_id": status.get("execution_id", "Unknown"),
            "performance": performance,
            "phases": phases,
            "failures": failures,
            "insights": insights,
            "raw_status": status
        }
        
        # Generate reports
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON report
        json_file = self.reports_dir / f"constellation_report_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"📄 JSON report saved: {json_file}")
        
        # HTML report
        html_content = self.generate_html_report(analysis)
        html_file = self.reports_dir / f"constellation_report_{timestamp}.html"
        with open(html_file, 'w') as f:
            f.write(html_content)
        print(f"🌐 HTML report saved: {html_file}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 EXECUTION REPORT SUMMARY")
        print("=" * 60)
        print(f"✅ Completed: {performance['completed_tasks']}/{performance['total_tasks']} tasks")
        print(f"📈 Success Rate: {performance['success_rate_percent']:.1f}%")
        print(f"⚡ Time Savings: {performance['efficiency_gain_percent']:.1f}%")
        print(f"🕐 Execution Time: {performance['wall_clock_time_hours']:.1f} hours")
        
        if failures['total_failures'] > 0:
            print(f"❌ Failures: {failures['total_failures']} tasks failed")
        
        print(f"\n🎯 Key Insights:")
        for insight in insights[:5]:  # Top 5 insights
            print(f"  • {insight}")
        
        print(f"\n📁 Reports saved to: {self.reports_dir}")
        
        return analysis


async def main():
    parser = argparse.ArgumentParser(description="Constellation Execution Report Generator")
    parser.add_argument("--output-dir", type=str, 
                       help="Output directory for reports (default: reports/constellation-execution)")
    
    args = parser.parse_args()
    
    generator = ConstellationReportGenerator()
    
    if args.output_dir:
        generator.reports_dir = Path(args.output_dir)
        generator.reports_dir.mkdir(parents=True, exist_ok=True)
    
    report = generator.generate_comprehensive_report()
    
    if report:
        print("\n🎉 Report generation completed successfully!")
    else:
        print("\n❌ Report generation failed!")
        sys.exit(1)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())