#!/usr/bin/env python3
"""
Setup script for DevPost Integration CLI

Makes the CLI installable and accessible via simple commands.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="devpost-integration-cli",
    version="0.1.0",
    description="DevPost Integration CLI - Systematic Project Interrogation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Kiro AI",
    author_email="kiro@kiro-ai.com",
    url="https://github.com/kiro-ai/devpost-integration",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "httpx>=0.24.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "devpost-cli=devpost_integration.cli:main",
            "devpost=devpost_integration.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "devpost_integration": ["*.py", "*.json", "*.yaml"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: System :: Systems Administration",
    ],
    keywords="devpost hackathon cli integration systematic development",
    project_urls={
        "Bug Reports": "https://github.com/kiro-ai/devpost-integration/issues",
        "Source": "https://github.com/kiro-ai/devpost-integration",
        "Documentation": "https://github.com/kiro-ai/devpost-integration#readme",
    },
)