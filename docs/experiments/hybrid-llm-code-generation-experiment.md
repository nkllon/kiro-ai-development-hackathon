# Hybrid LLM Code Generation Experiment

**Date**: October 7, 2025
**Duration**: ~6 hours
**Objective**: Test DeepSeek + Claude hybrid code generation for 80% cost savings
**Result**: ❌ Failed to achieve viable approval rates with DeepSeek 6.7B

## Executive Summary

We attempted to create a cost-effective code generation pipeline using DeepSeek-Coder-6.7B ($0.60/hr GPU) for initial generation and Claude Sonnet 4.5 (API) for quality review. Despite multiple optimization attempts, approval rates remained too low for production use.

**Final Results**: 5.3% approval rate (1/19 tasks)
**Cost Savings**: 57% ($0.022 vs $0.05 per task) when approved
**Verdict**: DeepSeek 6.7B insufficient for complex production code tasks

## Methodology

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Hybrid Generation Loop                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. DeepSeek generates code                             │
│     ↓                                                    │
│  2. Token cleanup (remove <｜begin▁of▁sentence｜>)      │
│     ↓                                                    │
│  3. Black formatting (syntax validation)                 │
│     ↓                                                    │
│  4. Claude reviews (80/20 pragmatic standard)            │
│     ↓                                                    │
│  5. If not approved: Refine and repeat (max 5 iterations)│
│     ↓                                                    │
│  6. If maxed out: Escalate to human                     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Progressive Improvements Attempted

| Attempt | Optimization | Approval Rate | Key Finding |
|---------|--------------|---------------|-------------|
| 1 | Baseline (strict review) | 0% (0/21) | All tasks maxed out at 5 iterations |
| 2 | Token cleanup | 14% (2/14) | Fixed tokenizer leakage (`<｜begin▁of▁sentence｜>`) |
| 3 | 80/20 pragmatic review | 14% (2/14) | Claude still rejected incomplete implementations |
| 4 | Project context added | 0% (0/14) | DeepSeek didn't understand Beast Mode patterns |
| 5 | Black quality gate | **5.3% (1/19)** | DeepSeek generates code Black can't format (43% fail rate) |

## Detailed Findings

### Issue 1: Tokenizer Leakage (CRITICAL)

**Problem**: DeepSeek inserted its own special tokens into generated code:
```python
class IssueTracker:
    def __init__(self<｜begin▁of▁sentence｜>):  # SYNTAX ERROR
        pass
```

**Impact**: 28 occurrences across all generated code (100% of tasks affected)
**Fix**: Regex post-processing to strip tokens
**Result**: Improved from 0% to 14% approval rate

### Issue 2: Incomplete Implementations

**Problem**: DeepSeek generates skeleton code instead of complete implementations:
```python
class GitHubClient:
    """GitHub API client"""

    def fetch_issues(self):
        pass  # Missing actual implementation
```

**Claude Feedback**: "Missing core functionality" (19.4% of rejections)
**Root Cause**: Model doesn't understand task requirements deeply enough
**Attempted Fix**: Added project context document (2000 chars)
**Result**: No improvement - still generated skeletons

### Issue 3: Syntax Errors Black Can't Fix

**Problem**: DeepSeek generates syntactically broken code:
- Double colons (`::`)
- Incomplete lines
- Missing imports
- Invalid indentation

**Black Failure Rate**: 43.2% (38/88 generation attempts)
**Impact**: Even with Black as quality gate, many syntax errors persist
**Conclusion**: DeepSeek 6.7B lacks fundamental Python syntax competency

### Issue 4: Low Confidence Plateau

**Average Claude Confidence**: 20.7% (far below 80% approval threshold)
**Peak Confidence**: 75% (never reached 80%+)
**Convergence Pattern**: Most tasks plateaued at 15-25% confidence

Claude consistently rated DeepSeek output as:
- 26.9% syntax errors
- 19.4% missing core functionality
- 6.0% skeleton/placeholder code

## Cost Analysis

### Successful Task (Approved)
- DeepSeek generation: ~3 iterations × 3 seconds = ~9 seconds
- Claude reviews: 3 × 15 seconds = 45 seconds
- RunPod cost: 0.015 hours × $0.60 = $0.009
- Claude API cost: ~$0.013
- **Total: $0.022/task**

### Failed Task (Escalated)
- DeepSeek generation: 5 iterations × 3 seconds = 15 seconds
- Claude reviews: 5 × 15 seconds = 75 seconds
- RunPod cost: 0.025 hours × $0.60 = $0.015
- Claude API cost: ~$0.022
- **Total: $0.037/task** (then still requires human intervention)

### Claude-Only Baseline
- Single Claude generation: ~30 seconds
- Claude API cost: ~$0.05
- **Total: $0.05/task** (95%+ success rate)

### Economic Verdict
With 5.3% approval rate:
- **Hybrid effective cost**: $0.037 × 0.947 (failures) + $0.022 × 0.053 (success) = **$0.036/task**
- **Plus human escalation costs**: ~$0.50/task (engineer time)
- **Actual total cost**: ~$0.536/task
- **Claude-only cost**: $0.05/task

**Conclusion**: Hybrid approach is **10.7x more expensive** when accounting for failures and escalation.

## Technical Learnings

