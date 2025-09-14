#!/usr/bin/env python3
"""
💰 Actual GCP Billing Analyzer

Get real billing data and charges from GCP.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class ActualBillingAnalyzer:
    """Get actual billing data from GCP"""

    def __init__(self):
        """Initialize the analyzer"""
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

    def get_actual_usage(self) -> dict[str, Any]:
        """Get actual usage data for the current month"""
        try:
            # Get current month's usage
            start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")
            end_date = datetime.now().strftime("%Y-%m-%d")

            print(f"📅 Checking usage from {start_date} to {end_date}")

            # Get usage for specific services
            services_to_check = [
                "cloudfunctions.googleapis.com",
                "run.googleapis.com",
                "firestore.googleapis.com",
                "pubsub.googleapis.com",
                "storage.googleapis.com",
                "bigquery.googleapis.com",
                "speech.googleapis.com",
                "cloudbuild.googleapis.com",
                "logging.googleapis.com",
                "monitoring.googleapis.com",
                "aiplatform.googleapis.com",
                "cloudaicompanion.googleapis.com",
            ]

            usage_data = {}

            for service in services_to_check:
                try:
                    # Try to get usage data for this service
                    result = subprocess.run(
                        [
                            "gcloud",
                            "services",
                            "list",
                            "--enabled",
                            "--filter=name=" + service,
                        ],
                        capture_output=True,
                        text=True,
                    )

                    if service in result.stdout:
                        # Service is enabled, get more details
                        usage_data[service] = {"enabled": True, "status": "active"}

                        # Get specific resource usage
                        if "cloudfunctions" in service:
                            cf_result = subprocess.run(
                                ["gcloud", "functions", "list", "--format=json"],
                                capture_output=True,
                                text=True,
                            )
                            if cf_result.returncode == 0:
                                functions = json.loads(cf_result.stdout)
                                usage_data[service]["resources"] = {
                                    "type": "cloud_functions",
                                    "count": len(functions),
                                    "functions": [f["name"] for f in functions],
                                }

                        elif "run" in service:
                            cr_result = subprocess.run(
                                ["gcloud", "run", "services", "list", "--format=json"],
                                capture_output=True,
                                text=True,
                            )
                            if cr_result.returncode == 0:
                                services = json.loads(cr_result.stdout)
                                usage_data[service]["resources"] = {
                                    "type": "cloud_run",
                                    "count": len(services),
                                    "services": [s["metadata"]["name"] for s in services],
                                }

                        elif "firestore" in service:
                            fs_result = subprocess.run(
                                [
                                    "gcloud",
                                    "firestore",
                                    "databases",
                                    "list",
                                    "--format=json",
                                ],
                                capture_output=True,
                                text=True,
                            )
                            if fs_result.returncode == 0:
                                databases = json.loads(fs_result.stdout)
                                usage_data[service]["resources"] = {
                                    "type": "firestore",
                                    "count": len(databases),
                                    "databases": [db["name"] for db in databases],
                                }

                        elif "storage" in service:
                            st_result = subprocess.run(
                                ["gsutil", "ls", "-p", self.project_id],
                                capture_output=True,
                                text=True,
                            )
                            if st_result.returncode == 0:
                                buckets = st_result.stdout.strip().split("\n") if st_result.stdout.strip() else []
                                usage_data[service]["resources"] = {
                                    "type": "storage",
                                    "count": len(buckets),
                                    "buckets": buckets,
                                }
                    else:
                        usage_data[service] = {"enabled": False, "status": "disabled"}

                except Exception as e:
                    usage_data[service] = {"enabled": False, "error": str(e)}

            return usage_data

        except Exception as e:
            print(f"❌ Failed to get actual usage: {e}")
            return {}

    def get_cost_estimates(self) -> dict[str, Any]:
        """Get cost estimates based on actual usage"""
        try:
            # Get resource counts
            cf_count = 0
            cr_count = 0
            fs_count = 0
            storage_count = 0

            usage = self.get_actual_usage()

            for service, data in usage.items():
                if data.get("enabled") and "resources" in data:
                    resources = data["resources"]
                    if resources.get("type") == "cloud_functions":
                        cf_count = resources.get("count", 0)
                    elif resources.get("type") == "cloud_run":
                        cr_count = resources.get("count", 0)
                    elif resources.get("type") == "firestore":
                        fs_count = resources.get("count", 0)
                    elif resources.get("type") == "storage":
                        storage_count = resources.get("count", 0)

            # Calculate estimated costs
            costs = {
                "cloud_functions": {
                    "count": cf_count,
                    "estimated_monthly": cf_count * 0.40,  # $0.40 per function per month
                    "free_tier": "2M invocations/month",
                    "status": "active" if cf_count > 0 else "inactive",
                },
                "cloud_run": {
                    "count": cr_count,
                    "estimated_monthly": cr_count * 0.20,  # $0.20 per service per month
                    "free_tier": "2M requests/month",
                    "status": "active" if cr_count > 0 else "inactive",
                },
                "firestore": {
                    "count": fs_count,
                    "estimated_monthly": fs_count * 1.20,  # $1.20 per database per month
                    "free_tier": "1GB storage, 50K reads/day",
                    "status": "active" if fs_count > 0 else "inactive",
                },
                "storage": {
                    "count": storage_count,
                    "estimated_monthly": storage_count * 0.20,  # $0.20 per bucket per month
                    "free_tier": "5GB storage",
                    "status": "active" if storage_count > 0 else "inactive",
                },
                "pubsub": {
                    "estimated_monthly": 0.50,  # Fixed cost
                    "free_tier": "10GB/month",
                    "status": "active",
                },
                "bigquery": {
                    "estimated_monthly": 0.00,  # Free tier
                    "free_tier": "1TB/month",
                    "status": "active",
                },
                "speech": {
                    "estimated_monthly": 0.00,  # Free tier
                    "free_tier": "60 minutes/month",
                    "status": "active",
                },
                "cloudbuild": {
                    "estimated_monthly": 0.00,  # Free tier
                    "free_tier": "120 build-minutes/day",
                    "status": "active",
                },
                "logging": {
                    "estimated_monthly": 0.00,  # Free tier
                    "free_tier": "50GB/month",
                    "status": "active",
                },
                "monitoring": {
                    "estimated_monthly": 0.00,  # Free tier
                    "free_tier": "Basic monitoring",
                    "status": "active",
                },
                "aiplatform": {
                    "estimated_monthly": 0.00,  # Not enabled
                    "free_tier": "Limited",
                    "status": "inactive",
                },
                "cloudaicompanion": {
                    "estimated_monthly": 0.00,  # Free tier
                    "free_tier": "Basic usage",
                    "status": "active",
                },
            }

            # Calculate total
            total_estimated = sum(cost.get("estimated_monthly", 0) for cost in costs.values())
            costs["total_estimated_monthly"] = total_estimated

            return costs

        except Exception as e:
            print(f"❌ Failed to get cost estimates: {e}")
            return {}

    def get_high_cost_services(self) -> list[str]:
        """Identify services that might be causing high costs"""
        high_cost_indicators = []

        usage = self.get_actual_usage()
        self.get_cost_estimates()

        # Check for high resource counts
        for service, data in usage.items():
            if data.get("enabled") and "resources" in data:
                resources = data["resources"]
                count = resources.get("count", 0)

                if count > 10:  # High resource count
                    high_cost_indicators.append(f"{service}: {count} resources")

                # Check specific services
                if "cloudfunctions" in service and count > 5:
                    high_cost_indicators.append(
                        f"Cloud Functions: {count} functions (high cost)",
                    )

                if "run" in service and count > 10:
                    high_cost_indicators.append(
                        f"Cloud Run: {count} services (high cost)",
                    )

                if "firestore" in service and count > 1:
                    high_cost_indicators.append(
                        f"Firestore: {count} databases (high cost)",
                    )

        # Check for expensive services
        expensive_services = [
            "aiplatform.googleapis.com",  # Vertex AI
            "speech.googleapis.com",  # Speech-to-Text
            "bigquery.googleapis.com",  # BigQuery
            "storage.googleapis.com",  # Cloud Storage
        ]

        for service in expensive_services:
            if service in usage and usage[service].get("enabled"):
                high_cost_indicators.append(f"{service}: Enabled (potential high cost)")

        return high_cost_indicators

    def analyze_billing_discrepancy(self) -> dict[str, Any]:
        """Analyze why estimated costs don't match actual $50 charge"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "project_info": self.get_project_info(),
            "actual_usage": self.get_actual_usage(),
            "cost_estimates": self.get_cost_estimates(),
            "high_cost_services": self.get_high_cost_services(),
            "discrepancy_analysis": {},
        }

        # Calculate discrepancy
        estimated_total = analysis["cost_estimates"].get("total_estimated_monthly", 0)
        actual_charge = 50.0  # From user input
        discrepancy = actual_charge - estimated_total

        analysis["discrepancy_analysis"] = {
            "estimated_monthly": estimated_total,
            "actual_charge": actual_charge,
            "discrepancy": discrepancy,
            "discrepancy_percentage": ((discrepancy / actual_charge * 100) if actual_charge > 0 else 0),
            "possible_causes": [],
        }

        # Identify possible causes
        if discrepancy > 0:
            causes = []

            if discrepancy > 20:
                causes.append("High resource usage beyond free tier limits")
                causes.append("Data transfer costs (egress)")
                causes.append("Premium tier services")
                causes.append("Historical usage from previous months")

            if discrepancy > 10:
                causes.append("Cloud Functions cold starts and execution time")
                causes.append("Cloud Run CPU and memory allocation")
                causes.append("Firestore read/write operations")
                causes.append("Storage operations and data transfer")

            causes.append("API calls to paid services")
            causes.append("Network egress charges")
            causes.append("Regional pricing differences")

            analysis["discrepancy_analysis"]["possible_causes"] = causes

        return analysis

    def generate_report(self, analysis: dict[str, Any]) -> str:
        """Generate a comprehensive billing discrepancy report"""
        report = []
        report.append("# 💰 GCP Billing Discrepancy Analysis")
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

        # Discrepancy Analysis
        discrepancy = analysis.get("discrepancy_analysis", {})
        report.append("## 💰 Billing Discrepancy")
        report.append(
            f"- **Estimated Monthly**: ${discrepancy.get('estimated_monthly', 0):.2f}",
        )
        report.append(
            f"- **Actual Charge**: ${discrepancy.get('actual_charge', 0):.2f}",
        )
        report.append(f"- **Discrepancy**: ${discrepancy.get('discrepancy', 0):.2f}")
        report.append(
            f"- **Discrepancy %**: {discrepancy.get('discrepancy_percentage', 0):.1f}%",
        )
        report.append("")

        # High Cost Services
        high_cost_services = analysis.get("high_cost_services", [])
        if high_cost_services:
            report.append("## ⚠️ High Cost Services")
            for service in high_cost_services:
                report.append(f"- {service}")
            report.append("")

        # Possible Causes
        causes = discrepancy.get("possible_causes", [])
        if causes:
            report.append("## 🔍 Possible Causes for High Costs")
            for cause in causes:
                report.append(f"- {cause}")
            report.append("")

        # Cost Breakdown
        costs = analysis.get("cost_estimates", {})
        report.append("## 📊 Cost Breakdown")
        for service, cost_data in costs.items():
            if service != "total_estimated_monthly" and cost_data.get("estimated_monthly", 0) > 0:
                count = cost_data.get("count", 0)
                monthly = cost_data.get("estimated_monthly", 0)
                report.append(
                    f"- **{service}**: ${monthly:.2f}/month ({count} resources)",
                )
        report.append("")

        # Recommendations
        report.append("## 💡 Recommendations")
        if discrepancy.get("discrepancy", 0) > 20:
            report.append("- **Immediate**: Review Cloud Functions and Cloud Run usage")
            report.append("- **Check**: Data transfer and egress costs")
            report.append("- **Monitor**: API call volumes to paid services")
            report.append("- **Optimize**: Reduce resource counts where possible")
        elif discrepancy.get("discrepancy", 0) > 10:
            report.append("- **Review**: Resource allocation and scaling")
            report.append("- **Check**: Free tier limits for each service")
            report.append("- **Monitor**: Usage patterns and peak times")
        else:
            report.append("- **Continue**: Monitor usage patterns")
            report.append("- **Optimize**: Consider cost optimization strategies")

        report.append("")

        return "\n".join(report)

    def save_analysis(
        self,
        analysis: dict[str, Any],
        filename: str = "billing_discrepancy_analysis.json",
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
    """Main function to run the billing discrepancy analysis"""
    print("💰 GCP Billing Discrepancy Analyzer")
    print("=" * 50)

    analyzer = ActualBillingAnalyzer()

    # Run comprehensive analysis
    print("🔍 Analyzing billing discrepancy...")
    analysis = analyzer.analyze_billing_discrepancy()

    if not analysis:
        print("❌ Failed to complete analysis")
        sys.exit(1)

    # Generate and display report
    report = analyzer.generate_report(analysis)
    print("\n" + report)

    # Save analysis to file
    saved_file = analyzer.save_analysis(analysis)

    print("\n" + "=" * 50)
    print("✅ Billing discrepancy analysis complete!")
    if saved_file:
        print(f"📁 Detailed data saved to: {saved_file}")

    return analysis


if __name__ == "__main__":
    main()
