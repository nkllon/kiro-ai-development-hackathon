#!/usr/bin/env python3
"""
Beast Mode Framework Setup

The comprehensive AI-powered development framework with domain-driven design
and reflective module architecture for systematic software development.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = requirements_path.read_text().strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="beast-mode-framework",
    version="1.0.0",
    description="Systematic AI-Powered Development Framework with Domain-Driven Design",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Beast Mode Development Team",
    author_email="team@beastmode.dev",
    url="https://github.com/beast-mode/framework",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords=[
        "ai", "development", "framework", "systematic", "collaboration", "agents",
        "domain-driven-design", "ddd", "reflective-module", "architecture", "patterns",
        "enterprise", "microservices", "bounded-context"
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "myst-parser>=1.0.0",
            "sphinx-autodoc-typehints>=1.23.0",
        ],
        "examples": [
            "fastapi>=0.100.0",
            "sqlalchemy>=2.0.0",
            "uvicorn>=0.23.0",
            "httpx>=0.24.0",
        ],
        "testing": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.11.0",
            "factory-boy>=3.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "beast-mode=beast_mode.messaging.cli:cli",
            "bm=beast_mode.messaging.cli:cli",
            "beast=beast_mode.messaging.cli:cli",
            "rm-ddd=rm_ddd.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "rm_ddd": [
            "templates/**/*.j2",
            "stubs/**/*",
            "examples/**/*.py",
            "docs/**/*.md",
        ],
    },
    project_urls={
        "Homepage": "https://beast-mode.dev",
        "Documentation": "https://beast-mode.readthedocs.io/",
        "Repository": "https://github.com/beast-mode/framework",
        "Bug Tracker": "https://github.com/beast-mode/framework/issues",
        "Ecosystem": "https://beast-mode.dev/ecosystem",
    },
    zip_safe=False,
)