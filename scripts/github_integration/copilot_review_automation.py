#!/usr/bin/env python3
"""
GitHub Copilot Review Automation
Integrates with our MCP system and security-first approach
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import with fallback for missing grpc module
try:
    from src.secure_shell_service.elegant_client import secure_execute
except ImportError:
    # Fallback for environments without grpc (like GitHub Actions)
    async def secure_execute(command: str) -> dict[str, Any]:
        """Fallback secure_execute for environments without grpc"""
        try:
            # Use secure shell service instead of subprocess with shell=True
            from src.secure_shell_service.client import secure_execute

            return await secure_execute(command, timeout=30)
        except Exception as e:
            return {"success": False, "error": str(e)}


class CopilotReviewAutomation:
    """Automate GitHub Copilot code reviews with our security-first approach"""

    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo_owner = os.getenv("GITHUB_REPOSITORY_OWNER")
        self.repo_name = os.getenv("GITHUB_REPOSITORY_NAME")

    async def request_copilot_review(self, pr_number: int) -> dict[str, Any]:
        """Request Copilot review for a pull request"""
        try:
            # Note: Direct Copilot review requests require GitHub App permissions
            # For now, we'll provide manual instructions
            return {
                "success": True,
                "message": f"Manual Copilot review instructions for PR #{pr_number}",
                "pr_number": pr_number,
                "instructions": [
                    "1. Open this PR in VS Code with GitHub Copilot extension",
                    "2. Use '@copilot review' to request a code review",
                    "3. Follow the security-first guidelines in .github/copilot-instructions.md",
                    "4. Address any issues identified by Copilot",
                ],
            }

        except Exception as e:
            return {"success": False, "error": str(e), "pr_number": pr_number}

    async def check_review_status(self, pr_number: int) -> dict[str, Any]:
        """Check the status of Copilot review"""
        try:
            # Get review status from GitHub API
            result = await secure_execute(f"gh pr view {pr_number} --json reviews")

            if result["success"]:
                reviews_data = json.loads(result["output"])
                copilot_review = None

                for review in reviews_data.get("reviews", []):
                    if review.get("author", {}).get("login") == "github-actions[bot]":
                        copilot_review = review
                        break

                return {
                    "success": True,
                    "review_found": copilot_review is not None,
                    "review_state": (copilot_review.get("state") if copilot_review else None),
                    "review_body": (copilot_review.get("body") if copilot_review else None),
                }
            return {"success": False, "error": result["error"]}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def analyze_security_issues(self, pr_number: int) -> dict[str, Any]:
        """Analyze PR for security issues using our guidelines"""
        try:
            # Get PR files
            result = await secure_execute(f"gh pr view {pr_number} --json files")

            if not result["success"]:
                return {"success": False, "error": result["error"]}

            files_data = json.loads(result["output"])
            security_issues = []

            # Check each file for security issues
            for file_info in files_data.get("files", []):
                file_path = file_info.get("path")
                if file_path and file_path.endswith(".py"):
                    # Check for subprocess usage
                    content_result = await secure_execute(
                        f"gh pr view {pr_number} --json files --json patches",
                    )

                    if content_result["success"]:
                        content_data = json.loads(content_result["output"])
                        # Analyze for security patterns
                        if "subprocess.run" in content_data.get("patches", ""):
                            security_issues.append(
                                {
                                    "file": file_path,
                                    "issue": "subprocess.run detected",
                                    "severity": "high",
                                    "recommendation": "Use elegant secure shell client instead",
                                },
                            )

            return {
                "success": True,
                "security_issues": security_issues,
                "total_issues": len(security_issues),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def validate_model_compliance(self, pr_number: int) -> dict[str, Any]:
        """Validate that PR changes comply with our model-driven architecture"""
        try:
            # Get PR changes
            result = await secure_execute(
                f"gh pr view {pr_number} --json files --json patches",
            )

            if not result["success"]:
                return {"success": False, "error": result["error"]}

            changes_data = json.loads(result["output"])
            compliance_issues = []

            # Check for model registry updates
            for file_info in changes_data.get("files", []):
                file_path = file_info.get("path")

                if file_path == "project_model_registry.json":
                    # Validate model registry changes
                    compliance_issues.append(
                        {
                            "file": file_path,
                            "type": "model_registry_change",
                            "severity": "medium",
                            "recommendation": "Verify domain classification and tool mappings",
                        },
                    )

                elif file_path.endswith(".py") and "src/" in file_path:
                    # Check for proper domain structure
                    if not any(
                        domain in file_path
                        for domain in [
                            "ghostbusters",
                            "mcp_integration",
                            "secure_shell_service",
                        ]
                    ):
                        compliance_issues.append(
                            {
                                "file": file_path,
                                "type": "domain_classification",
                                "severity": "low",
                                "recommendation": "Verify proper domain classification in project_model_registry.json",
                            },
                        )

            return {
                "success": True,
                "compliance_issues": compliance_issues,
                "total_issues": len(compliance_issues),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


async def main():
    """Main function for Copilot review automation"""
    print("🤖 GitHub Copilot Review Automation")
    print("=" * 50)

    automation = CopilotReviewAutomation()

    # Get PR number from environment
    pr_number = os.getenv("PR_NUMBER")
    if not pr_number:
        print("❌ PR_NUMBER environment variable not set")
        return

    print(f"🔍 Analyzing PR #{pr_number}")

    # Request Copilot review (manual instructions)
    review_result = await automation.request_copilot_review(int(pr_number))
    print(f"📝 Review Instructions: {review_result}")

    # Analyze security issues
    security_result = await automation.analyze_security_issues(int(pr_number))
    print(f"🛡️ Security Analysis: {security_result}")

    # Validate model compliance
    compliance_result = await automation.validate_model_compliance(int(pr_number))
    print(f"📋 Model Compliance: {compliance_result}")

    # Summary
    print("\n🎯 Summary:")
    print(f"   Security Issues: {security_result.get('total_issues', 0)}")
    print(f"   Compliance Issues: {compliance_result.get('total_issues', 0)}")
    print("   Review Method: Manual Copilot review")

    # Print manual instructions
    if review_result.get("instructions"):
        print("\n🤖 Manual Copilot Review Instructions:")
        for instruction in review_result["instructions"]:
            print(f"   • {instruction}")


if __name__ == "__main__":
    asyncio.run(main())
