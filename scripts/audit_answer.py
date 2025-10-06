#!/usr/bin/env python3
"""
Direct Answer: Audit Sample Size for 99% Confidence

Provides the exact answer to: "How many tasks need to be audited 
to have 99% certainty that all showing as completed are actually completed?"
"""

import math


def get_audit_answer(total_completed: int) -> dict:
    """Get direct answer for audit sample size."""
    
    # Statistical parameters for 99% confidence, 1% error rate
    z_score = 2.576  # 99% confidence
    margin_of_error = 0.01  # 1% acceptable error
    expected_accuracy = 0.95  # Assume 95% are actually complete
    
    # Calculate sample size
    p = expected_accuracy
    n_infinite = (z_score**2 * p * (1 - p)) / (margin_of_error**2)
    n_corrected = n_infinite / (1 + (n_infinite - 1) / total_completed)
    sample_size = min(math.ceil(n_corrected), total_completed)
    
    # Determine if full audit is needed
    percentage = (sample_size / total_completed) * 100
    
    if percentage >= 90:
        audit_type = "FULL AUDIT REQUIRED"
        explanation = "Sample size is so large that you might as well audit everything"
    else:
        audit_type = "STATISTICAL SAMPLING"
        explanation = f"Random sampling of {percentage:.1f}% provides sufficient confidence"
    
    return {
        "total_completed_tasks": total_completed,
        "audit_sample_required": sample_size,
        "percentage_to_audit": percentage,
        "audit_type": audit_type,
        "explanation": explanation,
        "confidence_level": "99%",
        "max_error_rate": "1%"
    }


def print_direct_answer(total_completed: int):
    """Print the direct answer."""
    result = get_audit_answer(total_completed)
    
    print("🎯 DIRECT ANSWER")
    print("=" * 50)
    print(f"Tasks marked as completed: {result['total_completed_tasks']}")
    print(f"Tasks to audit: {result['audit_sample_required']}")
    print(f"Percentage to audit: {result['percentage_to_audit']:.1f}%")
    print(f"Audit approach: {result['audit_type']}")
    print(f"Confidence level: {result['confidence_level']}")
    print(f"Maximum error rate: {result['max_error_rate']}")
    print()
    print(f"📝 EXPLANATION")
    print(f"{result['explanation']}")
    print()
    
    if result['audit_type'] == "FULL AUDIT REQUIRED":
        print("💡 RECOMMENDATION: Audit all completed tasks")
        print("   The population is small enough that statistical sampling")
        print("   doesn't provide significant efficiency gains.")
    else:
        print("💡 RECOMMENDATION: Use random statistical sampling")
        print(f"   Randomly select {result['audit_sample_required']} tasks from the {result['total_completed_tasks']} completed tasks.")
        print("   This provides 99% confidence that your error rate is ≤1%.")
    
    print()
    print("🔍 CONFUSION MATRIX FOCUS")
    print("   You're testing for FALSE POSITIVES:")
    print("   • Tasks marked 'complete' but not actually complete")
    print("   • This prevents overestimating project progress")


if __name__ == "__main__":
    import sys
    
    # Test with common population sizes
    test_sizes = [50, 100, 150, 200, 500, 1000, 2000]
    
    if len(sys.argv) == 2:
        try:
            total = int(sys.argv[1])
            print_direct_answer(total)
        except ValueError:
            print("Error: Please provide a valid number")
    else:
        print("AUDIT SAMPLE REQUIREMENTS FOR DIFFERENT POPULATION SIZES")
        print("=" * 65)
        print("Population | Audit Sample | Percentage | Approach")
        print("-" * 65)
        
        for size in test_sizes:
            result = get_audit_answer(size)
            approach = "Full" if result['audit_type'] == "FULL AUDIT REQUIRED" else "Sample"
            print(f"{size:>10} | {result['audit_sample_required']:>12} | {result['percentage_to_audit']:>9.1f}% | {approach}")
        
        print()
        print("Usage: python audit_answer.py <total_completed_tasks>")
        print("Example: python audit_answer.py 150")