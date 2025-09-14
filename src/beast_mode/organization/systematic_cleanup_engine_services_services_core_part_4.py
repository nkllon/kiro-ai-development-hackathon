
def create_systematic_cleanup_plan(self, entropy_analysis: Dict[str, Any]) -> CleanupPlan:
    """
        Create comprehensive systematic cleanup plan
        
        Generates actionable cleanup plan with systematic priorities
        """
    self.logger.info('📋 Creating systematic cleanup plan')
    plan_id = f"cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    cleanup_actions = []
    cleanup_actions.extend(self._plan_directory_creation())
    cleanup_actions.extend(self._plan_file_relocations(entropy_analysis))
    cleanup_actions.extend(self._plan_file_removals(entropy_analysis))
    cleanup_actions.extend(self._plan_maintenance_procedures())
    entropy_reduction = self._calculate_entropy_reduction(cleanup_actions)
    cleanup_plan = CleanupPlan(plan_id=plan_id, total_files=entropy_analysis['total_files_analyzed'], files_by_category=entropy_analysis['files_by_category'], files_by_priority=entropy_analysis['files_by_priority'], estimated_cleanup_time=self._estimate_cleanup_time(cleanup_actions), systematic_impact_assessment=self._assess_systematic_impact(entropy_reduction), cleanup_actions=cleanup_actions, entropy_reduction_score=entropy_reduction)
    self.cleanup_history.append(cleanup_plan)
    self.logger.info(f'✅ Cleanup plan created: {len(cleanup_actions)} actions planned')
    return cleanup_plan
