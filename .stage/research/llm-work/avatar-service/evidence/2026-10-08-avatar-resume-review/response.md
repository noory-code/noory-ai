**판정: REVISE.** 고쳐야 할 결함은 하나입니다. 내려받는 이어보기 파일에 실제로 담기는 내용을 화면 안내와 README가 다 밝히지 않습니다. 파일이 이 컴퓨터 밖으로 나가는 경로는 없고, 안내가 실제 내용보다 좁다는 문제입니다.

**1. [필수] 이어보기 파일에 담기는 내용 안내가 실제보다 좁음**
- `avatar/web/analysis.mjs`의 `normalize()`는 가져온 JSON 전체를 깊은 복사합니다. `avatar/web/session.mjs`의 `sessionText()`는 그 결과(`verified.data`)를 `records`로 그대로 직렬화합니다.
- 그래서 파일에는 화면 안내에 없는 항목도 들어갑니다. `projections`(외부 이력), `review_candidates`, 기준의 `events`와 버전별 `reason`, `origin.source_ref` 출처 경로, 가져온 파일에 있던 모르는 필드까지 포함됩니다. `projections`가 `normalize` → `restoreSession` → `JSON.stringify` 순서로 그대로 저장되는 것을 코드에서 확인했습니다.
- 그런데 `avatar/web/app.mjs`의 `showReport()`는 선택, 기준, 메모, AI 해석, 선택과 이유 원문만 안내합니다. `avatar/README.md`도 "choice and criterion source text, notes, and any selected AI interpretation"이라고만 씁니다.
- 기록 화면은 외부 이력을 "이 분석에서 사용하지 않는다"고 안내합니다. 그래서 사용자는 외부 이력이 파일에도 저장되지 않는다고 생각하기 쉽습니다.
- **수정안 (a), 권장:** `showReport()` 안내 문구에 `'외부 이력 ' + data.projections.length + '개, 출처 경로, 기준 변경 이력'`을 추가합니다. README의 같은 문장에도 "attached history projections, origin paths, criterion events and any extra fields from the imported file"을 넣습니다.
- **수정안 (b):** `sessionText()`에서 저장할 필드를 목록으로 정해 그것만 남깁니다. 다만 `review_candidates`를 빼면 다시 열었을 때 '나란히 볼 선택' 결과가 달라집니다. 그래서 (a)가 더 안전합니다.

**2. [필수, 작은 수정] 조사 오류**
- `app.mjs`의 `showReport()`에서 AI 결과가 있으면 문구가 "메모 N개와 AI 해석를 JSON 파일에…"로 나옵니다.
- 수정: `(aiResult ? '와 AI 해석을' : '를')`

**통과로 본 항목**
- 파일 내려받기와 파일 고르기는 모두 사용자가 직접 해야 합니다. 내려받기는 확인 체크박스를 켜야만 활성화됩니다.
- 이어보기 경로에는 네트워크 요청, 업로드, 자동 저장이 없습니다.
- `restoreSession`은 상태를 바꾸기 전에 먼저 검사하고 실패하면 예외를 던집니다. 그래서 가져오기에 실패하면 기존 화면이 그대로 남습니다.
- 메모 키는 현재 반복 기준 ref와, AI 결과가 있을 때의 `ai`만 허용합니다. `__proto__`도 거부됩니다.
- `evidence_ids`는 `selected_ids` 안에 있어야 하고, `selected_ids`는 저장된 선택 ID 안에 있어야 합니다.
- 기준을 자동으로 확인하거나 DB에 쓰는 경로는 없습니다. 기준은 "불러온 시점에 확인됨"이라는 스냅샷 문구로 표시되고, 다시 연 뒤에는 최신 상태를 Avatar에서 확인하라고 안내합니다.
- 화면에 넣는 사용자 텍스트는 모두 `escape`를 거치고, 리포트 Markdown은 줄바꿈을 정리합니다. `analyzed_at`에 줄바꿈이 있으면 거부됩니다.
- 이어보기를 열면 `revision++`가 되어, 진행 중이던 AI 응답이 도착해도 버려지고 오류 알림도 뜨지 않습니다. `finally`에서 `aiBusy`도 해제됩니다.
- `/session.mjs`와 `/text.mjs`가 서버의 `ASSETS`에 연결되어 있습니다.

**선택 제안 (결함은 아님)**
- `saved_at`을 저장하지만 화면에 보여주지 않습니다. `source-label`에 저장 시각을 표시하면 오래된 스냅샷이라는 점이 더 분명해집니다.
- 누군가 `source: 'demo'`로 손본 파일을 열면 실제 기록에도 "실제 사용자 기록이 아닙니다"라는 문구가 붙습니다. 예시 데이터와 같은지 비교하거나 "저장한 예시"로 표시하는 방법을 고려해 보세요.
- 메모 개수에 빈 문자열 메모도 들어갑니다. `filter(v => v)` 후에 세면 됩니다.
- 실시간 AI 결과가 복원 한도(인사이트 3개 초과, 한계 5개 초과, 2,000자 초과, ID 안 줄바꿈)를 넘으면 저장이 실패합니다. 이때 "Avatar 작업 파일을 골라주세요"라는 맞지 않는 메시지가 뜹니다. 서버 쪽 한도와 맞추거나 저장 전용 오류 문구를 두는 편이 좋습니다.
- README의 "download the report before closing" 문장은 틀리지는 않지만, 이제 이어보기 파일 안내도 함께 적는 것이 좋습니다. "Users can add corrections to the downloaded report"도 실제로는 뷰어에서 메모를 더하는 방식입니다.

**검토 한계**
- `avatar/web/text.mjs`가 제공되지 않아, `escape`가 `"`와 `'`를 처리하는지 확인하지 못했습니다. `selectionHtml`의 `value="…"` 속성 안전성이 여기에 달려 있습니다.
- `content.mjs`(예시의 `@4` ref), `avatar_analysis.py`, `avatar_view.show`의 출력 형식, CSS는 보지 못했습니다.
- 테스트는 직접 돌리지 않았습니다. 감독자가 보고한 결과(RED 후 집중 테스트 2개 GREEN, Python 47개, 계약 7개, Node 24개, 브라우저 저장·다시 열기)를 그대로 신뢰했습니다.
- 공개 갤러리와 창작 이야기는 요청대로 다시 검토하지 않았습니다.
