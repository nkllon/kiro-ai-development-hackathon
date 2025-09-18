"""
VARB Acronym Definition

Since we don't know what VARB originally meant, here are our candidate definitions
based on what we actually built:

V.A.R.B Acronym Options:
========================

1. **Voice-Authentic Requirements Behavior**
   - Preserves the authentic voice of stakeholders
   - Maintains behavioral patterns in requirements
   - Focus on authenticity preservation

2. **Validation Against Raw Behavior** 
   - Validates transformation against raw stakeholder behavior
   - Compares systematic vs behavioral implementations
   - Focus on validation methodology

3. **Vibe-Aligned Requirements Baseline**
   - Creates baseline from stakeholder vibe/intent
   - Aligns requirements with authentic stakeholder vibe
   - Focus on vibe coding integration

4. **Verified Authentic Requirements Behavior**
   - Verifies that requirements preserve authentic behavior
   - Systematic verification of authenticity
   - Focus on verification process

5. **Value-Authentic Requirements Behavior**
   - Preserves the authentic values of stakeholders
   - Maintains value alignment in requirements
   - Focus on value preservation

Our Chosen Definition:
=====================

**V.A.R.B = Voice-Authentic Requirements Behavior**

This best captures what we built:
- **Voice**: Preserves stakeholder's natural communication patterns
- **Authentic**: Maintains genuine intent without systematic filtering  
- **Requirements**: Applied to requirements transformation validation
- **Behavior**: Captures behavioral patterns and assumptions

The VARB methodology validates that requirements transformation preserves
the authentic voice and behavioral patterns of stakeholders.
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