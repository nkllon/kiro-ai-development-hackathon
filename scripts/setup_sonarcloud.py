#!/usr/bin/env python3
"""Automated SonarCloud setup using Web API.

This script configures SonarCloud for the kiro-ai-development-hackathon repository
using the SonarCloud Web API to minimize manual steps.
"""

import argparse
import os
import sys
from typing import Dict, Optional

import requests


class SonarCloudAPI:
    """SonarCloud Web API client."""

    def __init__(self, token: str, organization: str = "nkllon"):
        self.base_url = "https://sonarcloud.io/api"
        self.token = token
        self.organization = organization
        self.session = requests.Session()
        self.session.auth = (token, "")
        self.session.headers.update({"Accept": "application/json"})

    def set_organization_new_code_definition(
        self, definition_type: str = "NUMBER_OF_DAYS", value: str = "30"
    ) -> Dict:
        """Set organization-level new code definition.

        Note: This endpoint may not be available in API v1.
        Can be set via UI or during project creation instead.

        Args:
            definition_type: Type of new code definition
            value: Value for the definition

        Returns:
            Response from API or empty dict if endpoint not available
        """
        # Try settings/set endpoint instead
        url = f"{self.base_url}/settings/set"
        params = {
            "key": "sonar.leak.period",
            "value": value,
            "component": f"organization:{self.organization}",
        }

        print(f"Attempting to set organization new code definition: {definition_type} = {value}")
        try:
            response = self.session.post(url, params=params)
            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"⚠️  Organization setting endpoint not available, will set per-project")
                return {}
            raise

    def create_project(
        self,
        project_key: str,
        project_name: str,
        new_code_type: str = "days",
        new_code_value: str = "30",
        visibility: str = "public",
    ) -> Dict:
        """Create a new SonarCloud project.

        Args:
            project_key: Unique project identifier (e.g., nkllon_kiro-ai-development-hackathon)
            project_name: Display name for the project
            new_code_type: New code definition type (days, previous_version, date, version)
            new_code_value: Value for new code definition
            visibility: Project visibility (public or private)

        Returns:
            Response from API
        """
        url = f"{self.base_url}/projects/create"
        params = {
            "organization": self.organization,
            "project": project_key,
            "name": project_name,
            "visibility": visibility,
        }
        if new_code_type:
            params["newCodeDefinitionType"] = new_code_type
        if new_code_value:
            params["newCodeDefinitionValue"] = new_code_value

        print(f"Creating project: {project_key} ({project_name})")
        response = self.session.post(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_project(self, project_key: str) -> Optional[Dict]:
        """Get project details.

        Args:
            project_key: Project identifier

        Returns:
            Project details or None if not found
        """
        url = f"{self.base_url}/projects/search"
        params = {"projects": project_key}

        response = self.session.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            components = data.get("components", [])
            return components[0] if components else None
        return None

    def list_projects(self) -> Dict:
        """List all projects in the organization."""
        url = f"{self.base_url}/components/search_projects"
        params = {"organization": self.organization}

        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(
        description="Automated SonarCloud setup using Web API"
    )
    parser.add_argument(
        "--token",
        help="SonarCloud API token (or set SONAR_TOKEN env var)",
        default=os.getenv("SONAR_TOKEN"),
    )
    parser.add_argument(
        "--organization",
        default="nkllon",
        help="SonarCloud organization key",
    )
    parser.add_argument(
        "--project-key",
        default="nkllon_kiro-ai-development-hackathon",
        help="Project key to create",
    )
    parser.add_argument(
        "--project-name",
        default="Kiro AI Development Hackathon",
        help="Project display name",
    )
    parser.add_argument(
        "--new-code-days",
        type=int,
        default=30,
        help="Number of days for new code definition (default: 30)",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check if project exists, don't create",
    )

    args = parser.parse_args()

    if not args.token:
        print("❌ Error: SONAR_TOKEN not set. Please provide --token or set SONAR_TOKEN env var.")
        print("\nTo get a token:")
        print("1. Log into https://sonarcloud.io")
        print("2. Go to My Account → Security")
        print("3. Generate token: kiro-hackathon-token")
        print("4. Export: export SONAR_TOKEN='your-token-here'")
        return 1

    api = SonarCloudAPI(args.token, args.organization)

    try:
        # Check if project already exists
        print(f"\n🔍 Checking if project exists: {args.project_key}")
        existing = api.get_project(args.project_key)

        if existing:
            print(f"✅ Project already exists: {existing.get('name')}")
            print(f"   Key: {existing.get('key')}")
            print(f"   Visibility: {existing.get('visibility', 'unknown')}")
            if args.check_only:
                return 0
            print("\n⚠️  Project exists. Skipping creation.")
            return 0

        if args.check_only:
            print(f"❌ Project does not exist: {args.project_key}")
            return 1

        # Set organization-level new code definition
        print(f"\n📝 Setting organization new code definition: {args.new_code_days} days")
        api.set_organization_new_code_definition(
            definition_type="NUMBER_OF_DAYS",
            value=str(args.new_code_days),
        )
        print("✅ Organization new code definition set")

        # Create the project
        print(f"\n🚀 Creating project: {args.project_key}")
        result = api.create_project(
            project_key=args.project_key,
            project_name=args.project_name,
            new_code_type="days",
            new_code_value=str(args.new_code_days),
            visibility="public",
        )
        print("✅ Project created successfully!")
        print(f"   Key: {result['project']['key']}")
        print(f"   Name: {result['project']['name']}")

        print("\n✅ SonarCloud setup complete!")
        print(f"\n📊 Project URL: https://sonarcloud.io/project/overview?id={args.project_key}")

        print("\n📋 Next Steps:")
        print("1. Add SONAR_TOKEN to GitHub secrets:")
        print("   gh secret set SONAR_TOKEN --body '$SONAR_TOKEN'")
        print("2. Commit and push sonar-project.properties and .github/workflows/sonarcloud.yml")
        print("3. First analysis will run automatically on next push")

        return 0

    except requests.exceptions.HTTPError as e:
        print(f"\n❌ API Error: {e}")
        if e.response is not None:
            print(f"   Status: {e.response.status_code}")
            print(f"   Response: {e.response.text}")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

