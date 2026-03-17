---
name: pmf-init
description: >
  Initialize a new app design guide .lib.pen file.
  Triggers when the user asks to initialize, create a new design guide,
  or set up a new app's design system in Pencil.
user-invocable: true
---

# Init — App Design Guide

앱별 디자인 가이드 `.lib.pen` 파일을 생성한다.
`.lib.pen` 확장자를 사용해야 Pencil에서 다른 `.pen` 파일의 라이브러리로 import할 수 있다.
`material-design-guide.lib.pen`은 공용 라이브러리로 유지하고, 앱마다 별도 파일을 생성한다.

## Step 0 — 환경 검증

두 그룹으로 나누어 검증한다. **그룹 A**는 파일 작업에 필요하고, **그룹 B**는 Pencil/Dart 작업에 필요하다.
그룹 A가 실패하면 즉시 중단. 그룹 B는 Step 2 완료 후(Pencil 파일 열기 직전) 검증한다.

### 그룹 A — 파일 작업 전제 (Step 0에서 검증)

#### A-1. Python 3.9+ 설치 확인

```bash
python3 --version
```

- Python 3.9 이상 → 다음 검증으로
- 없거나 버전 미달 → **중단**:
  > "Python 3.9 이상이 필요합니다. 설치 후 다시 시도해주세요."

#### A-2. materialyoucolor 패키지 확인

```bash
python3 -c "import materialyoucolor; print('ok')"
```

- `ok` 출력 → 다음 검증으로
- ImportError → **중단**:
  > "pip install materialyoucolor 를 실행한 후 다시 시도해주세요."

#### A-3. Python 스크립트 파일 존재 확인

```bash
python3 -c "import pathlib; root=pathlib.Path('${CLAUDE_PLUGIN_ROOT}'); [exit(1) for p in ['pencil/md3calc/hct_palette.py','pencil/md3calc/gen_dart.py'] if not (root/p).exists()]"
```

- 두 파일 모두 존재 → **그룹 A 통과**
- 없음 → **중단**:
  > "플러그인 파일을 찾을 수 없습니다. pencil-m3-flutter 플러그인이 설치되어 있는지 확인해주세요.
  > `/plugin install pencil-m3-flutter@noory-ai`"

그룹 A 통과 시: `✓ 환경 확인 완료. 설정을 시작합니다.` 출력 후 Step 1로 진행.

### 그룹 B — Pencil MCP 연결 (Step 2-2에서 검증)

> Pencil은 파일 복사 이후에만 필요하다. Step 2-2에서 검증한다.

---

## Step 1 — 정보 수집

사용자에게 세 가지를 선택지로 확인한다. 각 항목에 기본 추천값을 제시하고 직접 입력 옵션도 포함한다.

1. **저장 경로** — `.lib.pen` 파일을 저장할 디렉토리:
   - `pencil/` (권장 — 프로젝트 루트 하위)
   - `apps/<appname>/pencil/`
   - 직접 입력

2. **앱 이름** — 파일명에 사용 (프로젝트 디렉토리명에서 기본값 추출):
   - `<프로젝트 디렉토리명>` (권장)
   - 직접 입력

3. **Flutter lib 경로** — Dart 코드를 생성할 위치:
   - `lib/src/design/` (권장)
   - `lib/core/theme/`
   - 직접 입력

> 시드 컬러와 로고는 이후 단계에서 별도로 수집한다.
> 각 단계 완료 후 결과를 보여주고 다음 단계로 넘어간다. 단계를 건너뛰지 않는다.

## Step 2 — 앱 디자인 가이드 파일 생성

`material-design-guide.lib.pen`을 복사해서 앱 전용 라이브러리 파일로 만든다.
빈 파일을 만들면 M3 컴포넌트/변수가 없으므로 반드시 복사 방식을 사용한다.

### 2-1. 파일 복사 (Pencil 불필요)

```bash
cp ${CLAUDE_PLUGIN_ROOT}/pencil/material-design-guide.lib.pen "<저장 경로>/<appname>-design-guide.lib.pen"
```

> 복사 방식을 사용하면 material-design-guide.lib.pen의 166개 M3 컴포넌트와 Color Scheme 변수가 모두 포함된다.

완료 후 보고: `✓ <appname>-design-guide.lib.pen 파일 복사 완료.`

### 2-2. Pencil MCP 연결 확인 (그룹 B 검증)

파일을 열기 전에 Pencil이 실행 중인지 확인한다:

```
mcp__pencil__get_editor_state()
```

- 응답 성공 → 2-3 진행
- 실패 → **중단**:
  > "Pencil MCP 연결이 안 됩니다. 다음을 확인해주세요:
  > 1. Pencil 앱이 실행 중인지 확인
  > 2. Pencil → Settings → MCP Server에서 서버 상태 확인
  > 3. Claude Code를 재시작하거나 `/mcp` 명령으로 재연결
  > 연결 후 이 스킬을 다시 실행해주세요."

### 2-3. Pencil에서 파일 열기

```
mcp__pencil__open_document("<저장 경로>/<appname>-design-guide.lib.pen")
```

완료 후 보고: `✓ <appname>-design-guide.lib.pen Pencil에서 열림. 다음: 시드 컬러 설정`

## Step 3 — 시드 컬러 설정 + Dart 코드 생성

`pmf-change-seed-color` 스킬의 전체 절차를 실행한다.
대상 파일은 Step 2에서 생성한 `<appname>-design-guide.lib.pen` (현재 에디터에 열려 있음).
Step 1에서 수집한 `flutter_lib_path`를 컨텍스트로 전달한다.

