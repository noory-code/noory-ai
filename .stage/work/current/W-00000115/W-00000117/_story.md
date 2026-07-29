---
id: W-00000117
title: 리뷰 판정을 파일로 받는다
kind: development
venue: codex
milestone:
priority:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/scripts/drive.py, stage/skills/stage-retrospective/close_work.py, stage/skills/stage-drive/SKILL.md, stage/scripts/tests/, .stage/settings.json, stage/templates/, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000117 리뷰 판정을 파일로 받는다

## Purpose

DE-00000039 §2. 리뷰어가 드라이버가 준 경로에 기준별 판정을 JSON 으로 쓰고 기계는 그것만 읽는다(O-00000004). 산문 라벨 탐색(reviewer_report_error, latest_review_failures)과 리뷰 명령 네 벌, 템플릿, 디스포지션 계약이 함께 움직인다. 템플릿에는 리뷰 계약이 처음 실린다.

## Actions

- 드라이버가 리뷰어에게 **판정을 쓸 파일 경로**를 넘긴다. 바뀐 파일 목록을 넘기는
  `STAGE_CHANGED_PATHS_FILE` 과 같은 모양이므로 새 개념이 아니다.
- 리뷰어는 기준별 통과/실패와 승인 여부를 그 파일에 JSON 으로 쓴다. 산문 리뷰는 지금처럼
  공유 로그에 남는다 — 사람이 읽을 몫은 안 줄인다. **기계는 JSON 만 읽는다.**
- 산문에서 표식을 찾는 자리를 없앤다. 오늘 여섯 번 걸린 곳이다:
  `close_work.py:318` `reviewer_report_error`, `:226` `latest_review_failures`,
  `:324` 의 절 표식 세기.
- 부르는 자리 넷을 같이 옮긴다 — `drive.py:1444`(다음 바퀴에 넘길 실패 목록), `:1670`(닫은 뒤
  남은 실패 확인), `:2160`(무인 판정), `close_work.py:674`·`717`(닫기 리뷰 둘).
- 리뷰 명령 **여섯 벌**을 새 계약으로 바꾼다(`.stage/settings.json` 의 `review.reviewers` 둘 +
  `review.strengths` 넷). 한 벌만 고치면 실행 방식마다 계약이 갈린다.
- `stage/templates/` 에 리뷰 계약을 싣는다. 지금 템플릿에는 판정 표식이 아예 없어서 새
  프로젝트는 리뷰 계약을 못 받는다.
- 실패 항목을 처분하는 계약(`executor_review_dispositions`)이 JSON 판정을 근거로 돌게 한다.
  지금은 산문 FAIL 줄을 글자로 맞춘다.
- **감독·무인의 처분 계약이 갈린 것을 함께 맞춘다** — 감독 쪽은 실패 목록을 안 넘기고
  빈 경로 목록을 바로 실패로 만든다. 프롬프트가 약속한 "이유 있는 안 받음·미룸은 빈 배열을
  주장해도 된다"가 무인에서만 참이다(W-00000121 이 넘긴 근거).
- 죽은 필드 `base_repository_paths` 를 걷는다(`drive.py:178`, `191-201`). 검증만 남고 안 쓰인다.
- `stage/CHANGELOG.md` 미출시 절에 적는다. **매니페스트 버전은 안 건드린다.**

## User value

통과한 일이 판정을 읽다가 실패로 기록되지 않는다. 오늘 여섯 번 그랬고, 그중 한 번은 리뷰어가
파서로 통과까지 확인해 놓고 **그 사실을 설명하다가** 걸렸다. 리뷰어에게 "네가 쓴 절 이름을
입에 담지 마라"를 요구할 수는 없다.

## Scope

### Included


### Excluded


## Risks

- **리뷰어가 JSON 을 안 쓰거나 깨뜨릴 수 있다.** 산문보다 형식이 빡빡하다. 그러나 못 읽으면
  못 읽는다고 명확히 실패하고, 지금처럼 "통과했는데 실패로 기록"되지는 않는다. 실패의 뜻이
  분명해지는 것이 이 카드의 값이다.
- 리뷰 명령 여섯 벌을 한꺼번에 바꾸므로 한 벌이라도 빠지면 그 자리만 옛 계약으로 남는다.
  기준에서 여섯 전부를 센다.
