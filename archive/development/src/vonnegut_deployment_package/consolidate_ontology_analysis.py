import json
import yaml
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

DIMENSION_MAPPING = {
    1: "problem_taxonomy",
    2: "infrastructure_architecture",
    3: "solution_architecture",
    4: "risk_assessment",
    5: "performance_requirements",
    6: "security_requirements",
    7: "deployment_strategy",
    8: "data_management",
    9: "dependency_management",
    10: "scalability_requirements",
    11: "maintainability",
    12: "cost_optimization",
    13: "testing_strategy",
    14: "documentation_requirements",
    15: "monitoring_observability",
    16: "recovery_mechanisms",
    17: "optimization_opportunities",
    18: "integration_patterns",
    19: "innovation_potential",
    20: "governance_compliance",
    21: "usability",
    22: "compliance_regulations",
}

BATCH_DIMENSION_RANGES = {
    1: (1, 6),
    3: (13, 18),
    4: (19, 22),
}

print("=" * 80)
print("ONTOLOGY ANALYSIS CONSOLIDATION")
print("=" * 80)

reports_dir = Path(".kiro/reports")
print(f"\n📁 Reports directory: {reports_dir}")

# Load batch files
print("\n📥 Loading batch files...")
batch_data = {}

for batch_num in [1, 3, 4]:
    batch_file = reports_dir / f"ontology-analysis-batch{batch_num}.json"
    if batch_file.exists():
        with open(batch_file) as f:
            data = json.load(f)
            batch_data[batch_num] = data
            has_specs = "specs" in data and isinstance(data["specs"], dict)
            spec_info = len(data.get("specs", {})) if has_specs else "summary only"
            print(f"✓ Loaded batch {batch_num}: {spec_info}")

# Get batch 1 summary
batch1_summary = {}
if 1 in batch_data and "dimension_summaries" in batch_data[1]:
    for dim_name, dim_data in batch_data[1]["dimension_summaries"].items():
        dim_id = dim_data.get("dimension_id")
        if dim_id:
            batch1_summary[dim_id] = {
                "name": dim_name,
                "avg_score": dim_data.get("avg_score", 0),
                "excellent_count": dim_data.get("excellent_count", 0),
                "good_count": dim_data.get("good_count", 0),
                "fair_count": dim_data.get("fair_count", 0),
                "poor_count": dim_data.get("poor_count", 0),
            }
    print(f"  ✓ Batch 1 summary: {len(batch1_summary)} dimension summaries")

# Extract dimension scores
print("\n🔍 Extracting dimension scores...")
all_scores = defaultdict(dict)

for batch_num in [3, 4]:
    if batch_num in batch_data and "specs" in batch_data[batch_num]:
        dim_range = BATCH_DIMENSION_RANGES[batch_num]
        specs = batch_data[batch_num]["specs"]
        
        for spec_name, spec_data in specs.items():
            for dim_num in range(dim_range[0], dim_range[1] + 1):
                dim_key = f"dimension_{dim_num}_{DIMENSION_MAPPING[dim_num]}"
                
                if dim_key in spec_data:
                    dim_data_item = spec_data[dim_key]
                    score = dim_data_item.get("score", 0)
                    
                    if score >= 4:
                        rating = "excellent"
                    elif score == 3:
                        rating = "good"
                    elif score == 2:
                        rating = "moderate"
                    elif score == 1:
                        rating = "poor"
                    else:
                        rating = "critical"
                    
                    all_scores[spec_name][dim_num] = {
                        "score": score * 20,
                        "rating": rating,
                        "gaps": dim_data_item.get("gaps", []),
                        "evidence": dim_data_item.get("evidence", [])
                    }
        
        extracted_count = len([s for s in specs if s in all_scores])
        print(f"  ✓ Batch {batch_num}: Extracted {extracted_count} specs, dimensions {dim_range[0]}-{dim_range[1]}")

total_specs = len(all_scores)
print(f"\n📊 Total specs with data: {total_specs}")

# Generate coverage matrix
print("\n🔨 Generating reports...")
print("  1. Building coverage matrix...")

coverage_matrix = {
    "metadata": {
        "generated_at": datetime.now().isoformat(),
        "total_specs": total_specs,
        "total_dimensions": 22,
        "available_dimensions": list(range(13, 23)),
        "missing_dimensions": list(range(1, 7)) + list(range(7, 13)),
    },
    "dimensions": {},
    "specs": {}
}

for dim_num, dim_name in DIMENSION_MAPPING.items():
    coverage_matrix["dimensions"][dim_num] = {
        "name": dim_name,
        "available": dim_num in range(13, 23),
    }

