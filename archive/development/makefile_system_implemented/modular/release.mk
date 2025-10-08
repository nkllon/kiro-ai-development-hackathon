# RELEASE MAKEFILE
# Generated from repository Makefiles
# Beast Mode Framework - Release Operations

release: clean build test ## Prepare release build
	@echo "Prepare release build"
	@echo "$(BLUE)🚀 Preparing systematic release...$(RESET)"
	@$(MAKE) docker-build
	@echo "$(GREEN)✅ Release build complete!$(RESET)"
	@echo "$(CYAN)📦 Artifacts:$(RESET)"
	@echo "  • Go binary: $(GO_MODULE)/bin/packer-systo"
	@echo "  • Go library: $(GO_MODULE)/lib/libpacker-systo-go.so"
	@echo "  • Python wheel: $(PYTHON_MODULE)/dist/*.whl"
	@echo "  • Docker image: $(DOCKER_IMAGE):$(VERSION)"
