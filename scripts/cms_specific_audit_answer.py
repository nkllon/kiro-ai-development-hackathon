#!/usr/bin/env python3
"""
CMS-Specific Audit Answer

Direct answer for the CMS task population audit requirements
with confusion matrix analysis for all statuses.
"""

import math
from typing import Dict, Any


def calculate_cms_audit_requirements() -> Dict[str, Any]:
    """Calculate audit requirements for the specific CMS population."""
    
    # CMS Task Population (from actual analysis)
    cms_data = {
        "total_tasks": 22,
        "total_acceptance_criteria": 152,
        "completed_criteria": 0,
        "overall_completion_rate": 0.0,
        "status_distribution": {
            "completed": 0,      # 0 tasks (0.0%)
            "in_progress": 0,    # 0 tasks (0.0%)
            "not_started": 22    # 22 tasks (100.0%)
        },
        "phase_distribution": {
            "Phase 1": 4,  # 18.2%
            "Phase 2": 4,  # 18.2%
            "Phase 3": 4,  # 18.2%
            "Phase 4": 4,  # 18.2%
            "Phase 5": 4,  # 18.2%
            "Phase 6": 2   # 9.1%
        },
        "priority_distribution": {
            "HIGH": 12,    # 54.5%
            "MEDIUM": 8,   # 36.4%
            "LOW": 2       # 9.1%
        }
    }
    
    # Calculate audit requirements for each status
    audit_results = {}
    
    for status, count in cms_data["status_distribution"].items():
        if count > 0:
            audit_results[status] = calculate_audit_sample(count, status)
        else:
            audit_results[status] = {
                "total_tasks": 0,
                "audit_required": 0,
                "audit_percentage": 0,
                "recommendation": "NO_AUDIT_NEEDED",
                "reason": f"No tasks with status '{status}'"
            }
    
    # Generate confusion matrices
    confusion_matrices = generate_confusion_matrices(cms_data["status_distribution"])
    
    return {
        "cms_population": cms_data,
        "audit_requirements": audit_results,
        "confusion_matrices": confusion_matrices
    }


def calculate_audit_sample(population: int, status: str) -> Dict[str, Any]:
    """Calculate audit sample size for a specific population and status."""
    
    # Statistical parameters for 99% confidence, 1% error rate
    z_score = 2.576  # 99% confidence
    margin_of_error = 0.01  # 1% acceptable error
    
    # Expected accuracy varies by status
    expected_accuracy = {
        "completed": 0.95,    # 95% of "completed" are actually complete
        "in_progress": 0.90,  # 90% of "in_progress" are actually in progress
        "not_started": 0.98   # 98% of "not_started" are actually not started
    }.get(status, 0.95)
    
    # Calculate sample size
    p = expected_accuracy
    n_infinite = (z_score**2 * p * (1 - p)) / (margin_of_error**2)
    n_corrected = n_infinite / (1 + (n_infinite - 1) / population)
    sample_size = min(math.ceil(n_corrected), population)
    
    percentage = (sample_size / population) * 100
    
    # Determine recommendation
    if percentage >= 90:
        recommendation = "FULL_AUDIT"
        reason = "Sample size approaches population size - audit all tasks"
    elif percentage >= 50:
        recommendation = "LARGE_SAMPLE"
        reason = "Large sample needed for high confidence"
    else:
        recommendation = "STATISTICAL_SAMPLE"
        reason = "Statistical sampling sufficient"
    
    return {
        "total_tasks": population,
        "audit_required": sample_size,
        "audit_percentage": percentage,
        "recommendation": recommendation,
        "reason": reason,
        "expected_accuracy": expected_accuracy,
        "confidence_level": "99%",
        "max_error_rate": "1%"
    }


def generate_confusion_matrices(status_distribution: Dict[str, int]) -> Dict[str, Dict[str, Any]]:
    """Generate confusion matrices for all task statuses."""
    
    matrices = {}
    
    for status, total in status_distribution.items():
        if total == 0:
            continue
        
        # Expected accuracy rates based on typical project management scenarios
        accuracy_rates = {
            "completed": 0.95,    # 95% accuracy for completed tasks
            "in_progress": 0.90,  # 90% accuracy for in-progress tasks
            "not_started": 0.98   # 98% accuracy for not-started tasks
        }
        
        accuracy = accuracy_rates.get(status, 0.95)
        
        # Calculate confusion matrix values
        true_positives = int(total * accuracy)
        false_positives = total - true_positives
        
        # For this analysis, we focus on the specific status vs. all others
        # In a real audit, these would come from actual verification
        true_negatives = 0  # Not applicable for single-status analysis
        false_negatives = 0  # Not applicable for single-status analysis
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 1
        
        matrices[status] = {
            "total_tasks": total,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "true_negatives": true_negatives,
            "false_negatives": false_negatives,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "expected_false_positive_rate": false_positives / total if total > 0 else 0
        }
    
    return matrices


