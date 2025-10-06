#!/usr/bin/env python3
"""
Setup automation for Deployment Data Governance Auditor.

This script provides easy setup for different automation modes:
1. Git pre-commit hooks (automatic on every commit)
2. Daemon mode (continuous background scanning)  
3. Cron jobs (periodic scheduled scanning)
4. CI/CD integration (for build pipelines)
"""

import os
import sys
from pathlib import Path


def show_automation_options():
    """Show all available automation options."""
    
    print("🤖 Deployment Data Governance - Automation Setup")
    print("=" * 55)
    print()
    
    print("📋 Available Automation Options:")
    print()
    
    print("1. 🔗 GIT PRE-COMMIT HOOK (Recommended)")
    print("   • Automatically scans before every commit")
    print("   • Blocks commits with violations")
    print("   • Zero configuration needed")
    print("   • Setup: python scripts/install_git_hook.py")
    print()
    
    print("2. 🕐 CRON JOB (Scheduled scanning)")
    print("   • Runs periodic scans (e.g., every hour)")
    print("   • Logs results to file")
    print("   • Good for monitoring existing deployments")
    print("   • Setup: python scripts/deployment_auditor_cron.py")
    print()
    
    print("3. 🔄 DAEMON MODE (Continuous scanning)")
    print("   • Runs continuously in background")
    print("   • Configurable scan intervals")
    print("   • Real-time violation detection")
    print("   • Setup: python scripts/deployment_auditor_daemon.py")
    print()
    
    print("4. 🏗️  CI/CD INTEGRATION (Build pipeline)")
    print("   • Integrates with GitHub Actions, Jenkins, etc.")
    print("   • Fails builds on violations")
    print("   • Automated deployment protection")
    print("   • Setup: See examples below")
    print()
    
    print("🎯 QUICK SETUP COMMANDS:")
    print("-" * 25)
    print()
    
    print("# Install git hook (most common)")
    print("python scripts/install_git_hook.py")
    print()
    
    print("# Test current state")
    print("python scripts/deployment_auditor_scan.py deployment/")
    print()
    
    print("# Run daemon for 1 hour")
    print("python scripts/deployment_auditor_daemon.py --interval 300")
    print()
    
    print("# Setup hourly cron job")
    print("python scripts/deployment_auditor_cron.py --interval 60")
    print()


def show_ci_cd_examples():
    """Show CI/CD integration examples."""
    
    print("🏗️  CI/CD Integration Examples")
    print("=" * 35)
    print()
    
    print("📋 GITHUB ACTIONS (.github/workflows/deployment-audit.yml):")
    print("-" * 60)
    print("""
name: Deployment Data Governance
on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Scan for deployment violations
        run: |
          python scripts/deployment_auditor_scan.py deployment/ --exit-on-violations
""")
    
    print("📋 JENKINS (Jenkinsfile):")
    print("-" * 25)
    print("""
pipeline {
    agent any
    stages {
        stage('Deployment Audit') {
            steps {
                sh 'python scripts/deployment_auditor_scan.py deployment/ --exit-on-violations'
            }
        }
    }
}
""")
    
    print("📋 GITLAB CI (.gitlab-ci.yml):")
    print("-" * 30)
    print("""
deployment_audit:
  stage: test
  script:
    - python scripts/deployment_auditor_scan.py deployment/ --exit-on-violations
  only:
    - main
    - merge_requests
""")


def interactive_setup():
    """Interactive setup wizard."""
    
    print("🧙 Interactive Setup Wizard")
    print("=" * 30)
    print()
    
    print("What type of automation do you want?")
    print("1. Git pre-commit hook (blocks bad commits)")
    print("2. Scheduled scanning (cron job)")
    print("3. Continuous monitoring (daemon)")
    print("4. CI/CD integration (show examples)")
    print("5. Show all options")
    print()
    
    try:
        choice = input("Enter choice (1-5): ").strip()
        
        if choice == "1":
            print("\n🔗 Setting up git pre-commit hook...")
            os.system("python scripts/install_git_hook.py")
            
        elif choice == "2":
            interval = input("Scan interval in minutes (default 60): ").strip() or "60"
            print(f"\n🕐 Setting up cron job (every {interval} minutes)...")
            os.system(f"python scripts/deployment_auditor_cron.py --interval {interval}")
            
        elif choice == "3":
            interval = input("Scan interval in seconds (default 300): ").strip() or "300"
            print(f"\n🔄 Starting daemon mode (scan every {interval} seconds)...")
            print("Press Ctrl+C to stop")
            os.system(f"python scripts/deployment_auditor_daemon.py --interval {interval}")
            
        elif choice == "4":
            show_ci_cd_examples()
            
        elif choice == "5":
            show_automation_options()
            
        else:
            print("Invalid choice")
            
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled")


def main():
    """Main setup function."""
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "interactive":
            interactive_setup()
        elif sys.argv[1] == "cicd":
            show_ci_cd_examples()
        else:
            show_automation_options()
    else:
        show_automation_options()
        print()
        print("🧙 For interactive setup: python scripts/setup_automation.py interactive")
        print("🏗️  For CI/CD examples: python scripts/setup_automation.py cicd")


if __name__ == '__main__':
    main()