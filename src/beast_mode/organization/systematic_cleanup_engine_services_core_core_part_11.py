
def _assess_systematic_impact_file(self, file_path: Path, category: FileCategory) -> str:
    """Assess systematic impact of individual file placement"""
    if category == FileCategory.TEMPORARY:
        return 'HIGH: Temporary files create organizational entropy'
    elif category in [FileCategory.DEVELOPMENT_ARTIFACT, FileCategory.UNKNOWN]:
        return 'MEDIUM: Misplaced files reduce systematic clarity'
    elif category == FileCategory.SYSTEMATIC_DOCUMENT:
        return 'LOW: Document placement affects accessibility but not core function'
    else:
        return 'LOW: Organizational improvement without functional impact'
