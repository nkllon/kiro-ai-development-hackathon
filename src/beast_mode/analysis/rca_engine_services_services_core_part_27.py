from src.rm_ddd.core.health import ModuleHealth

def _save_pattern_library(self):
    """Save pattern library to disk"""
    try:
        Path(self.pattern_library_path).parent.mkdir(parents=True, exist_ok=True)
        patterns_data = []
        for pattern in self.pattern_library.values():
            patterns_data.append({'pattern_id': pattern.pattern_id, 'pattern_name': pattern.pattern_name, 'failure_signature': pattern.failure_signature, 'root_cause_pattern': pattern.root_cause_pattern, 'prevention_steps': pattern.prevention_steps, 'detection_criteria': pattern.detection_criteria, 'automated_checks': pattern.automated_checks, 'pattern_hash': pattern.pattern_hash})
        data = {'patterns': patterns_data, 'last_updated': datetime.now().isoformat(), 'pattern_count': len(patterns_data)}
        with open(self.pattern_library_path, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        self.logger.error(f'Failed to save pattern library: {e}')
