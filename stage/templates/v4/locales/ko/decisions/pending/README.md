# 작업 중 결정 레코드

이 디렉터리는 작업 중 결정 지점에서 내린 결정 레코드의 SSOT를 소유한다.

작업 중 결정은 공식 진실이 아니다. 승인되면 `official/decisions/records/`로 승격된다.

## 규칙

- 결정 레코드 하나는 파일 하나를 가진다.
- frontmatter `work_item`은 결정 지점이 발생한 작업 항목과 일치한다.
- 레코드는 질문, 선택지, 적용된 원칙, 선택한 방향을 기술한다.
- 작업 항목의 `decision_refs`는 그 작업의 결정 레코드를 나열한다. 모든 작업에 결정 지점이 있는 것은 아니므로 `decision_refs`는 선택 사항이지만, 기록된 결정은 반드시 되돌아 링크되어야 한다.
- 링크된 결정이 아직 `status: open`인 동안 작업 항목은 완료될 수 없다 — 먼저 결정한다.
- venue 정책 예외를 승인하는 결정은 frontmatter에 `authorizes: venue_exception`을 선언한다. 등록과 감사는 decided/promoted 상태의 그런 레코드에서만 예외를 인정한다.

