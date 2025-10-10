#!/usr/bin/env python3
"""
Practical Audit Sample Calculator

Provides realistic audit sample sizes for different population sizes
and explains when full audits vs. sampling are appropriate.
"""

import math
from typing import Dict, Any, Tuple


def calculate_practical_audit_sample(
    total_completed: int,
    confidence_level: float = 0.99,
    max_error_rate: float = 0.01,
    expected_accuracy: float = 0.95
) -> Dict[str, Any]:
    """
    Calculate practical audit sample size with realistic constraints.
    """
    
    # For very small populations, audit everything
    if total_completed <= 30:
        return {
            "sample_size": total_completed,
            "sampling_percentage": 100.0,
            "recommendation": "FULL_AUDIT",
            "reason": "Population too small for statistical sampling",
            "confidence_achievable": True
        }
    
    # Z-score for confidence level
    z_scores = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576, 0.999: 3.291}
    z = z_scores.get(confidence_level, 2.576)
    
    # Calculate required sample size for infinite population
    p = expected_accuracy
    n_infinite = (z**2 * p * (1 - p)) / (max_error_rate**2)
    
    # Apply finite population correction
    n_corrected = n_infinite / (1 + (n_infinite - 1) / total_completed)
    
    # Round up and ensure it doesn't exceed population
    sample_size = min(math.ceil(n_corrected), total_completed)
    
    # Determine recommendation type
    sampling_percentage = (sample_size / total_completed) * 100
    
    if sampling_percentage >= 90:
        recommendation = "FULL_AUDIT"
        reason = "Sample size approaches population size"
    elif sampling_percentage >= 50:
        recommendation = "LARGE_SAMPLE"
        reason = "Large sample needed for high confidence"
    elif sampling_percentage >= 20:
        recommendation = "MEDIUM_SAMPLE"
        reason = "Medium sample provides good confidence"
    else:
        recommendation = "SMALL_SAMPLE"
        reason = "Small sample sufficient for large population"
    
    return {
        "sample_size": sample_size,
        "sampling_percentage": sampling_percentage,
        "recommendation": recommendation,
        "reason": reason,
        "confidence_achievable": True,
        "expected_false_positives": sample_size * (1 - expected_accuracy),
        "expected_true_positives": sample_size * expected_accuracy
    }


def generate_audit_scenarios(total_completed: int) -> Dict[str, Any]:
    """Generate audit scenarios for different population sizes."""
    
    scenarios = []
    
    # Test different population sizes to show scaling
    test_sizes = [10, 25, 50, 100, 200, 500, 1000, 2000, 5000]
    
    for size in test_sizes:
        if size <= total_completed * 2:  # Only show relevant sizes
            result = calculate_practical_audit_sample(size)
            scenarios.append({
                "population": size,
                "sample": result["sample_size"],
                "percentage": f"{result['sampling_percentage']:.1f}%",
                "type": result["recommendation"]
            })
    
    # Calculate for the actual population
    actual_result = calculate_practical_audit_sample(total_completed)
    
    return {
        "actual_population": total_completed,
        "actual_result": actual_result,
        "scaling_examples": scenarios
    }


def print_confusion_matrix_explanation():
    """Print detailed confusion matrix explanation."""
    print("📊 CONFUSION MATRIX FOR TASK COMPLETION AUDIT")
    print("=" * 55)
    print()
    print("                    ACTUAL STATUS")
    print("                 Complete | Incomplete")
    print("MARKED    Complete    TP   |    FP     ")
    print("STATUS  Incomplete   FN   |    TN     ")
    print()
    print("TP (True Positive):  Task marked complete AND actually complete ✅")
    print("FP (False Positive): Task marked complete BUT not complete ⚠️")
    print("FN (False Negative): Task marked incomplete BUT actually complete")
    print("TN (True Negative):  Task marked incomplete AND actually incomplete")
    print()
    print("🎯 AUDIT FOCUS: Detecting False Positives (FP)")
    print("   Goal: Verify that 'completed' claims are accurate")
    print("   Risk: Overestimating project completion status")
    print()


def print_practical_recommendations(total_completed: int):
    """Print practical audit recommendations."""
    result = calculate_practical_audit_sample(total_completed)
    
    print(f"🔍 PRACTICAL AUDIT RECOMMENDATION")
    print(f"=" * 50)
    print(f"Total tasks marked 'completed': {total_completed}")
    print(f"Recommended audit sample: {result['sample_size']} tasks")
    print(f"Sampling percentage: {result['sampling_percentage']:.1f}%")
    print(f"Audit type: {result['recommendation']}")
    print(f"Rationale: {result['reason']}")
    print()
    
    if result['recommendation'] == 'FULL_AUDIT':
        print("💡 FULL AUDIT APPROACH:")
        print("   • Review all completed tasks individually")
        print("   • Verify each task meets completion criteria")
        print("   • Document any discrepancies found")
        print("   • Calculate actual completion rate")
    else:
        print("💡 STATISTICAL SAMPLING APPROACH:")
        print(f"   • Randomly select {result['sample_size']} completed tasks")
        print("   • Audit each selected task thoroughly")
        print("   • Count true vs false completions")
        print("   • Extrapolate to full population with 99% confidence")
    
    print()
    print("📈 EXPECTED OUTCOMES:")
    print(f"   • True positives (actually complete): ~{int(result['expected_true_positives'])}")
    print(f"   • False positives (not actually complete): ~{int(result['expected_false_positives'])}")
    print(f"   • Confidence level: 99%")
    print(f"   • Maximum error rate: 1%")
    print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python practical_audit_calculator.py <total_completed_tasks>")
        print("Example: python practical_audit_calculator.py 150")
        sys.exit(1)
    
    try:
        total_completed = int(sys.argv[1])
        if total_completed <= 0:
            raise ValueError("Total completed tasks must be positive")
        
        print_confusion_matrix_explanation()
        print_practical_recommendations(total_completed)
        
        # Show scaling examples
        scenarios = generate_audit_scenarios(total_completed)
        print("📊 AUDIT SAMPLE SCALING EXAMPLES")
        print("=" * 40)
        print("Population | Sample | Percentage | Type")
        print("-" * 40)
        for scenario in scenarios["scaling_examples"]:
            print(f"{scenario['population']:>10} | {scenario['sample']:>6} | {scenario['percentage']:>10} | {scenario['type']}")
        
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)