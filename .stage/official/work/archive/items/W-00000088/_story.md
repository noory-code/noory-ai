---
id: W-00000088
title: 무인 모드에서 차단된 리뷰 판정 출력을 보존한다
kind: development
venue: codex
priority:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
  - "python3 -m unittest discover -s stage/hooks/tests -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000087
promotion: not_applicable
scope: stage/scripts/drive.py, stage/scripts/tests/, stage/docs/SCHEMA_V4.md, stage/skills/stage-drive/, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000088 무인 모드에서 차단된 리뷰 판정 출력을 보존한다

## Purpose

무인 드라이버에서 리뷰 판정이 통과하면 출력이 카드의 `## Verification` 에 남는데, P1 이나
명령 실패로 차단되면 `run_unattended()` 가 받은 판정 출력(`_close_out`)을 버리고 일반 실패
사유만 남긴다. 막힌 이유일수록 근거가 남아야 하는데 지금은 통과한 쪽만 남는다. 사람이 이유를
보려면 판정을 다시 돌려야 한다.

## Source

W-00000085 가 카드 Progress 에 기록한 무인 모드 조사 (처리: 미룬다). 상세는 그 카드.


## User value

무인 모드에서 리뷰가 막았을 때 사람이 그 자리에서 이유를 읽는다. 지금은 통과한 이유는 남고
막힌 이유는 사라지므로, 실패할수록 다시 돌려 봐야 하는 깜깜이가 된다. 무인 모드를 실전에
쓰려면 이것부터 있어야 한다.

## Scope

### Included

- `run_unattended()` (`drive.py`): 닫기가 검증 실패나 리뷰 차단으로 실패하면, `close_work.py`
  가 돌려준 출력(지금 `_close_out` 으로 받고 버리는 것)을 보존한다 — 통과 경로가 쓰는 것과
  같은 상한(마지막 40줄·4000바이트, 잘리면 생략 표시)으로 잘라 에스컬레이션 기록에 넣는다.
  재시도 후 다시 실패해도 마지막 출력이 남아야 한다.
- `stage/docs/SCHEMA_V4.md` 의 무인 루프 설명에 이 보존을 적는다.
- `stage/skills/stage-drive/SKILL.md` 의 무인 모드 상태 문단을 현재 사실로 바로잡는다 —
  "알려진 결함 열림(W-00000075)" 은 낡았다(그 카드는 고쳐져 아카이브됨). 지금 사실: 코드
  결함은 닫혔고, 실제 작업을 끝까지 돌린 적이 없다는 경고는 유지한다.

### Excluded

- 감독 모드 경로 — 사람이 그 자리에서 출력을 읽으므로 해당 없음.
- 리뷰 명령·계약 변경 — DE-00000032 소유.

## Dependencies

- 없음 (W-00000087 과 독립).

## Risks

- 에스컬레이션 기록이 커진다 — 상한이 이미 있으므로 통과 경로와 같은 크기로 묶인다.
- 출력에 개행·특수문자가 섞여 기록 형식을 깨뜨릴 수 있다 — 통과 경로가 이미 같은 출력을
  카드에 넣고 있으므로 같은 처리 방식을 쓴다.

## Success criteria

- 무인 모드에서 닫기가 리뷰 차단으로 실패하면, 차단 사유가 된 판정 출력(상한 적용)이
  에스컬레이션 기록에 남는다. 그것을 확인하는 테스트가 있고 고치기 전 코드에서 실패한다.
- 검증(acceptance) 실패로 닫기가 실패한 경우도 같은 방식으로 남는다.
- 통과 경로는 그대로다 — 기존 테스트가 전부 통과한다.
- `SCHEMA_V4.md` 가 차단 출력 보존을 무인 루프 계약으로 적고 있다.
- `stage-drive` 의 무인 모드 상태 문단이 현재 사실과 일치한다 — W-00000075 를 열린 결함으로
  말하지 않고, 실전 미검증 경고는 유지한다.
- 두 `plugin.json` 의 version 이 올라 있고 `stage/CHANGELOG.md` 에 항목이 있다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 통과.
- `python3 -m unittest discover -s stage/hooks/tests -q` 통과.

제약:

- **커밋하지 않는다.** 작업 트리에 변경만 남기고 멈춘다.
- 저장소 산출물은 영어로 쓴다. `.stage/` 안의 글만 한국어다.
- scope 밖은 건드리지 않는다.

## Next action

드라이버(감독 모드)로 돌린다 — W-00000082 가 열어 준 단일 카드 대상의 첫 실전이다:
`python3 stage/scripts/drive.py --project-root . --execute W-00000088`

