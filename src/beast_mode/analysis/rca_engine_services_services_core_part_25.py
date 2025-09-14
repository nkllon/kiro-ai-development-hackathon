
def _calculate_rca_confidence(self, analysis: ComprehensiveAnalysisResult, root_causes: List[RootCause], validations: List[ValidationResult]) -> float:
    """Calculate overall RCA confidence score"""
    analysis_confidence = analysis.analysis_confidence
    root_cause_confidence = sum((rc.confidence_score for rc in root_causes)) / max(1, len(root_causes))
    validation_confidence = sum((vr.confidence_score for vr in validations)) / max(1, len(validations))
    return (analysis_confidence + root_cause_confidence + validation_confidence) / 3
