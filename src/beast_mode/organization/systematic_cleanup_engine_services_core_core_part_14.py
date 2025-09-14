from src.rm_ddd.core.health import ModuleHealth

def _prioritize_files_summary(self, file_analyses: List[FileAnalysis]) -> Dict[str, int]:
    """Summarize files by cleanup priority"""
    summary = {}
    for analysis in file_analyses:
        priority = analysis.cleanup_priority.value
        summary[priority] = summary.get(priority, 0) + 1
    return summary
