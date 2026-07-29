---
id: W-00000085
title: 리뷰어가 카드의 성공 기준에 대고 판정하게 한다
kind: development
venue: codex
priority:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000084
promotion: not_applicable
scope: stage/scripts/drive.py, stage/scripts/tests/, stage/docs/SCHEMA_V4.md, .stage/settings.json, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000085 리뷰어가 카드의 성공 기준에 대고 판정하게 한다

## Purpose

지금 리뷰어는 변경 내용만 받고 그 작업이 무엇을 하기로 한 것인지 모른다. 그래서 "이 코드에서
뭘 더 찾을 수 있나"를 보게 되고, 그 질문에는 끝이 없다. DE-00000032 가 정한 대로 리뷰어에게
카드를 줘서 "성공 기준을 채웠나"를 판정하게 한다.

## Source

DE-00000032 (W-00000084 의 설계 결정). 배경 사례는 그 기록과 W-00000084 카드에 있다.

## User value

리뷰가 끝나는 조건이 생긴다. 기준을 채우면 카드가 닫히고, 기준 밖에서 본 것은 차단 없이
처리 단계로 넘어간다. 지적이 끝없이 쌓여 없던 결함까지 만들던 흐름이 멈춘다.

## Scope

### Included

- `drive.py` 가 리뷰 명령을 부를 때 환경에 `STAGE_WORK_ITEM_PATH` 를 넣는다. 실행하는 쪽에
  이미 넣는 값과 같다(`executor_environment`). 리뷰 호출은 이미 자기 환경을 만들어 쓰므로
  (`prepare_reviewer_index` 가 만든 env) 거기에 더한다.
- `stage/docs/SCHEMA_V4.md` 의 리뷰 명령 계약에 적는다: 리뷰 명령은
  `STAGE_WORK_ITEM_PATH` 를 받는다. 판정은 두 부분이다 — 카드의 `## Success criteria` 에
  대고 기준마다 채웠는지 답하는 기준 판정과, 그 밖에 본 것. 차단(P1)은 기준 판정에서만
  나온다.
- 이 저장소의 `.stage/settings.json` 리뷰 프롬프트를 그 계약에 맞게 바꾼다 — 카드를 읽고
  기준에 대고 판정하고, 기준 밖 관찰은 분리해 내라고.
- 무인 모드에서 기준 밖 관찰이 어디로 가는지 확인하고 결과를 이 카드에 적는다. 무인 모드는
  사람이 그 자리에서 관찰을 읽지 못하므로, 관찰이 소리 없이 사라지면 안 된다.

### Excluded

- 지적 처리(받는다/안 받는다/미룬다)를 스킬 문서에 적는 일 — W-00000086.
- 리뷰어 명령 자체의 교체나 리뷰 강도 정책 변경.

## Dependencies

- W-00000081, W-00000083 이 먼저다. 셋 다 `drive.py` 를 고치므로 순서대로 가야 안 엉킨다.
- DE-00000032 (decided).

## Risks

- 리뷰 명령이 환경 변수를 자식 프로세스에 안 물려주는 형태면 프롬프트가 카드를 못 읽는다.
  이 저장소의 리뷰 명령은 셸 한 줄이라 환경이 그대로 내려가지만, 계약으로는 "환경에 있다"
  까지만 보장하고 프롬프트가 그것을 쓰는 방식은 각 프로젝트의 몫임을 문서에 밝힐 것.
- 기준 판정만 차단이 되면, 기준에 안 적힌 진짜 위험이 차단 없이 흘러간다. 감독 모드에서는
  사람이 관찰을 읽으니 되지만 무인 모드는 확인이 필요하다(위 Included 마지막 항목).

## Success criteria

- 드라이버가 리뷰 명령을 부를 때 환경에 `STAGE_WORK_ITEM_PATH` 가 들어 있고, 그것을 확인하는
  테스트가 있다. 고치기 전 코드에서 실패해야 한다.
- 검증 명령 등 다른 명령의 환경은 달라지지 않는다 — 기존 테스트가 그대로 통과한다.
- `stage/docs/SCHEMA_V4.md` 가 두 부분 판정(기준 판정 + 그 밖에 본 것)과 "차단은 기준
  판정에서만" 을 리뷰 명령 계약으로 적고 있다.