## Progress

### 드라이버 첫 실전 가동으로 돌았다 (2026-07-26)

이 카드가 W-00000082 이후 처음으로 드라이버가 카드 하나를 직접 받아 돌린 실전이다. 실행
(codex) → 검증 두 벌 재실행 → 반대 venue 리뷰까지 한 스텝에 자동으로 이어졌고, 실행과 검증은
정상이었다.

리뷰 단계에서 구멍 둘이 실전으로 드러났다 (아래 Verification 의 기준 밖 관찰):

- 리뷰어(`claude -p`)가 입력이 너무 커서 리뷰를 못 하고 오류만 냈는데, 오류 문구에 "[P1]" 이
  없어 래퍼가 통과로 처리했다. 리뷰 없는 통과다.
- 입력이 커진 원인: 드라이버를 Claude 세션 안에서 돌리면 세션 식별 환경 변수가 리뷰어에게
  물려 내려가, 리뷰어가 diff(34KB)가 아니라 세션 대화(약 216만 토큰)를 끌고 들어간다.
  어느 변수가 정확한 원인인지는 아직 확인 전이다.

## Verification

리뷰어가 실제로는 리뷰하지 못했으므로(위 Progress), 반대 venue 리뷰는 Claude 가 직접 했다.
DE-00000032 방식.

### 기준 판정 (2026-07-26)

- 리뷰 차단으로 닫기가 실패하면 판정 출력이 에스컬레이션 기록에 남는다 — 채움. 통과 경로와
  같은 상한을 `close_work` 의 `clip` 재사용으로 적용(SSOT). 재시도 후에는 마지막 출력만
  남는 것까지 테스트가 검사한다.
- 검증 실패로 닫기가 실패한 경우도 같은 방식 — 채움. 별도 테스트 있음.
- 두 테스트가 고치기 전 코드에서 실패한다 — 확인. 저장소 밖 사본(0.43.13)에서 직접 재현했다.
- 통과 경로 그대로 — 채움. 드라이버 스텝의 acceptance 로 scripts 356개, hooks 327개 통과.
- `SCHEMA_V4.md` 가 차단 출력 보존을 무인 루프 계약으로 적고 있다 — 채움.
- `stage-drive` 무인 모드 상태 문단이 현재 사실과 일치한다 — 채움. W-00000075 는 닫힌
  결함으로, 실전 미검증 경고는 유지.
- 버전 0.43.14, CHANGELOG 항목 — 채움.

### 그 밖에 본 것 (기준 밖 관찰)

- 리뷰어 래퍼가 리뷰 실패를 통과로 처리한다 — 처리: 받는다 → 새 카드로 등록한다. 합격
  표식(APPROVED)이 있어야 통과, 없으면 차단으로 뒤집어야 한다. 리뷰어를 못 쓰는 상황(비용·
  사용량 한계)의 폴백 설계 물음도 이 카드가 답한다: 폴백은 자동 대체가 아니라 차단 후 사람
  인계다.
- 드라이버를 Claude 세션 안에서 돌리면 세션 환경이 리뷰어에게 샌다 — 처리: 받는다 → 새
  카드로 등록한다. 원인 변수 확인부터.

### Executed at close — 2026-07-26

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (34 earlier lines omitted)
Unattended run finished: 2 item(s) closed on isolated branch stage/driver/W-00000001-1785043259. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785043259 (base: main)
[W-00000001] completed on stage/driver/W-00000001-1785043259
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1785043259. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785043260 (base: main)
Outcome: blocked — cannot commit pre-close lifecycle for W-00000002: simulated lifecycle commit failure
Recommended next action: attempt cap reached / no progress / global limit exceeded → escalate_work
Outcome: blocked — unattended mode requires a `limits` config (absent is not unlimited here); refusing to run
Recommended next action: attempt cap reached / no progress / global limit exceeded → escalate_work
Unattended run on isolated branch: stage/driver/W-00000001-1785043260 (base: main)
[W-00000002] close failed (acceptance or independent review); close_work output:
obsolete first review output; retry 1/2
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785043260. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1785043261 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1785043261. Human review + merge required; the base branch was not modified.
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
Ran 356 tests in 42.418s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 327 tests in 0.958s

OK

$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

R-00000087. 핵심: 드라이버 첫 실전이 카드 자체의 수정을 성공시키면서 리뷰 단계의 구멍 둘을
즉시 드러냈다 — 실전 가동이 곧 검증이었다.

## Promotion decision

official 로 올릴 산출물 없음(promotion: not_applicable). 카드와 회고는 아카이브로 간다.
