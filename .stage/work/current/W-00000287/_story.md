---
id: W-00000287
title: 실행자가 정한 것을 닫을 때 카드에 남긴다
kind: fix
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_close_work.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/skills/stage-retrospective/close_work.py, stage/scripts/tests/test_close_work.py, stage/skills/stage-drive/SKILL.md, stage/docs/SCHEMA_V4.md, stage/templates/v4/project-stage/settings.jsonc, stage/CHANGELOG.md
promotes:
decision_refs: DE-00000078
---

# W-00000287 실행자가 정한 것을 닫을 때 카드에 남긴다

## Purpose

실행자가 스스로 정한 것과 하지 않은 일이 커밋되지 않는 작업 로그와 함께 사라지지 않고, 몇 달 뒤의 본인이 카드에서 읽을 수 있게 한다.

## Actions

- 지금 동작: 실행 보고는 `.stage/.runtime/driver/logs/<id>.md` 에만 있고 이 경로는 gitignore 대상이다.
  드라이버 커밋 메시지는 `driver: <id> executor output` 한 줄이다. 보관된 W-00000285 의 Progress 는
  커밋되지 않는 로그와 판정 파일을 가리킨다. 검증기 `executor_report_error()` 는 계약이 요구하는
  `Decisions made:`·`Work not done:` 을 검사하지 않는다.
- `close_work.py` 가 닫을 때 작업 로그의 마지막 `### Executor report` 에서 `What changed`, `Why`,
  `Decisions made`, `Work not done` 네 줄을 원문 그대로 카드의 `## Progress` 에 옮긴다. 로그에
  보고가 없으면(손으로 닫은 카드) 아무것도 옮기지 않고 닫기를 막지 않는다.
- 검증기가 `Decisions made:`·`Work not done:` 도 비어 있지 않은 한 줄로 요구한다(`None` 허용).
- 실행자 계약에 "마지막 판의 `Decisions made:` 는 그때까지 유효한 결정을 모두 다시 적는다"를 더한다.
  `stage/skills/stage-drive/SKILL.md`, `stage/docs/SCHEMA_V4.md`,
  `stage/templates/v4/project-stage/settings.jsonc` 실행 명령 안내가 같은 뜻으로 적는다.
- `stage/CHANGELOG.md` 의 `## Unreleased` 에 한 줄을 더한다.

## User value

몇 달 손 뗐다가 돌아왔을 때, 다른 컴퓨터나 클라우드 체크아웃에서도 카드만 열면 실행자가 무엇을
왜 그렇게 정했는지 읽을 수 있다. "스스로 정한 것을 안 적으면 은폐다"(PHILOSOPHY)가 구조적으로
지켜진다.

## Scope

### Included

- 닫기의 실행 보고 이관, 검증기의 두 칸 요구, 실행자 계약 문장, 시험, 변경 기록 한 줄

### Excluded

- 실패한 판의 원재료 보존 — 회고가 소화한다(사용자 결정).
- 작업 로그를 커밋하는 일, 드라이버 커밋 메시지 본문을 채우는 일.
- `Executed at close` 출력 꼬리 40줄을 줄이는 일.

## Risks

- 판이 여럿이면 앞 판의 결정이 마지막 보고에서 빠질 수 있다. 누적 기재 계약과 리뷰어의
  `Decisions made` 판정으로 잡는다. 모든 판을 모으는 안은 되돌린 결정까지 남겨 기록이 사실과
  어긋나므로 고르지 않았다.
- 검증기를 엄격하게 하면 두 칸을 빠뜨리던 실행 명령이 시도 횟수를 쓴다. 계약 문서는 이미 두 칸을
  요구하고 있었다.

## Success criteria

- 드라이버로 닫은 카드의 Progress 에 승인된 마지막 판의 What changed, Why, Decisions made, Work not done 이 원문 그대로 남는다는 것을 테스트가 확인한다
- Decisions made 나 Work not done 이 빠진 실행 보고는 거절된다는 것을 테스트가 확인한다
- 실행자 계약이 마지막 판의 Decisions made 에 그때까지 유효한 결정을 모두 다시 적으라고 요구하고, 계약 문서 셋이 같은 뜻으로 적는다

## Next action

클라우드 세션이 DE-00000078 계약대로 고치고 `claude/w268-cloud` 에 push 한다. 로컬에서 범위 대조,
실행 보고를 작업 로그로 옮기기, 인수 명령과 scripts 전체 시험, codex 판정, 회고, 닫기를 한다.

## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision
