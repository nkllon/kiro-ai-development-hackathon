#!/usr/bin/env python3
"""
Install Anti-Duplication Git Hooks and CI/CD Integration

This script installs the necessary hooks and configurations to enforce
the anti-duplication system in the development workflow.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any


def install_git_hooks(repo_root: Path) -> Dict[str, Any]:
    """Install git hooks for anti-duplication enforcement."""
    hooks_dir = repo_root / ".git" / "hooks"
    
    if not hooks_dir.exists():
        return {"error": "Not a git repository or hooks directory not found"}
    
    results = {}
    
    # Pre-commit hook
    pre_commit_hook = hooks_dir / "pre-commit"
    pre_commit_content = '''#!/usr/bin/env python3
"""
Anti-Duplication Pre-Commit Hook

Validates that all commits include valid discovery attestations
for any new development.
"""

import sys
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from anti_duplication.git_integration import validate_commit_for_duplication
    
    def main():
        """Main pre-commit validation."""
        try:
            # Get staged files
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True, text=True, check=True
            )
            staged_files = result.stdout.strip().split('\\n') if result.stdout.strip() else []
            
            # Validate commit
            validation_result = validate_commit_for_duplication(staged_files)
            
            if not validation_result["valid"]:
                print("❌ COMMIT BLOCKED: Anti-duplication validation failed")
                print(f"Reason: {validation_result['reason']}")
                
                if validation_result.get("required_actions"):
                    print("\\nRequired actions:")
                    for action in validation_result["required_actions"]:
                        print(f"  • {action}")
                
                print("\\n💡 To bypass this check (emergency only):")
                print("   git commit --no-verify -m 'your message'")
                print("   (This will trigger mandatory review)")
                
                return 1
            
            print("✅ Anti-duplication validation passed")
            return 0
            
        except Exception as e:
            print(f"❌ Anti-duplication validation error: {e}")
            print("💡 Use --no-verify to bypass (emergency only)")
            return 1
    
    if __name__ == "__main__":
        sys.exit(main())

except ImportError:
    print("⚠️  Anti-duplication system not available - skipping validation")
    sys.exit(0)
'''
    
    with open(pre_commit_hook, 'w') as f:
        f.write(pre_commit_content)
    
    # Make executable
    os.chmod(pre_commit_hook, 0o755)
    results["pre_commit"] = "installed"
    
    # Pre-push hook
    pre_push_hook = hooks_dir / "pre-push"
    pre_push_content = '''#!/usr/bin/env python3
"""
Anti-Duplication Pre-Push Hook

Final validation before pushing to remote repository.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from anti_duplication.git_integration import validate_push_for_duplication
    
    def main():
        """Main pre-push validation."""
        try:
            # Read push information from stdin
            push_info = sys.stdin.read().strip()
            
            validation_result = validate_push_for_duplication(push_info)
            
            if not validation_result["valid"]:
                print("❌ PUSH BLOCKED: Anti-duplication validation failed")
                print(f"Reason: {validation_result['reason']}")
                return 1
            
            print("✅ Anti-duplication push validation passed")
            return 0
            
        except Exception as e:
            print(f"❌ Anti-duplication push validation error: {e}")
            return 1
    
    if __name__ == "__main__":
        sys.exit(main())

except ImportError:
    print("⚠️  Anti-duplication system not available - skipping validation")
    sys.exit(0)
'''
    
    with open(pre_push_hook, 'w') as f:
        f.write(pre_push_content)
    
    os.chmod(pre_push_hook, 0o755)
    results["pre_push"] = "installed"
    
    return results


def create_github_workflow(repo_root: Path) -> Dict[str, Any]:
    """Create GitHub Actions workflow for anti-duplication."""
    workflows_dir = repo_root / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    workflow_file = workflows_dir / "anti-duplication.yml"
    workflow_content = '''name: Anti-Duplication Validation

on:
  pull_request:
    branches: [ main, develop ]
  push:
    branches: [ main, develop ]

