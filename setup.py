#!/usr/bin/env python3
"""
Setup script for Devpost Integration CLI

Multi-target agile delivery:
- Hackathon demo ready
- Kiro AI showcase
- TiDB architecture example
"""

from setuptools import setup, find_packages

setup(
    name="devpost-integration",
    version="0.1.0",
    description="Systematic hackathon project management - Where Requirements ARE the Solution",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Beast Mode Development Team",
    author_email="team@beastmode.dev",
    url="https://github.com/beast-mode/devpost-integration",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "click>=8.0.0",
        "pydantic>=2.0.0",
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "devpost=devpost_integration.cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Tools",
        "Topic :: System :: Systems Administration",
    ],
    keywords="hackathon devpost systematic development kiro ai tidb",
)