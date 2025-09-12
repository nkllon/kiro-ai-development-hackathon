"""
Templates Utils

This module was extracted from templates.py
as part of RM-DDD compliance refactoring.
"""

import logging
from typing import Dict, List, Optional
from .project_generator import ProjectTemplate, ProjectType, TemplateType

def create_cli_tool_template() -> ProjectTemplate:
    """Create CLI tool project template."""
    template = ProjectTemplate('cli_tool', TemplateType.STANDARD, [ProjectType.CLI_TOOL])
    directories = ['src', 'tests', 'docs', 'src/domain', 'src/application', 'src/infrastructure', 'src/cli', 'tests/unit', 'tests/integration', 'tests/cli']
    for directory in directories:
        template.add_directory(directory)
    template.add_file_template('src/cli/main.py', _get_cli_main_template())
    template.add_file_template('src/cli/commands.py', _get_cli_commands_template())
    template.add_file_template('src/cli/config.py', _get_cli_config_template())
    template.add_dependency('click', '>=8.0.0')
    template.add_dependency('rich', '>=13.0.0')
    template.add_dependency('typer', '>=0.7.0')
    return template

def _get_library_helpers_template() -> str:
    return '"""Helper utilities for {{project_name}} library."""\n\ndef helper_function(data: str) -> str:\n    """Example helper function."""\n    return f"Processed: {data}"\n'
