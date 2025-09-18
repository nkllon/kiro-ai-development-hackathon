"""
VARB Acronym Definition

Since we don't know what VARB originally meant, here are our candidate definitions
based on what we actually built:

V.A.R.B Acronym Options:
========================

## Professional/Polite Options:
1. **Voice-Authentic Requirements Behavior** (Our Official Choice)
2. **Validation Against Raw Behavior** 
3. **Vibe-Aligned Requirements Baseline**
4. **Verified Authentic Requirements Behavior**
5. **Value-Authentic Requirements Behavior**

## Defensive/Offensive Alternatives:
(Because someone else will think of these, so we better get there first)

6. **Viciously Accurate Requirements Behavior**
   - For when stakeholders are brutally honest about what they want
   - Captures the raw, unfiltered truth of requirements

7. **Violently Anti-Bullshit Requirements**
   - Cuts through corporate speak and gets to real intent
   - No tolerance for vague, meaningless requirements

8. **Vindictively Authentic Requirements Behavior**
   - Preserves stakeholder intent with ruthless accuracy
   - Exposes where systematic processes lose the plot

9. **Vulgar And Raw Behavior** 
   - For when stakeholders use... colorful language
   - Preserves authentic emotional expression

10. **Very Aggressive Requirements Baseline**
    - When stakeholders are demanding and urgent
    - Captures high-pressure, no-nonsense requirements

Our Chosen Definition:
=====================

**V.A.R.B = Voice-Authentic Requirements Behavior**

This best captures what we built while remaining professional:
- **Voice**: Preserves stakeholder's natural communication patterns
- **Authentic**: Maintains genuine intent without systematic filtering  
- **Requirements**: Applied to requirements transformation validation
- **Behavior**: Captures behavioral patterns and assumptions

But we're ready with alternatives if someone tries to make it offensive!
"""

# Official VARB definition for the codebase
VARB_ACRONYM = "Voice-Authentic Requirements Behavior"
VARB_DEFINITION = """
VARB (Voice-Authentic Requirements Behavior) is a validation methodology that 
preserves authentic stakeholder voice and behavioral patterns during requirements 
transformation, providing ground truth validation against systematic filtering.
"""

def get_varb_definition() -> str:
    """Get the official VARB definition."""
    return f"VARB = {VARB_ACRONYM}\n\n{VARB_DEFINITION}"

def explain_varb_acronym() -> dict:
    """Explain each letter of the VARB acronym."""
    return {
        "V": "Voice - Preserves stakeholder's natural communication patterns and emphasis",
        "A": "Authentic - Maintains genuine intent without systematic filtering or transformation", 
        "R": "Requirements - Applied to requirements engineering and transformation validation",
        "B": "Behavior - Captures behavioral patterns, assumptions, and thinking styles"
    }

if __name__ == "__main__":
    print("VARB Acronym Definition")
    print("=" * 30)
    print(get_varb_definition())
    print("\nAcronym Breakdown:")
    for letter, meaning in explain_varb_acronym().items():
        print(f"  {letter}: {meaning}")