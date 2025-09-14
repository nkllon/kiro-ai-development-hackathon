from src.rm_ddd.core.health import ModuleHealth

def _analyze_file_systematic_placement(self, file_path: Path) -> FileAnalysis:
    """Analyze individual file for systematic placement"""
    category = self._categorize_file(file_path)
    recommended_location = self._determine_systematic_location(file_path, category)
    priority = self._assess_cleanup_priority(file_path, category)
    rationale = self._generate_placement_rationale(file_path, category, recommended_location)
    systematic_impact = self._assess_systematic_impact_file(file_path, category)
    return FileAnalysis(file_path=file_path, current_location='root', category=category, recommended_location=recommended_location, cleanup_priority=priority, rationale=rationale, systematic_impact=systematic_impact, size_bytes=file_path.stat().st_size if file_path.exists() else 0, last_modified=datetime.fromtimestamp(file_path.stat().st_mtime) if file_path.exists() else datetime.now())
