#!/usr/bin/env python3
"""
Demonstration of enhanced file change detection and mapping functionality.

This script demonstrates the implementation of task 2.2:
- Code file change analysis to identify modified, added, and deleted files
- Implement mapping between file changes and claimed task completions
- Unit tests for file change detection accuracy
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from beast_mode.compliance.git.file_change_detector import FileChangeDetector
from beast_mode.compliance.models import CommitInfo


def main():
    """Demonstrate enhanced file change detection and mapping."""
    print("=== File Change Detection and Mapping Demo ===")
    print()
    
    # Initialize the file change detector
    detector = FileChangeDetector(".")
    
    # Create sample commits that represent typical development work
    sample_commits = [
        CommitInfo(
            commit_hash="abc123",
            author="Developer",
            timestamp=datetime.now(),
            message="Implement file change detection enhancements",
            modified_files=[
                "src/beast_mode/compliance/git/file_change_detector.py"
            ],
            added_files=[
                "tests/test_file_change_detector_enhanced.py",
                "examples/file_change_detection_demo.py"
            ],
            deleted_files=[]
        ),
        CommitInfo(
            commit_hash="def456",
            author="Developer", 
            timestamp=datetime.now(),
            message="Add comprehensive analysis and task mapping",
            modified_files=[
                "tests/test_file_change_detector.py",
                ".kiro/specs/rdi-rm-compliance-check/tasks.md"
            ],
            added_files=[],
            deleted_files=[]
        )
    ]
    
    # Simulate claimed completed tasks
    claimed_tasks = [
        "file_change_detection",
        "test_implementation", 
        "documentation_updates"
    ]
    
    print("1. Basic File Change Analysis")
    print("-" * 40)
    
    # Perform basic file change analysis
    analysis = detector.analyze_file_changes(sample_commits)
    
    print(f"Total files changed: {analysis.total_files_changed}")
    print(f"Complexity score: {analysis.complexity_score:.2f}")
    print(f"Risk assessment: {analysis.risk_assessment}")
    print(f"High-impact changes: {len(analysis.high_impact_changes)}")
    print()
    
    print("2. Enhanced Task Mapping")
    print("-" * 40)
    
    # Perform enhanced task mapping with claimed tasks
    task_mappings = detector.map_changes_to_task_completions(
        analysis, 
        claimed_tasks=claimed_tasks
    )
    
    for mapping in task_mappings[:5]:  # Show top 5 mappings
        print(f"Task: {mapping.task_id}")
        print(f"  Description: {mapping.task_description}")
        print(f"  Confidence: {mapping.confidence_score:.2f}")
        print(f"  Matching files: {len(mapping.matching_files)}")
        print(f"  Evidence items: {len(mapping.evidence)}")
        print()
    
    print("3. Comprehensive Analysis")
    print("-" * 40)
    
    # Perform comprehensive analysis
    comprehensive_results = detector.perform_comprehensive_file_change_analysis(
        sample_commits,
        claimed_tasks=claimed_tasks
    )
    
    # Display summary
    summary = comprehensive_results["analysis_summary"]
    print(f"Commits analyzed: {summary['total_commits_analyzed']}")
    print(f"Files added: {summary['files_added']}")
    print(f"Files modified: {summary['files_modified']}")
    print(f"Files deleted: {summary['files_deleted']}")
    print()
    
    # Display task validation results
    validation = comprehensive_results["task_validation"]
    if validation["validation_performed"]:
        print("Task Validation Results:")
        print(f"  Validated tasks: {len(validation['validated_tasks'])}")
        print(f"  Questionable tasks: {len(validation['questionable_tasks'])}")
        print(f"  Missing evidence: {len(validation['missing_evidence_tasks'])}")
        print(f"  Unclaimed implementations: {len(validation['unclaimed_implementations'])}")
        print()
    
    # Display accuracy metrics
    metrics = comprehensive_results["accuracy_metrics"]
    print("Accuracy Metrics:")
    print(f"  Overall accuracy: {metrics['overall_accuracy']:.2f}")
    print(f"  File categorization confidence: {metrics['file_categorization_confidence']:.2f}")
    print(f"  Task mapping confidence: {metrics['task_mapping_confidence']:.2f}")
    print(f"  Coverage completeness: {metrics['coverage_completeness']:.2f}")
    print()
    
    # Display recommendations
    recommendations = comprehensive_results["recommendations"]
    if recommendations:
        print("Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        print()
    
    print("4. Health Status")
    print("-" * 40)
    
    # Check detector health
    health_indicators = detector.get_health_indicators()
    for indicator, status in health_indicators.items():
        print(f"{indicator}: {status['status']} - {status['message']}")
    
    print()
    print("=== Demo Complete ===")
    print()
    print("This demonstration shows the enhanced file change detection")
    print("and mapping functionality implemented for task 2.2:")
    print("- Comprehensive file change analysis")
    print("- Enhanced task completion mapping")
    print("- Validation against claimed tasks")
    print("- Accuracy metrics and recommendations")


if __name__ == "__main__":
    main()