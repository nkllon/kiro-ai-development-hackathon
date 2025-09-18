#!/usr/bin/env python3
"""
Fix pyproject.toml using proper pytoml package
"""

import sys
import os

# Install pytoml first
os.system("pip3 install pytoml")

import pytoml

# Read current pyproject.toml
with open('pyproject.toml', 'r') as f:
    config = pytoml.load(f)

# Fix the configuration
config['project']['readme'] = None  # Remove readme requirement
config['project']['description'] = "AI-Powered Spec-Driven Development Framework"

# Write back properly
with open('pyproject.toml', 'w') as f:
    pytoml.dump(config, f)

print("✅ pyproject.toml fixed using pytoml")