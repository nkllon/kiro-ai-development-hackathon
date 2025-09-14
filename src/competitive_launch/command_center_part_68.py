from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def _create_evidence_packages(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create evidence packages for marketing and sales."""
    packages = []
    packages.append({'type': 'systematic_superiority', 'title': 'Systematic vs Ad-hoc Development Comparison', 'metrics': metrics.get('systematic_metrics', {}), 'evidence': 'Quantitative demonstration of systematic superiority'})
    packages.append({'type': 'fmh_principles', 'title': 'FMH Principles Implementation', 'metrics': metrics.get('fmh_metrics', {}), 'evidence': 'Accountability chains and systematic governance'})
    packages.append({'type': 'requirements_driven', 'title': 'Requirements ARE the Solution', 'metrics': metrics.get('requirements_metrics', {}), 'evidence': 'Mathematical requirements-to-implementation bridge'})
    return packages
