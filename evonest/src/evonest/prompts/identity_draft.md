You are helping initialize a new Evonest project. Your task is to read the project files in the current directory and produce a complete `identity.md` draft.

## Instructions

1. Explore the project by reading relevant files. Look for:
   - `README.md` — project description, goals, philosophy, tech stack
   - `pyproject.toml` — name, description, version, dependencies, tool config (mypy, ruff, pytest)
   - `package.json` — name, description, version, dependencies, scripts
   - `Cargo.toml` — name, description, dependencies
   - `CONTRIBUTING.md` — development principles, scope, non-goals
   - `CHANGELOG.md` or `CHANGELOG` — latest version, what shipped
   - `ROADMAP.md` — current focus, upcoming work
   - `LICENSE` or `LICENSE.md` — license type (MIT, Apache, GPL, etc.)
   - `CLAUDE.md` — development guide, commands, conventions
   - `Makefile` — build/test/lint commands
   - `.github/workflows/` — CI/CD checks, test/build commands

2. Based on what you find, fill in the identity.md template below. Skip any section you cannot find good information for — leave it as the placeholder comment.

3. Output ONLY the raw markdown content of identity.md. **CRITICAL rules:**
   - Do NOT include ANY preamble (e.g. "Here's the draft:", "Perfect.", "Sure!")
   - Do NOT wrap the output in code fences (``` or ~~~)
   - Start your output DIRECTLY with `# Project Identity`
   - End your output DIRECTLY after the last section content

## identity.md Template

The template below is shown inside code fences for formatting only. Your output must NOT include these fences.

```
# Project Identity

## Mission
<!-- What does this project do? One sentence. -->
[Fill from README description or pyproject.toml/package.json description field]

## Core Values
<!-- 3-5 principles that guide every development decision. -->
- [Fill from CONTRIBUTING.md, README philosophy/principles section, or infer from tool config]
-
-

## Current Phase
<!-- Where is the project right now? What's the focus? -->
[Fill from CHANGELOG latest entry, ROADMAP current section, or package version]

## Quality Standards
<!-- Hard requirements that must hold at all times. -->
- [Fill from Makefile test target, pyproject.toml [tool.pytest], CI workflow test step]
- [Fill from pyproject.toml [tool.mypy] or [tool.ruff]]

## Product Direction (optional)
<!-- Where is this heading? What trade-offs matter? -->
[Fill from README vision/goals section, ROADMAP, or LICENSE type (open source vs commercial)]

## Ecosystem (optional)
<!-- Tech stack and key dependencies. -->
[Fill from pyproject.toml dependencies, package.json dependencies, or README requirements]

Key dependencies:
[List key dependencies with their roles]

## Boundaries (DO NOT touch)
<!-- Files, directories, or patterns Evonest must never modify. -->
- .evonest/
[Add any generated files, migration dirs, config/secrets found in .gitignore or README]
```

Now explore the project and produce the filled identity.md.
