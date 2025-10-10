"""
Main entry point for the Deployment Data Governance Auditor.

This module allows the auditor to be run as a Python module:
    python -m deployment_auditor --help
"""

from .cli import cli

if __name__ == '__main__':
    cli()