#!/usr/bin/env python3
"""
VARB + VTI Demonstration CLI

Demonstrates the revolutionary combination of:
- VARB (Validation through Authentic Requirements Behavior) 
- VTI (Validation-through-Implementation) Feedback Loop

Shows how to validate requirements transformation by preserving authentic
stakeholder behavior and comparing parallel implementations.
"""

import click
from pathlib import Path

from src.spec_scrub.validation.varb_validator import VARBValidator
from src.spec_scrub.validation.vti_feedback_loop import VTIFeedbackLoop


@click.group()
def cli():
    """VARB + VTI Demo - Revolutionary Requirements Validation."""
    pass


@cli.command()
def demo():
    """Run comprehensive VARB + VTI demonstration."""
    click.echo("🚀 VARB + VTI Revolutionary Requirements Validation Demo")
    click.echo("=" * 60)
    
    # Initialize validators
    varb = VARBValidator()
    vti = VTIFeedbackLoop()
    
    # Sample stakeholder interview transcript
    stakeholder_transcript = """
    Interviewer: What's your biggest pain point with the current system?
    
    Stakeholder: Honestly, our users are really struggling. Like, they spend 
    way too much time just trying to complete basic tasks. It's really 
    frustrating for everyone.
    
    What we desperately need is something that just works intuitively. Users 
    shouldn't have to think about it, you know? They definitely need to get 
    their work done quickly - that's absolutely critical for our business.
    
    The current interface is frankly a mess. Users are constantly calling 
    support because they can't figure out simple things. We really need to 
    fix this user experience problem.
    
    Performance is super important too. If it takes more than 2 seconds to 
    load, users just give up. That's definitely not acceptable.
    """
    
    stakeholder_context = "Operations Manager - User Experience Focused"
    
    click.echo(f"📋 Stakeholder Context: {stakeholder_context}")
    click.echo(f"🎤 Processing audio transcript ({len(stakeholder_transcript)} chars)")
    
    # Step 1: VARB Coding - Preserve Authentic Stakeholder Behavior
    click.echo("\n🎯 Step 1: VARB Coding - Preserving Authentic Stakeholder Behavior")
    click.echo("-" * 50)
    
    varb_impl = varb.varb_code_from_transcript(stakeholder_transcript, stakeholder_context)
    
    click.echo(f"✅ VARB Implementation Generated:")
    click.echo(f"   Authentic Intent: {varb_impl.authentic_intent}")
    click.echo(f"   Behavioral Assumptions: {len(varb_impl.behavioral_assumptions)}")
    click.echo(f"   Authenticity Confidence: {varb_impl.confidence_in_authenticity:.2f}")
    
    # Step 2: VTI Validation - Compare Parallel Implementations
    click.echo("\n🔄 Step 2: VTI Validation - Parallel Implementation Comparison")
    click.echo("-" * 50)
    
    # Extract conversational requirements for VTI
    conversational_requirements = """
    Users are struggling with basic tasks and spending too much time.
    System needs to work intuitively without user thinking.
    Quick task completion is critical for business.
    Current interface causes support calls for simple operations.
    Performance must be under 2 seconds or users abandon tasks.
    """
    
    vti_results = vti.run_vti_validation(conversational_requirements, stakeholder_context)
    
    click.echo(f"✅ VTI Validation Results:")
    click.echo(f"   EARS Requirements: {len(vti_results['ears_requirements'])}")
    click.echo(f"   Implementation Gaps: {len(vti_results['gaps_identified'])}")
    click.echo(f"   Validation Score: {vti_results['validation_score']:.2f}")
    
    # Step 3: Combined VARB + VTI Analysis
    click.echo("\n🧠 Step 3: Combined VARB + VTI Analysis")
    click.echo("-" * 50)
    
    # Simulate structured implementation (from EARS)
    structured_implementation = """
    class TaskManagementSystem:
        def process_user_request(self, request):
            # Process request with standard validation
            return self.execute_task(request)
            
        def execute_task(self, task):
            # Execute task with logging
            self.log_task_execution(task)
            return "Task completed"
    """
    
    # VARB validation against structured implementation
    varb_validation = varb.validate_against_structured(structured_implementation, varb_impl)
    
    click.echo(f"🎯 VARB Authenticity Analysis:")
    click.echo(f"   Authenticity Gaps: {len(varb_validation.authenticity_gaps)}")
    for gap in varb_validation.authenticity_gaps:
        click.echo(f"     - {gap}")
    
    click.echo(f"   Behavioral Insights: {len(varb_validation.behavioral_insights)}")
    for insight in varb_validation.behavioral_insights[:2]:  # Show first 2
        click.echo(f"     - {insight}")
    
    click.echo(f"   VARB Validation Score: {varb_validation.validation_score:.2f}")
    
    # Step 4: Revolutionary Insights
    click.echo("\n💡 Step 4: Revolutionary Insights")
    click.echo("-" * 50)
    
    click.echo("🔍 What VARB + VTI Revealed:")
    
    # Combine insights from both approaches
    total_gaps = len(vti_results['gaps_identified']) + len(varb_validation.authenticity_gaps)
    combined_score = (vti_results['validation_score'] + varb_validation.validation_score) / 2
    
    click.echo(f"   📊 Total Validation Issues: {total_gaps}")
    click.echo(f"   📈 Combined Validation Score: {combined_score:.2f}")
    
    # Key insights
    click.echo(f"\n🎯 Key Insights:")
    click.echo(f"   • VARB preserved stakeholder's authentic user-centric focus")
    click.echo(f"   • VTI detected {len(vti_results['gaps_identified'])} implementation interpretation gaps")
    click.echo(f"   • Authenticity confidence: {varb_impl.confidence_in_authenticity:.2f}")
    click.echo(f"   • Stakeholder behavioral patterns: {len(varb_impl.behavioral_assumptions)} detected")
    
    # Recommendations
    click.echo(f"\n💡 Revolutionary Recommendations:")
    
    if varb_validation.recommended_adjustments:
        click.echo(f"   VARB Authenticity Improvements:")
        for rec in varb_validation.recommended_adjustments:
            click.echo(f"     - {rec}")
    
    if vti_results['parsing_improvements']:
        click.echo(f"   VTI Parsing Improvements:")
        for improvement in vti_results['parsing_improvements'][:2]:
            click.echo(f"     - {improvement}")
    
    # Step 5: The Revolutionary Impact
    click.echo(f"\n🚀 Step 5: Revolutionary Impact")
    click.echo("-" * 50)
    
    click.echo("🎉 VARB + VTI provides unprecedented validation capabilities:")
    click.echo("   ✅ Preserves authentic stakeholder voice and behavioral patterns")
    click.echo("   ✅ Validates transformation quality through parallel implementation")
    click.echo("   ✅ Detects where systematic processes lose human authenticity")
    click.echo("   ✅ Creates learning loops for continuous improvement")
    click.echo("   ✅ Bridges the gap between human intent and systematic implementation")
    
    click.echo(f"\n🎯 Bottom Line:")
    click.echo(f"   Traditional approach: Hope we understood requirements correctly")
    click.echo(f"   VARB + VTI approach: Systematically validate we preserved authenticity")
    click.echo(f"   Result: Objective measurement of subjective transformation quality!")


