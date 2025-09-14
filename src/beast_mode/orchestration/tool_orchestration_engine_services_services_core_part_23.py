from src.rm_ddd.core.health import ModuleHealth

def _update_adaptive_pattern_learning(self, pattern: Dict[str, Any], response_outcome: Dict[str, Any]):
    """Update adaptive pattern based on learning from outcomes"""
    if not hasattr(pattern, 'learning_history'):
        pattern['learning_history'] = []
    learning_entry = {'timestamp': datetime.now().isoformat(), 'response_strategy': response_outcome.get('strategy'), 'success': response_outcome.get('success', False), 'actions_taken': response_outcome.get('actions', [])}
    pattern['learning_history'].append(learning_entry)
    success_rate = sum((1 for entry in pattern['learning_history'] if entry['success'])) / len(pattern['learning_history'])
    if success_rate < 0.5:
        pattern['response_strategy'] = 'escalate_to_rca'
        pattern['pattern_evolution'] = 'evolved_due_to_low_success_rate'
    self.logger.info(f"Updated adaptive pattern learning: {pattern['failure_type']} (success rate: {success_rate:.2f})")
