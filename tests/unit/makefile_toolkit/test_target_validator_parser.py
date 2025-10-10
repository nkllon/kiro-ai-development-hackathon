import os

from src.makefile_toolkit.target_validator import MakefileTargetValidator


def test_makefile_parser_skips_variable_assignments(tmp_path, monkeypatch):
    """Ensure parser ignores variable/export assignments while keeping real targets."""
    makefile = tmp_path / "Makefile"
    makefile.write_text(
        """
.DEFAULT_GOAL := help
PROJECT_ROOT := $(abspath .)
PYTHON ?= python3
export PYTHONPATH := $(PROJECT_ROOT)/src
.PHONY: help build

help: ## Show help
\t@echo "help called"

build: requirements.txt
\t@echo "build called"

requirements.txt:
\t@touch $@
"""
    )

    monkeypatch.setenv("BEAST_MODE_PROMETHEUS_ENABLED", "false")
    monkeypatch.setenv("BEAST_MODE_REDIS_ENABLED", "false")

    validator = MakefileTargetValidator(repository_root=str(tmp_path))

    targets = validator.targets

    assert "help" in targets
    assert "build" in targets
    assert "requirements.txt" in targets
    assert targets["help"].phony is True
    assert targets["help"].description == "Show help"
    assert targets["build"].dependencies == ["requirements.txt"]

    assert ".DEFAULT_GOAL" not in targets
    assert "PROJECT_ROOT" not in targets
    assert "PYTHON" not in targets
    assert "export PYTHONPATH" not in targets
