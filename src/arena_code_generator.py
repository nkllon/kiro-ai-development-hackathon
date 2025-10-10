#!/usr/bin/env python3
"""
Arena Code Generator - Multi-model competitive code generation

Spins up multiple LLM models to generate code in parallel, then uses Claude
as a judge to select the best solution or synthesize features from multiple submissions.

PDCA Pattern:
- Plan: Multiple models generate solutions simultaneously
- Do: Execute all generations in parallel
- Check: Claude judges/ranks all submissions arena-style
- Act: Pick winner OR synthesize best features from top submissions
"""

import os
import json
import requests
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path
from anthropic import Anthropic


class ArenaModel:
    """Represents a single model in the arena"""
    def __init__(self, name: str, endpoint: str, model_id: str):
        self.name = name
        self.endpoint = endpoint
        self.model_id = model_id

    def generate(self, prompt: str, timeout: int = 30) -> str:
        """Generate code using this model"""
        try:
            response = requests.post(
                f"{self.endpoint}/api/generate",
                json={
                    "model": self.model_id,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1}
                },
                timeout=timeout
            )
            return response.json()['response']
        except Exception as e:
            return f"ERROR: {str(e)}"


class ArenaCodeGenerator:
    """Multi-model arena for competitive code generation"""

    def __init__(self, models: List[ArenaModel] = None):
        self.models = models or self._default_models()
        self.claude = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.learning_file = Path(__file__).parent.parent / "arena_learning.md"

    def _default_models(self) -> List[ArenaModel]:
        """Default model configuration"""
        # Primary: DeepSeek on RunPod
        return [
            ArenaModel("DeepSeek-Coder-6.7B", "http://localhost:11435", "deepseek-coder:6.7b"),
            # Can add more when we spin up additional pods:
            # ArenaModel("CodeLlama-7B", "http://localhost:11436", "codellama:7b"),
            # ArenaModel("StarCoder2-7B", "http://localhost:11437", "starcoder2:7b"),
        ]

    async def generate_parallel(self, prompt: str) -> Dict[str, str]:
        """Generate code from all models in parallel"""
        print(f"\n🏟️  ARENA: {len(self.models)} models competing...")

        async def generate_from_model(model: ArenaModel):
            print(f"  🤖 {model.name} generating...")
            # Run in thread pool since requests is sync
            loop = asyncio.get_event_loop()
            code = await loop.run_in_executor(None, model.generate, prompt)
            print(f"  ✅ {model.name} completed ({len(code)} chars)")
            return model.name, code

        # Run all models in parallel
        tasks = [generate_from_model(model) for model in self.models]
        results = await asyncio.gather(*tasks)

        return dict(results)

    def judge_with_claude(self, task_description: str, submissions: Dict[str, str]) -> Dict[str, Any]:
        """Have Claude judge all arena submissions"""

        # Format submissions for Claude
        submissions_text = "\n\n".join([
            f"## Submission from {name}:\n```python\n{code}\n```"
            for name, code in submissions.items()
        ])

        prompt = f"""You are judging a code generation arena. Multiple AI models submitted solutions to this task:

TASK: {task_description}

SUBMISSIONS:
{submissions_text}

Please analyze each submission and provide:

1. **Rankings**: Rank submissions from best to worst (1st, 2nd, 3rd, etc.)
2. **Scores**: Rate each on scale 1-10 for:
   - Correctness
   - Code quality
   - Completeness
   - Best practices
3. **Winner**: Declare which submission is best overall
4. **Synthesis Opportunities**: Identify if features from multiple submissions could be combined for an even better solution
5. **Improvement Feedback**: What would make the winner even better?

Respond in this exact format:

RANKINGS:
1. [Model Name] - [Brief reason]
2. [Model Name] - [Brief reason]
...

SCORES:
[Model Name]: Correctness=X, Quality=X, Completeness=X, BestPractices=X
...

WINNER: [Model Name]

SYNTHESIS: [Yes/No - explain if features could be combined]

IMPROVEMENTS: [Feedback for the winner]
"""

        print(f"\n⚖️  Claude judging {len(submissions)} submissions...")

        message = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )

        judgment = message.content[0].text

        # Parse winner from judgment
        winner_name = None
        for line in judgment.split('\n'):
            if line.startswith('WINNER:'):
                winner_name = line.replace('WINNER:', '').strip()
                break

        return {
            'judgment': judgment,
            'winner': winner_name,
            'winner_code': submissions.get(winner_name, list(submissions.values())[0])
        }

    def save_arena_results(self, task: str, submissions: Dict[str, str], judgment: Dict[str, Any]):
        """Save arena results to learning file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        submissions_summary = "\n".join([
            f"**{name}**: {len(code)} chars"
            for name, code in submissions.items()
        ])

        entry = f"""
---
## Arena Battle: {timestamp}

**Task**: {task[:200]}...

**Competitors**: {len(submissions)} models
{submissions_summary}

**Claude's Judgment**:
{judgment['judgment']}

**Winner**: {judgment['winner']}

**Winning Code**:
```python
{judgment['winner_code'][:500]}...
```

"""

        with open(self.learning_file, 'a') as f:
            f.write(entry)

        print(f"📊 Arena results saved to {self.learning_file}")

    async def arena_generate(self, task_description: str, requirements: str = "") -> Dict[str, Any]:
        """Main arena workflow"""
        print(f"\n{'='*80}")
        print("🏟️  ARENA CODE GENERATOR - Multi-Model Competition")
        print(f"{'='*80}\n")

        # Build generation prompt
        prompt = f"""Generate Python code for this task:

{task_description}

Requirements:
{requirements or 'Follow Python best practices'}

Provide only the code, no explanations."""

        # Step 1: Parallel generation from all models
        submissions = await self.generate_parallel(prompt)

        # Step 2: Claude judges
        judgment = self.judge_with_claude(task_description, submissions)

        # Step 3: Save learning data
        self.save_arena_results(task_description, submissions, judgment)

        print(f"\n{'='*80}")
        print("✨ ARENA COMPLETE")
        print(f"{'='*80}\n")
        print(f"🏆 Winner: {judgment['winner']}")

        return {
            'final_code': judgment['winner_code'],
            'winner': judgment['winner'],
            'all_submissions': submissions,
            'judgment': judgment['judgment']
        }


async def main():
    """Test the arena generator"""
    arena = ArenaCodeGenerator()

    task = """Create a Python class RateLimiter that:
- Uses token bucket algorithm
- Thread-safe with asyncio
- Methods: can_proceed(endpoint: str) -> bool, record_request(endpoint: str)
- Rate: 100 requests per minute
- Includes proper docstrings and type hints
"""

    result = await arena.arena_generate(task)

    print("\n🏆 WINNING CODE:")
    print(result['final_code'][:500])


if __name__ == "__main__":
    asyncio.run(main())
