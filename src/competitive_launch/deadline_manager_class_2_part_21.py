from src.rm_ddd.core.registry import register_module

    def _analyze_current_progress(self, progress: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current progress against deadline."""
        return {'completion_percentage': progress.get('completion_percentage', 0), 'tasks_completed': progress.get('tasks_completed', 0), 'tasks_remaining': progress.get('tasks_remaining', 0), 'behind_schedule': progress.get('behind_schedule', False), 'quality_issues': progress.get('quality_issues', [])}
