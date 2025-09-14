#!/usr/bin/env python3
"""
RM Compliance CLI Tool

Command-line interface for the RM Compliance Checker.
Provides easy access to RM compliance assessment and reporting.
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from project_management.rm_compliance_checker import create_rm_compliance_checker


async def assess_domain(domain_name: str, project_root: str = ".") -> None:
    """Assess RM compliance for a specific domain."""
    print(f"🔍 Assessing RM compliance for domain: {domain_name}")

    checker = await create_rm_compliance_checker(project_root)
    compliance = await checker.assess_domain_rm_compliance(domain_name)

    print(f"\n📊 Domain: {compliance.domain_name}")
    print(f"   Compliance Level: {compliance.compliance_level.value}")
    print(f"   Implementation Count: {compliance.implementation_count}")
    print(f"   Requirements Count: {compliance.requirements_count}")
    print(f"   RM Requirements Count: {compliance.rm_requirements_count}")
    print(f"   Compliance Score: {compliance.compliance_score:.2f}")

    if compliance.implementations:
        print(f"\n🔧 RM Implementations:")
        for impl in compliance.implementations:
            print(f"   - {impl.class_name} in {impl.file_path}")
            print(f"     Interface: {impl.interface_type}")
            if impl.methods_implemented:
                print(f"     Methods: {', '.join(impl.methods_implemented)}")


async def assess_all_domains(project_root: str = ".") -> None:
    """Assess RM compliance for all domains."""
    print("🔍 Assessing RM compliance for all domains...")

    checker = await create_rm_compliance_checker(project_root)
    results = await checker.assess_all_domains()

    print(f"\n📊 Assessment Complete: {len(results)} domains analyzed")

    # Group by compliance level
    full_compliant = []
    partial_compliant = []
    non_compliant = []

    for domain_name, compliance in results.items():
        if compliance.compliance_level.value == "full":
            full_compliant.append(domain_name)
        elif compliance.compliance_level.value == "partial":
            partial_compliant.append(domain_name)
        else:
            non_compliant.append(domain_name)

    print(f"\n✅ Fully RM Compliant ({len(full_compliant)}):")
    for domain in full_compliant:
        print(f"   - {domain}")

    print(f"\n⚠️  Partially RM Compliant ({len(partial_compliant)}):")
    for domain in partial_compliant:
        print(f"   - {domain}")

    print(f"\n❌ Non-RM Compliant ({len(non_compliant)}):")
    for domain in non_compliant:
        print(f"   - {domain}")


async def generate_report(output_file: Optional[str], project_root: str = ".") -> None:
    """Generate comprehensive RM compliance report."""
    print("📋 Generating RM compliance report...")

    checker = await create_rm_compliance_checker(project_root)
    report = await checker.generate_compliance_report()

    if output_file:
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)
        print(f"✅ Report saved to: {output_file}")
    else:
        print(json.dumps(report, indent=2))


async def show_status(project_root: str = ".") -> None:
    """Show RM Compliance Checker status."""
    print("📊 RM Compliance Checker Status")

    checker = await create_rm_compliance_checker(project_root)
    status = await checker.get_module_status()

    print(f"\n🏥 Module Status: {status.status.value}")
    print(f"📈 Health Indicators:")
    for key, value in status.health_indicators.items():
        print(f"   {key}: {value}")

    print(f"\n🔧 Capabilities:")
    for capability in status.capabilities:
        print(f"   - {capability.name}: {capability.description}")


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="RM Compliance Checker CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Assess all domains
  python scripts/rm_compliance_cli.py assess-all
  
  # Assess specific domain
  python scripts/rm_compliance_cli.py assess-domain reflective_modules
  
  # Generate report
  python scripts/rm_compliance_cli.py report --output rm_compliance_report.json
  
  # Show status
  python scripts/rm_compliance_cli.py status
        """,
    )

    parser.add_argument("--project-root", default=".", help="Project root directory (default: current directory)")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Assess domain command
    assess_domain_parser = subparsers.add_parser("assess-domain", help="Assess RM compliance for a specific domain")
    assess_domain_parser.add_argument("domain", help="Domain name to assess")

    # Assess all domains command
    subparsers.add_parser("assess-all", help="Assess RM compliance for all domains")

    # Generate report command
    report_parser = subparsers.add_parser("report", help="Generate RM compliance report")
    report_parser.add_argument("--output", "-o", help="Output file for report (default: stdout)")

    # Show status command
    subparsers.add_parser("status", help="Show RM Compliance Checker status")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "assess-domain":
            await assess_domain(args.domain, args.project_root)
        elif args.command == "assess-all":
            await assess_all_domains(args.project_root)
        elif args.command == "report":
            await generate_report(args.output, args.project_root)
        elif args.command == "status":
            await show_status(args.project_root)
        else:
            print(f"❌ Unknown command: {args.command}")
            parser.print_help()

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