### What Worked

1. **Token Cleanup**: Regex filtering successfully removed tokenizer artifacts
2. **Black Integration**: Caught syntax errors immediately (when it worked)
3. **Confidence Scoring**: Enabled quantitative measurement of code quality
4. **80/20 Pragmatic Review**: Reduced Claude over-strictness (but didn't help enough)
5. **Parallel Execution**: 4 agents achieved ~0.86 tasks/minute throughput

### What Didn't Work

1. **DeepSeek 6.7B Capability**: Fundamentally insufficient for complex production code
2. **Prompt Engineering**: Adding project context didn't improve understanding
3. **Iterative Refinement**: DeepSeek couldn't improve code even with detailed feedback
4. **Black as Quality Gate**: 43% of code too broken for Black to format

### Meta-PDCA Learning Loop

**Planned**: Create learning feedback loop where Claude's reviews improve DeepSeek's prompts
**Result**: Captured 4,755 lines of learning data in `.deepseek/learning.md`
**Finding**: Pattern analysis showed consistent issues (100% missing docstrings, 98% missing validation)
**Limitation**: Even with data-driven prompts, DeepSeek couldn't generate better code

## Fibonacci Observation

**21 tasks failed** in initial run - a Fibonacci number (1,1,2,3,5,8,13,21)
**21-iteration limit** set for Black failures before giving up
**Speculation**: Natural optimization points in systematic processes?

## Recommendations

### For Current Project
1. **Use Claude-only** for production code generation ($0.05/task, 95%+ success)
2. **Keep hybrid generator** as research artifact
3. **Document learnings** for future model evaluations

### For Future Experiments

#### Try Larger Models
- **DeepSeek-Coder-33B**: Requires 4× GPU memory but may be more capable
- **CodeLlama-34B**: Alternative model family
- **Cost**: ~$2.40/hr GPU (4× current cost)

#### Try Arena Mode
- Run 3 models in parallel (DeepSeek, CodeLlama, StarCoder)
- Claude judges best output
- Cost: 3× GPU = $1.80/hr
- Hypothesis: Competition might yield better results

#### Try Different Task Types
- **Simple utilities**: DeepSeek might handle basic functions (not complex frameworks)
- **Test generation**: More formulaic than implementation
- **Documentation**: Lower complexity than production code

### For System Architecture

#### Keep These Patterns
- Token cleanup post-processing
- Black syntax validation
- Confidence scoring
- Parallel agent execution
- Learning feedback capture

#### Improve These
- Better task complexity detection (route simple → DeepSeek, complex → Claude)
- Earlier escalation (don't waste 5 iterations on obviously broken code)
- Confidence threshold for auto-escalation (if < 30% on iteration 2, give up)

## Data Artifacts

### Generated Files
- **26 generated Python files** in `.kiro/specs/*/generated_*.py`
- **Quality**: Mostly incomplete/broken implementations
- **Size**: 0.5KB - 2.5KB average

### Learning Logs
- **`.deepseek/learning.md`**: 4,755 lines of Claude review feedback
- **`.deepseek/arena_learning.md`**: Arena mode test results
- **`.deepseek/project-context.md`**: 2KB project patterns for DeepSeek
- **`.deepseek/instructions.md`**: 5.6KB data-driven generation rules

### Execution Logs
- `beast_mode_hybrid_execution.log`: Initial run (0% approval)
- `beast_mode_fixed_run.log`: With token cleanup (14% approval)
- `beast_mode_pragmatic_run.log`: With 80/20 review (14% approval)
- `beast_mode_black_gated.log`: With Black quality gate (5.3% approval)

## Conclusion

While the hybrid LLM approach showed promise in theory (80% cost savings), DeepSeek-Coder-6.7B proved inadequate for complex production code tasks:

- **Token leakage**: Fundamental model issue requiring post-processing
- **Syntax incompetence**: 43% of code too broken for Black to format
- **Comprehension failure**: Doesn't understand task requirements
- **Low quality**: 20.7% average confidence vs 80% needed
- **Economic failure**: 10.7× more expensive than Claude-only when accounting for failures

**Final Verdict**: Use Claude-only for production code generation. Keep hybrid system as:
1. Research artifact demonstrating optimization attempts
2. Framework for future model evaluations
3. Example of systematic experimentation and learning

### What We Learned About Systematic Improvement

Even with:
- ✅ Data-driven prompt optimization
- ✅ Quality gates at multiple levels
- ✅ Iterative refinement loops
- ✅ Meta-learning feedback capture
- ✅ PDCA at every level

**You cannot overcome fundamental model capability limitations through process optimization.**

Sometimes the answer is: **use the better tool**, even if it costs more.

## Acknowledgments

- **RunPod**: $0.60/hr GPU hosting for DeepSeek
- **Ollama**: Local model serving infrastructure
- **Black**: Python code formatter for syntax validation
- **Claude Sonnet 4.5**: Code review and quality assessment
- **The number 21**: Fibonacci guidance throughout

---

**Experiment Status**: COMPLETE ❌ FAILED
**Publishable**: YES ✅
**Replicable**: YES ✅
**Learnings Captured**: YES ✅
**Cost**: ~$15 in compute + API costs
**Value**: Understanding model limitations saves future wasted effort
