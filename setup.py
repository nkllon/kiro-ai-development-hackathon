#!/usr/bin/env python3
"""
RM-DDD SDK Setup Configuration

The foundational package for systematic domain-driven development
using the Beast Mode framework and Reflective Module architecture.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "RM-DDD SDK: Systematic Domain-Driven Development Framework"

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="rm-ddd",
    version="0.1.0",
    author="Beast Mode Development Team",
    author_email="team@beastmode.dev",
    description="Systematic Domain-Driven Development SDK with Reflective Module Architecture",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/beast-mode/rm-ddd",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "myst-parser>=1.0.0",
        ],
        "examples": [
            "fastapi>=0.100.0",
            "sqlalchemy>=2.0.0",
            "pydantic>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
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
    keywords=[
        "domain-driven-design",
        "ddd",
        "reflective-module",
        "systematic-development",
        "beast-mode",
        "architecture",
        "patterns",
        "enterprise",
        "microservices",
        "bounded-context",
    ],
    project_urls={
        "Documentation": "https://rm-ddd.readthedocs.io/",
        "Source": "https://github.com/beast-mode/rm-ddd",
        "Tracker": "https://github.com/beast-mode/rm-ddd/issues",
        "Ecosystem": "https://beast-mode.dev/ecosystem",
    },
)