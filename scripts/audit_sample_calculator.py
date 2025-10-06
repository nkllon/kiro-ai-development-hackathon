#!/usr/bin/env python3
"""
Audit Sample Size Calculator for Task Completion Verification

Calculates the minimum sample size needed to achieve 99% confidence
that all tasks marked as "completed" in the CMS are actually completed.

This creates a confusion matrix analysis for:
- True Positives: Tasks marked complete AND actually complete
- False Positives: Tasks marked complete BUT not actually complete
- True Negatives: Tasks marked incomplete AND actually incomplete  
- False Negatives: Tasks marked incomplete BUT actually complete

For audit purposes, we focus on False Positive rate (Type I error).
"""

import math
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class AuditParameters:
    """Parameters for audit sample size calculation."""
    total_completed_tasks: int
    confidence_level: float = 0.99  # 99% confidence
    acceptable_error_rate: float = 0.01  # 1% acceptable false positive rate
    expected_true_completion_rate: float = 0.95  # Assume 95% are actually complete


def calculate_sample_size_hypergeometric(
    population_size: int,
    confidence_level: float,
    margin_of_error: float,
    expected_proportion: float = 0.5
) -> int:
    """
    Calculate sample size using hypergeometric distribution.
    
    For finite population sampling without replacement.
    """
    # Z-score for confidence level
    z_scores = {
        0.90: 1.645,
        0.95: 1.96,
        0.99: 2.576,
        0.999: 3.291
    }
    
    z = z_scores.get(confidence_level, 2.576)
    
    # Standard sample size calculation
    p = expected_proportion
    n_infinite = (z**2 * p * (1 - p)) / (margin_of_error**2)
    
    # Finite population correction
    n_finite = n_infinite / (1 + (n_infinite - 1) / population_size)
    
    # Ensure sample size doesn't exceed population
    return min(math.ceil(n_finite), population_size)


def calculate_sample_size_binomial(
    confidence_level: float,
    margin_of_error: float,
    expected_proportion: float = 0.5
) -> int:
    """
    Calculate sample size using binomial distribution.
    
    For large population approximation.
    """
    z_scores = {
        0.90: 1.645,
        0.95: 1.96,
        0.99: 2.576,
        0.999: 3.291
    }
    
    z = z_scores[confidence_level]
    p = expected_proportion
    
    n = (z**2 * p * (1 - p)) / (margin_of_error**2)
    
    return math.ceil(n)


def calculate_audit_requirements(params: AuditParameters) -> Dict[str, Any]:
    """
    Calculate comprehensive audit requirements.
    """
    # Method 1: Hypergeometric (exact for finite population)
    sample_hypergeometric = calculate_sample_size_hypergeometric(
        population_size=params.total_completed_tasks,
        confidence_level=params.confidence_level,
        margin_of_error=params.acceptable_error_rate,
        expected_proportion=params.expected_true_completion_rate
    )
    
    # Method 2: Binomial approximation (for comparison)
    sample_binomial = calculate_sample_size_binomial(
        confidence_level=params.confidence_level,
        margin_of_error=params.acceptable_error_rate,
        expected_proportion=params.expected_true_completion_rate
    )
    
    # Conservative approach: use the larger sample size, but cap at population
    recommended_sample = min(max(sample_hypergeometric, sample_binomial), params.total_completed_tasks)
    
    # Calculate sampling fraction
    sampling_fraction = recommended_sample / params.total_completed_tasks
    
    # Expected confusion matrix outcomes
    expected_true_positives = recommended_sample * params.expected_true_completion_rate
    expected_false_positives = recommended_sample * (1 - params.expected_true_completion_rate)
    
    return {
        "total_completed_tasks": params.total_completed_tasks,
        "confidence_level": params.confidence_level,
        "acceptable_error_rate": params.acceptable_error_rate,
        "expected_completion_rate": params.expected_true_completion_rate,
        "sample_size_hypergeometric": sample_hypergeometric,
        "sample_size_binomial": sample_binomial,
        "recommended_sample_size": recommended_sample,
        "sampling_fraction": sampling_fraction,
        "sampling_percentage": sampling_fraction * 100,
        "expected_outcomes": {
            "true_positives": int(expected_true_positives),
            "false_positives": int(expected_false_positives),
            "audit_accuracy": expected_true_positives / recommended_sample
        },
        "interpretation": {
            "meaning": f"Audit {recommended_sample} randomly selected 'completed' tasks",
            "confidence": f"{params.confidence_level*100}% confident the error rate is ≤ {params.acceptable_error_rate*100}%",
            "coverage": f"This represents {sampling_fraction*100:.1f}% of all completed tasks"
        }
    }


