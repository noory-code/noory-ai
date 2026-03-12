---
name: init
description: >
  Initialize a new app design guide .pen file.
  Triggers when the user asks to initialize, create a new design guide,
  or set up a new app's design system in Pencil.
user-invocable: true
---

# Init — App Design Guide

앱별 디자인 가이드 `.pen` 파일을 생성한다.
`material-design-guide.lib.pen`은 공용 라이브러리로 유지하고, 앱마다 별도 파일을 생성한다.

## Step 0 — 정보 수집

사용자에게 세 가지를 확인한다:

1. **저장 경로** — `.pen` 파일을 저장할 디렉토리 (예: `apps/myapp/pencil/`, `pencil/`)
2. **앱 이름** — 파일명에 사용 (예: `myapp` → `myapp-design-guide.pen`)
3. **시드 컬러 hex** — M3 팔레트 계산 기준색 (예: `#6750A4`)

## Step 2 — 새 .pen 파일 생성

```
mcp__pencil__open_document("new")
```

파일 저장 경로: `<Step 0에서 결정한 경로>/<appname>-design-guide.pen`

> Pencil이 파일명을 요청하면 `<appname>-design-guide`로 입력한다.

## Step 3 — 팔레트 계산

```bash
cd pencil_material/pencil/md3calc
python3 hct_palette.py <seed_hex>
```

출력 JSON의 `palettes` 키 아래 `primary`, `secondary`, `tertiary`, `neutral`, `neutralVariant`, `error` 팔레트를 사용한다.

## Step 4 — 컬러 변수 설정

`mcp__pencil__set_variables`로 아래 변수를 모두 업데이트한다.

### Semantic Colors Palette (테마: Default)

팔레트 tones → 변수명 매핑:

| 변수명 | 값 |
|--------|----|
| `seed` | seed hex |
| `primary/0` ~ `primary/100` | palettes.primary[tone] |
| `secondary/0` ~ `secondary/100` | palettes.secondary[tone] |
| `tertiary/0` ~ `tertiary/100` | palettes.tertiary[tone] |
| `neutral/0` ~ `neutral/100` | palettes.neutral[tone] |
| `neutralVariant/0` ~ `neutralVariant/100` | palettes.neutralVariant[tone] |
| `error/0` ~ `error/100` | palettes.error[tone] |

tones: `0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99, 100`

### Material Color Scheme — light 테마

| 변수명 | 팔레트 값 |
|--------|-----------|
| `primary` | primary/40 |
| `onPrimary` | primary/100 |
| `primaryContainer` | primary/90 |
| `onPrimaryContainer` | primary/10 |
| `primaryFixed` | primary/90 |
| `primaryFixedDim` | primary/80 |
| `onPrimaryFixed` | primary/10 |
| `onPrimaryFixedVariant` | primary/30 |
| `secondary` | secondary/40 |
| `onSecondary` | secondary/100 |
| `secondaryContainer` | secondary/90 |
| `onSecondaryContainer` | secondary/10 |
| `secondaryFixed` | secondary/90 |
| `secondaryFixedDim` | secondary/80 |
| `onSecondaryFixed` | secondary/10 |
| `onSecondaryFixedVariant` | secondary/30 |
| `tertiary` | tertiary/40 |
| `onTertiary` | tertiary/100 |
| `tertiaryContainer` | tertiary/90 |
| `onTertiaryContainer` | tertiary/10 |
| `tertiaryFixed` | tertiary/90 |
| `tertiaryFixedDim` | tertiary/80 |
| `onTertiaryFixed` | tertiary/10 |
| `onTertiaryFixedVariant` | tertiary/30 |
| `error` | error/40 |
| `onError` | error/100 |
| `errorContainer` | error/90 |
| `onErrorContainer` | error/10 |
| `surface` | neutral/99 |
| `onSurface` | neutral/10 |
| `onSurfaceVariant` | neutralVariant/30 |
| `surfaceContainerLowest` | neutral/100 |
| `surfaceContainerLow` | neutral/95 |
| `surfaceContainer` | neutral/95 |
| `surfaceContainerHigh` | neutral/90 |
| `surfaceContainerHighest` | neutral/90 |
| `surfaceDim` | neutral/90 |
| `surfaceBright` | neutral/99 |
| `outline` | neutralVariant/50 |
| `outlineVariant` | neutralVariant/80 |
| `inverseSurface` | neutral/20 |
| `onInverseSurface` | neutral/95 |
| `inversePrimary` | primary/80 |
| `shadow` | neutral/0 |
| `scrim` | neutral/0 |
| `surfaceTint` | primary/40 |