- 파일 하나가 더 오간다. 다만 바뀐 파일 목록이 이미 같은 방식이라 새 구조가 아니다.

## Success criteria

- 리뷰어가 판정을 JSON 파일로 쓰고, 드라이버·닫기가 그 파일만 읽어 통과를 정한다. 산문에서
  절 표식을 찾는 코드가 남아 있지 않다.
- **리뷰어가 산문에 절 이름이나 판정 라벨을 그대로 적어도 판정이 안 흔들린다.** 오늘 여섯 번
  걸린 그 상황을 고정하는 테스트가 있다.
- 판정 파일이 없거나 JSON 이 깨졌으면 **그 사유로** 실패한다. 통과를 실패로 바꾸는 것과
  구분된다. 두 경우를 각각 고정하는 테스트가 있다.
- 부르는 자리 다섯(감독 스텝, 무인 스텝, 닫기 리뷰 둘, 다음 바퀴 실패 목록)이 전부 새 계약을
  쓴다. 자리마다 테스트가 있다.
- 리뷰 명령 여섯 벌(`review.reviewers` 둘 + `review.strengths` 넷)이 전부 새 계약을 말한다.
- `stage/templates/` 가 리뷰 계약을 담는다. 새 프로젝트가 그것을 받는다.
- 실패 항목 처분이 JSON 판정을 근거로 돌고, 감독과 무인이 같은 규칙을 쓴다 — 이유를 단
  안 받음·미룸은 양쪽 다 빈 경로 목록을 주장할 수 있다. 두 자리를 각각 고정하는 테스트가 있다.
- `base_repository_paths` 필드가 코드에서 사라진다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 와
  `python3 -m unittest discover -s stage/hooks/tests -q` 가 전부 통과한다.
- `stage/CHANGELOG.md` 미출시 절에 항목이 있고 매니페스트 버전은 그대로다.

### 리뷰어가 왜 실패했는지 모른 채 시도를 쓰지 않는다

이 카드의 목적이 "통과한 일이 판정을 읽다가 실패로 안 된다"이므로, 새 계약이 **말 안 한
조건으로 실패시키는 것**도 같은 병이다. 아래를 같은 값으로 센다.

- **판정 파일을 읽다 죽는 조건을 리뷰 명령 여섯 벌이 전부 말한다.** 지금 `review.strengths`
  네 벌이 기준 이름 중복 금지, 한 줄·빈 값 금지, 키가 정확히 둘이라는 것을 안 말한다. 셋 다
  판정 읽기의 하드 실패 조건이라, 그 프롬프트만 따른 리뷰어는 이유도 모른 채 시도를 하나
  쓴다. 여섯 벌이 같은 조건을 말하는지 확인하는 테스트가 있다.
- **실행자 프롬프트가 코드보다 느슨하지 않다.** 프롬프트는 "이유를 단 안 받음·미룸은 빈 경로
  배열을 주장해도 된다"고 하는데, 코드는 처분이 **전부** 안 받음·미룸일 때만 받는다. 하나라도
  받은 라운드가 빈 배열을 주장하면 실패한다. 두 벌 다 코드와 같은 말을 하게 한다.
- **깨진 판정이 공짜 재시도로 흐르지 않는다.** 지금 판정을 못 읽으면 실패 목록이 빈 목록으로
  나오고, 닫기 출력에 인프라 표식이 우연히 섞이면 그 라운드가 시도를 안 쓴다. 못 읽는 것은
  인프라 실패가 아니라 리뷰 실패다. 그 경우를 고정하는 테스트가 있다.
- **없어진 `BLOCK:` 훑기를 설명하는 주석이 남아 있지 않다.** `close_work.py:455-458`,
  `:690-692` 가 아직 그 훑기로 동작을 설명한다.

## Next action

끝나면 사람이 O-00000004(산문 판독)와 O-00000010(도는 역할 짐작)을 다시 본다. 앞의 것은 이
카드가 닫고, 뒤의 것은 시도 기록에 도는 역할을 적어야 닫히므로 W-00000118·119 가 `drive.py`
를 만질 때 함께 판단한다.

## Progress

## Verification

## Retrospective

## Promotion decision
