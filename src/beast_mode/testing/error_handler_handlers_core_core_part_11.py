
def retry_with_simplified_parameters(self, operation: Callable, original_error: Exception, max_retries: int=3) -> Any:
    """
        Automatic retry logic with simplified parameters on test failures
        Requirements: 1.4 - Automatic retry logic with simplified parameters
        """
    self.retry_attempts_made += 1
    try:
        self.logger.info(f'Attempting retry with simplified parameters, max retries: {max_retries}')
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    delay = min(self.retry_config.base_delay_seconds * 2 ** (attempt - 1), self.retry_config.max_delay_seconds)
                    self.logger.info(f'Retry attempt {attempt + 1} after {delay:.1f}s delay')
                    time.sleep(delay)
                simplified_operation = self._simplify_operation_parameters(operation, attempt)
                result = simplified_operation()
                self.successful_retries += 1
                self.logger.info(f'Retry successful on attempt {attempt + 1}')
                return result
            except Exception as retry_error:
                self.logger.warning(f'Retry attempt {attempt + 1} failed: {retry_error}')
                if attempt == max_retries - 1:
                    continue
        raise Exception(f'All {max_retries} retry attempts failed. Original error: {original_error}')
    except Exception as e:
        self.logger.error(f'Retry logic failed: {e}')
        raise