### Material Color Scheme — dark 테마

| 변수명 | 팔레트 값 |
|--------|-----------|
| `primary` | primary/80 |
| `onPrimary` | primary/20 |
| `primaryContainer` | primary/30 |
| `onPrimaryContainer` | primary/90 |
| `primaryFixed` | primary/90 |
| `primaryFixedDim` | primary/80 |
| `onPrimaryFixed` | primary/10 |
| `onPrimaryFixedVariant` | primary/30 |
| `secondary` | secondary/80 |
| `onSecondary` | secondary/20 |
| `secondaryContainer` | secondary/30 |
| `onSecondaryContainer` | secondary/90 |
| `secondaryFixed` | secondary/90 |
| `secondaryFixedDim` | secondary/80 |
| `onSecondaryFixed` | secondary/10 |
| `onSecondaryFixedVariant` | secondary/30 |
| `tertiary` | tertiary/80 |
| `onTertiary` | tertiary/20 |
| `tertiaryContainer` | tertiary/30 |
| `onTertiaryContainer` | tertiary/90 |
| `tertiaryFixed` | tertiary/90 |
| `tertiaryFixedDim` | tertiary/80 |
| `onTertiaryFixed` | tertiary/10 |
| `onTertiaryFixedVariant` | tertiary/30 |
| `error` | error/80 |
| `onError` | error/20 |
| `errorContainer` | error/30 |
| `onErrorContainer` | error/90 |
| `surface` | neutral/10 |
| `onSurface` | neutral/90 |
| `onSurfaceVariant` | neutralVariant/80 |
| `surfaceContainerLowest` | neutral/0 |
| `surfaceContainerLow` | neutral/10 |
| `surfaceContainer` | neutral/10 |
| `surfaceContainerHigh` | neutral/20 |
| `surfaceContainerHighest` | neutral/20 |
| `surfaceDim` | neutral/10 |
| `surfaceBright` | neutral/20 |
| `outline` | neutralVariant/60 |
| `outlineVariant` | neutralVariant/30 |
| `inverseSurface` | neutral/90 |
| `onInverseSurface` | neutral/20 |
| `inversePrimary` | primary/40 |
| `shadow` | neutral/0 |
| `scrim` | neutral/0 |
| `surfaceTint` | primary/80 |

## Step 5 — 폼팩터 프레임 생성

`mcp__pencil__batch_design`으로 3개 폼팩터 프레임을 reusable 컴포넌트로 생성한다.

```
Frame/Mobile/390   — 390×844
  └ StatusBar (height: 44, fill: surfaceContainer)
  └ Content   (fill_container, layout: vertical, placeholder)
  └ NavigationBar (height: 80, fill: surfaceContainer)

Frame/Tablet/768   — 768×1024
  └ StatusBar (height: 44, fill: surfaceContainer)
  └ Content   (fill_container, layout: horizontal, placeholder)
  └ NavigationBar (height: 80, fill: surfaceContainer)

Frame/Desktop/1440 — 1440×900
  └ TopBar    (height: 64, fill: surfaceContainer)
  └ Content   (fill_container, layout: horizontal, placeholder)
```

## Step 6 — 로고 플레이스홀더 생성

```
Logo 컴포넌트 (reusable, 192×192)
  └ 배경: surfaceContainerHighest
  └ 텍스트: "Logo" (onSurface, 중앙 정렬)
```

`/pencil-material:change-logo` 스킬로 나중에 교체할 수 있다.

## Step 7 — 결과 안내

완료 후 사용자에게 보고:

```
✓ <appname>-design-guide.pen 생성 완료

- Seed color: <hex>
- Primary: <primary/40>
- 폼팩터 프레임: Mobile 390, Tablet 768, Desktop 1440

다음 작업:
  /pencil-material:change-seed-color — 시드 컬러 변경
  /pencil-material:change-logo       — 로고 교체
```