def print_cms_audit_answer():
    """Print the direct answer for CMS audit requirements."""
    
    results = calculate_cms_audit_requirements()
    cms_data = results["cms_population"]
    audit_reqs = results["audit_requirements"]
    confusion_matrices = results["confusion_matrices"]
    
    print("🎯 CMS TASK AUDIT REQUIREMENTS - DIRECT ANSWER")
    print("=" * 60)
    print()
    
    print("📊 CMS POPULATION ANALYSIS")
    print(f"Total Tasks: {cms_data['total_tasks']}")
    print(f"Total Acceptance Criteria: {cms_data['total_acceptance_criteria']}")
    print(f"Overall Completion Rate: {cms_data['overall_completion_rate']:.1f}%")
    print()
    
    print("📈 CURRENT STATUS DISTRIBUTION")
    for status, count in cms_data["status_distribution"].items():
        percentage = (count / cms_data['total_tasks']) * 100 if cms_data['total_tasks'] > 0 else 0
        print(f"  {status.replace('_', ' ').title()}: {count} tasks ({percentage:.1f}%)")
    print()
    
    print("🔍 AUDIT REQUIREMENTS BY STATUS")
    print("=" * 50)
    
    for status, audit_req in audit_reqs.items():
        if audit_req["total_tasks"] > 0:
            print(f"\n📊 {status.replace('_', ' ').upper()} TASKS")
            print(f"Population: {audit_req['total_tasks']} tasks")
            print(f"Audit Required: {audit_req['audit_required']} tasks")
            print(f"Audit Percentage: {audit_req['audit_percentage']:.1f}%")
            print(f"Recommendation: {audit_req['recommendation']}")
            print(f"Reason: {audit_req['reason']}")
            print(f"Expected Accuracy: {audit_req['expected_accuracy']:.0%}")
    
    print(f"\n🎯 CONFUSION MATRIX ANALYSIS")
    print("=" * 50)
    
    for status, matrix in confusion_matrices.items():
        print(f"\n📈 {status.replace('_', ' ').upper()} TASKS CONFUSION MATRIX")
        print(f"                    ACTUAL STATUS")
        print(f"                 {status.title():<12} | Other")
        print(f"REPORTED {status.title():<8}    {matrix['true_positives']:>3}   |   {matrix['false_positives']:>3}")
        print(f"         Other    {matrix['false_negatives']:>3}   |   {matrix['true_negatives']:>3}")
        print(f"")
        print(f"Expected Accuracy: {matrix['accuracy']:.1%}")
        print(f"Expected False Positives: {matrix['false_positives']} tasks")
        print(f"False Positive Rate: {matrix['expected_false_positive_rate']:.1%}")
    
    print(f"\n💡 SPECIFIC CMS RECOMMENDATIONS")
    print("=" * 50)
    
    # Current state: All tasks are "not_started"
    not_started_audit = audit_reqs["not_started"]
    
    print(f"🔍 IMMEDIATE AUDIT ACTION REQUIRED:")
    print(f"   • Current State: ALL 22 tasks marked as 'not_started'")
    print(f"   • Audit Required: {not_started_audit['audit_required']} tasks (100%)")
    print(f"   • Recommendation: {not_started_audit['recommendation']}")
    print(f"   • Focus: Verify no tasks have actually begun work")
    print()
    
    print(f"📋 AUDIT METHODOLOGY:")
    print(f"   1. **Random Selection**: Select all 22 tasks for verification")
    print(f"   2. **Status Verification**: Check if any work has actually started")
    print(f"   3. **Documentation Review**: Verify acceptance criteria are clear")
    print(f"   4. **Dependency Validation**: Confirm prerequisite relationships")
    print(f"   5. **Resource Assignment**: Verify team assignments are accurate")
    print()
    
    print(f"⚠️  EXPECTED FINDINGS:")
    print(f"   • True Negatives: ~21 tasks (95.5%) - Actually not started")
    print(f"   • False Positives: ~1 task (4.5%) - May have begun but not marked")
    print(f"   • Confidence Level: 99%")
    print(f"   • Maximum Error Rate: 1%")
    print()
    
    print(f"🎯 KEY AUDIT QUESTIONS:")
    print(f"   1. Are all 22 tasks truly not started?")
    print(f"   2. Have any preliminary discussions or planning begun?")
    print(f"   3. Are task dependencies accurately mapped?")
    print(f"   4. Are acceptance criteria measurable and complete?")
    print(f"   5. Are team assignments realistic and confirmed?")


if __name__ == "__main__":
    print_cms_audit_answer()