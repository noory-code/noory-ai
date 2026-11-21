---
id: W-00000378
title: 카드와 기록을 등록할 때 번호를 원격에 잡는다
kind: development
venue: claude
environment: cloud
milestone: M-00000005
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000378
promotion: not_applicable
review: passed
scope: stage/scripts/stage_record_ids.py,stage/skills/stage-work/register_work.py,stage/skills/stage-roadmap/manage_roadmap.py,stage/scripts/tests,stage/skills/stage-decision/SKILL.md,stage/operations/cloud-execution.md,stage/docs/BLUEPRINT.md,stage/CHANGELOG.md,.stage/operations/parallel-sessions.md
promotes:
decision_refs:
---

# W-00000378 카드와 기록을 등록할 때 번호를 원격에 잡는다

## Purpose

서로의 브랜치를 받아 오지 않은 두 세션이 같은 카드 번호나 기록 번호를 고르지 않게 한다

## Actions

- `stage_record_ids.py` 에 `IdReserver` 를 둔다. 원격의 `refs/stage-ids/*` 를 한 번 읽어 센다. 번호를 고르면
  그 번호만 담은 커밋 하나를 만들어 `--force-with-lease=<ref>:` 로 push 한다. 거절되면 원격에 그 ref 가
  생겼는지 다시 읽고, 생겼으면 다음 번호로, 없으면 원격이 push 를 거절한 것으로 보고 잡기를 끈다.
- `register_work.py` 의 번호 고르는 네 자리(진행 중/계획, 평면/계층)와 `manage_roadmap.py` 의
  `_create_atomic`(TH, M, 마일스톤 결정 DE)이 같은 `IdReserver` 를 쓴다. `--id` 로 번호를 직접 준 등록은
  원격에 가지 않는다.
- `stage_record_ids.py` 명령은 기본으로 번호를 잡는다. `--no-reserve` 는 번호만 말한다.

## User value

카드를 등록하기 전에 fetch 하고 등록한 뒤 바로 push 하는 순서를 기억하지 않아도 번호가 겹치지 않는다.
겹친 번호를 다시 매기느라 카드와 회고와 링크를 고치는 일이 없어진다.

## Scope

### Included

- `stage_record_ids.py` 와 `register_work.py` 가 번호를 고른 뒤 원격에 `refs/stage-ids/<번호>` 를 만든다.
  이미 있으면 다음 번호로 넘어간다.
- 원격에 닿지 못하거나 원격이 없으면 지금처럼 번호를 고르고, 잡지 못했다고 출력한다.
- 고칠 자리는 DE-00000092 의 "Where this applies" 표에 하나씩 적혀 있다.

### Excluded

- 목록 파일. W-00000377 가 한다.
- 이미 겹친 번호를 바꾸는 도구.

## Risks

- 이 저장소의 원격을 클라우드 세션에서 확인했다(2026-11-21). 결과는 아래 "원격 확인" 에 있다. 클라우드
  세션의 git 프록시가 push 를 거절하므로, 병렬로 가장 많이 도는 클라우드 세션에서는 이 기능이 번호를 잡지
  못하고 예전처럼 동작한다. GitHub 자체가 `refs/stage-ids/` 를 받는지는 프록시에 막혀 확인하지 못했다.
- 등록할 때마다 원격을 한 번 다녀온다. 느리면 세션이 이 기능을 끄고 일하게 된다.
- 테스트가 실제 원격에 가면 안 된다. 임시 폴더의 빈 저장소를 원격으로 쓴다.

## Success criteria

- 서로 받아 오지 않은 두 클론이 같은 원격을 두고 차례로 카드를 등록하면 서로 다른 번호를 받는다
- 원격에 닿지 못할 때도 등록이 되고, 번호를 원격에 잡지 못했다는 줄이 출력된다
- 원격이 없는 프로젝트에서 등록하면 지금과 같은 번호를 받는다
- 이 저장소의 GitHub 원격이 번호를 잡는 ref 를 받아 주는지 확인한 결과가 카드에 적혀 있다

## Next action

없다. PR #88 이 병합을 기다린다.

## 원격 확인

클라우드 세션(`claude/w378-reserve-ids`)에서 한 번 실행했다. 메인 세션이 이 확인을 지시했다.

