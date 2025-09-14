
    def register_pattern(self, pattern: CommandPattern) -> None:
        """Register a command pattern for validation."""
        key = f'{pattern.verb}_{pattern.noun}'
        self.command_patterns[key] = pattern
        self.update_activity()
