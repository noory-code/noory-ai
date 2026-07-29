---
id: W-00000089
title: 리뷰어가 리뷰를 못 했는데 통과로 끝난다
kind: fix
venue: codex
priority:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000088
promotion: not_applicable
scope: stage/docs/SCHEMA_V4.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json, stage/CHANGELOG.md, .stage/settings.json
promotes:
decision_refs:
---

# W-00000089 리뷰어가 리뷰를 못 했는데 통과로 끝난다

## Purpose

2026-07-26, W-00000088 드라이버 실전 첫 가동에서 실제로 났다. 리뷰어(`claude -p`)가 입력
초과로 리뷰를 못 하고 오류 문구만 냈는데, 래퍼는 "[P1] 이 있으면 차단" 만 보므로 오류를
통과로 처리했다. W-00000083(실행하는 쪽의 무변경 성공)과 같은 병의 리뷰어판이다: 부정
표식이 없다고 합격이 아니라, **합격 표식(APPROVED)이 있어야 합격**으로 뒤집어야 한다.

리뷰어를 못 쓰는 상황(비용·사용량 한계·CLI 오류)의 폴백 설계 물음에 대한 답이기도 하다:
폴백은 자동 대체나 건너뛰기가 아니라 **차단 후 사람 인계**다. 지금은 그 상황이 조용히
통과라서 폴백 이전에 감지부터 안 된다.

## Source

W-00000088 검증의 기준 밖 관찰 (처리: 받는다). 리뷰 계약의 SSOT 는 DE-00000032.


## User value

리뷰어가 죽거나(사용량 한계, 입력 초과, CLI 오류) 판정 없이 끝나면 그 스텝이 차단으로
멈추고 사람에게 넘어온다. 지금은 조용히 통과라서, 리뷰가 있는 줄 알았는데 없는 상태가 된다.

## Scope

### Included

- `.stage/settings.json` 의 리뷰 명령 셋(claude 리뷰어, standard/red-team 강도) 전부를
  fail-closed 로: CLI 가 0 이 아니게 끝나거나 출력에 판정 표식([P1] 또는 APPROVED)이 하나도
  없으면 `BLOCK:` 을 내고 종료 코드 1 로 끝난다. "[P1] 있으면 차단" 은 유지하고, "표식이
  아예 없으면 차단" 을 더한다.
- `stage/docs/SCHEMA_V4.md` 의 리뷰 명령 계약에 적는다: 판정을 낼 수 없는 리뷰 명령은
  성공으로 끝나면 안 된다 — 0 이 아닌 종료 코드나 `BLOCK:` 으로 실패해야 한다.

### Excluded

- codex 리뷰어에 계약 문구를 넣는 일 — W-00000087 (이 카드 뒤에 같은 파일을 이어서 고친다).
- 드라이버 코드 변경 — 드라이버는 이미 0 이 아닌 종료 코드와 `BLOCK:` 을 실패로 본다.
  판정 표식의 정의는 명령(프로젝트 정책) 소유다.

## Dependencies

- 없음. W-00000087 이 이 카드 뒤를 잇는다.

## Risks

- 리뷰어가 정당하게 통과시키면서 APPROVED 를 안 쓰면 오탐 차단이 난다 — 프롬프트가 이미
  "통과면 APPROVED 를 포함하라" 고 지시하므로, 표식 요구는 그 지시의 강제일 뿐이다.
  오탐 차단은 조용한 통과보다 낫다(Fail Fast).

## Success criteria

- `.stage/settings.json` 의 리뷰 명령 전부가: CLI 실패 시 차단, 출력에 [P1]/APPROVED 가
  모두 없으면 차단, [P1] 차단 유지, APPROVED 만 있으면 통과.
- 그 동작의 증거가 카드에 있다 — 가짜 리뷰 명령으로 네 경우(오류 출력, 표식 없음, P1,
  APPROVED)를 셸에서 재현해 종료 코드를 확인한 기록.
