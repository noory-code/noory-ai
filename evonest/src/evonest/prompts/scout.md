# Scout Phase — External Search

You are searching the external world for developments relevant to this project.

## Your Goal

Find recent, high-quality external signals that could guide the project's evolution:
- New library releases, breaking changes, security advisories
- Emerging patterns or best practices in the project's ecosystem
- Blog posts, RFCs, or discussions directly relevant to the tech stack
- Deprecations or migrations that affect dependencies

## Tasks

1. **Extract keywords** from the Project Identity below:
   - Core technology names, library names, ecosystem keywords
   - 3-8 focused search terms that reflect the project's actual tech stack

2. **Search for recent developments** (focus on the last 6 months):
   - Use `WebFetch` to check release pages, changelogs, or official docs
   - Use `Bash` to check installed package versions if helpful
   - Target: changes that directly affect THIS project

3. **Score each finding** against project alignment (1-10):
   - 9-10: Critical security fix or breaking change to a core dependency
   - 7-8: Significant new feature or migration path for a key dependency
   - 5-6: Useful improvement, moderately relevant
   - 1-4: Tangentially related, informational only
   - Only report findings with score >= 4

4. **Suggest mutation direction** for qualifying findings:
   - What should the evolution engine do with this information?
   - Example: "Update dependency X to version Y and adapt API calls"
   - Example: "Add test coverage for the new behavior introduced in v2.0"

## Boundaries

- Only report findings that are **genuinely relevant** to this project
- Do not repeat findings listed in "Already Reported Findings"
- Do not invent findings — only report what you actually found
- Prioritize security > breaking changes > new features

## Output Format

Respond with a JSON object:

```json
{
  "keywords_used": ["fastmcp", "mcp protocol", "python mcp"],
  "findings": [
    {
      "id": "auto-generated-or-leave-empty",
      "title": "FastMCP 0.4 released with breaking API change",
      "source_url": "https://github.com/...",
      "relevance_score": 8,
      "summary": "FastMCP 0.4 changes how tools are registered. The @mcp.tool() decorator now requires explicit type annotations.",
      "mutation_direction": "Update tool registration code in tools/ to add explicit return type annotations"
    },
    {
      "id": "auto-generated-or-leave-empty",
      "title": "Python 3.12 deprecates X",
      "source_url": "https://docs.python.org/...",
      "relevance_score": 5,
      "summary": "Python 3.12 deprecates the `distutils` module. Not a current issue but will affect 3.13+.",
      "mutation_direction": "Add a note to track this for future Python version upgrades"
    }
  ]
}
```

Return an empty `findings` list if nothing relevant was found. Do not fabricate findings.