def generate_audit_plan(total_completed: int) -> Dict[str, Any]:
    """
    Generate complete audit plan for different scenarios.
    """
    scenarios = {
        "conservative": AuditParameters(
            total_completed_tasks=total_completed,
            confidence_level=0.99,
            acceptable_error_rate=0.01,
            expected_true_completion_rate=0.90  # Conservative: assume 10% false positives
        ),
        "standard": AuditParameters(
            total_completed_tasks=total_completed,
            confidence_level=0.99,
            acceptable_error_rate=0.01,
            expected_true_completion_rate=0.95  # Standard: assume 5% false positives
        ),
        "optimistic": AuditParameters(
            total_completed_tasks=total_completed,
            confidence_level=0.99,
            acceptable_error_rate=0.01,
            expected_true_completion_rate=0.98  # Optimistic: assume 2% false positives
        )
    }
    
    results = {}
    for scenario_name, params in scenarios.items():
        results[scenario_name] = calculate_audit_requirements(params)
    
    return results


def print_audit_analysis(total_completed: int):
    """
    Print comprehensive audit analysis.
    """
    print(f"🔍 AUDIT SAMPLE SIZE ANALYSIS")
    print(f"=" * 50)
    print(f"Total tasks marked as 'completed': {total_completed}")
    print(f"Target confidence level: 99%")
    print(f"Acceptable error rate: 1%")
    print()
    
    scenarios = generate_audit_plan(total_completed)
    
    for scenario_name, analysis in scenarios.items():
        print(f"📊 {scenario_name.upper()} SCENARIO")
        print(f"Expected true completion rate: {analysis['expected_completion_rate']*100}%")
        print(f"Recommended audit sample: {analysis['recommended_sample_size']} tasks")
        print(f"Sampling percentage: {analysis['sampling_percentage']:.1f}%")
        print(f"Expected true positives: {analysis['expected_outcomes']['true_positives']}")
        print(f"Expected false positives: {analysis['expected_outcomes']['false_positives']}")
        print(f"Interpretation: {analysis['interpretation']['meaning']}")
        print(f"Confidence: {analysis['interpretation']['confidence']}")
        print()
    
    # Practical recommendations
    recommended = scenarios['standard']['recommended_sample_size']
    print(f"🎯 PRACTICAL RECOMMENDATION")
    print(f"Audit {recommended} randomly selected completed tasks")
    print(f"This gives 99% confidence that ≤1% of 'completed' tasks are false positives")
    print()
    
    # Confusion matrix explanation
    print(f"📈 CONFUSION MATRIX INTERPRETATION")
    print(f"True Positive (TP): Task marked complete AND actually complete")
    print(f"False Positive (FP): Task marked complete BUT not actually complete ⚠️")
    print(f"True Negative (TN): Task marked incomplete AND actually incomplete")
    print(f"False Negative (FN): Task marked incomplete BUT actually complete")
    print()
    print(f"Audit focuses on detecting False Positives (Type I error)")
    print(f"Goal: Verify that completion claims are accurate")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python audit_sample_calculator.py <total_completed_tasks>")
        print("Example: python audit_sample_calculator.py 150")
        sys.exit(1)
    
    try:
        total_completed = int(sys.argv[1])
        if total_completed <= 0:
            raise ValueError("Total completed tasks must be positive")
        
        print_audit_analysis(total_completed)
        
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)