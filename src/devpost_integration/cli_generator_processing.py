"""
Cli Generator Processing

This module was extracted from cli_generator.py
as part of RM-DDD compliance refactoring.
"""

import ast
import inspect
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from .reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, ModuleConfiguration, register_module
from .reflective_module import ReflectiveModuleRegistry

def process_input(self, input_data: bytes, format_type: str='auto') -> ProcessedInput:
    """Process stdin input based on format"""
    if format_type == 'auto':
        format_type = self.detect_format(input_data)
    processor = self.formats.get(format_type, self.process_text_input)
    return processor(input_data)

def process_json_input(self, input_data: bytes) -> ProcessedInput:
    """Process JSON input from stdin"""
    try:
        data = json.loads(input_data.decode('utf-8'))
        return ProcessedInput(format='json', data=data, success=True)
    except json.JSONDecodeError as e:
        return ProcessedInput(format='json', data=None, success=False, error=str(e))

def process_text_input(self, input_data: bytes) -> ProcessedInput:
    """Process text input from stdin"""
    try:
        text = input_data.decode('utf-8')
        lines = text.strip().split('\n') if text.strip() else []
        return ProcessedInput(format='text', data=lines, success=True)
    except UnicodeDecodeError as e:
        return ProcessedInput(format='text', data=None, success=False, error=str(e))

def process_binary_input(self, input_data: bytes) -> ProcessedInput:
    """Process binary input from stdin"""
    return ProcessedInput(format='binary', data=input_data, success=True)

def process_output(self, output_data: Any, format_type: str='json') -> bytes:
    """Process output data for stdout"""
    processor = self.formats.get(format_type, self.output_json)
    return processor(output_data)
