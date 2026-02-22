# evonest

Use this skill when the user asks to **analyze**, **improve**, or **evolve** a project with evonest, or when they mention:
- "run evonest", "analyze my code", "find improvements"
- "execute a proposal", "apply a proposal", "improve my project"
- "run a full evolution cycle", "evolve my code"
- "show proposals", "list proposals"
- "evonest status", "evonest history"

## Available MCP Tools

All tools take `project` (absolute path) as their first argument.

| Tool | When to use |
|------|-------------|
| `evonest_init` | First time setup — creates `.evonest/` in the target project |
| `evonest_analyze` | Scan and save ALL improvements as proposals (no code changes) |
| `evonest_improve` | Execute one proposal (no Observe/Plan — uses proposal as the plan) |
| `evonest_evolve` | Full cycle: Observe → Plan → Execute → Verify → commit/PR |
| `evonest_status` | Show project status summary |
| `evonest_proposals` | List pending proposals |
| `evonest_history` | Show cycle history |
| `evonest_config` | Read or update `.evonest/config.json` |
| `evonest_identity` | Read or write `.evonest/identity.md` |
| `evonest_backlog` | Manage the improvement backlog |
| `evonest_stimuli` | Add a stimulus (external input for the next observe cycle) |
| `evonest_decide` | Record a human decision (constrains LLM proposals) |
| `evonest_progress` | Show progress report |

## Typical Workflows

### First time on a new project
1. `evonest_init(project)` — initialize `.evonest/`
2. `evonest_identity(project)` — show the identity template, ask the user to fill it in
3. `evonest_analyze(project)` — run first analysis

### Analyze → review → improve loop
1. `evonest_analyze(project)` — generates proposals
2. `evonest_proposals(project)` — show proposals to user
3. User picks one → `evonest_improve(project, proposal_id=...)` — execute it

### Fully autonomous evolution
1. `evonest_evolve(project, cycles=3)` — run 3 full cycles

### Cautious mode (review before executing)
1. `evonest_evolve(project, cautious=True)` — pauses after Plan
2. Show plan summary to user, ask: "Proceed? [y/N]"
3. Yes → `evonest_evolve(project, resume=True)`
4. No → `evonest_evolve(project, resume=False)`

## Key Notes

- **`analyze` does NOT modify code** — it only saves proposals to `.evonest/proposals/`
- **`improve` requires existing proposals** — run `analyze` first if none exist
- **`evolve` is the full pipeline** — combines observe + plan + execute + verify in one call
- **identity.md matters** — the richer the project identity, the better the proposals
- The `project` path must be **absolute** (not relative)