- 이 저장소의 `.stage/settings.json` 리뷰 프롬프트가 그 계약대로 바뀌어 있다.
- 무인 모드에서 기준 밖 관찰이 어떻게 되는지 확인한 결과가 이 카드에 적혀 있다.
- 두 `plugin.json` 의 version 이 올라 있고 `stage/CHANGELOG.md` 에 항목이 있다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 통과.
- `python3 -m unittest discover -s stage/hooks/tests -q` 통과.

## Next action

W-00000081 과 W-00000083 이 닫힌 뒤 `start_work.py` 로 시작한다. scope 는 그때 준다:
`stage/scripts/drive.py, stage/scripts/tests/, stage/docs/SCHEMA_V4.md, .stage/settings.json,
stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json, stage/CHANGELOG.md`.

## Progress

### 무인 모드의 기준 밖 관찰 보존 확인 (2026-07-26)

무인 드라이버는 executor 결과를 커밋한 뒤 `close_via_close_work()` 로 `close_work.py` 를
부르고, 그 안에서 독립 판정을 실행한다. **판정이 통과하면** 명령과 출력은 카드의
`## Verification` 에 `Independent review at close` 블록으로 붙고, 드라이버가 그 카드 변경을
격리 실행 브랜치의 lifecycle 커밋에 넣는다. 마지막에는 사람이 그 브랜치를 검토하고 머지하므로,
이 경로의 기준 밖 관찰은 카드와 함께 인계된다.

보존되는 출력에는 명시적 상한이 있다. `close_work.py` 는 판정 출력의 마지막 40줄·4000바이트를
남기고, 앞부분을 잘랐으면 생략된 줄 수를 표시한다. 계약이 기준 밖 관찰을 두 번째 부분으로
요구하므로 이 관찰은 끝부분에 놓여 우선 보존되지만, 관찰 자체가 상한보다 길면 앞쪽 관찰은
잘릴 수 있다. 그 경우에도 생략 표시는 남으므로 조용한 소실은 아니며, 사람 머지 검토에서 원본
판정 출력 재확인이 필요하다는 신호가 된다.

**기준 판정이 P1 또는 명령 실패로 차단되면 기준 밖 관찰이 조용히 사라질 수 있다.**
`close_work.py` 는 실패 판정에서 카드를 바꾸지 않고 판정 출력을 호출자에게 돌려준다. 그런데
`run_unattended()` 는 그 출력을 `_close_out` 으로 받은 뒤 쓰지 않고
`close failed (acceptance or independent review)` 라는 일반 이유만 남긴다. 재시도나
에스컬레이션에도 원문을 카드에 옮기지 않는다. 따라서 통과 경로는 보존되지만 차단 경로는
보존되지 않는다. 이 카드는 확인만 scope 에 두었으므로 여기에는 사실을 기록하고 구현 범위를
넓혀 고치지 않는다.

## Verification

### 구현 검증 (2026-07-26)

- RED — `test_execute_passes_selected_work_item_path_to_reviewer` 를 구현 전에 실행했고,
  리뷰어 자식 프로세스에서 `KeyError: 'STAGE_WORK_ITEM_PATH'` 가 나며 종료 코드 1로 실패했다.
- focused GREEN — 구현 뒤 같은 테스트가 1개 통과했고, `test_drive.py` 전체 33개도 통과했다.
- full GREEN — `python3 -m unittest discover -s stage/scripts/tests -q` 346개,
  `python3 -m unittest discover -s stage/hooks/tests -q` 327개가 통과했다.
- 구조 검증 — 두 manifest와 `.stage/settings.json` 이 유효한 JSON이고 `git diff --check` 가
  통과했다.
- Stage 감사 — `python3 stage/scripts/audit_stage.py --project-root .` 결과
  `errors=0, warnings=0`.

### 기준 판정 — 반대 venue (Claude), DE-00000032 방식 (2026-07-26)

- 리뷰 환경에 `STAGE_WORK_ITEM_PATH` 가 있고 테스트가 고치기 전 실패한다 — 채움. RED 는
  실행자 보고와 별개로 저장소 밖 사본(0.43.10 코드)에서 직접 재현했다.
