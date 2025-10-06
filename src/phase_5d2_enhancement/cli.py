"""
Command-line interface for Phase 5D2 Enhancement System
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from .config import get_config
from .orchestration.enhancement_orchestrator import EnhancementOrchestrator
from .analysis.dimension_analyzer import DimensionAnalyzer
from .analysis.quality_validator import QualityValidator


class Phase5D2CLI(ReflectiveModule):
    """Command-line interface for Phase 5D2 Enhancement System."""
    
    def __init__(self):
        super().__init__()
        self.config = get_config()
        self.orchestrator = EnhancementOrchestrator()
        self.dimension_analyzer = DimensionAnalyzer()
        self.quality_validator = QualityValidator()
        
        self.logger.info("Phase 5D2 Enhancement CLI initialized")
    
    def get_capabilities(self):
        """Get CLI capabilities."""
        return {
            "commands": ["enhance", "validate", "report", "status"],
            "enhancement_types": ["cycle", "iterative"],
            "supported_dimensions": list(self.orchestrator.PRIORITY_DIMENSIONS.keys())
        }
    
    def get_health_status(self):
        """Get CLI health status."""
        return {
            "status": "healthy",
            "components": {
                "orchestrator": "initialized",
                "dimension_analyzer": "initialized", 
                "quality_validator": "initialized"
            }
        }
    
    def get_module_info(self):
        """Get CLI module information."""
        return {
            "name": "Phase5D2CLI",
            "version": "1.0.0",
            "description": "Command-line interface for Phase 5D2 Enhancement System"
        }
    
    def graceful_degradation(self, error):
        """Handle graceful degradation on errors."""
        self.logger.error(f"CLI error: {error}")
        return {"status": "degraded", "error": str(error)}
    
    def run_enhancement_cycle(self, target_dimensions: Optional[List[str]] = None) -> None:
        """Run a single enhancement cycle."""
        print("🚀 Starting Phase 5D2 Enhancement Cycle...")
        print(f"⚙️  Configuration: Target Score {self.config.quality_target_threshold}, Critical Gap Threshold {self.config.critical_gap_threshold}%")
        
        try:
            # Execute enhancement cycle
            cycle = self.orchestrator.execute_enhancement_cycle(target_dimensions)
            
            # Display results
            print(f"\n✅ Enhancement Cycle Completed: {cycle.cycle_id}")
            print(f"📊 Before Score: {cycle.before_scores.overall_score:.1f}")
            print(f"📈 After Score: {cycle.after_scores.overall_score:.1f}")
            print(f"🎯 Improvement: +{cycle.overall_improvement:.1f} points")
            print(f"⏱️  Duration: {cycle.duration_minutes:.1f} minutes")
            print(f"✅ Success: {'Yes' if cycle.success else 'No'}")
            
            # Show improvements by dimension
            print(f"\n🔧 Improvements Applied:")
            for dimension, improvements in cycle.improvements_applied.items():
                print(f"  📋 {dimension.replace('_', ' ').title()}: {len(improvements)} improvements")
                for improvement in improvements[:2]:  # Show first 2
                    print(f"    • {improvement}")
                if len(improvements) > 2:
                    print(f"    ... and {len(improvements) - 2} more")
            
            # Show validation results
            passed_validations = sum(1 for v in cycle.validation_results if v.passed)
            total_validations = len(cycle.validation_results)
            print(f"\n✅ Validation Results: {passed_validations}/{total_validations} passed")
            
            for validation in cycle.validation_results:
                status = "✅" if validation.passed else "❌"
                print(f"  {status} {validation.validation_name}: {validation.message}")
            
        except Exception as e:
            print(f"❌ Enhancement cycle failed: {e}")
            self.logger.error(f"Enhancement cycle failed: {e}")
    
    def run_iterative_enhancement(self, max_cycles: Optional[int] = None) -> None:
        """Run iterative enhancement until completion criteria are met."""
        print("🔄 Starting Iterative Phase 5D2 Enhancement...")
        
        if max_cycles is None:
            max_cycles = self.config.max_enhancement_cycles
        
        print(f"⚙️  Configuration: Max {max_cycles} cycles, Target Score {self.config.quality_target_threshold}")
        
        try:
            # Run iterative enhancement
            cycles = self.orchestrator.run_iterative_enhancement(max_cycles)
            
            # Display summary
            print(f"\n🏁 Iterative Enhancement Completed")
            print(f"📊 Cycles Executed: {len(cycles)}")
            
            if cycles:
                total_improvement = sum(cycle.overall_improvement for cycle in cycles)
                successful_cycles = sum(1 for cycle in cycles if cycle.success)
                
                print(f"📈 Total Improvement: +{total_improvement:.1f} points")
                print(f"✅ Success Rate: {successful_cycles}/{len(cycles)} cycles")
                print(f"🎯 Final Score: {cycles[-1].after_scores.overall_score:.1f}")
                
                # Check completion status
                completion_status = self.orchestrator.validate_phase_5d2_completion()
                print(f"\n🎯 Phase 5D2 Completion Status:")
                print(f"  Overall Quality: {completion_status.overall_quality_score:.1f} (target: {self.config.quality_target_threshold})")
                print(f"  Critical Gaps: {completion_status.critical_gap_percentage:.1f}% (target: <{self.config.critical_gap_threshold}%)")
                print(f"  Completion Met: {'✅ Yes' if completion_status.completion_criteria_met else '❌ No'}")
                print(f"  Phase 5D3 Ready: {'✅ Yes' if completion_status.phase_5d3_ready else '❌ No'}")
                
                if completion_status.blocking_issues:
                    print(f"\n🚨 Blocking Issues:")
                    for issue in completion_status.blocking_issues:
                        print(f"  • {issue}")
            
        except Exception as e:
            print(f"❌ Iterative enhancement failed: {e}")
            self.logger.error(f"Iterative enhancement failed: {e}")
    
    def validate_completion(self) -> None:
        """Validate Phase 5D2 completion criteria."""
        print("🔍 Validating Phase 5D2 Completion Criteria...")
        
        try:
            # Validate completion
            completion_status = self.orchestrator.validate_phase_5d2_completion()
            
            # Display results
            print(f"\n📊 Phase 5D2 Completion Status")
            print(f"Overall Quality Score: {completion_status.overall_quality_score:.1f}")
            print(f"Critical Gap Percentage: {completion_status.critical_gap_percentage:.1f}%")
            print(f"Completion Criteria Met: {'✅ Yes' if completion_status.completion_criteria_met else '❌ No'}")
            print(f"Phase 5D3 Ready: {'✅ Yes' if completion_status.phase_5d3_ready else '❌ No'}")
            
            # Show dimension scores
            print(f"\n📋 Dimension Scores:")
            sorted_dimensions = sorted(
                completion_status.dimension_scores.items(), 
                key=lambda x: x[1]
            )
            
            for dimension, score in sorted_dimensions:
                status = "✅" if score >= 60 else "⚠️" if score >= 40 else "❌"
                print(f"  {status} {dimension.replace('_', ' ').title()}: {score:.1f}")
            
            # Show blocking issues
            if completion_status.blocking_issues:
                print(f"\n🚨 Blocking Issues ({len(completion_status.blocking_issues)}):")
                for issue in completion_status.blocking_issues:
                    print(f"  • {issue}")
            
            # Show validation results
            passed_validations = sum(1 for v in completion_status.validation_results if v.passed)
            total_validations = len(completion_status.validation_results)
            print(f"\n✅ Validation Results: {passed_validations}/{total_validations} passed")
            
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            self.logger.error(f"Validation failed: {e}")
    
    def generate_readiness_report(self) -> None:
        """Generate Phase 5D3 readiness report."""
        print("📋 Generating Phase 5D3 Readiness Report...")
        
        try:
            # Generate report
            report = self.orchestrator.generate_phase_5d3_readiness_report()
            
            # Display report
            print(f"\n📊 Phase 5D3 Readiness Report")
            print(f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Overall Quality Score: {report.overall_quality_score:.1f}")
            print(f"Critical Gap Percentage: {report.critical_gap_percentage:.1f}%")
            print(f"Phase 5D3 Ready: {'✅ Yes' if report.phase_5d3_ready else '❌ No'}")
            
            # Show blocking issues
            if report.blocking_issues:
                print(f"\n🚨 Blocking Issues ({len(report.blocking_issues)}):")
                for issue in report.blocking_issues:
                    print(f"  • {issue}")
            
            # Show recommendations
            if report.recommendations:
                print(f"\n💡 Recommendations ({len(report.recommendations)}):")
                for recommendation in report.recommendations:
                    print(f"  • {recommendation}")
            
            # Save report to file
            report_path = Path(self.config.reports_path) / f"phase-5d3-readiness-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            
            report_data = {
                "overall_quality_score": report.overall_quality_score,
                "critical_gap_percentage": report.critical_gap_percentage,
                "phase_5d3_ready": report.phase_5d3_ready,
                "blocking_issues": report.blocking_issues,
                "recommendations": report.recommendations,
                "generated_at": report.generated_at.isoformat(),
                "completion_status": {
                    "overall_quality_score": report.completion_status.overall_quality_score,
                    "critical_gap_percentage": report.completion_status.critical_gap_percentage,
                    "completion_criteria_met": report.completion_status.completion_criteria_met,
                    "phase_5d3_ready": report.completion_status.phase_5d3_ready,
                    "blocking_issues": report.completion_status.blocking_issues,
                    "dimension_scores": report.completion_status.dimension_scores
                }
            }
            
            with open(report_path, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            print(f"\n💾 Report saved to: {report_path}")
            
        except Exception as e:
            print(f"❌ Report generation failed: {e}")
            self.logger.error(f"Report generation failed: {e}")
    
    def show_status(self) -> None:
        """Show current system status."""
        print("📊 Phase 5D2 Enhancement System Status")
        
        try:
            # Get enhancement summary
            summary = self.orchestrator.get_enhancement_summary()
            
            if "message" in summary:
                print(f"\n{summary['message']}")
                return
            
            # Display enhancement cycles summary
            cycles_info = summary["enhancement_cycles"]
            print(f"\n🔄 Enhancement Cycles:")
            print(f"  Total Cycles: {cycles_info['total_cycles']}")
            print(f"  Successful Cycles: {cycles_info['successful_cycles']}")
            print(f"  Success Rate: {cycles_info['success_rate']:.1f}%")
            print(f"  Total Improvement: +{cycles_info['total_improvement']:.1f} points")
            print(f"  Average Improvement: +{cycles_info['average_improvement']:.1f} points per cycle")
            
            # Display current status
            current_status = summary["current_status"]
            print(f"\n📈 Current Status:")
            print(f"  Overall Quality Score: {current_status['overall_quality_score']:.1f}")
            print(f"  Critical Gap Percentage: {current_status['critical_gap_percentage']:.1f}%")
            print(f"  Dimensions Analyzed: {current_status['dimensions_analyzed']}")
            
            # Display priority dimensions
            priority_status = summary["priority_dimensions_status"]
            print(f"\n🎯 Priority Dimensions Status:")
            for dimension, status in priority_status.items():
                target_met = "✅" if status["target_met"] else "❌"
                print(f"  {target_met} {dimension.replace('_', ' ').title()}: {status['current_score']:.1f} (target: {status['target_score']:.1f})")
                if not status["target_met"]:
                    print(f"      Gap: {status['gap']:.1f} points needed")
            
            print(f"\nLast Updated: {summary['last_updated']}")
            
        except Exception as e:
            print(f"❌ Status retrieval failed: {e}")
            self.logger.error(f"Status retrieval failed: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Phase 5D2 Enhancement System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.phase_5d2_enhancement.cli enhance --cycle
  python -m src.phase_5d2_enhancement.cli enhance --iterative --max-cycles 3
  python -m src.phase_5d2_enhancement.cli validate
  python -m src.phase_5d2_enhancement.cli report
  python -m src.phase_5d2_enhancement.cli status
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Enhancement command
    enhance_parser = subparsers.add_parser('enhance', help='Run enhancement operations')
    enhance_group = enhance_parser.add_mutually_exclusive_group(required=True)
    enhance_group.add_argument('--cycle', action='store_true', help='Run single enhancement cycle')
    enhance_group.add_argument('--iterative', action='store_true', help='Run iterative enhancement')
    enhance_parser.add_argument('--max-cycles', type=int, help='Maximum cycles for iterative enhancement')
    enhance_parser.add_argument('--dimensions', nargs='+', help='Target specific dimensions')
    
    # Validation command
    validate_parser = subparsers.add_parser('validate', help='Validate Phase 5D2 completion')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate Phase 5D3 readiness report')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize CLI
    try:
        cli = Phase5D2CLI()
    except Exception as e:
        print(f"❌ Failed to initialize CLI: {e}")
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == 'enhance':
            if args.cycle:
                cli.run_enhancement_cycle(args.dimensions)
            elif args.iterative:
                cli.run_iterative_enhancement(args.max_cycles)
        
        elif args.command == 'validate':
            cli.validate_completion()
        
        elif args.command == 'report':
            cli.generate_readiness_report()
        
        elif args.command == 'status':
            cli.show_status()
    
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Command failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()