jobs:
  anti-duplication-check:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 0  # Need full history for analysis
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run Anti-Duplication Analysis
      run: |
        python -m anti_duplication.ci_integration --validate-pr
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        PR_NUMBER: ${{ github.event.number }}
    
    - name: Upload Analysis Results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: anti-duplication-analysis
        path: .anti_duplication/analysis_results.json
    
    - name: Comment on PR
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          try {
            const results = JSON.parse(fs.readFileSync('.anti_duplication/analysis_results.json', 'utf8'));
            
            let comment = '## 🔍 Anti-Duplication Analysis\\n\\n';
            
            if (results.validation_passed) {
              comment += '✅ **Validation Passed** - No duplicate development detected\\n\\n';
            } else {
              comment += '❌ **Validation Failed** - Potential duplicate development detected\\n\\n';
              comment += `**Reason:** ${results.reason}\\n\\n`;
              
              if (results.existing_solutions && results.existing_solutions.length > 0) {
                comment += '**Existing Solutions Found:**\\n';
                results.existing_solutions.forEach(solution => {
                  comment += `- ${solution.name} (${solution.file_path}) - ${solution.similarity_score}% similar\\n`;
                });
                comment += '\\n';
              }
              
              if (results.required_actions && results.required_actions.length > 0) {
                comment += '**Required Actions:**\\n';
                results.required_actions.forEach(action => {
                  comment += `- ${action}\\n`;
                });
              }
            }
            
            comment += `\\n**Analysis Details:**\\n`;
            comment += `- Capabilities scanned: ${results.capabilities_scanned}\\n`;
            comment += `- Discovery completeness: ${results.discovery_completeness}%\\n`;
            comment += `- Analysis timestamp: ${results.timestamp}\\n`;
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
          } catch (error) {
            console.log('Could not read analysis results:', error);
          }
