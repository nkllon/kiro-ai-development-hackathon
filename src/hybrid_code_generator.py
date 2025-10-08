#!/usr/bin/env python3
"""
Simple Hybrid Code Generator - Direct API calls, no LangChain

Uses direct HTTP calls to Ollama and Anthropic APIs for faster,  more reliable execution.
"""

import os
import json
import requests
from anthropic import Anthropic


def generate_with_deepseek(prompt: str, deepseek_url="http://localhost:11435") -> str:
    """Generate code using DeepSeek via direct Ollama API"""
    try:
        response = requests.post(
            f"{deepseek_url}/api/generate",
            json={
                "model": "deepseek-coder:6.7b",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1
                }
            },
            timeout=30
        )
        response.raise_for_status()
        generated_code = response.json()['response']

        # CRITICAL FIX: Remove DeepSeek tokenizer leakage
        # DeepSeek inserts <｜begin▁of▁sentence｜> tokens into code output
        import re
        generated_code = re.sub(r'<｜begin▁of▁sentence｜>', '', generated_code)
        generated_code = re.sub(r'<｜end▁of▁sentence｜>', '', generated_code)
        generated_code = re.sub(r'<\|.*?\|>', '', generated_code)  # Catch any other special tokens

        # Strip markdown code blocks if present
        generated_code = re.sub(r'^```python\s*\n', '', generated_code)
        generated_code = re.sub(r'\n```\s*$', '', generated_code)
        generated_code = generated_code.strip()

        # FIX SYNTAX WITH BLACK: Auto-format to fix many syntax errors
        try:
            import black
            try:
                formatted_code = black.format_file_contents(
                    generated_code,
                    fast=False,
                    mode=black.FileMode()
                )
                generated_code = formatted_code
                print("  ✅ Black auto-format applied - syntax clean")
                return generated_code
            except black.NothingChanged:
                print("  ✓ Code already properly formatted")
                return generated_code
            except Exception as black_error:
                # Black failed (syntax too broken) - REJECT immediately
                error_msg = str(black_error)[:100]
                print(f"  ❌ Black formatting FAILED: {error_msg}")
                print(f"  🔄 Code rejected - DeepSeek must fix syntax")
                # Return with error marker so Claude knows it's broken
                return f"# BLACK FORMATTING FAILED - SYNTAX ERROR\n# Error: {error_msg}\n\n{generated_code}"
        except ImportError:
            print("  ⚠️ Black not installed, skipping auto-format")
            return generated_code
    except Exception as e:
        print(f"DeepSeek generation error: {e}")
        raise


def review_with_claude(code: str, task_description: str) -> dict:
    """Review code using Claude"""
    try:
        client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        prompt = f"""Review this generated Python code. Use pragmatic 80/20 rule - approve if good enough.

Task: {task_description}

Generated Code:
```python
{code}
```

APPROVAL CRITERIA (80/20 Rule):

🔴 BLOCKING ISSUES (must fix to approve):
- Critical bugs that prevent code from running
- Security vulnerabilities (hardcoded secrets, injection risks)
- Missing core functionality from task requirements

🟢 ACCEPTABLE (don't block approval):
- Has docstrings (even if brief)
- Has type hints (even if not exhaustive)
- Has error handling (even if basic)
- Has input validation (even if minimal)
- Minor style issues

STANDARD: If code is 80%+ ready with NO blocking issues → APPROVE.
Don't let perfect be the enemy of good. Minor polish can happen later.

Respond in this EXACT format:
CONFIDENCE: [0-100]%
STATUS: [APPROVED or NEEDS_REVISION]
REASON: [brief explanation]

If CONFIDENCE >= 80% and no blocking issues → STATUS must be APPROVED.
"""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            temperature=0,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        review = message.content[0].text

        # Extract confidence score
        import re
        confidence_match = re.search(r'CONFIDENCE:\s*(\d+)%', review)
        confidence = int(confidence_match.group(1)) if confidence_match else 0

        # Check approval status
        approved = 'STATUS: APPROVED' in review or 'APPROVED:' in review.upper()

        return {
            'review': review,
            'approved': approved,
            'confidence': confidence
        }

    except Exception as e:
        print(f"Claude review error: {e}")
        raise


def run_code_generation(task_description: str, spec_requirements: str = "", max_iterations: int = 5):
    """Run hybrid generation workflow - main entry point"""
    return hybrid_generate(task_description, spec_requirements, max_iterations)


def save_learning_feedback(task_description: str, iteration: int, generated_code: str, review_feedback: str, approved: bool):
    """Save Claude's review feedback to deepseek_learning.md for future improvements"""
    from datetime import datetime
    from pathlib import Path

    learning_file = Path(__file__).parent.parent / "deepseek_learning.md"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry = f"""
---
## Learning Entry: {timestamp}

**Task**: {task_description[:200]}...

**Iteration**: {iteration}

**Generated Code**:
```python
{generated_code[:500]}...
```

**Claude Review Feedback**:
{review_feedback}

**Status**: {'✅ APPROVED' if approved else '⚠️ NEEDS REVISION'}

"""

    with open(learning_file, 'a') as f:
        f.write(entry)


