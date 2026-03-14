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

## Step 4 — 로고 설정

`change-logo` 스킬의 전체 절차를 실행한다.

> `change-logo` 스킬 참조.

## Step 5 — 프로젝트 design-guide 스킬 생성

`pencil-material:design-guide`를 베이스로 삼아 이 프로젝트 전용 `design-guide` 스킬 파일을 생성한다.

저장 경로: `<프로젝트 루트>/.claude-plugin/skills/design-guide/SKILL.md`

파일 내용:
```markdown
---
name: design-guide
description: >
  Design screens for <appname> using the app design guide library.
  Triggers when the user asks to design a screen, create a UI, or build a layout.
user-invocable: true
---

# Design Guide — <appname>

`pencil-material:design-guide` 스킬을 베이스로 한다.
아래는 이 프로젝트에 특화된 추가 규칙이다.

## Target file

`<appname>-design-guide.lib.pen`을 import한 화면 작업용 `.pen` 파일.

## 프로젝트 고유 규칙

> 이 섹션은 프로젝트에 맞게 채워야 한다:
> - 앱 고유 컴포넌트 및 ID
> - 반복 사용되는 화면 패턴
> - 브랜드 컬러 사용 규칙 (시드 컬러 기반)
> - 타이포그래피 / 간격 특이사항

## Workflow

`pencil-material:design-guide` 스킬의 전체 워크플로우를 따른다.
위 프로젝트 고유 규칙을 추가로 적용한다.
```

> 생성 후 사용자에게 "프로젝트 고유 규칙 섹션을 채워달라"고 안내한다.

## Step 6 — 결과 안내

완료 후 사용자에게 보고:

```
✓ <appname>-design-guide.lib.pen 생성 완료

- Seed color: <hex>
- Primary: <primary/40>
- 로고: 적용 완료
- 프로젝트 design-guide 스킬: .claude-plugin/skills/design-guide/SKILL.md

다음 단계:
  1. SKILL.md의 "프로젝트 고유 규칙" 섹션을 앱에 맞게 작성
  2. Pencil에서 새 .pen 파일 생성 (예: <appname>-screens.pen)
  3. 해당 파일에 <appname>-design-guide.lib.pen import 추가
  4. /<appname>:design-guide 로 화면 디자인 시작
```
