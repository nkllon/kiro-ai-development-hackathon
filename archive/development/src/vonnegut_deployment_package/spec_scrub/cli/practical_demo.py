#!/usr/bin/env python3
"""
Practical Spec Scrub Demo

Let's see what actually works when we hit real specifications with perverse cases.
This will expose the gaps between theory and reality.
"""

import click
from pathlib import Path

from src.spec_scrub.core.spec_scrub_engine import SpecScrubEngine


@click.group()
def cli():
    """Practical Spec Scrub Demo - Learning from Real-World Perverse Cases."""
    pass


@cli.command()
def reality_check():
    """Run spec scrub on actual repository specs to see what breaks."""
    click.echo("🔍 Reality Check: Testing Spec Scrub on Actual Repository")
    click.echo("=" * 60)
    
    engine = SpecScrubEngine()
    
    # Test on the actual repository specs
    repo_path = Path(".")
    click.echo(f"📁 Scanning repository: {repo_path.absolute()}")
    
    try:
        reports = engine.scrub_repository(repo_path)
        
        click.echo(f"✅ Successfully analyzed {len(reports)} specifications")
        
        # Show the perverse cases - specs with problems
        problem_specs = [r for r in reports if len(r.gaps) > 5]
        good_specs = [r for r in reports if len(r.gaps) <= 2]
        
        click.echo(f"\n📊 Reality Check Results:")
        click.echo(f"   Total specs: {len(reports)}")
        click.echo(f"   Problem specs (>5 gaps): {len(problem_specs)}")
        click.echo(f"   Good specs (≤2 gaps): {len(good_specs)}")
        click.echo(f"   Average gaps per spec: {sum(len(r.gaps) for r in reports) / len(reports):.1f}")
        
        # Show the worst offenders (perverse cases)
        click.echo(f"\n🚨 Worst Offenders (Perverse Cases):")
        worst_specs = sorted(reports, key=lambda r: len(r.gaps), reverse=True)[:5]
        
        for i, spec in enumerate(worst_specs, 1):
            click.echo(f"   {i}. {spec.spec_name}: {len(spec.gaps)} gaps, {spec.coverage_score:.2f} coverage")
            
        # Show what we learned
        click.echo(f"\n💡 What We Learned:")
        
        # Common gap types
        all_gaps = []
        for report in reports:
            all_gaps.extend(report.gaps)
            
        gap_types = {}
        for gap in all_gaps:
            gap_types[gap.gap_type] = gap_types.get(gap.gap_type, 0) + 1
            
        click.echo(f"   Most common gap types:")
        for gap_type, count in sorted(gap_types.items(), key=lambda x: x[1], reverse=True)[:3]:
            click.echo(f"     - {gap_type}: {count} occurrences")
            
        # Recommendations based on reality
        click.echo(f"\n🎯 Reality-Based Recommendations:")
        if len(problem_specs) > len(good_specs):
            click.echo(f"   - Most specs have problems - this is normal brownfield reality")
            click.echo(f"   - Focus on systematic improvement, not perfection")
        
        if gap_types.get("missing_implementation", 0) > gap_types.get("orphaned_task", 0):
            click.echo(f"   - More missing implementations than orphaned tasks")
            click.echo(f"   - Design elements aren't being implemented systematically")
        
        click.echo(f"   - The perverse cases teach us more than the perfect ones")
        
    except Exception as e:
        click.echo(f"❌ Reality check failed: {e}")
        click.echo("This is exactly the kind of perverse case we need to handle!")


@cli.command()
@click.argument('spec_name')
def deep_dive(spec_name):
    """Deep dive into a specific spec to understand its perverse cases."""
    click.echo(f"🔬 Deep Dive: {spec_name}")
    click.echo("=" * 50)
    
    engine = SpecScrubEngine()
    spec_path = Path(f".kiro/specs/{spec_name}")
    
    if not spec_path.exists():
        click.echo(f"❌ Spec not found: {spec_path}")
        return
    
    try:
        report = engine.scrub_specification(spec_path)
        
        click.echo(f"📋 Spec Analysis:")
        click.echo(f"   Requirements: {report.requirements_count}")
        click.echo(f"   Design Elements: {report.design_elements_count}")
        click.echo(f"   Tasks: {report.tasks_count}")
        click.echo(f"   Coverage Score: {report.coverage_score:.2f}")
        
        if report.gaps:
            click.echo(f"\n🚨 Gaps Found ({len(report.gaps)}):")
            for gap in report.gaps[:10]:  # Show first 10
                click.echo(f"   - {gap.gap_type}: {gap.description}")
                
        if report.recommendations:
            click.echo(f"\n💡 Recommendations:")
            for rec in report.recommendations:
                click.echo(f"   - {rec}")
                
        # The perverse case analysis
        click.echo(f"\n🎯 Perverse Case Analysis:")
        
        if report.requirements_count == 0:
            click.echo("   - No requirements found - Beast Mode parser couldn't handle the format")
            click.echo("   - This is a common perverse case with non-standard requirement formats")
            
        if report.design_elements_count > report.tasks_count * 2:
            click.echo("   - Way more design elements than tasks - over-designed or under-implemented")
            
        if len(report.gaps) > (report.requirements_count + report.design_elements_count + report.tasks_count) / 2:
            click.echo("   - More gaps than elements - this spec is in rough shape")
            click.echo("   - Classic brownfield perverse case")
            
        click.echo(f"\n🧠 Learning Opportunity:")
        click.echo(f"   This spec teaches us about real-world messiness")
        click.echo(f"   Perfect theory meets imperfect reality here")
        
    except Exception as e:
        click.echo(f"❌ Deep dive failed: {e}")
        click.echo("Another perverse case to learn from!")