- 다른 명령의 환경은 안 바뀐다 — 채움. acceptance 는 드라이버 변수를 하나도 안 받고,
  리뷰어는 `STAGE_WORK_ITEM_PATH` 와 실행하는 쪽 임시 인덱스만 받는다. `SCHEMA_V4.md` 가
  이 경계를 명시하고, 기존 환경 테스트가 전부 통과한다.
- `SCHEMA_V4.md` 가 두 부분 판정(기준 판정 + 기준 밖 관찰)과 "P1 은 기준 실패에서만" 을
  리뷰 계약으로 적고 있다 — 채움.
- 이 저장소의 리뷰 프롬프트가 계약대로다 — 채움. 프롬프트를 가진 두 명령(claude, red-team)
  모두 카드를 읽고 기준마다 PASS/FAIL 을 내고 관찰을 분리한다. codex 기본 리뷰는 프롬프트
  자리가 없어 계약을 못 받는다 — 아래 관찰로 넘긴다.
- 무인 모드의 기준 밖 관찰 확인 결과가 카드에 있다 — 채움(위 Progress 절). 확인이 실제
  구멍 하나를 찾았다 — 아래 관찰.
- 버전 0.43.11, CHANGELOG 항목, 테스트 두 벌(346/327), 감사 0 — 채움.

### 그 밖에 본 것 (기준 밖 관찰)

- codex 기본 리뷰(`review --wait`)는 프롬프트 자리가 없어 기준 판정 계약을 못 받는다 —
  처리: 미룬다 → W-00000087. claude venue 카드를 드라이버로 돌리기 시작할 때가 시점이다.
- 무인 모드에서 차단된 리뷰 판정의 출력이 버려진다(`_close_out` 미사용) — 처리: 미룬다 →
  W-00000088. 무인 모드를 실제로 쓰기 시작할 때 고친다.
- 받지 않은 지적 없음, 차단할 지적 없음.

### Executed at close — 2026-07-26

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (25 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1785040300 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1785040300
Outcome: blocked — parent aggregation-close failed: W-00000001: parent close failed: boom; handoff on stage/driver/W-00000001-1785040300
Recommended next action: attempt cap reached / no progress / global limit exceeded → escalate_work
Unattended run on isolated branch: stage/driver/W-00000001-1785040300 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1785040300
[W-00000003] completed on stage/driver/W-00000001-1785040300
Unattended run finished: 2 item(s) closed on isolated branch stage/driver/W-00000001-1785040300. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785040301 (base: main)
Outcome: blocked — cannot commit pre-close lifecycle for W-00000002: simulated lifecycle commit failure
Recommended next action: attempt cap reached / no progress / global limit exceeded → escalate_work
Outcome: blocked — unattended mode requires a `limits` config (absent is not unlimited here); refusing to run
Recommended next action: attempt cap reached / no progress / global limit exceeded → escalate_work
Unattended run on isolated branch: stage/driver/W-00000001-1785040301 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785040301. Human review + merge required; the base branch was not modified.
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 migration complete with no blocking audit findings. Guidance drift remains a non-blocking audit warning until the explicit refresh command is run.
All migration changes are staged; this command does not commit. Review them, then commit with: git commit -m "chore(stage): migrate project harness to schema v4"
Before committing, `migrate_stage.py --abort` restores the staged/working tree. After committing, rollback means `git revert <migration-commit>`.
Stage project already uses schema v4; no migration needed.
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 migration complete with no blocking audit findings. Guidance drift remains a non-blocking audit warning until the explicit refresh command is run.
All migration changes are staged; this command does not commit. Review them, then commit with: git commit -m "chore(stage): migrate project harness to schema v4"
Before committing, `migrate_stage.py --abort` restores the staged/working tree. After committing, rollback means `git revert <migration-commit>`.
----------------------------------------------------------------------
Ran 346 tests in 37.893s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 327 tests in 0.908s

OK

$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

R-00000084. 핵심: 리뷰의 질문이 "기준을 채웠나" 로 닫혔고, 이번 카드의 검증 자체가 그
방식(기준 판정 + 관찰 분리 + 미룸 카드화)의 두 번째 실전 적용이었다.

## Promotion decision

official 로 올릴 산출물 없음(promotion: not_applicable). 계약의 SSOT 는 이미 승격된
DE-00000032 다. 카드와 회고는 아카이브로 간다.
