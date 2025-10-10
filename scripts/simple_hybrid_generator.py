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
        return response.json()['response']
    except Exception as e:
        print(f"DeepSeek generation error: {e}")
        raise


def review_with_claude(code: str, task_description: str) -> dict:
    """Review code using Claude"""
    try:
        client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        prompt = f"""Review this generated Python code for a production system.

Task: {task_description}

Generated Code:
```python
{code}
```

Evaluate:
1. Correctness - Does it meet requirements?
2. Security - Any vulnerabilities?
3. Best practices - Proper error handling, typing, docstrings?
4. Edge cases - Are they handled?
5. Performance - Any concerns?

Respond with:
- APPROVED: [reason] (if code is production-ready)
- NEEDS_REVISION: [specific improvements needed] (if changes required)
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

        return {
            'review': review,
            'approved': 'APPROVED:' in review.upper()
        }

    except Exception as e:
        print(f"Claude review error: {e}")
        raise


def hybrid_generate(task_description: str, requirements: str = "", max_iterations: int = 5):
    """Run hybrid generation workflow"""
    print(f"\n{'='*80}")
    print("🚀 HYBRID CODE GENERATOR - DeepSeek + Claude")
    print(f"{'='*80}\n")

    iteration = 0
    generated_code = None
    review_feedback = None
    approved = False

    while iteration < max_iterations and not approved:
        iteration += 1
        print(f"\n🔄 ITERATION {iteration}/{max_iterations}")
        print("-" * 40)

        # Generate code with DeepSeek
        if iteration == 1:
            # Initial generation
            prompt = f"""Generate Python code for this task:

{task_description}

Requirements:
{requirements or 'Follow Python best practices'}

Provide only the code, no explanations."""

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
        print(f"✅ Generated {len(generated_code)} characters")

        # Review with Claude
        print(f"👁️  Claude reviewing...")
        review_result = review_with_claude(generated_code, task_description)

        review_feedback = review_result['review']
        approved = review_result['approved']

        if approved:
            print("✅ Code APPROVED!")
        else:
            print("⚠️  Code needs revision")
            print(f"Feedback: {review_feedback[:150]}...")

    print(f"\n{'='*80}")
    print("✨ WORKFLOW COMPLETE")
    print(f"{'='*80}\n")
    print(f"Iterations: {iteration}")
    print(f"Status: {'APPROVED' if approved else 'MAX ITERATIONS REACHED'}")

    return {
        'final_code': generated_code,
        'generated_code': generated_code,
        'approval_status': 'approved' if approved else 'max_iterations',
        'iteration_count': iteration,
        'review_feedback': review_feedback
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
