---
id: W-00000152
title: 카드 제목을 할 일로 쓰게 규칙을 바꾼다
kind: documentation
venue: claude
milestone:
source:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000152
promotion: not_applicable
review: not_required
scope: stage/skills/stage-work/SKILL.md, stage/CHANGELOG.md, .stage/work/planned/
promotes:
decision_refs:
---

# W-00000152 카드 제목을 할 일로 쓰게 규칙을 바꾼다

## Purpose

카드 제목을 "끝난 상태"로 쓰라는 규칙이 있었다. 그래서 할 일인 카드가 이미 된 일처럼 읽힌다.
사용자가 계획 카드 하나를 열어 보고 "이게 일감인가요? 뭔가요?"라고 물었다 — 제목만으로는 앞으로
할 일인지 이미 참인 사실인지 구분이 안 됐다.

같은 자리에서 두 가지가 더 드러났다.

- **카드가 답해야 할 것을 아무 데도 안 적어 뒀다.** 무엇을 하는지, 왜 지금 하는지, 무엇을
  이루려는지, 언제 끝나는지. 템플릿에 칸은 있지만 "비워도 되는 칸"과 구분이 없어서, 나중에
  하려고 잡아 둔 카드는 대부분 목적만 있고 나머지가 비어 있다.
- **본문이 번호로 쓰인다.** "DE-00000046 이 정한 것", "감사 WORK015", "남의 결정" 같은 문장은
  이미 맥락을 아는 사람만 읽을 수 있다. 처음 읽는 사람은 파일 두세 개를 더 열어야 뜻이 생긴다.

셋 다 같은 실패다 — **카드가 읽는 사람 몫을 자기가 안 지고 있다.**

## Actions

카드 등록 절차 문서에 규칙 셋을 적는다.

- 제목은 할 일을 적는다. 끝난 상태로 쓰지 않는다.
- 카드는 네 가지에 답한다: 무엇을 하는가, 왜 지금인가, 무엇을 이루려는가, 언제 끝나는가.
  어느 칸이 무엇을 쥐는지 표로 못 박고, 나중에 하려고 잡아 두는 카드도 예외가 아님을 적는다.
- 뜻을 먼저 쓰고 번호는 뒤에 붙인다. 진행 메모와 도구 출력은 카드가 아니라 작업 로그 몫이다.

변경 이력에 두 줄을 더한다. 매니페스트 버전은 안 건드린다.

지금 열려 있는 계획 카드 하나(문서에 결정 칸의 뜻을 적는 일)를 새 규칙대로 다시 쓴다 — 규칙이
실제로 읽히는 글을 만드는지 그 카드로 확인한다.

## Scope

`stage/skills/stage-work/SKILL.md`, `stage/CHANGELOG.md`, `.stage/work/planned/`.

**안 하는 것**: 이미 보관된 카드 140여 장의 제목. 과거 카드는 그대로 둔다 — 고치면 그 카드를
가리키는 회고·결정의 인용이 어긋난다. 규칙은 앞으로 쓰는 카드부터 적용한다.

## Success criteria

- 등록 절차 문서에 규칙 셋이 있고, 각각 **왜 그런지**가 함께 적혀 있다. 이유 없는 규칙은 급할 때
  제일 먼저 버려진다.
- 네 가지 답을 어느 칸이 쥐는지 표로 적혀 있다.
- 끝나는 조건 칸에 "사람이 겪는 결과를 하나는 적는다"가 들어 있다. 구조 검사만 채우면 좁게
  통과한다 — 이 저장소가 그 실패를 네 번 밟았다.
- 다시 쓴 계획 카드를 **처음 읽는 사람이 다른 파일을 안 열고** 무슨 일인지 안다.
- 변경 이력에 항목이 있고 매니페스트 버전은 그대로다.

## Related truth

- 카드 본문에 궁극적 목적을 쓰라는 지적을 전에도 받았다(에픽 둘이 목적 칸을 비운 채 돌았다).
  그때는 그 카드들만 채우고 규칙으로 안 올렸다. 같은 지적이 두 번째다.
- 기준을 구조 검사만으로 채워 좁게 통과한 사례 넷 — 사람이 겪는 결과를 기준에 넣는 것이 그
  대책이다.
- 카드 등록 절차 문서 `stage/skills/stage-work/SKILL.md` 의 "Draft the item" 절이 규칙이 사는 자리다.

## Progress

규칙 셋을 등록 절차 문서에 넣고, 열려 있던 계획 카드 하나를 그 규칙대로 다시 썼다.

## Verification

- 등록 절차 문서에 규칙 셋이 이유와 함께 있고, 네 가지 답을 어느 칸이 쥐는지 표로 적혀 있다.
- 끝나는 조건 칸 설명에 "사람이 겪는 결과를 하나는 적는다"가 들어 있다.
- 다시 쓴 계획 카드가 번호 대신 뜻으로 읽힌다 — "결정 기록 46이 정한 것" 대신 "카드에는 그 카드가
  내린 결정을 적는 칸이 있고, 거기 무엇을 적는지가 어디에도 안 적혀 있다".
- 변경 이력에 두 항목이 있고 매니페스트 버전은 그대로다.
- `stage/hooks/tests` 347개 통과, 감사 0/0.

### Executed at close — 2026-07-30

```
$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 347 tests in 1.064s

OK

$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

[R-00000152](../../retrospectives/R-00000152.md) — 카드가 읽는 사람 몫을 자기가 안 지고 있었다.

## Promotion decision

FINAL: not_applicable. 플러그인 문서 변경이고 승격할 산출물이 없다.
