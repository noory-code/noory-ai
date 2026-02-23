---
name: personas
description: List all personas and adversarials with enabled/disabled status, or toggle them on/off
allowed-tools:
  - mcp: evonest_personas
---

Use the `evonest_personas` MCP tool to list all available personas and adversarials.

- To list all: `evonest_personas(project="$PROJECT", action="list")`
- To disable: `evonest_personas(project="$PROJECT", action="disable", ids=["persona-id"])`
- To enable: `evonest_personas(project="$PROJECT", action="enable", ids=["persona-id"])`
- To filter by group: `evonest_personas(project="$PROJECT", action="list", group="biz")`

Show the results to the user clearly, highlighting which personas are enabled vs disabled.
