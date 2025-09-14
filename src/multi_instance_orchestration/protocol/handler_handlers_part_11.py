
    def _normalize_command_text(self, text: str) -> str:
        """Normalize command text for parsing."""
        replacements = {'\\bexecute\\b': 'run', '\\bhalt\\b': 'stop', '\\bin beast mode\\b': 'beast-mode', '\\bin parallel\\b': 'parallel', '\\ball running threads\\b': 'instances all', '\\bactive processes\\b': 'instances active', '\\bgracefully\\b': 'graceful'}
        normalized = text.lower().strip()
        for pattern, replacement in replacements.items():
            normalized = re.sub(pattern, replacement, normalized)
        return normalized
