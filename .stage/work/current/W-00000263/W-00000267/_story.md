---
id: W-00000267
title: 플레인리를 릴리스하고 새 세션에서 한국어 답을 확인한다
kind: release
venue: claude
milestone:
autonomous: false
acceptance: []
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000267
promotion: not_applicable
review: not_required
scope: plainly/
promotes:
decision_refs:
---

# W-00000267 플레인리를 릴리스하고 새 세션에서 한국어 답을 확인한다

## Purpose

새 버전을 실제로 켠 세션에서 한국어 문장이 나아졌는지 사람이 본다.

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 두 매니페스트와 변경 기록의 버전이 같고 그 커밋이 원격에 올라간다
- 새 버전이 실제로 불러와지는 것을 관측한다
- 새 세션에서 한국어 답을 받아 보고 사람이 어색하지 않다고 확인한다

## Next action

사람이 한국어 답을 읽고 판정한다. 어색한 문장이 있으면 그대로 가져와
`plainly/output-styles/plainly.md` 의 한국어 규칙을 고친다. 없으면 이 카드를 닫고 W-00000263 을
닫는다.

함께 볼 것: 대화형 세션에서 "시스템 프롬프트에 코딩 지침이 남아 있나"를 물어 확인한다. 조립
코드는 읽었지만 실제로 남는 것을 본 적이 없다. `claude -p` 로는 안 갈린다.

## Related truth

DE-00000073 이 이 구조를 정했다. W-00000265 가 그 결정을 소유한다.

## Progress

0.5.0 을 냈다가 스타일을 하나로 줄여 0.6.0 을 냈다. 두 판 모두 커밋이 원격에 올라갔다.

설치본을 갱신하는 데 `/plugin` 메뉴로는 안 됐다. 설치 기록이 옛 버전에 못 박혀 있어서 리로드나
재시작이 새 버전을 찾지 않는다. CLI 두 줄이 필요했다.

```
claude plugin marketplace update noory-ai
claude plugin update plainly@noory-ai
```

마켓플레이스 기록이 8월 19일에 멈춰 있어서 첫 줄이 필요했고, 그것만으로는 플러그인이 안 올라가서
둘째 줄이 따로 필요했다.

스타일 이름이 바뀌었으므로 사용자 설정의 `outputStyle` 값도 `plainly:Plainly` 로 고쳤다.

## Verification

기준 세 개 중 둘이 찼다.

- 버전이 매니페스트와 변경 기록에서 같고 그 커밋이 원격에 올라갔다 — `4b190027` 이후 0.6.0.
- 새 버전이 실제로 불러와지는 것을 봤다. 설치본이 `0.6.0` 이고, 실제 설정으로 띄운 세션이
  시스템 프롬프트에 `# Output Style: plainly:Plainly` 절이 있다고 인용했다. 디버그 로그도
  `Loaded 1 output styles from plugin plainly default directory` 를 찍었다.

셋째가 남았다. 사람이 한국어 답을 읽고 어색하지 않다고 확인해야 한다. 사용자가 이 세션을 여기서
닫고 다른 곳에서 써 보겠다고 했으므로 판정은 그쪽에서 나온다.

### 2026-11-16 사람의 판정

- 셋째 기준: 사용자가 2026-11-16 에 플레인리를 두고 "ㅇㅋ 1 은 충분한듯"이라고 답했다. 그날
  사용자는 0.7.1 이 켜진 긴 작업 세션에서 Claude 의 한국어 문장을 여러 번 고쳐 줬고, 그
  지적을 바탕으로 지침을 0.7.2, 0.7.3 으로 고쳤다. 고친 지침은 새 세션 테스트에서 표 칸을
  문장으로 쓰는 쪽으로 달라졌다. 사용자의 판정은 그 과정을 본 뒤에 나왔다. 0.7.3 을 켠
  새 작업 세션에서 다시 읽어 본 것은 아니다.
- 그 사이 버전은 0.7.3 까지 올라갔다. `claude plugin list` 가 `plainly@noory-ai` 를
  `Version: 0.7.3` 으로, 저장소의 `plainly` 폴더에서 읽는다고 답한다.

### Executed at close — 2026-11-16

```
$ python3 -m unittest discover -s plainly/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 19 tests in 0.002s

OK
```

## Retrospective

[R-00000267](../../../retrospectives/R-00000267.md)

## Promotion decision

`not_applicable` — 릴리스 카드라 공식 문서로 올릴 산출물이 없다.
