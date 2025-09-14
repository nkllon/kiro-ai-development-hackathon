from src.rm_ddd.core.health import ModuleHealth

    def parse_pytest_output(self, output: str) -> List[TestFailureData]:
        """
        Parse pytest text output to extract failure information
        Requirements: 1.3, 5.1 - Extract stack traces, error messages, and context
        """
        try:
            failures = []
            lines = output.split('\n')
            in_failures_section = False
            current_failure = None
            current_traceback = []
            current_error_lines = []
            for i, line in enumerate(lines):
                if re.match(self.pytest_output_patterns['failure_header'], line):
                    in_failures_section = True
                    continue
                if not in_failures_section:
                    continue
                failure_match = re.match(self.pytest_output_patterns['test_failure_start'], line)
                if failure_match:
                    if current_failure:
                        failure_data = self._create_failure_data(current_failure, current_traceback, current_error_lines)
                        if failure_data:
                            failures.append(failure_data)
                    current_failure = failure_match.group(1).strip()
                    current_traceback = []
                    current_error_lines = []
                    continue
                if current_failure:
                    if line.startswith('E '):
                        current_error_lines.append(line[2:].strip())
                    elif line.startswith('>'):
                        current_traceback.append(line[1:].strip())
                    elif line.strip() and (not line.startswith('_')):
                        current_traceback.append(line.strip())
            if current_failure:
                failure_data = self._create_failure_data(current_failure, current_traceback, current_error_lines)
                if failure_data:
                    failures.append(failure_data)
            self.logger.info(f'Parsed {len(failures)} failures from pytest output')
            return failures
        except Exception as e:
            self.logger.error(f'Pytest output parsing failed: {e}')
            return []
