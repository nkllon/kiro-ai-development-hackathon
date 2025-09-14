
    def monitor_test_execution(self, test_command: str, working_dir: str='.') -> List[TestFailureData]:
        """
        Monitor pytest execution and capture failure information
        Requirements: 1.1 - Automatic test failure detection
        """
        self.total_test_runs_monitored += 1
        try:
            self.logger.info(f'Monitoring test execution: {test_command}')
            with self.error_handler.handle_rca_operation('monitor_test_execution', 'test_failure_detector'):
                json_output_file = f'/tmp/pytest_output_{int(datetime.now().timestamp())}.json'
            cmd_parts = test_command.split()
            if '--json-report' not in cmd_parts:
                cmd_parts.extend(['--json-report', f'--json-report-file={json_output_file}'])
            result = subprocess.run(cmd_parts, cwd=working_dir, capture_output=True, text=True, timeout=300)
            failures = []
            if os.path.exists(json_output_file):
                try:
                    failures = self._parse_json_output(json_output_file)
                    self.logger.info(f'Parsed {len(failures)} failures from JSON output')
                    self.error_handler.monitor_component_health('json_parser', True, 100.0)
                except Exception as e:
                    self.logger.warning(f'JSON parsing failed: {e}, falling back to text parsing')
                    self.error_handler.monitor_component_health('json_parser', False, 1000.0)
                finally:
                    try:
                        os.remove(json_output_file)
                    except:
                        pass
            if not failures and result.returncode != 0:
                try:
                    failures = self.parse_pytest_output(result.stdout + result.stderr)
                    self.logger.info(f'Parsed {len(failures)} failures from text output')
                    self.error_handler.monitor_component_health('text_parser', True, 200.0)
                except Exception as e:
                    self.logger.error(f'Text parsing also failed: {e}')
                    self.error_handler.monitor_component_health('text_parser', False, 2000.0)
                    failures = [self._create_parsing_failure(test_command, str(e))]
            self.total_failures_detected += len(failures)
            if self.total_test_runs_monitored > 0:
                self.parsing_success_rate = (self.parsing_success_rate * (self.total_test_runs_monitored - 1) + (1.0 if failures or result.returncode == 0 else 0.0)) / self.total_test_runs_monitored
            return failures
        except subprocess.TimeoutExpired:
            self.logger.error('Test execution timeout - creating timeout failure')
            self.error_handler.monitor_component_health('test_execution', False, 300000.0)
            return [self._create_timeout_failure(test_command)]
        except Exception as e:
            self.logger.error(f'Test monitoring failed: {e}')
            self.error_handler.monitor_component_health('test_monitoring', False, 1000.0)
            return [self._create_monitoring_failure(test_command, str(e))]
