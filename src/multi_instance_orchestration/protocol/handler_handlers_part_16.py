
    def get_command_help(self, verb: Optional[str]=None, noun: Optional[str]=None) -> str:
        """Get help text for commands."""
        if verb and noun:
            key = f'{verb}_{noun}'
            if key in self.command_patterns:
                pattern = self.command_patterns[key]
                help_text = f'{pattern.verb} {pattern.noun} - {pattern.description}\n'
                if pattern.allowed_modifiers:
                    help_text += f"Modifiers: {', '.join(pattern.allowed_modifiers)}\n"
                if pattern.required_parameters:
                    help_text += f"Required: {', '.join(pattern.required_parameters)}\n"
                if pattern.optional_parameters:
                    help_text += f"Optional: {', '.join(pattern.optional_parameters)}\n"
                if pattern.examples:
                    help_text += 'Examples:\n'
                    for example in pattern.examples:
                        help_text += f'  {example}\n'
                return help_text
            else:
                return f'No help available for: {verb} {noun}'
        else:
            help_text = 'Available commands:\n'
            for _key, pattern in self.command_patterns.items():
                help_text += f'  {pattern.verb} {pattern.noun} - {pattern.description}\n'
            return help_text
