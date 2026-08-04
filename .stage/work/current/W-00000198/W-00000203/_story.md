---
id: W-00000203
title: 이 저장소의 끝난 기록을 서랍에서 비운다
kind: documentation
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: .stage/, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000203 이 저장소의 끝난 기록을 서랍에서 비운다

## Purpose

이 저장소에는 끝난 기록 스물한 장이 살아 있는 서랍에 남아 있고 관측 여섯 장은 열렸는지조차 기계가 못 세므로, 새 명령으로 끝난 것을 모두 보관함에 넣고 상태 절이 빠진 관측을 사람이 판정해 채운다

## Actions

없음 — 판정과 이동이 기록마다 붙어 있어 나누면 같은 파일을 두 번 연다.

## User value

세션을 열면 서랍에 진짜 살아 있는 것만 뜬다. 지금은 다 끝난 열여섯 장이 진행 중이나 계획으로
잡혀서 매번 다시 확인하게 된다.

## Scope

### Included

- 제안 네 장을 닫는다. 넷 다 결론이 이미 인덱스에 적혀 있고, P-00000004 는 절반이다.
- 닫힌 관측 열 장을 옮긴다. 상태 절 본문이 근거다.
- 답한 질문 한 장을 옮긴다.
- 다 쓴 허가증 여섯 장을 옮긴다.
- 상태 절이 없는 관측 여섯 장(O-00000024~29)을 사람이 판정해 절을 채운다. 열려 있으면 열린
  채로 남기고, 닫혔으면 근거를 적고 옮긴다.
- 관측 인덱스가 옮긴 기록을 안 들고 있게 한다.

### Excluded

- 다른 프로젝트의 기록은 안 옮긴다.
- 열린 기록의 내용은 안 고친다. 상태 절이 빠진 여섯 장만 예외고, 그것도 판정 결과만 적는다.

## Risks

- **관측 여섯 장 판정은 기계가 못 대신한다.** 잘못 닫으면 살아 있는 문제가 보관함으로 사라진다.
  애매하면 열어 둔다.
- 앞선 세 스토리가 다 실려야 시작할 수 있다. 명령이 없으면 또 손으로 옮기게 되고, 그러면
  이 에픽이 막으려던 자리를 내가 다시 만든다.
- O-00000003 은 첫 줄이 "대부분 닫힘"이고 아래에서 닫혔다고 말한다. 첫 줄만 읽으면 잘못 센다.

## Success criteria

- 결정·제안·관측·질문 네 서랍에 살아 있는 기록만 남는다.
- 세션을 열면 요약이 끝난 기록을 진행 중이나 계획으로 안 센다.
- 옮긴 기록을 가리키던 인용이 그대로 열린다.
- 관측 스물아홉 장 전부가 열렸는지 닫혔는지 서랍으로 판정된다.
- 손으로 옮긴 파일이 하나도 없다 — 전부 명령이 옮겼다.

## Next action

W-00000201 의 명령이 실린 뒤에 시작한다. 그 전에 손으로 옮기면 안 된다.

## Related truth

- 실측 (2026-08-04): 제안 4/4 처리 끝, 관측 10/29 닫힘, 질문 1/1 답함, 허가증 6/6 소진.
- O-00000029 — 내가 기억해서 적어야 하는 상태는 예외 없이 낡는다.

## Progress


## Verification


## Retrospective


## Promotion decision
