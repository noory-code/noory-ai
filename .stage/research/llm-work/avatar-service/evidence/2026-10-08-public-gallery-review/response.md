**판정: PASS**

보여주신 소스 안에서는 배포를 막아야 할 결함이 없습니다.

**확인한 내용**
- **개인 기록 도구 제외 (`avatar_public.py`)**: 공개 빌드는 정해진 `FILES` 목록만 복사합니다. 그래서 `app.mjs`, `ai.mjs`, `analysis.mjs`, `content.mjs`, DB 파일은 결과물에 들어가지 않습니다.
- **출력 폴더 보호**: 출력 폴더가 이미 있으면 `FileExistsError`로 빌드를 거부합니다. 기존 파일을 합치거나 지우지 않습니다.
- **CSP 메타 태그**: 두 HTML 모두 `<head>` 바로 뒤, 스크립트보다 앞에 CSP 메타 태그가 들어가고 `connect-src 'none'`이 적용됩니다. `frame-ancestors`는 메타 태그에서 무시되므로 미리보기 서버의 응답 헤더로만 보내는 것이 맞습니다.
- **기록·요청 거부**: 미리보기 서버는 목록에 없는 경로를 404로, POST/PUT/PATCH/DELETE를 405로 거부합니다. `/../avatar.db` 같은 경로도 목록에 없어서 404가 됩니다.
- **localhost 자동 확인 없음**: `start.mjs`의 `127.0.0.1:4173`은 사용자가 직접 눌러야 하는 링크(`target=_blank rel="noopener noreferrer"`)일 뿐입니다. fetch, 이미지, preconnect 요청은 없고, 있더라도 CSP가 막습니다.
- **공개 갤러리는 읽기 전용 (`stories.mjs`)**: 공개 화면에서는 편집, 취소, 초기화, 제출, 입력이 모두 막히고 편집 버튼도 표시되지 않습니다. 로컬 화면에는 `data-surface`가 없으므로 기존처럼 수정 내용이 유지됩니다.
- **escape() 분리 후 기존 개인 뷰어**: `ai.mjs`가 `export {escape}`로 다시 내보내므로 기존 import 경로가 그대로 동작합니다. `avatar_web.py`의 `ASSETS`에 `/text.mjs`가 있어서 모듈 404도 생기지 않습니다.
- **가이드와 README·`avatar_web.py`의 일치**: 다음 항목이 모두 맞습니다.
  - 기본 포트 4173
  - `show --json`으로 JSON을 만들어 직접 가져오기
  - `--ai claude` 옵션과 동의 체크박스(`ai-consent`), 계정 사용량 안내
  - 미배포 상태와 소스가 필요하다는 안내, Python 3.9 이상 (`removeprefix`도 3.9 이상이 필요해 조건이 같음)
  - 개인 뷰어 UI는 한국어 전용, 기록은 탭에만 남는다는 안내

**결함으로 보지 않은 것**
- **공개 서버에 Host 검사가 없음**: 가상 정적 콘텐츠만 제공하므로 문제가 없습니다.
- **하위 경로 호스팅, `.mjs` MIME 설정, 광고 CSP**: 요청하신 대로 별도 설정 대상이며 README에도 적혀 있습니다.
- **`/stories`는 두 언어를 지원하는데 가이드에는 "한국어 전용"으로 적힌 점**: README가 나머지 뷰어를 한국어로 설명하는 것과 같아서 문제가 아닙니다.

**선택 제안 (승인 조건 아님)**
1. `avatar_public.py`: 파일 쓰기 도중 실패하면 일부만 만들어진 폴더가 남습니다. 임시 폴더에 쓴 뒤 `rename`으로 옮기면 깔끔합니다.
2. `test_avatar_public.py`: `start.html`에도 CSP 메타 태그가 들어갔는지 확인하는 줄을 추가하면 좋습니다. 지금은 `index.html`만 확인합니다.
3. `stories.mjs`: 공개 화면의 로고 링크(`href="/"`)에도 `?lang=`을 붙이면 영어 화면에서 로고를 눌러도 언어가 유지됩니다.

**검토의 한계**
- 테스트와 브라우저는 직접 실행하지 않았습니다. 실제 CSP 위반 여부, 예를 들어 `illustrations.mjs`가 만드는 SVG의 인라인 `style` 차단 여부는 확인하지 못했습니다. 다만 로컬 뷰어도 같은 `style-src 'self'`를 쓰므로 이번 변경으로 생긴 문제는 아닙니다.
- 아래 두 가지는 해당 파일을 받지 못해 확인하지 못했고, 다르게 나오면 판정이 REVISE로 바뀝니다.
  - `app.mjs`의 가져오기 버튼 문구가 가이드의 '기록 가져오기'와 같은지
  - `story-content.mjs`의 `words.ko`와 `words.en` 양쪽에 `publicStart`와 `publicMethod`가 있는지. 없으면 공개 화면에 "undefined"가 나옵니다. 각 파일에서 해당 문구와 키를 검색하면 바로 확인할 수 있습니다.
- `text.mjs`의 `escape`는 null을 빈 문자열로 바꿉니다. 분리 전 구현과 같은지는 이전 버전이 없어 비교하지 못했고, 보고받은 Node 테스트 22개 통과에 기대고 있습니다.
