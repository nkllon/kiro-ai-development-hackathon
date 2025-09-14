
def add_consistency_check(self, check: ConsistencyCheck) -> None:
    """Add custom consistency check"""
    self._consistency_checks.append(check)
    self.logger.info(f'Added consistency check: {check.name}')
