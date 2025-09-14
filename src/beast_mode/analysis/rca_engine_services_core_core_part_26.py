from src.rm_ddd.core.health import ModuleHealth

def _load_pattern_library(self):
    """Load existing pattern library from disk"""
    try:
        if Path(self.pattern_library_path).exists():
            with open(self.pattern_library_path, 'r') as f:
                data = json.load(f)
            for pattern_data in data.get('patterns', []):
                pattern = PreventionPattern(**pattern_data)
                self.pattern_library[pattern.pattern_id] = pattern
                if pattern.pattern_hash not in self.pattern_index:
                    self.pattern_index[pattern.pattern_hash] = []
                self.pattern_index[pattern.pattern_hash].append(pattern.pattern_id)
            self.logger.info(f'Loaded {len(self.pattern_library)} patterns from library')
    except Exception as e:
        self.logger.warning(f'Failed to load pattern library: {e}')
