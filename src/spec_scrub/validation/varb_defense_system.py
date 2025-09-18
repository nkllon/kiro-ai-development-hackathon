"""
VARB Defense System

Defensive acronym alternatives for when someone inevitably tries to make VARB offensive.
We're getting ahead of the problem by defining all the alternatives ourselves!
"""

from typing import Dict, List
from enum import Enum


class VARBInterpretationLevel(Enum):
    """Different levels of VARB interpretation"""
    PROFESSIONAL = "professional"
    DEFENSIVE = "defensive" 
    AGGRESSIVE = "aggressive"
    NSFW = "nsfw"  # Not Safe For Work


class VARBDefenseSystem:
    """
    Defense system for VARB acronym interpretations.
    
    Since someone will inevitably try to make VARB offensive (like FUBAR),
    we're getting ahead of it by defining all possible interpretations ourselves.
    """
    
    def __init__(self):
        self.interpretations = {
            VARBInterpretationLevel.PROFESSIONAL: {
                "Voice-Authentic Requirements Behavior": "Our official definition",
                "Validation Against Raw Behavior": "Validation methodology focus",
                "Vibe-Aligned Requirements Baseline": "Vibe coding integration",
                "Verified Authentic Requirements Behavior": "Verification process focus",
                "Value-Authentic Requirements Behavior": "Value preservation focus"
            },
            
            VARBInterpretationLevel.DEFENSIVE: {
                "Viciously Accurate Requirements Behavior": "For brutally honest stakeholders",
                "Violently Anti-Bullshit Requirements": "Cuts through corporate speak",
                "Vindictively Authentic Requirements Behavior": "Ruthlessly preserves intent",
                "Very Aggressive Requirements Baseline": "For demanding stakeholders"
            },
            
            VARBInterpretationLevel.AGGRESSIVE: {
                "Vulgar And Raw Behavior": "For stakeholders who use colorful language",
                "Vicious Attack on Requirements Bullshit": "No tolerance for vague requirements",
                "Violently Authentic Requirements Behavior": "Aggressively preserves stakeholder voice",
                "Vindictive Anti-Requirements Bureaucracy": "Fights systematic filtering"
            },
            
            VARBInterpretationLevel.NSFW: {
                # We're not actually defining these, but we acknowledge they exist
                "Redacted": "We know someone will think of these, but we're staying professional"
            }
        }
    
    def get_official_definition(self) -> str:
        """Get the official, professional VARB definition."""
        return "Voice-Authentic Requirements Behavior"
    
    def get_defensive_alternatives(self) -> List[str]:
        """Get defensive alternatives for when people try to be offensive."""
        return list(self.interpretations[VARBInterpretationLevel.DEFENSIVE].keys())
    
    def explain_defense_strategy(self) -> str:
        """Explain our defense strategy."""
        return """
        VARB Defense Strategy:
        
        1. We define the professional interpretation first
        2. We anticipate offensive alternatives and get ahead of them
        3. We own the narrative by defining all reasonable interpretations
        4. We acknowledge that offensive versions will exist but stay professional
        5. We use humor to defuse attempts to make it offensive
        
        Like FUBAR (F***ed Up Beyond All Recognition), acronyms can become offensive.
        But unlike FUBAR, we're controlling the narrative from the start!
        """
    
    def handle_offensive_interpretation(self, offensive_suggestion: str) -> str:
        """Handle when someone suggests an offensive VARB interpretation."""
        return f"""
        Nice try! We already thought of that and worse.
        
        VARB officially means: {self.get_official_definition()}
        
        We've prepared defensive alternatives if needed:
        {', '.join(self.get_defensive_alternatives())}
        
        But we're sticking with the professional definition because:
        1. It accurately describes what we built
        2. It's not offensive like FUBAR
        3. It maintains credibility in professional settings
        4. It focuses on the methodology, not shock value
        
        Your offensive suggestion: "{offensive_suggestion}" is noted but rejected! 😄
        """
    
    def get_context_appropriate_definition(self, context: str) -> str:
        """Get context-appropriate VARB definition."""
        context_lower = context.lower()
        
        if any(word in context_lower for word in ["corporate", "executive", "board", "client"]):
            return "Voice-Authentic Requirements Behavior - preserving stakeholder intent"
        
        elif any(word in context_lower for word in ["developer", "engineer", "technical"]):
            return "Voice-Authentic Requirements Behavior - validation through authentic behavior preservation"
        
        elif any(word in context_lower for word in ["frustrated", "angry", "demanding"]):
            return "Viciously Accurate Requirements Behavior - cutting through the BS to get real requirements"
        
        else:
            return self.get_official_definition()
    
    def varb_vs_fubar_comparison(self) -> str:
        """Compare VARB to FUBAR to show we're being proactive."""
        return """
        VARB vs FUBAR: Learning from History
        
        FUBAR: F***ed Up Beyond All Recognition
        - Started as military slang
        - Became widely offensive
        - Lost professional credibility
        - Now can't be used in polite company
        
        VARB: Voice-Authentic Requirements Behavior  
        - Started with professional definition
        - Anticipated offensive alternatives
        - Maintained professional credibility
        - Can be used in any business context
        
        We learned from FUBAR's trajectory and controlled our own narrative!
        """


def demonstrate_varb_defense():
    """Demonstrate the VARB defense system."""
    defense = VARBDefenseSystem()
    
    print("VARB Defense System Demonstration")
    print("=" * 40)
    
    print(f"Official Definition: {defense.get_official_definition()}")
    print(f"\nDefensive Alternatives: {defense.get_defensive_alternatives()}")
    
    print(f"\nContext Examples:")
    print(f"Corporate context: {defense.get_context_appropriate_definition('corporate board meeting')}")
    print(f"Technical context: {defense.get_context_appropriate_definition('developer standup')}")
    print(f"Frustrated context: {defense.get_context_appropriate_definition('frustrated stakeholder')}")
    
    print(f"\nHandling offensive suggestion:")
    print(defense.handle_offensive_interpretation("Very Awful Requirements Bullsh*t"))
    
    print(f"\nVARB vs FUBAR:")
    print(defense.varb_vs_fubar_comparison())


if __name__ == "__main__":
    demonstrate_varb_defense()