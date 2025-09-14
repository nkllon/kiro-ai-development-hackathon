from src.rm_ddd.core.health import ModuleHealth

def _categorize_files_summary(self, file_analyses: List[FileAnalysis]) -> Dict[str, int]:
    """Summarize files by category"""
    summary = {}
    for analysis in file_analyses:
        category = analysis.category.value
        summary[category] = summary.get(category, 0) + 1
    return summary
