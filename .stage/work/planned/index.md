# 계획된 작업 인덱스

이 문서는 계획된 작업 카드의 현재 인덱스를 소유한다.

카드 본문은 `work/planned/`에 있다. 이 문서는 순서, 상태, 링크만 관리한다. 작업을 시작한 카드는
`work/current/`로 이동하고(`scripts/start_work.py`), 그 행은 이 인덱스를 떠나
`work/active.md`로 간다.

## 계획된 작업

| ID | 제목 | 종류 | 상태 | 우선순위 | 부모 | 항목 |
|---|---|---|---|---|---|---|
| W-00000298 | 실제 codex 플러그인으로 codex 명령 경로 찾기를 확인한다 | qa | captured |  |  | [W-00000298/_story.md](W-00000298/_story.md) |
| W-00000299 | 클라우드에서 닫은 카드를 로컬 codex 로 표본 재검토한다 | qa | captured |  |  | [W-00000299/_story.md](W-00000299/_story.md) |

## 상태 값

- `captured`: 캡처되었지만 아직 정리되지 않음.
- `triaged`: 목적과 영향이 확인됨.
- `ready`: 실행 후보가 될 만큼 구체화됨.
- `selected`: 현재 또는 다음 작업으로 선택됨.
- `deferred`: 보류.
- `rejected`: 하지 않기로 결정.
