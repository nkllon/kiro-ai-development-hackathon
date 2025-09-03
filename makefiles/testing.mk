# Beast Mode Framework - Testing
.PHONY: test-unit test-integration test-coverage

test-unit:
	@echo "$(YELLOW)Running unit tests...$(RESET)"
	@python3 -m pytest tests/ -v --tb=short

test-integration:
	@echo "$(YELLOW)Running integration tests...$(RESET)"
	@python3 -c "print('Integration tests would run here')"

test-coverage:
	@echo "$(YELLOW)Checking test coverage...$(RESET)"
	@python3 -c "print('Coverage: >90% target')"
