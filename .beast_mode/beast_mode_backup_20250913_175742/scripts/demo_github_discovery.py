#!/usr/bin/env python3
"""
Demo script for the Comprehensive GitHub Discovery Tool

This script demonstrates the capabilities of our discovery tool
by analyzing a sample repository.
"""

import asyncio
import sys
from pathlib import Path

from comprehensive_github_discovery import ComprehensiveGitHubDiscovery

# Add the scripts directory to the path
sys.path.append(str(Path(__file__).parent))


async def demo_discovery():
    """Demonstrate the comprehensive GitHub discovery tool"""

    print("🚀 Comprehensive GitHub Discovery Tool Demo")
    print("=" * 60)

    # Create discovery tool
    discovery = ComprehensiveGitHubDiscovery()

    # Demo with a well-known repository
    demo_repo = "https://github.com/astral-sh/uv"  # UV package manager

    print(f"📁 Analyzing repository: {demo_repo}")
    print("⏱️  This will take a few moments...")
    print()

    try:
        # Analyze repository
        analysis = await discovery.analyze_repository(demo_repo)

        # Generate different report formats
        print("📊 Generated Reports:")
        print("-" * 30)

        # Markdown report
        markdown_report = discovery.generate_report(analysis, "markdown")
        print("📝 Markdown Report (first 500 chars):")
        print(markdown_report[:500] + "..." if len(markdown_report) > 500 else markdown_report)
        print()

        # JSON report
        json_report = discovery.generate_report(analysis, "json")
        print("🔧 JSON Report (first 300 chars):")
        print(json_report[:300] + "..." if len(json_report) > 300 else json_report)
        print()

        # Summary
        print("📈 Analysis Summary:")
        print(f"   Repository: {analysis.repo_name}")
        print(f"   Owner: {analysis.owner}")
        print(f"   Language: {analysis.language}")
        print(f"   Total Files: {analysis.total_files:,}")
        print(f"   Quality Score: {analysis.quality_score:.1f}/100")
        print(f"   Analysis Duration: {analysis.analysis_duration:.2f}s")

        # File types
        print(f"\n📁 Top File Types:")
        for file_type, count in sorted(analysis.file_types.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {file_type}: {count:,} files")

        # Artifacts
        if analysis.artifact_summary:
            print(f"\n🔍 Artifact Discovery:")
            for artifact_type, info in analysis.artifact_summary.items():
                print(f"   {artifact_type}: {info['count']} files")

        # Schemas
        if analysis.detected_schemas:
            print(f"\n🧠 Detected Schemas:")
            for schema_name, schema_info in analysis.detected_schemas.items():
                if "count" in schema_info:
                    print(f"   {schema_name}: {schema_info['count']} files")

        # Quality
        print(f"\n⭐ Quality Analysis:")
        print(f"   Score: {analysis.quality_score:.1f}/100")
        if analysis.quality_issues:
            print(f"   Issues: {len(analysis.quality_issues)}")
        if analysis.recommendations:
            print(f"   Recommendations: {len(analysis.recommendations)}")

        print(f"\n✅ Demo completed successfully!")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(demo_discovery())
