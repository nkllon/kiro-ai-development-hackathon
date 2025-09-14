
    def parse_command(self, text: str) -> StructuredAction:
        """Parse human-readable text into structured action.

        Supports natural language variations:
        - 'run task abc beast mode' -> verb=run, noun=task, modifiers=[beast-mode]
        - 'execute task xyz in parallel' -> verb=run, noun=task, modifiers=[parallel]
        - 'stop all running threads' -> verb=stop, noun=instances, modifiers=[all]
        """
        try:
            normalized = self._normalize_command_text(text)
            try:
                action = StructuredAction.from_command_string(normalized, self.instance_id)
                self.command_history.append(action)
                return action
            except ValueError:
                action = self._parse_natural_language(text)
                self.command_history.append(action)
                return action
        except Exception as e:
            self.add_health_indicator(self.create_health_indicator('command_parsing', 'warning', f'Failed to parse command: {text}', {'error': str(e)}))
            raise ValueError(f"Failed to parse command '{text}': {e}") from e
