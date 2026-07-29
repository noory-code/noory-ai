---
id: W-00000090
title: 세션 안에서 돌린 드라이버가 세션 환경을 리뷰어에게 흘린다
kind: planning
venue: claude
priority:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000091
promotion: not_applicable
scope: .stage/state/
promotes:
decision_refs:
---

# W-00000090 세션 안에서 돌린 드라이버가 세션 환경을 리뷰어에게 흘린다

## Purpose

2026-07-26, W-00000088 드라이버 실전 첫 가동에서 실제로 났다. 드라이버를 Claude Code 세션
안에서 돌리면 세션 식별 환경 변수(`CLAUDE_CODE_SESSION_ID`, `CLAUDE_CODE_CHILD_SESSION` 등)가
자식인 리뷰어 `claude -p` 까지 내려가, 리뷰어가 34KB diff 대신 세션 대화 전체(약 216만
토큰)를 입력으로 받아 입력 초과로 죽었다. 어느 변수가 원인인지는 확인 전이다 — 확인부터가
이 카드의 첫 일이다.

드라이버는 이미 자식 환경을 직접 만든다(`executor_environment`, 리뷰어 env). 원인 변수를
확인한 뒤, 그 자리에서 세션 식별 변수를 걷어내는 것이 방향이다. 사람이 평범한 터미널에서
돌리면 안 나는 문제지만, 에이전트가 세션 안에서 드라이버를 돌리는 것이 오늘부터 정식
흐름이 됐으므로 막아야 한다.

## Source

W-00000088 검증의 기준 밖 관찰 (처리: 받는다). 사고 경위는 그 카드 Progress 절.

종류를 fix 에서 planning 으로 바로잡았다 (2026-07-26): 이 카드의 일은 원인 실측과 판단이다.
원인이 재현되지 않으면 fix 의 통과 기준(재현 테스트)을 정직하게 채울 수 없다. 원인이 잡히면
고치는 일은 별도 fix 카드로 잇는다.

## Success criteria

- 실측 셋이 실행되고 결과가 카드에 기록되어 있다: ① 사고 당시와 같은 환경 변수 조합으로
  `claude -p` 소형 호출 재현, ② 리뷰어 환경(임시 인덱스 + intent-to-add)에서
  `git diff HEAD~1` 크기 실측, ③ codex 실행자가 저장소 안에 큰 미추적 파일을 남기는지 확인.
- 결론이 기록되어 있다 — 원인이 잡혔으면 fix 카드로 이어지고, 안 잡혔으면 미해결 질문
  (`state/questions/`)으로 라우팅되고 재발 시 잡는 길(무엇을 재면 되는지)이 적혀 있다.
- 어느 쪽이든: W-00000089 의 fail-closed 방벽 덕에 재발해도 조용히 통과하지 않는다는 사실이
  결론에 명시되어 있다.


## User value


## Scope

### Included


### Excluded


## Dependencies


## Risks


## Success criteria


## Next action

### 반증 하나 (2026-07-26, 사고 직후 확인)

세션 안에서 `printf 'hi' | claude -p "Reply OK."` 를 그대로 돌리면 **정상으로 OK 가 온다.**
즉 "세션 환경 변수를 물려받아 대화가 딸려 간다" 는 첫 가설은 이 단순 형태로는 재현되지
않는다. 원인은 아직 모른다 — 제목의 가설을 사실로 취급하지 말 것.

### 다음 조사

사고 당시와 같은 조건을 하나씩 복원해 어디서 입력이 커지는지 찾는다:

- 드라이버 스텝 안에서 리뷰 명령의 stdin 크기를 실측한다 — 리뷰 명령을
  `git diff HEAD~1 | tee /tmp/review-stdin.bin | claude -p ...` 로 바꿔 한 스텝 돌려 보면
  stdin 이 실제로 몇 바이트였는지 남는다.
- 리뷰어 환경(GIT_INDEX_FILE=실행자 인덱스, intent-to-add 반영)에서 `git diff HEAD~1` 이
  평소보다 커지는 경우가 있는지 본다 — intent-to-add 된 미추적 파일의 내용이 diff 에
  포함되므로, 실행자가 큰 미추적 파일을 남기면 diff 가 그만큼 커진다.
- 그래도 안 나오면 `claude -p` 가 stdin 외에 무엇을 문맥으로 붙이는지(오류 문구의
  "attachment content") 확인한다.

원인이 확인되면 드라이버 쪽에서 막을 수 있는 것인지(자식 환경 정리, stdin 상한), 운영
규칙으로 둘 것인지 정한다. W-00000089(판정 없으면 차단)가 먼저 닫히면 이 문제는 최소한
조용히 통과하지는 않게 된다 — 그 뒤에는 급하지 않다.

## Progress

### 실측 셋 (2026-07-26)

1. **환경 변수 조합 재현** — 사고 당시 조합(임시 `GIT_INDEX_FILE` + `STAGE_WORK_ITEM_PATH` +
   이 세션의 식별 변수 전부 상속)으로 `claude -p` 소형 호출 → 정상 "OK". 가설 반증.
2. **리뷰어 환경 diff 크기** — 임시 인덱스 아래 `git diff HEAD~1 | wc -c` = 13,896 바이트.
   340만 토큰(약 8MB 상당)과 두 자릿수 차이. 가설 반증.
3. **codex 의 큰 미추적 파일** — 저장소 안 1MB 이상 파일은 전부 gitignore 상태
   (`.venv`, `.mypy_cache`, 빌드 산출물, `.pen`)라 intent-to-add 대상이 아니다. 미추적
   비무시 파일은 `.stage` 문서 셋뿐. 가설 반증.

남은 단서 하나: 오류 문구의 대화 크기(약 216만 토큰)가 당시 이 세션 기록 크기와 자릿수가
같고, `CODEX_COMPANION_TRANSCRIPT_PATH` 가 그 기록을 가리키고 있었다 — 그러나 같은 변수가
있는 지금 재현이 안 되므로 단정하지 않는다.

**결론**: 원인 미상으로 남긴다 → Q-00000001 로 라우팅. 재발 시 계측(리뷰 stdin `tee` 실측 +
호출 환경 보존)으로 잡는다. W-00000089 의 fail-closed 방벽 덕에 재발해도 조용히 통과하지
않고 차단으로 드러나므로, 이 질문이 열려 있어도 드라이버 운용은 안전하다.

## Verification

### 기준 판정 (2026-07-26)

- 실측 셋 실행·기록 — 채움 (위 Progress).
- 결론 기록 — 채움. 원인 미상 → Q-00000001 (재발 시 계측 방법 포함).
- fail-closed 방벽 명시 — 채움 (Progress 결론과 Q-00000001 의 Blocked work 절).

### 그 밖에 본 것 (기준 밖 관찰)

- 없음.

### Executed at close — 2026-07-26

```
$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

R-00000091. 핵심: 가설 셋을 실측으로 반증하고 "모른다" 를 기록으로 남겼다 — 추측으로 고치는
것보다 계측을 심어 두는 쪽을 골랐다.

## Promotion decision

official 로 올릴 산출물 없음(promotion: not_applicable). 카드와 회고는 아카이브로 간다.
