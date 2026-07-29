---
id: W-00000069
title: 드라이버를 이 저장소에서 처음으로 실제 실행한다
kind: qa
venue: codex
source:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000072
promotion: not_applicable
review: not_required
scope: .stage/settings.json
promotes:
decision_refs:
---

# W-00000069 드라이버를 이 저장소에서 처음으로 실제 실행한다

## Purpose

드라이버는 코드로는 완성돼 있지만 이 저장소에서 한 번도 돌지 않았다. 실행자 설정을 채우고 감독 모드로 한 번 태워, 선택→실행→검증→독립 리뷰 경로가 실제로 이어지는지 확인한다.

## Scope

이 저장소의 `.stage/settings.json` 에 `executors` (venue → 실행 명령) 를 채우고,
`stage/scripts/drive.py` 를 W-00000069 대상으로 dry-run → `--execute` 순서로 돌린다.
자식 W-00000070 이 실행 대상이 된다.

플러그인 코드는 이 카드에서 고치지 않는다. 실행 중에 드라이버의 결함이 드러나면 별도 카드로
등록한다.

## Success criteria

- dry-run 이 선택 항목·실행자 명령·acceptance 명령·독립 리뷰어를 모두 해결해 출력한다.
- `--execute` 한 번이 실행자 → acceptance → 반대 venue 리뷰어까지 끝까지 간다.
- 실행 결과(성공이든 실패든)와 막힌 지점이 이 카드의 `## Verification` 에 기록된다.
- 자식 W-00000070 이 실행 산출물로 완료 후보에 오른다.

## Related truth

- 드라이버 사양: `stage/docs/SCHEMA_V4.md` — `### Supervised driver and executor settings`.
- 실행자 설정의 모양은 `.stage/settings.json` 의 `review.reviewers` 와 같다 (venue → 명령).

**위험**: `claude -p` 를 실행자로 쓴 전례가 없다. 헤드리스 세션이 파일을 쓸 권한을 갖는지부터
미확인이다. 막히면 그 지점을 기록하는 것이 이 카드의 결과다 — 우회해서 손으로 끝내지 않는다.

## Progress

### 실행 시나리오와 결과 (2026-07-25)

드라이버를 이 저장소에서 처음으로 실제 실행했다. 대상은 이 카드, 실행 대상 자식은 W-00000070
(스킬 작성, claude venue). 감독 모드로 세 스텝을 돌렸다.

**사전 확인 (dry-run).** 부작용 없이 선택 항목·실행자 명령·검증 명령 셋·반대 venue 리뷰어를
모두 해결해 출력했다. `.stage/.runtime/` 도 만들지 않았다.

**1스텝.** 실행자(헤드리스 claude, `--permission-mode acceptEdits`)가 카드만 읽고 116줄짜리
스킬을 실제로 만들었다. 검증 셋 통과. 리뷰어가 P1 둘로 막았다.

**2스텝.** 카드에 지적을 담아 되돌렸더니 실행자가 그것만 읽고 고쳤다. 시도 2회차·지문 비교
정상. 리뷰어가 다시 막았다.

**3스텝.** 통과. 비차단 지적 하나만 남았고 손으로 반영했다.

| 확인 항목 | 결과 |
|---|---|
| 말단 자식 선택 | 정상 — 세 번 모두 W-00000070 |
| 실행자에게 항목 전달 | 정상 — 환경 변수로 카드 경로가 전달돼 실제로 읽혔다 |
| 헤드리스 실행자의 파일 쓰기 | 정상 |
| 검증 명령 실행 | 정상 — 세 스텝 모두 |
| 반대 venue 독립 리뷰 | 정상 — 매번 실제 판정을 냈고 두 번 막았다 |
| 재시도(시도 횟수·지문) | 정상 |
| 커밋·닫기·부모 전진을 하지 않음 | 정상 — 전부 사람이 했다 |
| 되먹임 고리의 수렴 | 3라운드에 수렴 |

**드러난 결함** (전부 실전 실행에서만 나왔다):

| 결함 | 처리 |
|---|---|
| 실행자가 자기 작업 항목을 알 수 없음 | W-00000071 완료 (0.42.2) |
| 코덱스 실행자가 읽기 전용으로 뜸 | 이 카드에서 수정 (`--write`) |
| 스킬의 플러그인 경로 표기가 동작하지 않음 | DE-00000031 확정 · W-00000074 |
| 감독 모드 리뷰어와 진전 판정이 새 파일·색인 변경을 못 봄 | W-00000073 |
| 무인 모드가 기록 커밋 실패를 삼키고 부모 감사를 건너뜀 | W-00000075 |

**아직 확인하지 않은 것**: 코덱스 venue 실행자. 이번 실행 대상이 claude venue 였으므로 코덱스
쪽 실행 경로는 설정만 고쳤고 실제로 돌려보지 않았다.


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