for spec_name, dimensions in all_scores.items():
    spec_entry = {
        "dimensions": {},
        "available_dimensions": len(dimensions),
        "missing_dimensions": 12,
    }
    
    for dim_num in range(1, 23):
        if dim_num in dimensions:
            spec_entry["dimensions"][dim_num] = dimensions[dim_num]
        else:
            spec_entry["dimensions"][dim_num] = {
                "score": None,
                "rating": "missing",
                "gaps": [],
                "evidence": []
            }
    
    coverage_matrix["specs"][spec_name] = spec_entry

# Dimension analysis
print("  2. Analyzing dimensions...")
dimension_stats = {}

for dim_num, dim_name in DIMENSION_MAPPING.items():
    if dim_num in batch1_summary:
        dimension_stats[dim_num] = {
            "name": dim_name,
            "available": True,
            "data_type": "summary_only",
            "average_score": batch1_summary[dim_num]["avg_score"],
            "rating_distribution": {
                "excellent": batch1_summary[dim_num]["excellent_count"],
                "good": batch1_summary[dim_num]["good_count"],
                "fair": batch1_summary[dim_num]["fair_count"],
                "poor": batch1_summary[dim_num]["poor_count"],
            }
        }
    else:
        scores_list = []
        rating_counts = Counter()
        gaps_by_spec = []
        
        for spec_name, dimensions in all_scores.items():
            if dim_num in dimensions:
                dim_data_item = dimensions[dim_num]
                score = dim_data_item.get("score", 0)
                rating = dim_data_item.get("rating", "unknown")
                
                scores_list.append((spec_name, score))
                rating_counts[rating] += 1
                
                if dim_data_item.get("gaps"):
                    gaps_by_spec.append({
                        "spec": spec_name,
                        "rating": rating,
                        "score": score,
                        "gaps": dim_data_item["gaps"]
                    })
        
        if scores_list:
            avg_score = sum(s for _, s in scores_list) / len(scores_list)
            sorted_scores = sorted(scores_list, key=lambda x: x[1])
            
            dimension_stats[dim_num] = {
                "name": dim_name,
                "available": True,
                "data_type": "per_spec",
                "total_specs_analyzed": len(scores_list),
                "average_score": round(avg_score, 2),
                "rating_distribution": dict(rating_counts),
                "top_performers": [
                    {"spec": name, "score": score}
                    for name, score in sorted_scores[-5:][::-1]
                ],
                "bottom_performers": [
                    {"spec": name, "score": score}
                    for name, score in sorted_scores[:5]
                ],
                "total_gaps": sum(len(item["gaps"]) for item in gaps_by_spec),
            }
        else:
            dimension_stats[dim_num] = {
                "name": dim_name,
                "available": False,
                "status": "missing (batch 2)",
            }

all_available_scores = []
for spec_name, dimensions in all_scores.items():
    spec_scores = [d["score"] for d in dimensions.values() if d.get("score") is not None]
    if spec_scores:
        all_available_scores.append(sum(spec_scores) / len(spec_scores))

overall_avg = sum(all_available_scores) / len(all_available_scores) if all_available_scores else 0

dimension_analysis = {
    "metadata": {
        "generated_at": datetime.now().isoformat(),
        "total_dimensions": 22,
        "available_dimensions_per_spec": 10,
        "summary_only_dimensions": 6,
        "missing_dimensions": 6,
        "overall_average_score": round(overall_avg, 2),
    },
    "dimension_analysis": dimension_stats
}

# Remediation plan
print("  3. Generating remediation plan...")
remediation_items = []

for spec_name, dimensions in all_scores.items():
    spec_avg_score = 0
    spec_score_count = 0
    spec_issues = []
    
    for dim_num, dim_data_item in dimensions.items():
        score = dim_data_item.get("score", 0)
        rating = dim_data_item.get("rating", "unknown")
        gaps = dim_data_item.get("gaps", [])
        
        if score is not None:
            spec_avg_score += score
            spec_score_count += 1
        
        if rating in ["critical", "poor"] or gaps:
            spec_issues.append({
                "dimension": DIMENSION_MAPPING[dim_num],
                "dimension_num": dim_num,
                "score": score,
                "rating": rating,
                "gaps": gaps
            })
    
    if spec_score_count > 0:
        spec_avg = spec_avg_score / spec_score_count
    else:
        spec_avg = 0
    
    if spec_issues:
        critical_count = sum(1 for i in spec_issues if i["rating"] == "critical")
        poor_count = sum(1 for i in spec_issues if i["rating"] == "poor")
        
        if critical_count >= 2 or spec_avg < 40:
            priority = "critical"
        elif critical_count >= 1 or poor_count >= 2 or spec_avg < 60:
            priority = "high"
        elif poor_count >= 1 or spec_avg < 75:
            priority = "medium"
        else:
            priority = "low"
        
        remediation_items.append({
            "spec_name": spec_name,
            "priority": priority,
            "average_score": round(spec_avg, 2),
            "critical_dimensions": critical_count,
            "poor_dimensions": poor_count,
            "total_issues": len(spec_issues),
            "issues": spec_issues
        })

priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
remediation_items.sort(key=lambda x: (priority_order[x["priority"]], x["average_score"]))

by_priority = defaultdict(list)
for item in remediation_items:
    by_priority[item["priority"]].append(item)

remediation_plan = {
    "metadata": {
        "generated_at": datetime.now().isoformat(),
        "total_items": len(remediation_items),
        "priority_distribution": {
            "critical": len(by_priority["critical"]),
            "high": len(by_priority["high"]),
            "medium": len(by_priority["medium"]),
            "low": len(by_priority["low"]),
        }
    },
    "remediation_plan": {
        "critical_priority": by_priority["critical"],
        "high_priority": by_priority["high"],
        "medium_priority": by_priority["medium"],
        "low_priority": by_priority["low"],
    }
}

# Heatmap data
print("  4. Preparing heatmap data...")
sorted_specs = sorted(all_scores.keys())

heatmap_data = {
    "metadata": {
        "generated_at": datetime.now().isoformat(),
        "rows": len(all_scores),
        "columns": 22,
        "available_dimensions": list(range(13, 23)),
        "missing_dimensions": list(range(1, 13))
    },
    "dimensions": [DIMENSION_MAPPING[i] for i in range(1, 23)],
    "specs": sorted_specs,
    "data": []
}

for spec_name in sorted_specs:
    row = []
    for dim_num in range(1, 23):
        if dim_num in all_scores[spec_name]:
            score = all_scores[spec_name][dim_num].get("score")
            row.append(score if score is not None else -1)
        else:
            row.append(-1)
    heatmap_data["data"].append(row)

# Write output files
print("\n💾 Writing output files...")

output_files = {
    "dimension-coverage-complete.json": coverage_matrix,
    "dimension-analysis-summary.json": dimension_analysis,
    "coverage-heatmap-data.json": heatmap_data,
}

for filename, data in output_files.items():
    output_path = reports_dir / filename
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  ✓ {filename}")

remediation_path = reports_dir / "gap-remediation-plan.yaml"
with open(remediation_path, "w") as f:
    yaml.dump(remediation_plan, f, default_flow_style=False, sort_keys=False)
print(f"  ✓ gap-remediation-plan.yaml")

# Summary
print("\n" + "=" * 80)
print("CONSOLIDATION SUMMARY")
print("=" * 80)

print(f"\n📈 Coverage Statistics:")
print(f"  • Total specs analyzed: {total_specs}")
print(f"  • Total dimensions: 22")
print(f"  • Available dimensions (per-spec): 10 (batches 3, 4)")
print(f"  • Summary-only dimensions: 6 (batch 1: dimensions 1-6)")
print(f"  • Missing dimensions: 6 (batch 2: dimensions 7-12)")
print(f"  • Overall average score: {overall_avg:.2f}/100")

print(f"\n🎯 Priority Distribution:")
prio_dist = remediation_plan["metadata"]["priority_distribution"]
print(f"  • Critical: {prio_dist['critical']} specs")
print(f"  • High: {prio_dist['high']} specs")
print(f"  • Medium: {prio_dist['medium']} specs")
print(f"  • Low: {prio_dist['low']} specs")

print(f"\n🚨 Top 5 Critical Remediation Priorities:")
critical_items = remediation_plan["remediation_plan"]["critical_priority"][:5]

if critical_items:
    for i, item in enumerate(critical_items, 1):
        spec_name_str = item["spec_name"]
        avg_score_str = item["average_score"]
        crit_dims = item["critical_dimensions"]
        poor_dims = item["poor_dimensions"]
        total_iss = item["total_issues"]
        print(f"\n  {i}. {spec_name_str}")
        print(f"     Score: {avg_score_str}/100")
        print(f"     Critical dimensions: {crit_dims}")
        print(f"     Poor dimensions: {poor_dims}")
        print(f"     Total issues: {total_iss}")
        if item["issues"]:
            print(f"     Key issues:")
            for issue in item["issues"][:3]:
                dim_str = issue["dimension"]
                rating_str = issue["rating"]
                score_str = issue["score"]
                print(f"       - {dim_str}: {rating_str} ({score_str}/100)")
else:
    print("  (No critical priority items)")

print(f"\n📂 Output files written to: {reports_dir}/")
print("  • dimension-coverage-complete.json")
print("  • dimension-analysis-summary.json")
print("  • gap-remediation-plan.yaml")
print("  • coverage-heatmap-data.json")

print("\n✅ Consolidation complete!")
print("=" * 80)
