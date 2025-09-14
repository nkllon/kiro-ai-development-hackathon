
def _add_pattern_to_library(self, pattern: PreventionPattern):
    """Add pattern to library with hash-based indexing for fast lookup"""
    self.pattern_library[pattern.pattern_id] = pattern
    if pattern.pattern_hash not in self.pattern_index:
        self.pattern_index[pattern.pattern_hash] = []
    self.pattern_index[pattern.pattern_hash].append(pattern.pattern_id)
    self._save_pattern_library()
