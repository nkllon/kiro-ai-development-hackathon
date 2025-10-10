#!/usr/bin/env python3
"""
🗑️ Delete All Cloud Functions

Safely delete all Cloud Functions to reduce costs.
"""

import json
import subprocess
from typing import Any


class CloudFunctionDeleter:
    """Delete all Cloud Functions safely"""

    def __init__(self):
        """Initialize the deleter"""
        self.project_id = None
        self.functions = []

    def get_project_info(self) -> dict[str, str]:
        """Get current project information"""
        try:
            result = subprocess.run(
                ["gcloud", "config", "get-value", "project"],
                capture_output=True,
                text=True,
                check=True,
            )
            self.project_id = result.stdout.strip()

            return {"project_id": self.project_id}
        except Exception as e:
            print(f"❌ Failed to get project info: {e}")
            return {}

    def list_all_functions(self) -> list[dict[str, Any]]:
        """List all Cloud Functions"""
        try:
            result = subprocess.run(
                ["gcloud", "functions", "list", "--format=json"],
                capture_output=True,
                text=True,
                check=True,
            )

            functions = json.loads(result.stdout)
            self.functions = functions

            print(f"📋 Found {len(functions)} Cloud Functions:")
            for i, func in enumerate(functions, 1):
                name = func.get("name", "Unknown")
                # Extract just the function name from the full path
                func_name = name.split("/")[-1] if "/" in name else name
                print(f"  {i}. {func_name}")

            return functions

        except Exception as e:
            print(f"❌ Failed to list functions: {e}")
            return []

    def delete_function(self, function_name: str, region: str = "us-central1") -> bool:
        """Delete a single Cloud Function"""
        try:
            print(f"🗑️ Deleting function: {function_name}")

            result = subprocess.run(
                [
                    "gcloud",
                    "functions",
                    "delete",
                    function_name,
                    "--region=" + region,
                    "--quiet",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print(f"✅ Successfully deleted: {function_name}")
                return True
            print(f"❌ Failed to delete {function_name}: {result.stderr}")
            return False

        except Exception as e:
            print(f"❌ Error deleting {function_name}: {e}")
            return False

    def delete_all_functions(self, confirm: bool = False) -> dict[str, Any]:
        """Delete all Cloud Functions"""
        if not confirm:
            print("⚠️  WARNING: This will delete ALL Cloud Functions!")
            print("📊 Current functions:")
            functions = self.list_all_functions()

            if not functions:
                print("✅ No Cloud Functions found to delete")
                return {"deleted": 0, "failed": 0, "total": 0}

            response = input(
                "\n❓ Are you sure you want to delete ALL Cloud Functions? (yes/no): ",
            )
            if response.lower() != "yes":
                print("❌ Operation cancelled")
                return {"deleted": 0, "failed": 0, "total": len(functions)}

        functions = self.functions if self.functions else self.list_all_functions()

        if not functions:
            print("✅ No Cloud Functions found to delete")
            return {"deleted": 0, "failed": 0, "total": 0}

        print(f"\n🗑️ Starting deletion of {len(functions)} Cloud Functions...")

        deleted_count = 0
        failed_count = 0

        for func in functions:
            name = func.get("name", "")
            # Extract just the function name from the full path
            func_name = name.split("/")[-1] if "/" in name else name

            if self.delete_function(func_name):
                deleted_count += 1
            else:
                failed_count += 1

        result = {
            "deleted": deleted_count,
            "failed": failed_count,
            "total": len(functions),
        }

        print("\n📊 Deletion Summary:")
        print(f"  ✅ Successfully deleted: {deleted_count}")
        print(f"  ❌ Failed to delete: {failed_count}")
        print(f"  📋 Total functions: {len(functions)}")

        return result

    def estimate_cost_savings(self) -> dict[str, float]:
        """Estimate cost savings from deleting functions"""
        functions = self.functions if self.functions else self.list_all_functions()

        if not functions:
            return {"monthly_savings": 0.0, "annual_savings": 0.0}

        # Estimate $2.40 per function per month
        monthly_cost = len(functions) * 2.40
        annual_cost = monthly_cost * 12

        return {
            "monthly_savings": monthly_cost,
            "annual_savings": annual_cost,
            "functions_count": len(functions),
        }


def main():
    """Main function to delete all Cloud Functions"""
    print("🗑️ Cloud Functions Deletion Tool")
    print("=" * 50)

    deleter = CloudFunctionDeleter()

    # Get project info
    project_info = deleter.get_project_info()
    print(f"📋 Project: {project_info.get('project_id', 'Unknown')}")
    print("")

    # List current functions
    functions = deleter.list_all_functions()

    if not functions:
        print("✅ No Cloud Functions found to delete")
        return None

    # Estimate cost savings
    savings = deleter.estimate_cost_savings()
    print("\n💰 Estimated Cost Savings:")
    print(f"  Monthly: ${savings['monthly_savings']:.2f}")
    print(f"  Annual: ${savings['annual_savings']:.2f}")
    print(f"  Functions: {savings['functions_count']}")
    print("")

    # Delete all functions
    result = deleter.delete_all_functions()

    print("\n" + "=" * 50)
    if result["deleted"] > 0:
        print("✅ Cloud Functions deletion completed!")
        print(f"💰 Estimated monthly savings: ${savings['monthly_savings']:.2f}")
    else:
        print("❌ No functions were deleted")

    return result


if __name__ == "__main__":
    main()
