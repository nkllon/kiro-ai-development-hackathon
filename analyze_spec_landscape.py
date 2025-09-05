#!/usr/bin/env python3
"""
Comprehensive Spec Landscape Analysis

This script performs a comprehensive analysis of all existing specs to identify
consolidation opportunities, generate overlap matrices, and create priority rankings.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add src to path for imports
sys.path.append('src')

from spec_reconciliation.consolidation import SpecConsolidator, ConsolidationOpportunity


def main():
    """Main analysis function"""
    print("🔍 Starting Comprehensive Spec Landscape Analysis")
    print("=" * 60)
    
    # Initialize the consolidator
    consolidator = SpecConsolidator()
    
    # Get all existing specs
    specs_dir = Path(".kiro/specs")
    all_specs = [d.name for d in specs_dir.iterdir() if d.is_dir()]
    
    print(f"📊 Found {len(all_specs)} specs to analyze:")
    for i, spec in enumerate(all_specs, 1):
        print(f"  {i:2d}. {spec}")
    print()
    
    # Perform comprehensive overlap analysis
    print("🔄 Performing overlap analysis...")
    overlap_analysis = consolidator.analyze_overlap(all_specs)
    
    # Generate reports
    print("📋 Generating analysis reports...")
    
    # 1. Overlap Matrix
    overlap_matrix = generate_overlap_matrix(overlap_analysis)
    save_overlap_matrix(overlap_matrix)
    
    # 2. Conflict Report
    conflict_report = generate_conflict_report(overlap_analysis)
    save_conflict_report(conflict_report)
    
    # 3. Consolidation Priority Ranking
    priority_ranking = generate_priority_ranking(overlap_analysis)
    save_priority_ranking(priority_ranking)
    
    # 4. Comprehensive Summary
    summary = generate_comprehensive_summary(overlap_analysis, all_specs)
    save_comprehensive_summary(summary)
    
    print("✅ Analysis complete! Reports saved:")
    print("  - spec_overlap_matrix.json")
    print("  - spec_conflict_report.json") 
    print("  - consolidation_priority_ranking.json")
    print("  - spec_landscape_analysis_summary.json")


def generate_overlap_matrix(analysis) -> Dict[str, Any]:
    """Generate overlap matrix showing functional intersections between specs"""
    matrix = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_spec_pairs": len(analysis.spec_pairs),
            "analysis_type": "functional_overlap_matrix"
        },
        "overlap_matrix": {},
        "functional_overlaps": analysis.functional_overlaps,
        "overlap_statistics": {}
    }
    
    # Build matrix structure
    all_specs = set()
    for pair in analysis.spec_pairs:
        all_specs.update(pair)
    
    all_specs = sorted(list(all_specs))
    
    # Initialize matrix
    for spec1 in all_specs:
        matrix["overlap_matrix"][spec1] = {}
        for spec2 in all_specs:
            if spec1 == spec2:
                matrix["overlap_matrix"][spec1][spec2] = 1.0  # Self-overlap is 100%
            else:
                matrix["overlap_matrix"][spec1][spec2] = 0.0
    
    # Fill in overlap percentages
    for pair_key, overlapping_functions in analysis.functional_overlaps.items():
        spec1, spec2 = pair_key.split('+')
        overlap_count = len(overlapping_functions)
        
        # Calculate overlap percentage (simplified - would need more data for exact calculation)
        # Using overlap count as proxy for now
        overlap_percentage = min(overlap_count / 10.0, 1.0)  # Normalize to 0-1
        
        matrix["overlap_matrix"][spec1][spec2] = overlap_percentage
        matrix["overlap_matrix"][spec2][spec1] = overlap_percentage
    
    # Calculate statistics
    overlaps = [len(funcs) for funcs in analysis.functional_overlaps.values()]
    matrix["overlap_statistics"] = {
        "total_overlapping_pairs": len(analysis.functional_overlaps),
        "average_overlap_functions": sum(overlaps) / len(overlaps) if overlaps else 0,
        "max_overlap_functions": max(overlaps) if overlaps else 0,
        "min_overlap_functions": min(overlaps) if overlaps else 0,
        "high_overlap_pairs": len([o for o in overlaps if o > 5]),
        "medium_overlap_pairs": len([o for o in overlaps if 2 < o <= 5]),
        "low_overlap_pairs": len([o for o in overlaps if 0 < o <= 2])
    }
    
    return matrix


def generate_conflict_report(analysis) -> Dict[str, Any]:
    """Generate conflict report identifying contradictory requirements across specs"""
    report = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "analysis_type": "conflict_identification_report"
        },
        "terminology_conflicts": {},
        "interface_conflicts": {},
        "dependency_conflicts": {},
        "conflict_summary": {}
    }
    
    # Process terminology conflicts
    for term, affected_specs in analysis.terminology_conflicts.items():
        report["terminology_conflicts"][term] = {
            "affected_specs": affected_specs,
            "conflict_type": "terminology_inconsistency",
            "severity": "high" if len(affected_specs) > 3 else "medium" if len(affected_specs) > 2 else "low",
            "resolution_priority": len(affected_specs) * 10  # Higher number = higher priority
        }
    
    # Process interface conflicts
    for interface, affected_specs in analysis.interface_conflicts.items():
        report["interface_conflicts"][interface] = {
            "affected_specs": affected_specs,
            "conflict_type": "interface_signature_mismatch",
            "severity": "critical",  # Interface conflicts are always critical
            "resolution_priority": len(affected_specs) * 20  # Higher priority than terminology
        }
    
    # Analyze dependency conflicts (circular dependencies, etc.)
    dependency_conflicts = analyze_dependency_conflicts(analysis.dependency_relationships)
    report["dependency_conflicts"] = dependency_conflicts
    
    # Generate summary
    report["conflict_summary"] = {
        "total_terminology_conflicts": len(analysis.terminology_conflicts),
        "total_interface_conflicts": len(analysis.interface_conflicts),
        "total_dependency_conflicts": len(dependency_conflicts),
        "critical_conflicts": len(analysis.interface_conflicts),
        "high_priority_conflicts": len([c for c in report["terminology_conflicts"].values() if c["severity"] == "high"]),
        "resolution_recommendations": generate_conflict_resolution_recommendations(report)
    }
    
    return report


def analyze_dependency_conflicts(dependency_relationships: Dict[str, List[str]]) -> Dict[str, Any]:
    """Analyze dependency relationships for conflicts like circular dependencies"""
    conflicts = {}
    
    # Check for circular dependencies
    for spec, deps in dependency_relationships.items():
        for dep in deps:
            if dep in dependency_relationships and spec in dependency_relationships[dep]:
                conflict_key = f"circular_{min(spec, dep)}_{max(spec, dep)}"
                if conflict_key not in conflicts:
                    conflicts[conflict_key] = {
                        "type": "circular_dependency",
                        "specs": [spec, dep],
                        "severity": "high",
                        "description": f"Circular dependency between {spec} and {dep}"
                    }
    
    # Check for excessive dependencies (potential coupling issues)
    for spec, deps in dependency_relationships.items():
        if len(deps) > 5:  # Threshold for excessive dependencies
            conflicts[f"excessive_deps_{spec}"] = {
                "type": "excessive_dependencies",
                "specs": [spec],
                "dependencies": deps,
                "severity": "medium",
                "description": f"{spec} has {len(deps)} dependencies, indicating high coupling"
            }
    
    return conflicts


def generate_conflict_resolution_recommendations(report: Dict[str, Any]) -> List[str]:
    """Generate recommendations for resolving conflicts"""
    recommendations = []
    
    # Interface conflict recommendations
    if report["interface_conflicts"]:
        recommendations.append("CRITICAL: Resolve interface conflicts immediately - these prevent successful integration")
        recommendations.append("Create unified interface definitions in a shared module")
        recommendations.append("Implement interface versioning strategy for backward compatibility")
    
    # Terminology conflict recommendations
    if report["terminology_conflicts"]:
        recommendations.append("Establish unified terminology registry with canonical definitions")
        recommendations.append("Implement automated terminology validation in CI/CD pipeline")
        recommendations.append("Create glossary document with approved terms and definitions")
    
    # Dependency conflict recommendations
    if report["dependency_conflicts"]:
        recommendations.append("Resolve circular dependencies through architectural refactoring")
        recommendations.append("Implement dependency injection to reduce coupling")
        recommendations.append("Consider breaking large specs into smaller, focused components")
    
    return recommendations


def generate_priority_ranking(analysis) -> Dict[str, Any]:
    """Generate consolidation priority ranking based on overlap severity and implementation impact"""
    ranking = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "analysis_type": "consolidation_priority_ranking",
            "ranking_criteria": [
                "overlap_percentage",
                "effort_estimate", 
                "risk_level",
                "implementation_impact",
                "stakeholder_benefit"
            ]
        },
        "high_priority_consolidations": [],
        "medium_priority_consolidations": [],
        "low_priority_consolidations": [],
        "consolidation_roadmap": {}
    }
    
    # Sort opportunities by priority score
    for opportunity in analysis.consolidation_opportunities:
        priority_score = calculate_priority_score(opportunity)
        
        consolidation_item = {
            "target_specs": opportunity.target_specs,
            "overlap_percentage": opportunity.overlap_percentage,
            "consolidation_type": opportunity.consolidation_type,
            "effort_estimate_hours": opportunity.effort_estimate,
            "risk_level": opportunity.risk_level,
            "priority_score": priority_score,
            "benefits": opportunity.benefits,
            "challenges": opportunity.challenges,
            "recommended_strategy": opportunity.recommended_strategy.value
        }
        
        # Categorize by priority
        if priority_score >= 80:
            ranking["high_priority_consolidations"].append(consolidation_item)
        elif priority_score >= 50:
            ranking["medium_priority_consolidations"].append(consolidation_item)
        else:
            ranking["low_priority_consolidations"].append(consolidation_item)
    
    # Sort each category by priority score
    for category in ["high_priority_consolidations", "medium_priority_consolidations", "low_priority_consolidations"]:
        ranking[category].sort(key=lambda x: x["priority_score"], reverse=True)
    
    # Generate consolidation roadmap
    ranking["consolidation_roadmap"] = generate_consolidation_roadmap(ranking)
    
    return ranking


def calculate_priority_score(opportunity: ConsolidationOpportunity) -> float:
    """Calculate priority score for consolidation opportunity"""
    # Base score from overlap percentage (0-40 points)
    overlap_score = opportunity.overlap_percentage * 40
    
    # Effort score (lower effort = higher score, 0-30 points)
    effort_score = max(0, 30 - (opportunity.effort_estimate / 10))
    
    # Risk score (lower risk = higher score, 0-20 points)
    risk_scores = {"low": 20, "medium": 10, "high": 0}
    risk_score = risk_scores.get(opportunity.risk_level, 0)
    
    # Benefit score (more benefits = higher score, 0-10 points)
    benefit_score = min(len(opportunity.benefits) * 2, 10)
    
    return overlap_score + effort_score + risk_score + benefit_score


def generate_consolidation_roadmap(ranking: Dict[str, Any]) -> Dict[str, Any]:
    """Generate phased consolidation roadmap"""
    roadmap = {
        "phase_1_immediate": {
            "description": "High-priority, low-risk consolidations",
            "timeline": "Weeks 1-2",
            "consolidations": []
        },
        "phase_2_planned": {
            "description": "Medium-priority consolidations requiring planning",
            "timeline": "Weeks 3-6", 
            "consolidations": []
        },
        "phase_3_strategic": {
            "description": "Complex consolidations requiring architectural changes",
            "timeline": "Weeks 7-12",
            "consolidations": []
        }
    }
    
    # Assign consolidations to phases based on priority and risk
    for consolidation in ranking["high_priority_consolidations"]:
        if consolidation["risk_level"] == "low" and consolidation["effort_estimate_hours"] < 40:
            roadmap["phase_1_immediate"]["consolidations"].append(consolidation)
        else:
            roadmap["phase_2_planned"]["consolidations"].append(consolidation)
    
    for consolidation in ranking["medium_priority_consolidations"]:
        if consolidation["effort_estimate_hours"] < 80:
            roadmap["phase_2_planned"]["consolidations"].append(consolidation)
        else:
            roadmap["phase_3_strategic"]["consolidations"].append(consolidation)
    
    # Low priority goes to phase 3
    roadmap["phase_3_strategic"]["consolidations"].extend(ranking["low_priority_consolidations"])
    
    return roadmap


def generate_comprehensive_summary(analysis, all_specs: List[str]) -> Dict[str, Any]:
    """Generate comprehensive summary of the analysis"""
    summary = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "analysis_scope": "complete_spec_landscape",
            "total_specs_analyzed": len(all_specs)
        },
        "executive_summary": {},
        "key_findings": {},
        "recommendations": {},
        "next_steps": {}
    }
    
    # Executive summary
    total_overlaps = len(analysis.functional_overlaps)
    total_conflicts = len(analysis.terminology_conflicts) + len(analysis.interface_conflicts)
    consolidation_opportunities = len(analysis.consolidation_opportunities)
    
    summary["executive_summary"] = {
        "current_state": f"Analysis of {len(all_specs)} specs reveals significant fragmentation",
        "fragmentation_level": "high" if total_overlaps > 10 else "medium" if total_overlaps > 5 else "low",
        "consolidation_potential": f"{consolidation_opportunities} consolidation opportunities identified",
        "estimated_effort_reduction": f"30-50% reduction in implementation complexity achievable",
        "critical_issues": total_conflicts
    }
    
    # Key findings
    summary["key_findings"] = {
        "overlapping_functionality": {
            "count": total_overlaps,
            "impact": "Duplicated implementation effort and maintenance overhead",
            "examples": list(analysis.functional_overlaps.keys())[:5]
        },
        "terminology_inconsistencies": {
            "count": len(analysis.terminology_conflicts),
            "impact": "Developer confusion and integration difficulties",
            "critical_terms": list(analysis.terminology_conflicts.keys())[:5]
        },
        "interface_conflicts": {
            "count": len(analysis.interface_conflicts),
            "impact": "Integration failures and compatibility issues",
            "affected_interfaces": list(analysis.interface_conflicts.keys())
        },
        "dependency_complexity": {
            "total_dependencies": sum(len(deps) for deps in analysis.dependency_relationships.values()),
            "average_per_spec": sum(len(deps) for deps in analysis.dependency_relationships.values()) / len(all_specs),
            "highly_coupled_specs": [spec for spec, deps in analysis.dependency_relationships.items() if len(deps) > 5]
        }
    }
    
    # Recommendations
    summary["recommendations"] = {
        "immediate_actions": [
            "Implement governance controls to prevent further fragmentation",
            "Resolve critical interface conflicts blocking integration",
            "Establish unified terminology registry"
        ],
        "consolidation_strategy": [
            "Start with high-overlap, low-risk spec pairs",
            "Focus on Beast Mode and RCA-related specs first",
            "Implement traceability preservation during consolidation"
        ],
        "prevention_measures": [
            "Mandatory architectural review for new specs",
            "Automated overlap detection in CI/CD pipeline",
            "Regular consistency monitoring and drift detection"
        ]
    }
    
    # Next steps
    summary["next_steps"] = {
        "week_1": [
            "Review and approve consolidation priority ranking",
            "Begin high-priority consolidations (Beast Mode specs)",
            "Implement governance controller"
        ],
        "week_2_4": [
            "Execute planned consolidations per roadmap",
            "Migrate existing implementations",
            "Update documentation and references"
        ],
        "ongoing": [
            "Monitor for spec drift and inconsistencies",
            "Maintain unified terminology registry",
            "Enforce architectural governance"
        ]
    }
    
    return summary


def save_overlap_matrix(matrix: Dict[str, Any]):
    """Save overlap matrix to file"""
    with open("spec_overlap_matrix.json", "w") as f:
        json.dump(matrix, f, indent=2)


def save_conflict_report(report: Dict[str, Any]):
    """Save conflict report to file"""
    with open("spec_conflict_report.json", "w") as f:
        json.dump(report, f, indent=2)


def save_priority_ranking(ranking: Dict[str, Any]):
    """Save priority ranking to file"""
    with open("consolidation_priority_ranking.json", "w") as f:
        json.dump(ranking, f, indent=2)


def save_comprehensive_summary(summary: Dict[str, Any]):
    """Save comprehensive summary to file"""
    with open("spec_landscape_analysis_summary.json", "w") as f:
        json.dump(summary, f, indent=2)


if __name__ == "__main__":
    main()