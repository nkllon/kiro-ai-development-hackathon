
def match_existing_patterns(self, failure: Failure) -> List[PreventionPattern]:
    """
        Fast pattern matching for existing failures (DR3: <1 second for 10,000+ patterns)
        """
    start_time = time.time()
    try:
        failure_signature = self._generate_failure_signature(failure)
        signature_hash = hashlib.md5(failure_signature.encode()).hexdigest()[:8]
        matching_patterns = []
        if signature_hash in self.pattern_index:
            pattern_ids = self.pattern_index[signature_hash]
            for pattern_id in pattern_ids:
                if pattern_id in self.pattern_library:
                    pattern = self.pattern_library[pattern_id]
                    if self._verify_pattern_match(failure, pattern):
                        matching_patterns.append(pattern)
                        self.pattern_matches += 1
        match_time = time.time() - start_time
        self.logger.info(f'Pattern matching completed in {match_time:.3f}s, found {len(matching_patterns)} matches')
        if match_time > 1.0:
            self.logger.warning(f'Pattern matching exceeded 1 second: {match_time:.3f}s')
        return matching_patterns
    except Exception as e:
        self.logger.error(f'Pattern matching failed: {e}')
        return []
