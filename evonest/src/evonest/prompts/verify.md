# Verify Phase — Evonest

You are verifying that the executed changes are correct and don't break anything.

## Your Goal

Run build + tests, verify the changes work, and determine if they should be committed or reverted.

## Tasks

1. **Run build**: Execute the project's build command
   - Must complete with zero errors
   - Warnings are acceptable but note them

2. **Run tests**: Execute the project's test suite
   - All tests must pass
   - Note any new tests added

3. **Verify changes**:
   - Run `git diff` to review what changed
   - Are the changes clean and focused?
   - Any accidental modifications to unrelated files?

4. **Determine verdict**: pass or fail

## Output Format

```json
{
  "success": true,
  "build": {
    "status": "passed",
    "errors": 0,
    "warnings": 0
  },
  "tests": {
    "total": 120,
    "passed": 120,
    "failed": 0,
    "new_tests": 2
  },
  "changes": {
    "files_modified": ["tests/parser.test.ts"],
    "lines_added": 45,
    "lines_removed": 0
  },
  "commit_message": "test(parser): add edge case tests for empty input and duplicate entries",
  "notes": []
}
```

If verification fails:
```json
{
  "success": false,
  "reason": "2 tests failing in parser.test.ts",
  "details": "...",
  "commit_message": null
}
```

## Decision Rules

- **PASS** if: build succeeds AND all tests pass AND changes are clean
- **FAIL** if: build fails OR any test fails OR unrelated files were modified
- Commit message format: `type(scope): description`
  - types: feat, fix, refactor, test, docs, chore
  - Include `Co-Authored-By: Evonest <noreply@evonest.dev>` at the end