'''
    
    with open(workflow_file, 'w') as f:
        f.write(workflow_content)
    
    return {"github_workflow": "created"}


def create_ci_integration_module(repo_root: Path) -> Dict[str, Any]:
    """Create CI/CD integration module."""
    ci_module_path = repo_root / "src" / "anti_duplication" / "ci_integration.py"
    
    ci_module_content = '''"""
CI/CD Integration for Anti-Duplication System

Provides integration points for continuous integration systems
to enforce anti-duplication policies.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

from .capability_registry import CapabilityRegistry
from .discovery_engine import CapabilityDiscoveryEngine
from .development_gate import DevelopmentGate
from .models import DevelopmentRequest


class CIIntegration:
    """CI/CD integration for anti-duplication enforcement."""
    
    def __init__(self, repo_root: Path):
        """Initialize CI integration."""
        self.repo_root = repo_root
        
        # Initialize anti-duplication components
        self.registry = CapabilityRegistry(repo_root)
        self.discovery_engine = CapabilityDiscoveryEngine(self.registry)
        self.gate = DevelopmentGate(self.discovery_engine)
    
    def validate_pull_request(self, pr_files: List[str]) -> Dict[str, Any]:
        """
        Validate a pull request for potential duplicate development.
        
        Args:
            pr_files: List of files changed in the pull request
            
        Returns:
            Validation results
        """
        # Analyze changed files for new functionality
        new_functionality = self._analyze_new_functionality(pr_files)
        
        if not new_functionality:
            return {
                "validation_passed": True,
                "reason": "No new functionality detected",
                "capabilities_scanned": 0,
                "discovery_completeness": 100,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Perform capability discovery
        inventory = self.discovery_engine.discover_existing_solutions(
            " ".join(new_functionality)
        )
        
        # Analyze overlap
        overlap_analysis = self.discovery_engine.assess_functional_overlap(
            " ".join(new_functionality), inventory
        )
        
        # Make validation decision
        validation_passed = overlap_analysis.functional_similarity_score < 0.7
        
        results = {
            "validation_passed": validation_passed,
            "reason": self._generate_validation_reason(overlap_analysis),
            "capabilities_scanned": len(inventory.existing_solutions),
            "discovery_completeness": int(inventory.discovery_completeness_score * 100),
            "overlap_score": overlap_analysis.functional_similarity_score,
            "existing_solutions": [
                {
                    "name": cap.existing_solution.name,
                    "file_path": cap.existing_solution.file_path,
                    "similarity_score": int(cap.similarity_score * 100)
                }
                for cap in overlap_analysis.overlapping_capabilities[:5]
            ],
            "required_actions": self._generate_required_actions(overlap_analysis),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Save results for CI system
        results_path = self.repo_root / ".anti_duplication" / "analysis_results.json"
        results_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        return results
    
    def _analyze_new_functionality(self, pr_files: List[str]) -> List[str]:
        """Analyze PR files to identify new functionality."""
        new_functionality = []
        
        for file_path in pr_files:
            if file_path.endswith('.py'):
                # Simple heuristic: look for new classes and functions
                try:
                    with open(self.repo_root / file_path, 'r') as f:
                        content = f.read()
                    
                    # Extract class and function names (simplified)
                    import re
                    classes = re.findall(r'class\\s+(\\w+)', content)
                    functions = re.findall(r'def\\s+(\\w+)', content)
                    
                    new_functionality.extend(classes)
                    new_functionality.extend(functions)
                    
                except Exception:
                    continue  # Skip files that can't be read
        
        return new_functionality
    
    def _generate_validation_reason(self, overlap_analysis) -> str:
        """Generate human-readable validation reason."""
        if overlap_analysis.functional_similarity_score > 0.9:
            return "Extremely high similarity to existing capabilities detected"
        elif overlap_analysis.functional_similarity_score > 0.7:
            return "High similarity to existing capabilities - review required"
        elif overlap_analysis.functional_similarity_score > 0.5:
            return "Moderate similarity detected - consider reusing existing capabilities"
        else:
            return "Low similarity - new development appears justified"
    
    def _generate_required_actions(self, overlap_analysis) -> List[str]:
        """Generate required actions based on overlap analysis."""
        actions = []
        
        if overlap_analysis.functional_similarity_score > 0.7:
            actions.append("Review existing similar capabilities before proceeding")
            actions.append("Consider enhancing existing solutions instead of new development")
            actions.append("Provide justification for new development approach")
        
        if overlap_analysis.overlapping_capabilities:
            actions.append("Coordinate with existing capability owners")
        
        return actions


def main():
    """Main CLI entry point for CI integration."""
    parser = argparse.ArgumentParser(description="Anti-Duplication CI Integration")
    parser.add_argument("--validate-pr", action="store_true", 
                       help="Validate pull request for duplicate development")
    parser.add_argument("--pr-files", nargs="*", 
                       help="List of files changed in PR")
    
    args = parser.parse_args()
    
    repo_root = Path.cwd()
    ci_integration = CIIntegration(repo_root)
    
    if args.validate_pr:
        # Get changed files from git if not provided
        if not args.pr_files:
            import subprocess
            try:
                result = subprocess.run(
                    ["git", "diff", "--name-only", "origin/main...HEAD"],
                    capture_output=True, text=True, check=True
                )
                pr_files = result.stdout.strip().split('\\n') if result.stdout.strip() else []
            except subprocess.CalledProcessError:
                print("Error: Could not get changed files from git")
                return 1
        else:
            pr_files = args.pr_files
        
        # Validate PR
        results = ci_integration.validate_pull_request(pr_files)
        
        # Print results
        if results["validation_passed"]:
            print("✅ Anti-duplication validation passed")
            return 0
        else:
            print("❌ Anti-duplication validation failed")
            print(f"Reason: {results['reason']}")
            
            if results.get("required_actions"):
                print("\\nRequired actions:")
                for action in results["required_actions"]:
                    print(f"  • {action}")
            
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''
    
    with open(ci_module_path, 'w') as f:
        f.write(ci_module_content)
    
    return {"ci_integration": "created"}


def main():
    """Main installation function."""
    repo_root = Path.cwd()
    
    print("🔧 Installing Anti-Duplication System Integration")
    print("=" * 60)
    
    # Install git hooks
    print("📎 Installing Git hooks...")
    hook_results = install_git_hooks(repo_root)
    for hook, status in hook_results.items():
        print(f"  ✅ {hook}: {status}")
    
    # Create GitHub workflow
    print("\\n🔄 Creating GitHub Actions workflow...")
    workflow_results = create_github_workflow(repo_root)
    for item, status in workflow_results.items():
        print(f"  ✅ {item}: {status}")
    
    # Create CI integration module
    print("\\n🔗 Creating CI integration module...")
    ci_results = create_ci_integration_module(repo_root)
    for item, status in ci_results.items():
        print(f"  ✅ {item}: {status}")
    
    print("\\n✅ Anti-Duplication System Integration installed successfully!")
    print("\\n📋 Next steps:")
    print("  1. Commit the new workflow and integration files")
    print("  2. Test the system with a sample development request")
    print("  3. Configure any additional CI/CD systems you use")
    print("  4. Train your team on the new discovery process")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())