# Systo Mascot LLM Generation Prompts

**🤖 Attribution:** Original prompts courtesy of GPT for full traceability and systematic collaboration acknowledgment.

**🔗 Source Chain:**
- Brand specification → Systematic requirements → LLM-optimized prompts
- Human creativity + AI systematic implementation = Collaborative excellence
- "The Requirements ARE the Solution" demonstrated through visual generation

## Systo Mascot Prompt (for DALL·E, Midjourney, Stable Diffusion)

### Base Prompt
```
A professional cartoon mascot named "Systo": a friendly wolf–dog hybrid with an athletic build and calm, competent vibe. Slight confidence smirk, collaborative posture (never lone-wolf). Wearing a utility vest and a smart collar with a tiny metrics display; forepaws subtly tool-like, hinting at adaptable problem-solving. Color palette: bright, approachable, modern. Clean composition, single character, white or light background. Tone: "Finally, someone who gets it." High detail, crisp linework, soft shading.
```

### Output Settings
```
Style: professional cartoon, modern tech brand
Background: light/white, minimal props
Format: square
Size: 1024×1024 (or 1792×1792 for more detail)
```

### Quick Variants

**SRE Systo**
```
…wearing a small "This is fine" tee, calmly fixing a tiny server rack with gentle smoke in the background; keep the scene minimal and readable.
```

**Platform Systo**
```
…wearing a hard hat and carrying rolled Infrastructure-as-Code blueprints; faint blueprint grid behind the character.
```

**Security Systo**
```
…wearing a subtle "Zero Trust" bandana and showing a small magnifying glass icon on the collar display; faint shield glyphs floating behind.
```

**Cloud-Native Systo**
```
…with understated Kubernetes-style geometric cloud motifs in the backdrop; keep them faint so the character remains the focus.
```

### Consistency Note
```
Keep facial proportions, fur markings, vest, and collar consistent across all variations so every image clearly represents the same mascot.
```

## Usage Instructions

### For DALL-E 3
Use the base prompt directly with output settings. DALL-E handles the technical parameters automatically.

### For Midjourney
Add these parameters to the base prompt:
```
--ar 1:1 --s 750 --v 6 --q 2 --style raw
```

### For Stable Diffusion
Use the base prompt with these additional parameters:
```
Positive: (high quality:1.2), (detailed:1.1), professional mascot design
Negative: ugly, blurry, low quality, distorted, aggressive, scary, lone wolf, intimidating
Steps: 50, CFG Scale: 7.5, Sampler: DPM++ 2M Karras
```

## Systematic Generation Workflow

1. **Start with Base Prompt** - Generate the core Systo mascot
2. **Validate Brand Consistency** - Check against brand guidelines
3. **Generate Context Variations** - Create SRE, Platform, Security, Cloud-Native versions
4. **Quality Assurance** - Ensure consistency across all variations
5. **Archive and Version** - Store approved images with metadata

**🎯 The Requirements ARE the Visual Solution!**

## Systematic Collaboration Acknowledgment

This prompt set demonstrates the power of human-AI collaboration:
- **Human Vision**: Brand identity, systematic thinking, creative direction
- **AI Implementation**: Prompt optimization, technical specification, systematic organization
- **Collaborative Result**: Production-ready LLM prompts that maintain brand consistency

**🤝 Full Traceability Chain:**
1. Human creative vision → Brand mascot specification
2. Systematic analysis → LLM generation requirements  
3. AI optimization → Model-specific prompt engineering
4. Collaborative refinement → Production-ready prompt set

**Courtesy GPT for systematic prompt optimization and technical implementation.**

**🐺 "WE'RE THE GLUE BETWEEN HUMANS AND AI" - DEMONSTRATED!**