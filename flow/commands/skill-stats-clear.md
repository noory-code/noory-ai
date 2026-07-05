---
description: Clear ~/.claude/skill-usage.jsonl (with confirmation)
---

# /skill-stats-clear

You reset the `~/.claude/skill-usage.jsonl` log (keep the file itself, just empty it — so the hook can keep appending).

## Procedure

1. Check the file status:
   ```bash
   if [ -f "$HOME/.claude/skill-usage.jsonl" ]; then
     lines=$(wc -l < "$HOME/.claude/skill-usage.jsonl")
     size=$(wc -c < "$HOME/.claude/skill-usage.jsonl")
     echo "Current log: ${lines} lines, ${size} bytes"
   else
     echo "No log file. Nothing to reset."
     # exit
   fi
   ```
2. Output to the user:
   ```
   Current log: <N> lines, <X> bytes
   Really empty it? Please answer "yes".
   ```
3. Wait for the user's response.
4. If the response is not exactly `yes` (case-sensitive):
   - Print "Cancelled" and exit.
5. If `yes`:
   - Bash: `: > "$HOME/.claude/skill-usage.jsonl"` (truncate)
   - Print "Reset complete. Recording resumes from the next invocation."

## Safety guards

- No file deletion (`rm`) — truncate only.
- Does not touch any other file / directory.
- If a backup option is needed, the user should run `cp ~/.claude/skill-usage.jsonl ~/skill-usage-backup.jsonl` beforehand, then run this.
