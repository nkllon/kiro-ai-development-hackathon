"""
Visualization helpers for 5D2 demonstrations.
"""

import json
from typing import Dict, List, Any


def create_quality_dashboard(dimension_scores: Dict[str, float]) -> str:
    """Create a quality dashboard visualization."""
    
    # Calculate metrics
    overall_score = sum(dimension_scores.values()) / len(dimension_scores)
    critical_gaps = [dim for dim, score in dimension_scores.items() if score < 0.70]
    
    # Create text-based dashboard
    dashboard = f"""
📊 5D2 Quality Dashboard
========================

Overall Quality Score: {overall_score:.3f}
Critical Gaps: {len(critical_gaps)} dimensions
Phase 5D2 Complete: {'✅ YES' if overall_score >= 0.85 else '❌ NO'}
Phase 5D3 Ready: {'✅ YES' if overall_score >= 0.90 and len(critical_gaps) == 0 else '❌ NO'}

Top Performing Dimensions:
"""
    
    # Sort dimensions by score
    sorted_dims = sorted(dimension_scores.items(), key=lambda x: x[1], reverse=True)
    
    for i, (dim, score) in enumerate(sorted_dims[:5]):
        status = "🟢" if score >= 0.80 else "🟡" if score >= 0.70 else "🔴"
        dashboard += f"{status} {dim}: {score:.3f}\n"
    
    if critical_gaps:
        dashboard += "\nCritical Gaps:\n"
        for gap in critical_gaps:
            dashboard += f"🔴 {gap}: {dimension_scores[gap]:.3f}\n"
    
    return dashboard


def create_enhancement_progress_chart(enhancement_cycles: List[Dict[str, Any]]) -> str:
    """Create enhancement progress visualization."""
    
    chart = """
📈 Enhancement Progress
======================

"""
    
    for i, cycle in enumerate(enhancement_cycles):
        chart += f"Cycle {i+1}: {cycle.get('improvements', 0)} improvements\n"
    
    return chart


def create_system_architecture_diagram() -> str:
    """Create system architecture diagram."""
    
    return """
🏗️ 5D2 System Architecture
===========================

┌─────────────────────────────────────────────────────────────┐
│                5D2 Enhancement Orchestrator                 │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ 22-Dimension    │  │ Quality         │  │ Enhancement  │ │
│  │ Analyzer        │  │ Validator       │  │ Engines      │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Jaeger Tracing  │  │ CLI Interface   │  │ Production   │ │
│  │ & Observability │  │ & Automation    │  │ Validation   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
"""