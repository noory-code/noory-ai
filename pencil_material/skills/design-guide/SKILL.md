---
name: design-guide
description: >
  Design screens using the Material Design 3 guide library.
  Triggers when the user asks to design a screen, create a UI, add a new screen,
  or build a layout using the Material Design 3 components.
user-invocable: true
---

# Design Guide — M3 Expressive

`material-design-guide.lib.pen`을 import한 `.pen` 파일에서 화면을 디자인할 때 사용하는 스킬.
이 라이브러리의 Context 노드(`M3 Expressive Guide`)를 참조해서 컴포넌트를 올바르게 사용한다.

## Target file

사용자가 현재 작업 중인 앱의 `.pen` 파일 (예: `myapp-design-guide.pen`)
반드시 `material-design-guide.lib.pen`을 import하고 있어야 한다.

## Context 노드 참조

`material-design-guide.lib.pen` 안에 있는 **"M3 Expressive Guide"** 프레임의 Context 노드에
각 컴포넌트의 사용 규칙, 계층 구조, Do/Don't가 정의되어 있다.

디자인 전에 반드시 이 Context를 읽고 아래 규칙을 따른다:

### 컴포넌트 사용 규칙 요약

| 컴포넌트 | 규칙 |
|---------|------|
| **Buttons** | 화면당 Filled는 1개만. 계층: Filled > FilledTonal > Elevated > Outlined > Text |
| **FAB** | 화면당 1개만. 가장 중요한 단일 액션에만 사용 |
| **NavigationBar** | 모바일, 2~5개 destination. 항상 화면 하단 고정 |
| **NavigationRail** | 태블릿/데스크탑 전용 |
| **NavigationDrawer** | 5개 이상 destination일 때 |
| **TextFields** | 기본은 Filled. 복잡한 배경에서만 Outlined |
| **Cards** | Elevated: 평면 배경, Filled: 미묘한 그룹핑, Outlined: 복잡한 배경 |
| **Chips** | Assist: 제안 액션, Filter: 필터링, Input: 사용자 입력값, Suggestion: 동적 옵션 |
| **Selection** | Checkbox: 복수 선택, Radio: 목록에서 단일 선택, Switch: On/Off 토글 |
| **Snackbar** | 방해 없는 간단한 메시지. 중요한 결정은 Dialog 사용 |
| **Colors** | 항상 Color Role 변수 사용 ($primary, $surface 등). 절대 하드코딩 금지 |

## Workflow

### Step 1 — 작업 파일 준비

```
mcp__pencil__get_editor_state()
```

현재 열린 파일 상태를 확인한다:

- **화면 작업용 `.pen` 파일이 열려 있고** `<appname>-design-guide.lib.pen`을 import하고 있으면 → Step 2로 진행
- **파일이 없거나 import가 없으면** → 아래 절차 안내:
  1. Pencil에서 새 `.pen` 파일 생성 (확장자 `.pen`, 라이브러리 아님)
  2. 해당 파일에 `<appname>-design-guide.lib.pen` import 추가
  3. 파일을 열고 다시 스킬 실행

### Step 2 — 디자인 요구사항 파악

사용자가 요청한 화면/컴포넌트를 파악하고:
- 어떤 컴포넌트가 필요한지
- M3 Expressive Guide의 규칙에 맞는지
- 사용할 컴포넌트 ID (라이브러리에서 import된 것)

### Step 3 — 빈 공간 찾기

```
mcp__pencil__find_empty_space_on_canvas(direction: "right", width: ..., height: ..., padding: 100)
```

### Step 4 — Placeholder 프레임 생성

작업할 모든 프레임을 먼저 `placeholder: true`로 생성한다.

```javascript
screen=I(document, {type: "ref", ref: "dnJUo", placeholder: true, x: ..., y: ...})
```

폼팩터별 프레임 컴포넌트 ID (라이브러리에서 import):
- Mobile 390px: `dnJUo` (Frame/Mobile/390)
- Tablet 768px: `P7T42` (Frame/Tablet/768)
- Desktop 1440px: `YzwZK` (Frame/Desktop/1440)

### Step 5 — 컴포넌트 조립

M3 Expressive Guide 규칙에 따라 컴포넌트를 배치한다.

**자주 쓰는 컴포넌트 ID:**

| 컴포넌트 | ID |
|---------|-----|
| TopAppBar/Small | `Mv3K9` |
| TopAppBar/CenterAligned | `Z4NCN` |
| NavigationBar/3Items | `ItYES` |
| NavigationBar/4Items | `7PeTi` |
| NavigationBar/5Items | `0StZU` |
| FAB/Default | `9XN45` |
| FAB/Extended | `7Gdu4` |
| Buttons/Filled/Rounded/lg | `SgybC` |
| Buttons/Filled/Rounded/md | `wq43H` |
| Buttons/FilledTonal/Rounded/md | `f8Ndk` |
| Buttons/Outlined/Rounded/md | `JTH1z` |
| Buttons/Text/Rounded/md | `hgI1q` |
| TextFields/Filled/Empty | `1gP7O` |
| TextFields/Outlined/Empty | `j0QDR` |
| Lists/OneLineItem | `HoJ5r` |
| Lists/TwoLineItem | `X6KcN` |
| Lists/ThreeLineItem | `AIucm` |
| Cards/Elevated | `WTD0O` |
| Cards/Filled | `r90Tz` |
| Cards/Outlined | `y9sA7` |
| Switch/On | `4cwpx` |
| Switch/Off | `wKKuZ` |
| Checkbox/Checked | `WMMjV` |
| Checkbox/Unchecked | `FgBKf` |
| RadioButton/Selected | `zAPPR` |
| Divider/Full | `YQxB2` |
| Snackbar/TextOnly | `BR6ZB` |

### Step 6 — 색상 변수 사용

하드코딩 금지. 항상 라이브러리 변수 참조:

```javascript
// 올바른 예
{fill: "$primary"}
{fill: "$surface"}
{fill: "$onSurface"}
{fill: "$primaryContainer"}

// 잘못된 예 ❌
{fill: "#6750A4"}
```

### Step 7 — 검증

```
mcp__pencil__get_screenshot(nodeId)
```

완료 후 placeholder 제거:

```javascript
U("frameId", {placeholder: false})
```

## 화면 타입별 레이아웃 패턴

### 로그인 / 온보딩
```
Frame/Mobile/390
  └ Hero 영역 (gradient, ~40% 높이)
      └ 앱 아이콘 + 앱 이름
  └ Form 카드 (cornerRadius [28,28,0,0], surface)
      └ 제목 + 부제목
      └ TextFields
      └ Filled 버튼 (full-width, 가장 중요한 액션)
      └ Text 버튼 (보조 액션)
```

### 홈 / 리스트
```
Frame/Mobile/390
  └ TopAppBar/Small (상단 고정)
  └ 스크롤 콘텐츠 영역
      └ List 아이템들
  └ FAB (우측 하단, y: 화면높이-100)
  └ NavigationBar (하단 고정)
```

### 설정
```
Frame/Mobile/390
  └ TopAppBar/Small
  └ 섹션 레이블 (14px, $primary)
  └ ListItem + Switch 행
  └ Divider
  └ 다음 섹션 반복
```

### 디테일 / 상세
```
Frame/Mobile/390
  └ TopAppBar/Medium 또는 Large (뒤로가기 포함)
  └ 콘텐츠 카드
  └ FAB/Extended (주요 액션)
```
