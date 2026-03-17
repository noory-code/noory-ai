# Privacy Policy

**Evonest** is a Claude Code plugin that operates entirely on your local machine.

## Data Collection

Evonest does **not** collect, transmit, or store any data on external servers. There is no telemetry, analytics, or usage tracking.

## How Data Is Stored

All Evonest data is stored locally in the `.evonest/` directory within your project:

| File | Purpose |
|------|---------|
| `config.json` | Engine configuration (turn limits, verify commands) |
| `identity.md` | Project identity document |
| `proposals.json` | Analysis proposals and execution history |
| `dynamic-personas.json` | Runtime-generated personas |
| `dynamic-adversarials.json` | Runtime-generated challenges |

You have full control: delete `.evonest/` to remove all Evonest data from a project.

## Code Execution Safety

Evonest modifies code in your local repository only. Safety mechanisms:
- **Git stash checkpoint** before every code change
- **Auto-revert** on test/build failure
- **Lock file** prevents concurrent execution
- **Turn limits** cap resource usage per phase

## Third-Party Services

Evonest does not integrate with or send data to any third-party services. It uses `claude -p` subprocess calls which route through your existing Claude subscription.

## Changes to This Policy

Updates will be documented in the [CHANGELOG](./CHANGELOG.md) and reflected in the plugin version.

## Contact

For questions, open an issue at [github.com/noory-code/noory-ai](https://github.com/noory-code/noory-ai/issues).

---

*Last updated: 2026-03-17 | Evonest v1.0.2*
