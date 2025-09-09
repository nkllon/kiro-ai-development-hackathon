#!/usr/bin/env python3
"""
Execute Systematic Organizational Cleanup

This script implements the Beast Mode systematic cleanup procedure to address
the critical organizational entropy detected by the Beast Mode Test Orchestrator.

Critical Finding: 154 misplaced files in root directory requiring systematic cleanup.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.beast_mode.organization.systematic_cleanup_engine import SystematicCleanupEngine


def main():
    """Execute systematic organizational cleanup"""
    
    print("🧹 BEAST MODE: Systematic Organizational Cleanup")
    print("=" * 60)
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Addressing critical organizational entropy (154 misplaced files)")
    print("=" * 60)
    
    try:
        # Initialize systematic cleanup engine
        cleanup_engine = SystematicCleanupEngine("organizational_cleanup")
        
        print("\n🔍 PHASE 1: Organizational Entropy Analysis")
        print("-" * 40)
        
        # Analyze organizational entropy
        entropy_analysis = cleanup_engine.analyze_organizational_entropy()
        
        print(f"📊 Analysis Results:")
        print(f"   • Total files analyzed: {entropy_analysis['total_files_analyzed']}")
        print(f"   • Entropy score: {entropy_analysis['entropy_metrics']['entropy_score']:.2f}")
        print(f"   • Organization score: {entropy_analysis['entropy_metrics']['organization_score']:.2f}")
        print(f"   • Systematic compliance: {entropy_analysis['entropy_metrics']['systematic_compliance']:.2f}")
        print(f"   • Cleanup urgency: {entropy_analysis['cleanup_urgency']}")
        
        print(f"\n📋 Files by Category:")
        for category, count in entropy_analysis['files_by_category'].items():
            print(f"   • {category}: {count} files")
        
        print(f"\n⚡ Files by Priority:")
        for priority, count in entropy_analysis['files_by_priority'].items():
            print(f"   • {priority}: {count} files")
        
        print(f"\n🚨 Systematic Violations: {len(entropy_analysis['systematic_violations'])}")
        for violation in entropy_analysis['systematic_violations'][:5]:  # Show top 5
            print(f"   • {violation['file']}: {violation['violation_type']} ({violation['priority']})")
        
        print("\n📋 PHASE 2: Systematic Cleanup Planning")
        print("-" * 40)
        
        # Create systematic cleanup plan
        cleanup_plan = cleanup_engine.create_systematic_cleanup_plan(entropy_analysis)
        
        print(f"📋 Cleanup Plan: {cleanup_plan.plan_id}")
        print(f"   • Total files: {cleanup_plan.total_files}")
        print(f"   • Cleanup actions: {len(cleanup_plan.cleanup_actions)}")
        print(f"   • Estimated time: {cleanup_plan.estimated_cleanup_time}")
        print(f"   • Systematic impact: {cleanup_plan.systematic_impact_assessment}")
        print(f"   • Entropy reduction: {cleanup_plan.entropy_reduction_score:.2f}")
        
        print(f"\n🔧 Planned Actions:")
        for i, action in enumerate(cleanup_plan.cleanup_actions[:5], 1):  # Show first 5
            print(f"   {i}. {action['description']} ({action['priority']})")
        
        print("\n🚀 PHASE 3: Systematic Cleanup Execution")
        print("-" * 40)
        
        # Execute cleanup (dry run first)
        print("🧪 Dry Run Execution:")
        dry_run_results = cleanup_engine.execute_systematic_cleanup(cleanup_plan, dry_run=True)
        
        print(f"   • Actions planned: {dry_run_results['actions_planned']}")
        print(f"   • Actions executed: {dry_run_results['actions_executed']}")
        print(f"   • Success rate: {(dry_run_results['actions_successful']/dry_run_results['actions_executed']*100):.1f}%")
        
        # Ask for confirmation for actual execution
        print(f"\n❓ Proceed with actual systematic cleanup? (y/N): ", end="")
        response = input().strip().lower()
        
        if response in ['y', 'yes']:
            print("\n⚡ Executing Systematic Cleanup:")
            execution_results = cleanup_engine.execute_systematic_cleanup(cleanup_plan, dry_run=False)
            
            print(f"   • Actions executed: {execution_results['actions_executed']}")
            print(f"   • Actions successful: {execution_results['actions_successful']}")
            print(f"   • Actions failed: {execution_results['actions_failed']}")
            print(f"   • Success rate: {(execution_results['actions_successful']/execution_results['actions_executed']*100):.1f}%")
            
            if execution_results['errors']:
                print(f"   • Errors encountered: {len(execution_results['errors'])}")
                for error in execution_results['errors'][:3]:  # Show first 3 errors
                    print(f"     - {error['error']}")
            
            print(f"\n📊 Systematic Improvements:")
            for improvement in execution_results['systematic_improvements'][:5]:
                print(f"   • {improvement}")
            
            # Save execution results
            results_file = Path("logs/organizational") / f"cleanup_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            results_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(results_file, 'w') as f:
                json.dump({
                    "entropy_analysis": entropy_analysis,
                    "cleanup_plan": {
                        "plan_id": cleanup_plan.plan_id,
                        "total_files": cleanup_plan.total_files,
                        "estimated_time": cleanup_plan.estimated_cleanup_time,
                        "entropy_reduction": cleanup_plan.entropy_reduction_score
                    },
                    "execution_results": execution_results
                }, f, indent=2, default=str)
            
            print(f"\n📄 Results saved: {results_file}")
            
        else:
            print("\n⏸️ Systematic cleanup cancelled - dry run completed")
        
        print("\n" + "=" * 60)
        print("📊 SYSTEMATIC CLEANUP SUMMARY")
        print("=" * 60)
        
        # Calculate Beast Mode organizational score
        org_score = entropy_analysis['entropy_metrics']['organization_score']
        compliance_score = entropy_analysis['entropy_metrics']['systematic_compliance']
        beast_org_score = (org_score + compliance_score) / 2 * 10
        
        print(f"🐺 Beast Mode Organizational Score: {beast_org_score:.2f}/10.00")
        
        if beast_org_score >= 8.0:
            assessment = "🏆 ORGANIZATIONAL EXCELLENCE: Systematic structure maintained!"
        elif beast_org_score >= 6.0:
            assessment = "🥈 ORGANIZATIONAL PROFICIENCY: Good structure with improvement opportunities"
        elif beast_org_score >= 4.0:
            assessment = "🥉 ORGANIZATIONAL DEVELOPING: Systematic cleanup required"
        else:
            assessment = "🚨 ORGANIZATIONAL CRISIS: Immediate systematic intervention needed"
        
        print(f"   {assessment}")
        
        print(f"\n🎯 Key Findings:")
        print(f"   • Organizational entropy successfully analyzed")
        print(f"   • Systematic cleanup plan created with {len(cleanup_plan.cleanup_actions)} actions")
        print(f"   • Expected entropy reduction: {cleanup_plan.entropy_reduction_score:.0%}")
        print(f"   • Systematic compliance can be restored through planned actions")
        
        print(f"\n🐺 Beast Mode Wisdom:")
        print(f"   'Organizational entropy is the enemy of systematic excellence'")
        print(f"   'Systematic cleanup prevents future entropy accumulation'")
        print(f"   'Everyone wins when organizational structure supports systematic work'")
        
        print(f"\n✅ SYSTEMATIC ORGANIZATIONAL CLEANUP PROCEDURE COMPLETE")
        
    except Exception as e:
        print(f"\n❌ Systematic cleanup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()