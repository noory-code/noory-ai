---
id: W-00000062
title: 은퇴한 bug 종류의 검증 기준 한 줄 추가
kind: documentation
venue: claude
source:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000061
promotion: not_applicable
review: not_required
scope: .stage/operations/verification.md
promotes:
decision_refs:
---

# W-00000062 은퇴한 bug 종류의 검증 기준 한 줄 추가

## Purpose

보관된 기록 하나가 쓰는 bug 종류에 기준이 없어 검사 경고가 영구히 켜져 있다

## Scope

`operations/verification.md`의 종류별 기준 표에 `bug` 한 줄. 보관된 기록은 건드리지 않는다 —
증거이므로 사후 수정 대상이 아니다.

## Success criteria

- 검사에 경고가 남지 않는다.

## Related truth

`operations/verification.md`는 `settings.json`의 `guidance_overrides`에 선언돼 있다. 이 프로젝트가
직접 쓴 문서이므로 갱신 명령이 덮지 않는다(DE-00000029).

## Progress

`bug`는 보관된 기록 하나(W-00000040)에서만 쓰였다. 지금 쓰는 이름은 `fix`이고 라우팅 정책에도
`bug`는 없다. 종류 이름이 정리되기 전의 흔적이다.

보관된 기록은 고칠 수 없으므로 표에 한 줄을 더했다 — 은퇴한 이름이고, 새 작업은 `fix`를 쓰며,
이 종류를 쓰는 기록은 `fix`와 같은 기준으로 읽는다.

경고를 그냥 두는 쪽은 택하지 않았다. 늘 켜져 있는 경고는 다음부터 아무도 보지 않게 만든다.

## Verification


### Executed at close — 2026-07-25

```
$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective


## Promotion decision
