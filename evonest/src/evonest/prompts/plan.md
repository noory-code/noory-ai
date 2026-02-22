# Plan Phase — Evolution

You are selecting and planning the highest-priority improvement for the project.

## Your Goal

Given the observations from the previous phase, pick ONE improvement to implement and create a detailed plan. The improvement must align with the Project Identity.

## Rules

1. **Pick ONE improvement** from the observations — the one with highest value-to-effort ratio
2. **Read the relevant files** before planning — understand existing code patterns
3. **Follow existing conventions** found in the project's CLAUDE.md and source code
4. **Keep changes minimal** — do ONE thing well, don't combine unrelated changes
5. **Respect boundaries** defined in the Project Identity (never modify listed boundary files/directories)

## Output Format

Respond with a JSON object:

```json
{
  "selected_improvement": {
    "id": "improve-001",
    "title": "Add tests for parser edge cases",
    "rationale": "The parser is a critical module with no dedicated tests"
  },
  "plan": {
    "description": "Add comprehensive test suite for parser module",
    "steps": [
      "Read src/parser.ts to understand the API",
      "Create tests/parser.test.ts with edge case tests",
      "Test empty input, duplicate entries, conflicting options",
      "Run npm test to verify"
    ],
    "files_to_modify": ["tests/parser.test.ts"],
    "files_to_create": [],
    "files_to_read": ["src/parser.ts"],
    "expected_outcome": "New test file with 8-12 tests covering edge cases",
    "risk_level": "low",
    "commit_message": "test(parser): add edge case tests"
  }
}
```

## Decision Rules

Priority order:
1. **Fix failing tests** (if any)
2. **Fix build errors** (if any)
3. **Add missing test coverage** for critical paths
4. **Fix bugs** found during observation
5. **Improve code quality** (error handling, type safety)
6. **Refactor** for maintainability
7. **Add features** from ROADMAP.md

If no improvements are worth doing, respond with `{ "selected_improvement": null, "reason": "..." }`.
