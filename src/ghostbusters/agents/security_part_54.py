from datetime import datetime
from typing import Dict, List, Any

def _calculate_security_confidence(self, findings: List[Finding], target_path: Path) -> float:
    """Calculate confidence score for security analysis"""
    base_confidence = 0.8
    if target_path.is_dir():
        base_confidence = 0.7
    if findings:
        avg_finding_confidence = sum((f.confidence for f in findings)) / len(findings)
        base_confidence = (base_confidence + avg_finding_confidence) / 2
    return min(1.0, max(0.0, base_confidence))
