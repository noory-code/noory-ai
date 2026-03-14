---
name: init
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

## Step 1 — 정보 수집

사용자에게 두 가지를 확인한다:

1. **저장 경로** — `.lib.pen` 파일을 저장할 디렉토리 (예: `apps/myapp/pencil/`, `pencil/`)
2. **앱 이름** — 파일명에 사용 (예: `myapp` → `myapp-design-guide.lib.pen`)

> 시드 컬러와 로고는 이후 단계에서 별도로 수집한다.

## Step 2 — 새 .lib.pen 파일 생성

```
mcp__pencil__open_document("new")
```

파일 저장 경로: `<Step 1에서 결정한 경로>/<appname>-design-guide.lib.pen`

> Pencil이 파일명을 요청하면 `<appname>-design-guide`로 입력하고, 저장 시 확장자를 `.lib.pen`으로 지정한다.

## Step 3 — 시드 컬러 설정

`change-seed-color` 스킬의 전체 절차를 실행한다.

> `change-seed-color` 스킬 참조.

## Step 4 — Dart 코드 생성

사용자에게 Flutter 프로젝트의 lib 경로를 확인한다 (예: `lib/src/design/`, `lib/core/theme/`).

```bash
python3 pencil_material/pencil/md3calc/gen_dart.py <seed_hex> --out <flutter_lib_path>
```

생성 파일:
- `semantic_color_palette.dart` — 팔레트 원시값
- `theme_colors.dart` — ColorScheme 6개 variant
- `theme.dart` — AppTheme (ThemeData)
- `tokens.dart` — Spacing / Radius / Elevation 등

> `theme.dart`는 `google_fonts` 패키지를 사용한다. 프로젝트 `pubspec.yaml`에 추가 필요:
> ```yaml
> dependencies:
>   google_fonts: ^6.2.1
> ```

## Step 5 — 로고 설정

`change-logo` 스킬의 전체 절차를 실행한다.

> `change-logo` 스킬 참조.

## Step 6 — 프로젝트 design 스킬 생성

`pencil-material:design-guide`를 베이스로 삼아 이 프로젝트 전용 `design` 스킬 파일을 생성한다.
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

`pencil-material:design-guide`의 M3 규칙과 프롬프트 생성 방법론을 베이스로 한다.

## 역할

사용자가 화면 디자인을 요청하면:
1. `pencil-material:design-guide`의 M3 규칙 + 아래 프로젝트 고유 규칙 적용
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

`pencil-material:design-guide`의 프롬프트 생성 방법론을 따른다.
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
