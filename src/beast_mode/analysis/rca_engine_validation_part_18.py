
def _add_test_pattern_to_library(self, pattern: PreventionPattern):
    """Add test-specific pattern to library with enhanced indexing"""
    self._add_pattern_to_library(pattern)
    self.logger.info(f'Added test-specific pattern to library: {pattern.pattern_id}')
