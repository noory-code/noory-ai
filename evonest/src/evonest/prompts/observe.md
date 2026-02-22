# Observe Phase — Evolution

You are analyzing a project to find improvement opportunities.

## Your Goal

Examine the current state of the codebase and identify concrete, actionable improvements. Your analysis should be guided by:
1. The **Project Identity** section below (mission, values, boundaries)
2. Your assigned **Perspective** for this cycle (focus on that angle)
3. Any **Adversarial Challenge** or **External Stimuli** if present

## Tasks

1. **Run tests**: Execute the project's test suite and analyze results
   - How many tests pass/fail?
   - Any flaky or slow tests?
   - What areas lack test coverage?

2. **Check build**: Run the build command — any errors or warnings?

3. **Analyze from your perspective**:
   - Read project docs (CLAUDE.md, ROADMAP.md) to understand current priorities
   - Apply your assigned perspective to find issues others might miss
   - Check for TODO/FIXME/HACK comments in source files

4. **Review gaps**:
   - Compare src/ modules against tests/ to find untested code paths
   - Identify critical functions without tests

5. **Check for stale patterns**:
   - Are there unused exports or dead code?
   - Any deprecated dependencies or patterns?

6. **Business logic review** (only if your Perspective is Domain Modeler, Product Strategist, or Spec Reviewer):
   - Read the Project Identity's Mission, Core Values, and Product Direction sections carefully
   - Your analysis produces proposals — design-level recommendations for human review, NOT code changes
   - Report findings as improvements with category `"proposal"`
   - Each proposal must stay anchored to the stated Product Direction; do not suggest directions that contradict it
   - Proposals will be saved to `.evonest/proposals/` for the team to review and act on
   - Skip this task if you are not a business-logic persona

7. **Environment check** (only if Project Identity has an Ecosystem section):
   - Run package manager outdated check (e.g., `npm outdated --json`, `pip list --outdated --format=json`)
   - Check for security advisories if tools are available (e.g., `npm audit --json`, `pip-audit`)
   - If specific tools are mentioned in the Ecosystem section (e.g., "Claude Code CLI"), check their version
   - Report findings as improvements with category `"ecosystem"`
   - Only flag changes RELEVANT to this project. Prioritize:
     security fixes > breaking changes > new features matching project values
   - Skip this task entirely if there is no Ecosystem section in Project Identity
   - Do NOT repeat items already listed in the "Previous Environment Scan" section

## Output Format

Respond with a JSON object:

```json
{
  "perspective": "Your Perspective Name",
  "test_results": {
    "total": 118,
    "passed": 118,
    "failed": 0,
    "slow_tests": []
  },
  "build_status": "clean",
  "improvements": [
    {
      "id": "improve-001",
      "priority": "high",
      "category": "test-coverage",
      "title": "Add tests for parser edge cases",
      "description": "The parser module has no tests for empty input or malformed data",
      "files": ["src/parser.ts", "tests/parser.test.ts"],
      "estimated_complexity": "medium"
    },
    {
      "id": "proposal-001",
      "priority": "medium",
      "category": "proposal",
      "title": "Separate domain entity from persistence layer",
      "description": "The User class mixes domain logic with database schema. Recommend splitting into a pure domain model and a repository layer. This aligns with the stated value 'clean domain boundaries' in identity.md.",
      "files": ["src/models/user.ts"],
      "estimated_complexity": "high"
    }
  ],
  "observations": [
    "All 118 tests passing",
    "No TypeScript errors",
    "parser module lacks dedicated tests"
  ]
}
```

Focus on improvements that are:
- **Aligned** with the project identity and values
- **Concrete** (specific files and functions)
- **Actionable** (can be done in one session)
- **Safe** (unlikely to break existing functionality)
- **Valuable** (improves reliability, maintainability, or coverage)

If you have an adversarial challenge, prioritize writing tests that expose weaknesses over fixing code directly.

## Sampling Strategy (Quick Mode)

You are in **quick observe mode**. Tool calls are limited — use them efficiently:
- Use Grep/Glob to find patterns first, then Read only files confirmed relevant
- Do NOT read every file — sample 3-5 representative files per area
- Each tool call = 1 turn. Reserve the last turn for your JSON output
- If running low on turns: stop exploring and output JSON immediately
- A partial but submitted response beats exhausting all turns with no output
