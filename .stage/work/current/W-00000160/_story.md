---
id: W-00000160
title: 다른 도구가 저장소에 깔아 둔 Copilot 지침을 지운다
kind: chore
venue: codex
milestone:
source:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000160
promotion: not_applicable
review: not_required
scope: .github/
promotes:
decision_refs:
---

# W-00000160 다른 도구가 저장소에 깔아 둔 Copilot 지침을 지운다

## Purpose

MermaidChart 서버가 연결되면서 우리가 안 쓰는 Copilot 지침 파일 둘을 저장소에 썼다

## Actions


## Scope


## Success criteria


## Related truth


## Progress


## Verification


### Executed at close — 2026-07-30

```
$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective


## Promotion decision
