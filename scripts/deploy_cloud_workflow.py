#!/usr/bin/env python3
"""
Deploy Cloud Workflow - Deploy GCP setup workflow to Cloud Workflows
"""

import os
import subprocess
import json
from typing import Dict, Any


class CloudWorkflowDeployer:
    """Deploy GCP setup workflow to Cloud Workflows"""

    def __init__(self, project_id: str, region: str = "us-central1"):
        self.project_id = project_id
        self.region = region
        self.workflow_name = "gcp-setup-workflow"

    def deploy_workflow(self) -> Dict[str, Any]:
        """Deploy the workflow to Cloud Workflows"""
        print("🚀 Deploying GCP Setup Workflow to Cloud Workflows")
        print("=" * 60)

        try:
            # Deploy the workflow
            result = subprocess.run(
                [
                    "gcloud",
                    "workflows",
                    "deploy",
                    self.workflow_name,
                    "--source",
                    "scripts/gcp_cloud_workflows_setup.yaml",
                    "--location",
                    self.region,
                    "--project",
                    self.project_id,
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            print("✅ Workflow deployed successfully")
            print(f"📁 Workflow name: {self.workflow_name}")
            print(f"📍 Region: {self.region}")
            print(f"🏗️ Project: {self.project_id}")

            return {
                "success": True,
                "workflow_name": self.workflow_name,
                "region": self.region,
                "project_id": self.project_id,
            }

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to deploy workflow: {e.stderr}")
            return {"success": False, "error": e.stderr}

    def execute_workflow(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the deployed workflow"""
        print(f"\n🎯 Executing Workflow: {self.workflow_name}")
        print("=" * 50)

        try:
            # Execute the workflow
            result = subprocess.run(
                [
                    "gcloud",
                    "workflows",
                    "execute",
                    self.workflow_name,
                    "--location",
                    self.region,
                    "--project",
                    self.project_id,
                    "--data",
                    json.dumps(input_data),
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            print("✅ Workflow executed successfully")
            print(f"📊 Execution result: {result.stdout}")

            return {"success": True, "execution_result": result.stdout}

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to execute workflow: {e.stderr}")
            return {"success": False, "error": e.stderr}

    def list_workflows(self) -> Dict[str, Any]:
        """List all workflows in the project"""
        try:
            result = subprocess.run(
                [
                    "gcloud",
                    "workflows",
                    "list",
                    "--location",
                    self.region,
                    "--project",
                    self.project_id,
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            print("📋 Available Workflows:")
            print(result.stdout)

            return {"success": True, "workflows": result.stdout}

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to list workflows: {e.stderr}")
            return {"success": False, "error": e.stderr}

    def get_workflow_info(self) -> Dict[str, Any]:
        """Get information about the deployed workflow"""
        try:
            result = subprocess.run(
                [
                    "gcloud",
                    "workflows",
                    "describe",
                    self.workflow_name,
                    "--location",
                    self.region,
                    "--project",
                    self.project_id,
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            print("📊 Workflow Information:")
            print(result.stdout)

            return {"success": True, "workflow_info": result.stdout}

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to get workflow info: {e.stderr}")
            return {"success": False, "error": e.stderr}


def main():
    """Main deployment function"""
    print("🚀 Cloud Workflows Deployment")
    print("=" * 40)

    # Get project information
    project_id = input("Enter GCP project ID: ").strip()
    if not project_id:
        print("❌ Project ID required")
        return

    region = input("Enter region (default: us-central1): ").strip() or "us-central1"

    # Create deployer
    deployer = CloudWorkflowDeployer(project_id, region)

    # Deploy workflow
    deploy_result = deployer.deploy_workflow()
    if not deploy_result["success"]:
        return

    # List workflows
    deployer.list_workflows()

    # Get workflow info
    deployer.get_workflow_info()

    print("\n🎉 Cloud Workflow Deployment Complete!")
    print("=" * 40)
    print("✅ Workflow deployed to Cloud Workflows")
    print("✅ Ready for GCP setup automation")
    print("✅ Serverless, scalable, and reliable")

    print("\n🎯 Next Steps:")
    print("1. Execute workflow with input data")
    print("2. Monitor workflow execution")
    print("3. Use for automated GCP setup")


if __name__ == "__main__":
    main()
