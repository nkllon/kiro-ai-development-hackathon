
    def _parse_test_name(self, test_name: str) -> Tuple[str, str, Optional[str]]:
        """Parse pytest node ID to extract file, function, and class"""
        try:
            parts = test_name.split('::')
            test_file = parts[0] if parts else 'unknown'
            test_function = 'unknown'
            test_class = None
            if len(parts) >= 2:
                if len(parts) == 2:
                    test_function = parts[1]
                elif len(parts) == 3:
                    test_class = parts[1]
                    test_function = parts[2]
            return (test_file, test_function, test_class)
        except Exception as e:
            self.logger.error(f'Test name parsing failed: {e}')
            return ('unknown', 'unknown', None)
