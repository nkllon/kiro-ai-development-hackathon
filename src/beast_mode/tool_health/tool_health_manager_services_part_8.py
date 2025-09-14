
    def repair_tool_systematically(self, tool_name: str, diagnosis: ToolDiagnosis) -> ToolRepairResult:
        """Repair actual tool problems systematically, not workarounds"""
        self.logger.info(f'🔧 Performing systematic repair of {tool_name}')
        start_time = datetime.now()
        repairs_applied = []
        try:
            for root_cause in diagnosis.root_causes:
                repair_action = self._apply_systematic_repair(tool_name, root_cause)
                if repair_action['applied']:
                    repairs_applied.append(repair_action['description'])
            validation_result = self._validate_tool_repair(tool_name)
            repair_duration = datetime.now() - start_time
            prevention_pattern = self._document_prevention_pattern(tool_name, diagnosis, repairs_applied)
            result = ToolRepairResult(tool_name=tool_name, repair_successful=validation_result['success'], repairs_applied=repairs_applied, validation_passed=validation_result['success'], time_to_repair=repair_duration, prevention_pattern=prevention_pattern)
            self.repair_history.append(result)
            status = 'SUCCESS' if result.repair_successful else 'FAILED'
            self.logger.info(f'🔧 Repair {status}: {tool_name} in {repair_duration.total_seconds():.1f}s')
            return result
        except Exception as e:
            repair_duration = datetime.now() - start_time
            self.logger.error(f'💥 Repair failed for {tool_name}: {e}')
            return ToolRepairResult(tool_name=tool_name, repair_successful=False, repairs_applied=repairs_applied, validation_passed=False, time_to_repair=repair_duration)