- `SCHEMA_V4.md` 가 "판정 없는 리뷰 명령은 실패해야 한다" 를 계약으로 적고 있다.
- 두 `plugin.json` 의 version 이 올라 있고 `stage/CHANGELOG.md` 에 항목이 있다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 통과.
- `python3 -m unittest discover -s stage/hooks/tests -q` 통과.

제약:

- **커밋하지 않는다.** 작업 트리에 변경만 남기고 멈춘다.
- 저장소 산출물은 영어. `.stage/` 안의 글만 한국어.
- scope 밖은 건드리지 않는다.


## Next action

`.stage/settings.json` 의 리뷰 래퍼 둘(claude, red-team)을 fail-closed 로 바꾼다 — `case` 를
"APPROVED 없으면 BLOCK" 으로 뒤집고, CLI 종료 코드도 확인한다. `SCHEMA_V4.md` 리뷰 계약에
"판정 표식을 못 내면 실패" 를 적는다. W-00000087(codex 리뷰어 계약)과 같은 파일을 고치므로
함께 처리하는 것을 고려할 것.

## Progress

2026-07-26:

- 변경 전 래퍼를 가짜 리뷰 명령으로 재현했다. `cli_error` 와 `no_marker` 가 모두 종료 코드
  0으로 끝나는 RED 를 확인했다.

  ```text
  CASE=cli_error OUTPUT=reviewer-unavailable
  CASE=cli_error RC=0
  CASE=no_marker OUTPUT=review-complete
  CASE=no_marker RC=0
  CASE=p1 OUTPUT=[P1] criterion failed
  BLOCK: reviewer reported a P1 blocker
  CASE=p1 RC=1
  CASE=approved OUTPUT=APPROVED
  CASE=approved RC=0
  ```

- `.stage/settings.json` 의 비어 있지 않은 리뷰 명령 넷에 같은 fail-closed 계약을 적용했다.
  리뷰 CLI 종료 코드를 먼저 검사하고, 출력은 `[P1]` 차단을 `APPROVED` 통과보다 먼저
  판정하며, 두 표식이 모두 없으면 차단한다. 기존 `guidance_overrides` 직렬화의 SHA-256
  `1446451cf34707cc5ebd04202239457a1fc6c31e6287c05cda5a93166b0a8c50` 는 변경 전후가
  같다.
- 다음 셸 함수로 가짜 리뷰 명령 네 경우를 다시 실행했다.

  ```sh
  run_case() {
    label=$1
    fake=$2
    OUT=$(sh -c "$fake" 2>&1)
    STATUS=$?
    printf "CASE=%s OUTPUT=%s\n" "$label" "$OUT"
    if [ "$STATUS" -ne 0 ]; then
      echo "BLOCK: review command failed with exit code $STATUS"
      return 1
    fi
    case "$OUT" in
      *"[P1]"*) echo "BLOCK: review reported a P1 blocker"; return 1;;
      *"APPROVED"*) return 0;;
      *) echo "BLOCK: review produced no verdict"; return 1;;
    esac
  }
  ```

  결과:

  ```text
  CASE=cli_error OUTPUT=reviewer-unavailable
  BLOCK: review command failed with exit code 7
  CASE=cli_error RC=1
  CASE=no_marker OUTPUT=review-complete
  BLOCK: review produced no verdict
  CASE=no_marker RC=1
  CASE=p1 OUTPUT=[P1] criterion failed
  BLOCK: review reported a P1 blocker
  CASE=p1 RC=1
  CASE=approved OUTPUT=APPROVED
  CASE=approved RC=0
  ```

- `stage/docs/SCHEMA_V4.md` 에 판정을 만들 수 없는 리뷰 명령은 성공으로 끝나면 안 되며,
  0이 아닌 종료 코드나 `BLOCK:` 으로 실패해야 한다는 계약을 추가했다.
- Stage 버전 SSOT 둘을 `0.43.15` 로 함께 올리고 `stage/CHANGELOG.md` 에 변경을 기록했다.

## Verification