| 명령 | 결과 |
|---|---|
| `git push --force-with-lease=refs/stage-ids/W-99999999: origin HEAD:refs/stage-ids/W-99999999` | `error: RPC failed; HTTP 403 curl 22 The requested URL returned error: 403`, `fatal: the remote end hung up unexpectedly`, 종료 코드 1 |
| `git ls-remote origin 'refs/stage-ids/*'` | 아무것도 없다. ref 는 만들어지지 않았다. 지울 것이 없다. |

- 403 은 세션의 에이전트 프록시가 준 것이다. 프록시 안내(`/root/.ccr/README.md`)는 403 을 정책 거절로 보고
  다시 시도하거나 돌아가지 말라고 한다. 그래서 태그나 다른 이름으로는 시험하지 않았다.
- 같은 세션에서 세션 브랜치(`refs/heads/claude/w378-reserve-ids`) push 는 성공했다. 프록시는 세션
  브랜치 밖의 ref 를 막는 것으로 보인다. 정책 문서를 보지 못했으므로 추정이다.
- 확인하지 못한 것: GitHub 이 `refs/stage-ids/` 를 받는지, 사용자의 로컬 세션(맥북, Windows)에서 push 가
  되는지.

## Related truth

## Progress

### Executor report at close — 2026-11-21

```
What changed: Added IdReserver and default_remote to stage/scripts/stage_record_ids.py (reads remote refs/stage-ids/*, pushes a one-commit marker with --force-with-lease=<ref>:, re-reads the ref on failure to tell a lost race from a refusing remote, prints one not-reserved line); the CLI reserves by default with --no-reserve to only name the id; register_work.py's four auto-allocation paths and manage_roadmap.py's _create_atomic (TH, M, milestone DE) use it; added stage/scripts/tests/test_stage_id_reservation.py (13 tests, bare remotes in temp dirs); updated the decision skill, cloud-execution.md, BLUEPRINT.md, parallel-sessions.md, the card, and the stage CHANGELOG.
Why: Counting only fetched refs cannot see an unfetched session's ids; git accepts only one create-only push per ref, which removes the need to remember fetch-then-push.
Decisions made: Push a marker commit built from the empty tree instead of HEAD so reservation never uploads branch work; add a random nonce to the marker message because two sessions building identical commits in the same second made the second push a successful no-op (caught by a test); treat a failed push as a lost race only when the ref then exists remotely, otherwise turn reservation off for the run; explicit --id registrations do not reserve, to avoid refusing a session's own earlier reservation; print the not-reserved line also when there is no remote, as the card asks.
Work not done: Cleanup of accumulated refs/stage-ids refs; GitHub acceptance of refs/stage-ids is unverified because this cloud session's git proxy refused the push with HTTP 403, so cloud sessions fall back to the fetch-then-push rule; no alternative ref name was probed because the proxy guidance forbids routing around a policy denial.
```

## Verification

- 환경은 `cloud` 다. 닫기 리뷰는 같은 모델의 리뷰이고 교차 venue 리뷰가 아니다.
- 닫기 전 전체 실행(2026-11-21): hooks 455 OK, scripts 821 OK(skipped 2), `audit_stage.py` errors=0.
  새 시험 13개(`test_stage_id_reservation.py`)는 모두 임시 폴더의 bare 저장소를 원격으로 쓴다.
- 성공 기준: 받아 오지 않은 두 클론의 차례 등록 → W-00000003, W-00000004(시험). 닿지 못하는 원격 → 등록되고
  한 줄 출력(시험). 원격 없음 → `--no-reserve` 와 같은 번호(시험). GitHub 원격 확인 → 위 "원격 확인"(403).
- 코드 커밋이 둘(9c1e5727, f03ea628)이라 리뷰가 모든 경로를 받도록 두 커밋을 합친 로컬 커밋 1d423a08 에서
  닫았다.

- Checks at close 2026-11-21: 3 passed — `python3 -m unittest discover -s stage/scripts/tests -p test_stage_id_reservation.py -q`; `python3 -m unittest discover -s stage/scripts/tests -p test_stage_record_ids.py -q`; `python3 stage/scripts/audit_stage.py --project-root .`
- Review at close 2026-11-21 by claude_review_companion: approved (1 PASS, 2 PASS, 3 PASS, 4 PASS)
