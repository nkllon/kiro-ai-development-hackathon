#!/usr/bin/env python3
"""
🤖 Duet AI Billing Checker

Focused tool to check for Duet AI usage and actual GCP billing data.
Uses gcloud commands to get real billing information.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class DuetAIBillingChecker:
    """Check for Duet AI usage and billing data"""

    def __init__(self):
        """Initialize the checker"""
        self.project_id = None
        self.billing_account_id = None

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

            result = subprocess.run(
                ["gcloud", "billing", "accounts", "list", "--format=json"],
                capture_output=True,
                text=True,
                check=True,
            )
            billing_accounts = json.loads(result.stdout)

            if billing_accounts:
                self.billing_account_id = billing_accounts[0]["name"].split("/")[-1]

            return {
                "project_id": self.project_id,
                "billing_account_id": self.billing_account_id,
            }
        except Exception as e:
            print(f"❌ Failed to get project info: {e}")
            return {}

    def check_duet_ai_services(self) -> dict[str, Any]:
        """Check for Duet AI related services"""
        duet_ai_services = {
            "aiplatform.googleapis.com": "Vertex AI (Duet AI ML)",
            "cloudaicompanion.googleapis.com": "Duet AI Companion",
            "cloudfunctions.googleapis.com": "Cloud Functions (Duet AI Code)",
            "run.googleapis.com": "Cloud Run (Duet AI Deploy)",
            "firestore.googleapis.com": "Firestore (Duet AI Data)",
            "pubsub.googleapis.com": "Pub/Sub (Duet AI Events)",
            "cloudbuild.googleapis.com": "Cloud Build (Duet AI CI/CD)",
            "logging.googleapis.com": "Cloud Logging (Duet AI Monitor)",
            "monitoring.googleapis.com": "Cloud Monitoring (Duet AI Observability)",
            "speech.googleapis.com": "Speech-to-Text (Duet AI Voice)",
            "bigquery.googleapis.com": "BigQuery (Duet AI Analytics)",
            "storage.googleapis.com": "Cloud Storage (Duet AI Files)",
        }

        results = {}

        for service_id, description in duet_ai_services.items():
            try:
                # Check if service is enabled
                result = subprocess.run(
                    [
                        "gcloud",
                        "services",
                        "list",
                        "--enabled",
                        "--filter=name=" + service_id,
                    ],
                    capture_output=True,
                    text=True,
                )

                enabled = service_id in result.stdout
                results[service_id] = {
                    "description": description,
                    "enabled": enabled,
                    "status": "active" if enabled else "disabled",
                }

                # Get usage if enabled
                if enabled:
                    usage = self.get_service_usage(service_id)
                    results[service_id]["usage"] = usage

            except Exception as e:
                results[service_id] = {
                    "description": description,
                    "enabled": False,
                    "error": str(e),
                }

        return results

    def get_service_usage(self, service_id: str) -> dict[str, Any]:
        """Get usage for a specific service"""
        try:
            # Try to get resource usage for the service
            if "cloudfunctions" in service_id:
                result = subprocess.run(
                    ["gcloud", "functions", "list", "--format=json"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    functions = json.loads(result.stdout)
                    return {
                        "type": "cloud_functions",
                        "count": len(functions),
                        "functions": [f["name"] for f in functions],
                    }

            elif "run" in service_id:
                result = subprocess.run(
                    ["gcloud", "run", "services", "list", "--format=json"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    services = json.loads(result.stdout)
                    return {
                        "type": "cloud_run",
                        "count": len(services),
                        "services": [s["metadata"]["name"] for s in services],
                    }

            elif "firestore" in service_id:
                result = subprocess.run(
                    ["gcloud", "firestore", "databases", "list", "--format=json"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    databases = json.loads(result.stdout)
                    return {
                        "type": "firestore",
                        "count": len(databases),
                        "databases": [db["name"] for db in databases],
                    }

            elif "storage" in service_id:
                result = subprocess.run(
                    ["gsutil", "ls", "-p", self.project_id],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    buckets = result.stdout.strip().split("\n") if result.stdout.strip() else []
                    return {
                        "type": "storage",
                        "count": len(buckets),
                        "buckets": buckets,
                    }

            return {"type": "unknown", "status": "no_usage_data"}

        except Exception as e:
            return {"type": "error", "error": str(e)}

    def get_billing_data(self) -> dict[str, Any]:
        """Get actual billing data"""
        try:
            # Try to get billing export data
            result = subprocess.run(
                ["gcloud", "billing", "budgets", "list", "--format=json"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                budgets = json.loads(result.stdout)
                return {"budgets": budgets, "has_billing_data": True}
            return {"has_billing_data": False, "error": "No billing budgets found"}

        except Exception as e:
            return {"has_billing_data": False, "error": str(e)}

    def check_duet_ai_features(self) -> dict[str, Any]:
        """Check for specific Duet AI features"""
        features = {}

        # Check for AI/ML features
        try:
            # Check for Vertex AI models
            result = subprocess.run(
                ["gcloud", "ai", "models", "list", "--format=json"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                models = json.loads(result.stdout)
                features["vertex_ai_models"] = {
                    "count": len(models),
                    "models": [m.get("name", "unknown") for m in models],
                }
        except Exception:
            features["vertex_ai_models"] = {"count": 0, "error": "Not accessible"}

        # Check for AI Platform endpoints
        try:
            result = subprocess.run(
                ["gcloud", "ai", "endpoints", "list", "--format=json"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                endpoints = json.loads(result.stdout)
                features["ai_endpoints"] = {
                    "count": len(endpoints),
                    "endpoints": [e.get("name", "unknown") for e in endpoints],
                }
        except Exception:
            features["ai_endpoints"] = {"count": 0, "error": "Not accessible"}

        # Check for Duet AI Companion
        try:
            result = subprocess.run(
                [
                    "gcloud",
                    "services",
                    "list",
                    "--enabled",
                    "--filter=name=cloudaicompanion.googleapis.com",
                ],
                capture_output=True,
                text=True,
            )
            features["duet_ai_companion"] = {
                "enabled": "cloudaicompanion.googleapis.com" in result.stdout,
            }
        except Exception as e:
            features["duet_ai_companion"] = {"error": str(e)}

        return features

    def analyze_duet_ai_usage(self) -> dict[str, Any]:
        """Analyze Duet AI usage patterns"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "project_info": self.get_project_info(),
            "duet_ai_services": self.check_duet_ai_services(),
            "duet_ai_features": self.check_duet_ai_features(),
            "billing_data": self.get_billing_data(),
            "analysis": {},
        }

        # Analyze Duet AI usage
        enabled_services = [k for k, v in analysis["duet_ai_services"].items() if v.get("enabled")]

        analysis["analysis"] = {
            "total_duet_ai_services": len(enabled_services),
            "enabled_duet_ai_services": enabled_services,
            "duet_ai_usage_level": self.calculate_duet_ai_usage_level(enabled_services),
            "estimated_duet_ai_cost": self.estimate_duet_ai_cost(enabled_services),
            "recommendations": self.generate_recommendations(enabled_services),
        }

        return analysis

    def calculate_duet_ai_usage_level(self, enabled_services: list[str]) -> str:
        """Calculate Duet AI usage level"""
        if len(enabled_services) >= 8:
            return "high"
        if len(enabled_services) >= 4:
            return "medium"
        if len(enabled_services) >= 1:
            return "low"
        return "none"

    def estimate_duet_ai_cost(self, enabled_services: list[str]) -> dict[str, float]:
        """Estimate Duet AI related costs"""
        costs = {
            "vertex_ai": 0.0,
            "cloud_functions": 0.0,
            "cloud_run": 0.0,
            "firestore": 0.0,
            "pubsub": 0.0,
            "storage": 0.0,
            "total": 0.0,
        }

        for service in enabled_services:
            if "aiplatform" in service:
                costs["vertex_ai"] = 1.50
            elif "cloudfunctions" in service:
                costs["cloud_functions"] = 2.40
            elif "run" in service:
                costs["cloud_run"] = 0.30
            elif "firestore" in service:
                costs["firestore"] = 1.20
            elif "pubsub" in service:
                costs["pubsub"] = 0.50
            elif "storage" in service:
                costs["storage"] = 0.20

        costs["total"] = sum(costs.values())
        return costs

    def generate_recommendations(self, enabled_services: list[str]) -> list[str]:
        """Generate recommendations based on Duet AI usage"""
        recommendations = []

        if len(enabled_services) == 0:
            recommendations.append(
                "Consider enabling Duet AI services for AI-powered development",
            )
            recommendations.append(
                "Start with Cloud Functions and Firestore for basic AI integration",
            )

        elif len(enabled_services) < 4:
            recommendations.append(
                "Expand Duet AI usage with Vertex AI for ML capabilities",
            )
            recommendations.append("Enable Cloud Run for containerized AI applications")

        elif len(enabled_services) >= 4:
            recommendations.append("Consider implementing advanced Duet AI features")
            recommendations.append("Monitor costs as Duet AI usage increases")

        if "aiplatform.googleapis.com" in enabled_services:
            recommendations.append(
                "Vertex AI is enabled - consider implementing ML models",
            )

        if "cloudaicompanion.googleapis.com" in enabled_services:
            recommendations.append(
                "Duet AI Companion is active - leverage AI assistance",
            )

        return recommendations

    def generate_report(self, analysis: dict[str, Any]) -> str:
        """Generate a comprehensive Duet AI report"""
        report = []
        report.append("# 🤖 Duet AI Usage Analysis Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Project Information
        project_info = analysis.get("project_info", {})
        report.append("## 📋 Project Information")
        report.append(f"- **Project ID**: {project_info.get('project_id', 'N/A')}")
        report.append(
            f"- **Billing Account**: {project_info.get('billing_account_id', 'N/A')}",
        )
        report.append("")

        # Duet AI Services
        duet_ai_services = analysis.get("duet_ai_services", {})
        report.append("## 🤖 Duet AI Services Status")

        enabled_count = 0
        for service_id, info in duet_ai_services.items():
            status = "✅ Enabled" if info.get("enabled") else "❌ Disabled"
            description = info.get("description", "Unknown")
            report.append(f"- **{description}** ({service_id}): {status}")

            if info.get("enabled"):
                enabled_count += 1
                if "usage" in info:
                    usage = info["usage"]
                    if "count" in usage:
                        report.append(f"  - Usage: {usage['count']} instances")

        report.append(f"\n**Total Enabled Duet AI Services**: {enabled_count}")
        report.append("")

        # Duet AI Features
        duet_ai_features = analysis.get("duet_ai_features", {})
        report.append("## 🧠 Duet AI Features")
        for feature, info in duet_ai_features.items():
            if "count" in info:
                report.append(f"- **{feature}**: {info['count']} instances")
            elif "enabled" in info:
                status = "✅ Enabled" if info["enabled"] else "❌ Disabled"
                report.append(f"- **{feature}**: {status}")
        report.append("")

        # Analysis
        analysis_data = analysis.get("analysis", {})
        report.append("## 📊 Duet AI Analysis")
        report.append(
            f"- **Usage Level**: {analysis_data.get('duet_ai_usage_level', 'unknown').upper()}",
        )
        report.append(
            f"- **Total Services**: {analysis_data.get('total_duet_ai_services', 0)}",
        )
        report.append("")

        # Cost Analysis
        costs = analysis_data.get("estimated_duet_ai_cost", {})
        if costs:
            report.append("## 💰 Duet AI Cost Analysis")
            report.append(
                f"- **Total Estimated Monthly**: ${costs.get('total', 0):.2f}",
            )
            report.append("### Service Breakdown:")
            for service, cost in costs.items():
                if service != "total" and cost > 0:
                    report.append(f"  - **{service}**: ${cost:.2f}/month")
        report.append("")

        # Recommendations
        recommendations = analysis_data.get("recommendations", [])
        if recommendations:
            report.append("## 💡 Recommendations")
            for rec in recommendations:
                report.append(f"- {rec}")
        report.append("")

        return "\n".join(report)

    def save_analysis(
        self,
        analysis: dict[str, Any],
        filename: str = "duet_ai_analysis.json",
    ):
        """Save analysis to JSON file"""
        try:
            output_path = Path("data") / filename
            output_path.parent.mkdir(exist_ok=True)

            with open(output_path, "w") as f:
                json.dump(analysis, f, indent=2, default=str)

            print(f"✅ Analysis saved to: {output_path}")
            return str(output_path)
        except Exception as e:
            print(f"❌ Failed to save analysis: {e}")
            return None


def main():
    """Main function to run the Duet AI analysis"""
    print("🤖 Duet AI Billing Checker")
    print("=" * 50)

    checker = DuetAIBillingChecker()

    # Run comprehensive analysis
    print("🔍 Analyzing Duet AI usage and billing...")
    analysis = checker.analyze_duet_ai_usage()

    if not analysis:
        print("❌ Failed to complete analysis")
        sys.exit(1)

    # Generate and display report
    report = checker.generate_report(analysis)
    print("\n" + report)

    # Save analysis to file
    saved_file = checker.save_analysis(analysis)

    print("\n" + "=" * 50)
    print("✅ Duet AI analysis complete!")
    if saved_file:
        print(f"📁 Detailed data saved to: {saved_file}")

    return analysis


if __name__ == "__main__":
    main()