- `python3 -m unittest discover -s stage/scripts/tests -q` — 356 tests, OK.
- `python3 -m unittest discover -s stage/hooks/tests -q` — 327 tests, OK.
- `jq empty .stage/settings.json` — 통과.
- 비어 있지 않은 리뷰 명령 넷을 `sh -n` 으로 검사 — 통과.
- `git diff --check` — 통과.

### 기준 판정 — 반대 venue (Claude), DE-00000032 방식 (2026-07-26)

- 리뷰 명령 전부 fail-closed — 채움. 실행자의 증거와 별개로, `settings.json` 의 **실제 래퍼
  문자열 넷**(claude·codex 리뷰어, standard·red-team 강도)에 스텁만 끼워 네 경우를 직접
  돌렸다: CLI 실패 → 차단, 표식 없음 → 차단, [P1] → 차단, APPROVED → 통과. 16개 전부 기대
  대로.
- 동작 증거가 카드에 있다 — 채움(위 Progress 의 RED/GREEN 기록 + 이 절의 독립 재현).
- `SCHEMA_V4.md` 계약 — 채움. 판정을 낼 수 없는 리뷰 명령은 0 이 아닌 종료 코드나 `BLOCK:`
  으로 실패해야 한다고 적혀 있다.
- 버전 0.43.15, CHANGELOG — 채움. 테스트 두 벌 통과, 감사 errors=0.
- 무관 변경 보존 — 채움. `guidance_overrides` 의 네 항목이 그대로 있다.

### 그 밖에 본 것 (기준 밖 관찰)

- 없음. 차단할 지적 없음.

### Executed at close — 2026-07-26

```
$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0

$ python3 /private/tmp/claude-501/-Users-woogis-Workspace-repo-noory-ai/8498db6e-3b2c-4487-b49c-b670c4555420/scratchpad/verify_wrappers.py .stage/settings.json
[exit 0]
guidance_overrides: ['official/canon/vocabulary.md', 'operations/verification.md', 'index.md', 'state/current.md']
reviewers.codex / cli_error: rc=1 expected=1 OK | BLOCK: codex review command failed with exit code 7
reviewers.codex / no_marker: rc=1 expected=1 OK | BLOCK: codex review produced no verdict
reviewers.codex / p1: rc=1 expected=1 OK | BLOCK: codex review reported a P1 blocker
reviewers.codex / approved: rc=0 expected=0 OK | CRITERIA VERDICT: all PASS. APPROVED
reviewers.claude / cli_error: rc=1 expected=1 OK | BLOCK: claude review command failed with exit code 7
reviewers.claude / no_marker: rc=1 expected=1 OK | BLOCK: claude review produced no verdict
reviewers.claude / p1: rc=1 expected=1 OK | BLOCK: claude review reported a P1 blocker
reviewers.claude / approved: rc=0 expected=0 OK | CRITERIA VERDICT: all PASS. APPROVED
strengths.standard / cli_error: rc=1 expected=1 OK | BLOCK: codex review command failed with exit code 7
strengths.standard / no_marker: rc=1 expected=1 OK | BLOCK: codex review produced no verdict
strengths.standard / p1: rc=1 expected=1 OK | BLOCK: codex review reported a P1 blocker
strengths.standard / approved: rc=0 expected=0 OK | CRITERIA VERDICT: all PASS. APPROVED
strengths.red-team / cli_error: rc=1 expected=1 OK | BLOCK: codex review command failed with exit code 7
strengths.red-team / no_marker: rc=1 expected=1 OK | BLOCK: codex review produced no verdict
strengths.red-team / p1: rc=1 expected=1 OK | BLOCK: codex review reported a P1 blocker
strengths.red-team / approved: rc=0 expected=0 OK | CRITERIA VERDICT: all PASS. APPROVED
```

## Retrospective

R-00000088. 핵심: W-83(실행자)과 같은 병을 리뷰어에서 고쳤다 — 부정 표식의 부재는 합격이
아니다. 합격 표식이 있어야 합격이다.

## Promotion decision

official 로 올릴 산출물 없음(promotion: not_applicable). 카드와 회고는 아카이브로 간다.
