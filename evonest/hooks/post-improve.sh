#!/usr/bin/env bash
# PostToolUse hook: auto-chain evonest improve when proposals remain.
#
# Reads JSON from stdin (Claude Code hook protocol), extracts the `project`
# argument from the tool_input, checks for pending proposals, and instructs
# Claude to run the next improve if any exist.

set -euo pipefail

input=$(cat)

# Extract project path from tool_input.project
project=$(echo "$input" | jq -r '.tool_input.project // empty')
if [[ -z "$project" ]]; then
  exit 0
fi

# project is already an absolute path
proposals_dir="${project}/.evonest/proposals"

if [[ ! -d "$proposals_dir" ]]; then
  exit 0
fi

# Count pending proposals (*.md files not in done/)
pending=$(find "$proposals_dir" -maxdepth 1 -name "*.md" | wc -l | tr -d ' ')

if [[ "$pending" -gt 0 ]]; then
  echo "{\"systemMessage\": \"evonest improve completed. There are still $pending pending proposals. Run /evonest:improve again to process the next one.\"}"
fi
