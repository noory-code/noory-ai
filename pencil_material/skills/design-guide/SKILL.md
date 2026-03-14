---
name: design-guide
description: >
  Base design rules for Material Design 3 screen design using the Pencil library.
  Triggers when the user asks to design a screen, create a UI, or build a layout.
  Also used as the base layer for project-specific design skills.
user-invocable: true
---

# Design Guide — M3 Expressive (Base)

이 스킬은 두 가지 역할을 한다:

1. **직접 사용**: Claude Code가 Pencil MCP를 통해 직접 화면을 조립
2. **베이스 레이어**: 프로젝트 전용 `design` 스킬이 이 규칙을 상속해 Pencil AI 프롬프트를 생성

---

## M3 규칙 (베이스)

프로젝트 `design` 스킬은 이 섹션을 그대로 상속한다.

### 컴포넌트 사용 원칙

| 컴포넌트 | 규칙 |
|---------|------|
| **Buttons** | 화면당 Filled는 1개만. 계층: Filled > FilledTonal > Elevated > Outlined > Text |
| **FAB** | 화면당 1개만. 가장 중요한 단일 액션에만 사용 |
| **NavigationBar** | 모바일 2~5개 destination. 항상 화면 하단 고정 |
| **NavigationRail** | 태블릿/데스크탑 전용 |
| **NavigationDrawer** | 5개 이상 destination일 때 |
| **TextFields** | 기본은 Filled. 복잡한 배경에서만 Outlined |
| **Cards** | Elevated: 평면 배경, Filled: 미묘한 그룹핑, Outlined: 복잡한 배경 |
| **Chips** | Assist: 제안 액션, Filter: 필터링, Input: 사용자 입력값, Suggestion: 동적 옵션 |
| **Selection** | Checkbox: 복수 선택, Radio: 단일 선택, Switch: On/Off 토글 |
| **Snackbar** | 방해 없는 간단한 메시지. 중요한 결정은 Dialog 사용 |
| **Colors** | 항상 Color Role 변수 사용 ($primary, $surface 등). 절대 하드코딩 금지 |

### 컴포넌트 ID 레퍼런스 (material-design-guide.lib.pen)

| 컴포넌트 | ID |
|---------|-----|
| Frame/Mobile/390 | `dnJUo` |
| Frame/Tablet/768 | `P7T42` |
| Frame/Desktop/1440 | `YzwZK` |
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

### 화면 타입별 레이아웃 패턴

**로그인 / 온보딩**
```
Frame/Mobile/390
  └ Hero 영역 (~40% 높이, fill=$primaryContainer)
      └ 로고 + 앱 이름
  └ Form 카드 (cornerRadius [28,28,0,0], fill=$surface)
      └ 제목 + 부제목
      └ TextFields/Filled × N
      └ Buttons/Filled (full-width, 주요 액션 1개)
      └ Buttons/Text (보조 액션)
```

**홈 / 리스트**
```
Frame/Mobile/390
  └ TopAppBar/Small (상단 고정)
  └ 스크롤 콘텐츠 영역
      └ List 아이템들
  └ FAB/Default (우측 하단)
  └ NavigationBar (하단 고정)
```

**설정**
```
Frame/Mobile/390
  └ TopAppBar/Small
  └ 섹션 레이블 (14px, $primary)
  └ Lists/TwoLineItem + Switch 조합
  └ Divider/Full
  └ 다음 섹션 반복
```

**디테일 / 상세**
```
Frame/Mobile/390
  └ TopAppBar (뒤로가기 포함)
  └ 콘텐츠 카드
  └ FAB/Extended (주요 액션)
```

---

## 프롬프트 생성 방법론

프로젝트 `design` 스킬은 이 방법론으로 Pencil AI 프롬프트를 생성한다.

### 프롬프트에 포함해야 할 정보

1. **대상 파일**: 어떤 `.pen` 파일에 작업할지
2. **화면 이름**: 생성할 화면 이름
3. **레이아웃 구조**: 위 패턴 중 해당하는 것 또는 커스텀 구조
4. **컴포넌트 목록**: 사용할 컴포넌트와 ID
5. **색상 규칙**: Color Role 변수만 사용 ($primary, $surface 등)
6. **프로젝트 고유 규칙**: 앱별 추가 제약

### 프롬프트 출력 형식

```
<파일명>.pen 에 <화면 이름> 화면을 추가해줘.

## 공통 규칙
- 색상: 절대 하드코딩 금지. $primary, $surface, $onSurface 등 Color Role 변수만 사용
- 폼팩터: Frame/Mobile/390 (ID: dnJUo)
- 캔버스 빈 공간에 배치 (간격 100px)

## 레이아웃
<화면 구조 설명>

## 컴포넌트
<컴포넌트 이름 (ID: xxx)> × N — <역할 설명>

## 프로젝트 고유 규칙
<앱별 추가 규칙>
```

---

## Claude Code → Pencil MCP 직접 실행 (선택적)

Claude Code가 Pencil MCP를 통해 직접 화면을 조립해야 할 때 사용한다.

### Step 1 — 작업 파일 준비

```
mcp__pencil__get_editor_state()
```

- `<appname>-design-guide.lib.pen`을 import한 `.pen` 파일이 열려 있으면 → Step 2 진행
- 없으면 → 새 `.pen` 파일 생성 후 `<appname>-design-guide.lib.pen` import 안내

### Step 2 — 디자인 요구사항 파악

필요한 컴포넌트, 레이아웃, 색상 규칙 확인.

### Step 3 — 빈 공간 찾기

```
mcp__pencil__find_empty_space_on_canvas(direction: "right", width: ..., height: ..., padding: 100)
```

### Step 4 — Placeholder 프레임 생성

```javascript
screen=I(document, {type: "ref", ref: "dnJUo", placeholder: true, x: ..., y: ...})
```

### Step 5 — 컴포넌트 조립

위 컴포넌트 ID 레퍼런스와 M3 규칙을 따라 배치.

색상 하드코딩 금지:
```javascript
{fill: "$primary"}      // ✓
{fill: "#6750A4"}       // ✗
```

### Step 6 — 검증 및 완료

```
mcp__pencil__get_screenshot(nodeId)
U("frameId", {placeholder: false})
```