@cli.command()
@click.argument('transcript_file', type=click.Path(exists=True))
def analyze_transcript(transcript_file):
    """Analyze a stakeholder interview transcript with VARB + VTI."""
    transcript_path = Path(transcript_file)
    
    click.echo(f"🎤 Analyzing transcript: {transcript_path.name}")
    
    # Read transcript
    transcript_content = transcript_path.read_text(encoding='utf-8')
    
    # Initialize validators
    varb = VARBValidator()
    vti = VTIFeedbackLoop()
    
    # VARB analysis
    click.echo("\n🎯 VARB Analysis:")
    varb_impl = varb.varb_code_from_transcript(transcript_content, "Transcript Analysis")
    
    click.echo(f"   Authentic Intent: {varb_impl.authentic_intent}")
    click.echo(f"   Authenticity Confidence: {varb_impl.confidence_in_authenticity:.2f}")
    
    # VTI analysis
    click.echo("\n🔄 VTI Analysis:")
    vti_results = vti.run_audio_vti_validation(transcript_content, "Transcript Analysis")
    
    click.echo(f"   Speech Patterns: {vti_results['speech_patterns']}")
    click.echo(f"   Conversational Conventions: {len(vti_results['conversational_conventions'])}")
    click.echo(f"   Audio Confidence: {vti_results['audio_confidence']:.2f}")
    
    # Combined insights
    click.echo(f"\n💡 Combined Insights:")
    click.echo(f"   VARB Authenticity: {varb_impl.confidence_in_authenticity:.2f}")
    click.echo(f"   VTI Audio Quality: {vti_results['audio_confidence']:.2f}")
    click.echo(f"   Validation Score: {vti_results['validation_score']:.2f}")


@cli.command()
@click.option('--stakeholder-type', default='Product Manager', help='Type of stakeholder')
@click.option('--domain', default='Software Development', help='Domain context')
def interactive_varb(stakeholder_type, domain):
    """Interactive VARB coding session."""
    click.echo(f"🎯 Interactive VARB Coding Session")
    click.echo(f"   Stakeholder Type: {stakeholder_type}")
    click.echo(f"   Domain: {domain}")
    click.echo("-" * 50)
    
    varb = VARBValidator()
    
    # Get stakeholder input
    click.echo("📝 Please describe the stakeholder's behavior or provide a transcript:")
    stakeholder_input = click.get_text_stream('stdin').read()
    
    if not stakeholder_input.strip():
        click.echo("❌ No input provided")
        return
    
    # Perform VARB coding
    click.echo("\n🎯 Performing VARB Coding...")
    
    if len(stakeholder_input) > 200:  # Looks like transcript
        varb_impl = varb.varb_code_from_transcript(stakeholder_input, f"{stakeholder_type} - {domain}")
    else:  # Looks like behavioral description
        varb_impl = varb.varb_code_from_behavior(stakeholder_input, domain)
    
    # Display results
    click.echo(f"\n✅ VARB Results:")
    click.echo(f"   Style: {varb_impl.style.value}")
    click.echo(f"   Authentic Intent: {varb_impl.authentic_intent}")
    click.echo(f"   Behavioral Assumptions: {len(varb_impl.behavioral_assumptions)}")
    click.echo(f"   Authenticity Confidence: {varb_impl.confidence_in_authenticity:.2f}")
    
    click.echo(f"\n📋 Behavioral Assumptions:")
    for assumption in varb_impl.behavioral_assumptions:
        click.echo(f"     - {assumption}")


if __name__ == '__main__':
    cli()