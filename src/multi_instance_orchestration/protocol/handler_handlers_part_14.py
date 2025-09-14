
    def execute_action(self, action: StructuredAction) -> ActionResult:
        """Execute structured action and return result."""
        start_time = datetime.now()
        try:
            validation = self.validate_command(action)
            if not validation.is_valid:
                return ActionResult(success=False, message=f"Invalid command: {', '.join(validation.errors)}", execution_time=datetime.now() - start_time, correlation_id=action.correlation_id)
            key = f'{action.verb}_{action.noun}'
            if key in self.action_handlers:
                handler = self.action_handlers[key]
                result = handler(action)
                self.execution_stats['total_commands'] += 1
                if result.success:
                    self.execution_stats['successful_commands'] += 1
                else:
                    self.execution_stats['failed_commands'] += 1
                total_time = (self.execution_stats['average_execution_time'] * (self.execution_stats['total_commands'] - 1) + result.execution_time.total_seconds()) / self.execution_stats['total_commands']
                self.execution_stats['average_execution_time'] = total_time
                self.update_activity()
                return result
            else:
                return ActionResult(success=False, message=f'No handler registered for: {action.verb} {action.noun}', execution_time=datetime.now() - start_time, correlation_id=action.correlation_id)
        except Exception as e:
            self.add_health_indicator(self.create_health_indicator('action_execution', 'critical', f'Failed to execute action: {action.to_command_string()}', {'error': str(e), 'action': action.model_dump()}))
            return ActionResult(success=False, message=f'Execution failed: {str(e)}', execution_time=datetime.now() - start_time, correlation_id=action.correlation_id)
