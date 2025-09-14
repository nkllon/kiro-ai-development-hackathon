from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _create_execution_summary(self, execution_start: datetime, iterations: int) -> Dict:
        """Create execution summary."""
        execution_end = datetime.now()
        total_duration = (execution_end - execution_start).total_seconds()
        stats = self.task_manager.get_task_stats()
        
        # Handle Git operations
        git_status = "branch_preserved"
        if self.git_session and self.git_session.changes_made:
            commit_msg = f"Task execution completed - {stats[TaskStatus.COMPLETED.value]} tasks"
            self.git_session.commit_changes(commit_msg)
            self.git_session.push_branch()
            
            success_rate = stats[TaskStatus.COMPLETED.value] / sum(stats.values()) * 100
            
            if self.auto_merge and success_rate >= 80:
                if self.git_session.merge_to_base():
                    self.git_session.cleanup_branch()
                    git_status = "merged_and_cleaned"
                else:
                    git_status = "merge_failed"
        
        return {
            "execution_start": execution_start.isoformat(),
            "execution_end": execution_end.isoformat(),
            "total_duration_seconds": total_duration,
            "iterations": iterations,
            "task_stats": stats,
            "git_status": git_status,
            "success": stats[TaskStatus.COMPLETED.value] > 0
        }