def hybrid_generate(task_description: str, requirements: str = "", max_iterations: int = 5):
    """Run hybrid generation workflow"""
    print(f"\n{'='*80}")
    print("🚀 HYBRID CODE GENERATOR - DeepSeek + Claude")
    print(f"{'='*80}\n")

    # Load DeepSeek project context and instructions (level playing field with Claude)
    from pathlib import Path
    deepseek_dir = Path(__file__).parent.parent / ".deepseek"

    context_file = deepseek_dir / "project-context.md"
    project_context = ""
    if context_file.exists():
        # Extract key patterns section (first 2000 chars)
        full_context = context_file.read_text()
        project_context = full_context[:2000]  # Keep prompt manageable
        print("✅ Loaded project context (patterns, frameworks, requirements)")

    instructions_file = deepseek_dir / "instructions.md"
    if instructions_file.exists():
        print("✅ Loaded Claude feedback patterns\n")

    iteration = 0
    generated_code = None
    review_feedback = None
    approved = False
    black_failures = 0
    MAX_BLACK_FAILURES = 21  # Fibonacci limit - if can't pass Black in 21 tries, give up

    while iteration < max_iterations and not approved and black_failures < MAX_BLACK_FAILURES:
        iteration += 1
        print(f"\n🔄 ITERATION {iteration}/{max_iterations}")
        print("-" * 40)

        # Generate code with DeepSeek
        if iteration == 1:
            # Initial generation with project context + data-driven guidance
            prompt = f"""You are generating production-quality Python code for the Kiro AI Hackathon Beast Mode framework.

PROJECT CONTEXT:
{project_context}

🔴 MANDATORY (causes 100% of rejections if missing):
1. Comprehensive docstrings for EVERY class, function, module
2. Proper error handling with specific exceptions (no bare except)
3. Input validation at function entry (check None, empty, types)
4. Complete type hints on all parameters and returns
5. Logging with logger = logging.getLogger(__name__)
6. NO pass statements or TODO comments in production code

TASK:
{task_description}

REQUIREMENTS:
{requirements or 'Follow Python best practices and Beast Mode patterns'}

Provide ONLY the Python code, no markdown wrappers, no explanations."""

        else:
            # Refinement based on feedback
            prompt = f"""Improve this code based on the review feedback.

Original code:
{generated_code}

Review feedback:
{review_feedback}

Task requirements:
{task_description}

Provide the improved code only, no explanations."""

        print(f"🤖 DeepSeek generating code...")
        generated_code = generate_with_deepseek(prompt)

        # Check if Black rejected it
        if generated_code.startswith("# BLACK FORMATTING FAILED"):
            black_failures += 1
            print(f"❌ Black failure #{black_failures}/{MAX_BLACK_FAILURES}")
            if black_failures >= MAX_BLACK_FAILURES:
                print(f"🚨 GIVING UP: Code failed Black formatting {MAX_BLACK_FAILURES} times (Fibonacci limit)")
                break
            # Continue to next iteration with syntax error feedback
            review_feedback = "CRITICAL: Code has syntax errors that prevent Black formatting. Fix syntax first."
            approved = False
            continue

        print(f"✅ Generated {len(generated_code)} characters")

        # Review with Claude
        print(f"👁️  Claude reviewing...")
        review_result = review_with_claude(generated_code, task_description)

        review_feedback = review_result['review']
        approved = review_result['approved']

        # Save learning feedback for DeepSeek improvement
        save_learning_feedback(task_description, iteration, generated_code, review_feedback, approved)

        if approved:
            print("✅ Code APPROVED!")
        else:
            print("⚠️  Code needs revision")
            print(f"Feedback: {review_feedback[:150]}...")

    print(f"\n{'='*80}")
    print("✨ WORKFLOW COMPLETE")
    print(f"{'='*80}\n")
    print(f"Iterations: {iteration}")

    # Escalation handling
    if black_failures >= MAX_BLACK_FAILURES:
        print(f"🚨 BLACK LIMIT REACHED: Code failed formatting {black_failures} times")
        print(f"   DeepSeek cannot generate syntactically valid code for this task")
        status = 'black_failure'
    elif not approved and iteration >= max_iterations:
        print(f"🚨 ESCALATION: Task maxed out at {max_iterations} iterations without approval")
        print(f"   This task requires human review and intervention")
        status = 'escalation_required'
    elif approved:
        status = 'approved'
    else:
        status = 'in_progress'

    print(f"Status: {status.upper()}")
    print(f"Black failures: {black_failures}/{MAX_BLACK_FAILURES}")

    return {
        'final_code': generated_code,
        'generated_code': generated_code,
        'approval_status': status,
        'iteration_count': iteration,
        'black_failures': black_failures,
        'review_feedback': review_feedback,
        'requires_escalation': (not approved and iteration >= max_iterations)
    }


if __name__ == "__main__":
    # Test
    task = """Create a Python function validate_email(email: str) -> bool that:
- Validates email addresses using regex
- Returns False for None or empty strings
- Includes proper docstring and type hints
"""

    requirements = "Use re module. Handle all edge cases. Follow PEP 8."

    result = hybrid_generate(task, requirements)
    print("\n\nFINAL CODE:")
    print(result['final_code'])
