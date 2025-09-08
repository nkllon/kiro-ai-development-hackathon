#!/usr/bin/env python3
"""
Beast Mode Framework Setup
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
    description="Systematic AI-Powered Development Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Beast Mode Development Team",
    author_email="team@beastmode.dev",
    url="https://github.com/beast-mode/framework",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=requirements,
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
        ],
    },
    entry_points={
        "console_scripts": [
            "beast-mode=beast_mode.messaging.cli:cli",
            "bm=beast_mode.messaging.cli:cli",
            "beast=beast_mode.messaging.cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: System :: Monitoring",
    ],
    keywords="ai development framework systematic collaboration agents",
    project_urls={
        "Bug Reports": "https://github.com/beast-mode/framework/issues",
        "Source": "https://github.com/beast-mode/framework",
        "Documentation": "https://beast-mode.readthedocs.io/",
    },
    include_package_data=True,
    zip_safe=False,
)