`pmf-change-seed-color`가 Pencil 변수 업데이트 + Dart 파일 생성까지 완료한다.
Dart 생성은 `.pen` 파일이 SSOT — `get_variables()` → `--from-json`으로 실제 변수값 기반 생성.
`--barrel <appname>_ui` 옵션을 포함해 배럴 파일도 함께 생성한다:
- `semantic_color_palette.dart` — 팔레트 원시값
- `theme_colors.dart` — ColorScheme 6개 variant
- `theme.dart` — AppTheme (ThemeData)
- `tokens.dart` — Spacing / Radius / Elevation 등
- `<appname>_ui.dart` — 배럴 파일 (위 4개를 한 번에 import)

> `theme.dart`는 `google_fonts` 패키지를 사용한다. 프로젝트 `pubspec.yaml`에 추가 필요:
> ```yaml
> dependencies:
>   google_fonts: ^6.2.1
> ```

완료 후 보고: `✓ 시드 컬러 + Dart 코드 생성 완료. 다음: 로고 설정`

## Step 4 — 로고 설정

`pmf-change-logo` 스킬의 전체 절차를 실행한다.

> `pmf-change-logo` 스킬 참조.

완료 후 보고: `✓ 로고 설정 완료. 다음: 프로젝트 design 스킬 생성`

## Step 5 — Flutter workspace 등록 (해당 시)

루트 `pubspec.yaml`에 `workspace:` 섹션이 있는지 확인한다:

```bash
grep -q "workspace:" pubspec.yaml 2>/dev/null && echo "workspace project" || echo "standalone"
```

- workspace 프로젝트인 경우 → 루트 `pubspec.yaml`의 `workspace:` 목록에 앱 경로 추가 안내:
  > "루트 pubspec.yaml의 workspace: 목록에 앱 경로를 추가해주세요."
- standalone 프로젝트 → 이 단계 건너뛰기

## Step 6 — 프로젝트 design 스킬 생성

`pencil-m3-flutter:design-guide`를 베이스로 삼아 이 프로젝트 전용 `design` 스킬 파일을 생성한다.
이 스킬의 역할: **사용자 요청 → Pencil AI 채팅창에 붙여넣을 프롬프트 텍스트 출력**.

저장 경로: `<프로젝트 루트>/.claude-plugin/skills/design/SKILL.md`

파일 내용:
```markdown
---
name: design
description: >
  Generate a Pencil AI prompt for designing screens of <appname>.
  Triggers when the user asks to design a screen, create a UI, or build a layout.
user-invocable: true
---

# Design — <appname>

`pencil-m3-flutter:design-guide`의 M3 규칙과 프롬프트 생성 방법론을 베이스로 한다.

## 역할

사용자가 화면 디자인을 요청하면:
1. `pencil-m3-flutter:design-guide`의 M3 규칙 + 아래 프로젝트 고유 규칙 적용
2. **Pencil AI 채팅창에 붙여넣을 프롬프트 텍스트를 출력**

> Claude Code가 직접 Pencil을 조작하지 않는다.
> 출력된 프롬프트를 복사해서 Pencil AI 채팅창에 붙여넣으면 된다.

## 프로젝트 정보

- Pencil 라이브러리: `<pen_file_path>/<appname>-design-guide.lib.pen`
- 화면 작업 파일: `<pen_file_path>/<appname>-screens.pen` (또는 사용자 지정)
- Flutter 테마 코드: `<flutter_lib_path>/`

## 프로젝트 고유 규칙

> 이 섹션을 프로젝트에 맞게 채워라:
> - 앱 고유 컴포넌트 및 ID (<appname>-design-guide.lib.pen 에 정의된 것)
> - 반복 사용되는 화면 패턴
> - 브랜드 컬러 / 타이포그래피 특이사항

## 프롬프트 출력 형식

`pencil-m3-flutter:design-guide`의 프롬프트 생성 방법론을 따른다.
아래 템플릿에 화면 내용을 채워 출력한다:

\`\`\`
<appname>-screens.pen 에 <화면 이름> 화면을 추가해줘.

## 공통 규칙
- 색상: 절대 하드코딩 금지. $primary, $surface, $onSurface 등 Color Role 변수만 사용
- 폼팩터: Frame/Mobile/390 (ID: dnJUo)
- 캔버스 빈 공간에 배치 (간격 100px)

## 레이아웃
<화면 구조>

## 컴포넌트
<컴포넌트 목록과 ID>

## 프로젝트 고유 규칙
<위 섹션의 규칙 적용>
\`\`\`
```

> 생성 후 사용자에게 "프로젝트 고유 규칙 섹션을 채워달라"고 안내한다.

## Step 7 — 결과 안내

완료 후 사용자에게 보고:

```
✓ <appname>-design-guide.lib.pen 생성 완료

- Seed color: <hex>
- Primary (light): <primary/40>
- Primary (dark):  <primary/80>
- Flutter 테마 코드: <flutter_lib_path>/
- 로고: 적용 완료
- 프로젝트 design 스킬: .claude-plugin/skills/design/SKILL.md

다음 단계:
  1. SKILL.md의 "프로젝트 고유 규칙" 섹션을 앱에 맞게 작성
  2. Pencil에서 새 .pen 파일 생성 (예: <appname>-screens.pen)
  3. 해당 파일에 <appname>-design-guide.lib.pen import 추가
  4. /<appname>:design 으로 화면 디자인 시작
```