@cli.command()
def find_perverse_cases():
    """Find the most perverse cases in the repository for learning."""
    click.echo("🎯 Hunting for Perverse Cases")
    click.echo("=" * 40)
    
    engine = SpecScrubEngine()
    
    try:
        reports = engine.scrub_repository(Path("."))
        
        # Define perverse case criteria
        perverse_cases = []
        
        for report in reports:
            perversity_score = 0
            reasons = []
            
            # No requirements found
            if report.requirements_count == 0:
                perversity_score += 3
                reasons.append("No requirements detected")
                
            # Massive gap count
            if len(report.gaps) > 10:
                perversity_score += 2
                reasons.append(f"{len(report.gaps)} gaps found")
                
            # Very low coverage
            if report.coverage_score < 0.3:
                perversity_score += 2
                reasons.append(f"Low coverage: {report.coverage_score:.2f}")
                
            # Imbalanced elements
            total_elements = report.requirements_count + report.design_elements_count + report.tasks_count
            if total_elements > 0 and len(report.gaps) > total_elements:
                perversity_score += 1
                reasons.append("More gaps than elements")
                
            if perversity_score > 0:
                perverse_cases.append({
                    'spec': report.spec_name,
                    'score': perversity_score,
                    'reasons': reasons,
                    'report': report
                })
        
        # Sort by perversity score
        perverse_cases.sort(key=lambda x: x['score'], reverse=True)
        
        click.echo(f"🔍 Found {len(perverse_cases)} perverse cases:")
        
        for i, case in enumerate(perverse_cases[:10], 1):
            click.echo(f"\n{i}. {case['spec']} (Perversity Score: {case['score']})")
            for reason in case['reasons']:
                click.echo(f"     - {reason}")
                
        if perverse_cases:
            click.echo(f"\n🎓 Learning Opportunities:")
            click.echo(f"   These perverse cases will teach us:")
            click.echo(f"   - How real specs differ from theoretical models")
            click.echo(f"   - Where our parsing assumptions break down")
            click.echo(f"   - What brownfield reality actually looks like")
            click.echo(f"   - How to make our system more robust")
            
            worst_case = perverse_cases[0]
            click.echo(f"\n🎯 Suggested Next Step:")
            click.echo(f"   Run: python -m src.spec_scrub.cli.practical_demo deep-dive {worst_case['spec']}")
            click.echo(f"   This will show you the messiest case for maximum learning")
        
    except Exception as e:
        click.echo(f"❌ Perverse case hunting failed: {e}")
        click.echo("Even our perverse case finder hit a perverse case!")


@cli.command()
def learning_summary():
    """Summarize what we've learned from perverse cases."""
    click.echo("🧠 Learning Summary: What Perverse Cases Taught Us")
    click.echo("=" * 55)
    
    click.echo("📚 Key Learnings:")
    click.echo("   1. Beast Mode parsers expect different formats than our specs use")
    click.echo("   2. Most real specs are messy - this is normal brownfield reality")
    click.echo("   3. Perfect theory meets imperfect practice in every real system")
    click.echo("   4. Gap detection works, but gap types reveal systematic issues")
    click.echo("   5. Coverage scores show the health of spec-to-implementation alignment")
    
    click.echo(f"\n🎯 What Actually Works:")
    click.echo("   ✅ Design element extraction from markdown")
    click.echo("   ✅ Task parsing using Beast Mode infrastructure")
    click.echo("   ✅ Gap identification and categorization")
    click.echo("   ✅ Coverage scoring for spec health assessment")
    
    click.echo(f"\n🚨 What Needs Work:")
    click.echo("   ❌ Requirements parsing (format mismatch with Beast Mode)")
    click.echo("   ❌ Cross-spec dependency analysis")
    click.echo("   ❌ Handling specs with non-standard formats")
    click.echo("   ❌ Dealing with incomplete or evolving specifications")
    
    click.echo(f"\n💡 Next Steps Based on Reality:")
    click.echo("   1. Adapt requirements parsing to handle our actual spec formats")
    click.echo("   2. Build tolerance for incomplete and messy specifications")
    click.echo("   3. Focus on practical gap remediation over theoretical perfection")
    click.echo("   4. Use perverse cases as test cases for system robustness")
    
    click.echo(f"\n🎉 The Real Victory:")
    click.echo("   We built a system that exposes real problems in real specs")
    click.echo("   The perverse cases are features, not bugs - they teach us!")
    click.echo("   Reality-based learning beats theoretical perfection")


if __name__ == '__main__':
    cli()