# pencil-m3-flutter

Claude Code 플러그인 — Flutter Material Design 3 디자인 시스템 자동화.

[Pencil](https://pencil.ai) 앱과 Claude Code를 연동해 앱별 M3 디자인 라이브러리를 초기화하고,
시드 컬러 기반 Flutter 테마 코드를 자동 생성하며, 화면 디자인 프롬프트를 만든다.

---

## 이 플러그인이 하는 일

```
/pencil-m3-flutter:init
  → 앱별 <appname>-design-guide.lib.pen 생성
  → 시드 컬러 설정 (Pencil 변수 + Flutter Dart 코드 자동 생성)
  → 로고 설정
  → 프로젝트 전용 design 스킬 생성

/pencil-m3-flutter:design-guide
  → M3 Expressive 규칙 기반으로 화면 디자인
  → Claude Code가 Pencil MCP 직접 조작 또는 프롬프트 생성

/pencil-m3-flutter:change-seed-color
  → 시드 컬러 변경 → Pencil 변수 + Flutter 코드 동시 업데이트

/pencil-m3-flutter:change-logo
  → 로고 컴포넌트 교체 (AI 생성 / 이미지 / 텍스트 이니셜)
```

---

## 스킬 목록

| 스킬 | 역할 |
|------|------|
| `init` | 앱 디자인 시스템 초기화 (원스톱 온보딩) |
| `design-guide` | M3 화면 디자인 베이스 규칙 + MCP 직접 실행 |
| `change-seed-color` | 시드 컬러 변경 → Pencil + Flutter 코드 동기화 |
| `change-logo` | 로고 컴포넌트 교체 |

---

## 환경 요구사항

### 1. Pencil 앱 + MCP 서버

[Pencil](https://pencil.ai) 앱이 실행 중이어야 하고, Claude Code와 MCP로 연결되어 있어야 한다.
`material-design-guide.lib.pen` 파일이 Pencil에서 열려 있어야 한다.

### 2. Python 3.9+

시드 컬러 팔레트 계산 및 Dart 코드 생성에 Python이 필요하다.

```bash
# materialyoucolor 설치 (HCT 알고리즘)
pip install materialyoucolor
```

### 3. Python 스크립트 위치

```
pencil_m3_flutter/pencil/md3calc/
├── hct_palette.py   # 시드 컬러 → M3 팔레트 JSON 계산
└── gen_dart.py      # 팔레트 JSON → Flutter Dart 파일 생성
```

스킬 실행 시 Claude Code가 이 스크립트들을 자동으로 호출한다.
프로젝트 루트에서 실행되므로 별도 설정 불필요.

---

## 빠른 시작

### 1. 플러그인 설치

이 `pencil_m3_flutter` 디렉토리를 프로젝트에 포함하거나 경로를 Claude Code에 등록한다.

### 2. 앱 초기화

```
/pencil-m3-flutter:init
```

Claude가 순서대로 안내한다:
- 저장 경로 및 앱 이름 → `.lib.pen` 파일 생성
- 시드 컬러 hex → Pencil 변수 + Flutter Dart 코드 자동 생성
- 로고 설정
- 프로젝트 전용 `design` 스킬 생성

### 3. 화면 디자인

`init` 완료 후 프로젝트에 생성된 `design` 스킬 사용:

```
/<appname>:design 로그인 화면 만들어줘
```

→ Pencil AI 채팅창에 붙여넣을 프롬프트 출력.
→ 복사해서 Pencil AI에 붙여넣으면 화면 자동 생성.

---

## 스킬 상세

### `init` — 앱 디자인 시스템 초기화

1. `<appname>-design-guide.lib.pen` 생성 (Pencil 라이브러리)
2. 시드 컬러 설정:
   - Pencil: Color Scheme 변수 전체 업데이트 (light/dark)
   - Flutter: `gen_dart.py`로 Dart 파일 4개 자동 생성
3. 로고 설정
4. 프로젝트 전용 `design` 스킬 생성 (`.claude-plugin/skills/design/SKILL.md`)

### `design-guide` — M3 화면 디자인 베이스

두 가지 역할:
- **베이스 레이어**: 프로젝트 `design` 스킬이 이 규칙을 상속
- **직접 실행**: Claude Code가 Pencil MCP를 통해 화면을 직접 조립

M3 Expressive 규칙, 컴포넌트 ID 레퍼런스, 화면 패턴, 프롬프트 생성 방법론 포함.

### `change-seed-color` — 시드 컬러 변경

1. `hct_palette.py`로 새 팔레트 계산
2. Pencil `set_variables`로 Color Scheme 업데이트
3. `gen_dart.py`로 Flutter Dart 파일 재생성

### `change-logo` — 로고 교체

AI 생성 / 이미지 파일 / 텍스트 이니셜 중 선택.
`Logo` reusable 컴포넌트를 교체하면 모든 인스턴스에 즉시 반영.

---

## 프로젝트 design 스킬

`init` 실행 시 프로젝트에 자동 생성되는 스킬 (`.claude-plugin/skills/design/SKILL.md`).

- `pencil-m3-flutter:design-guide`의 M3 규칙을 베이스로 상속
- 프로젝트 고유 컴포넌트, 화면 패턴 추가 정의
- 사용자 요청 → **Pencil AI 채팅창에 붙여넣을 프롬프트 텍스트 출력**

생성 후 `## 프로젝트 고유 규칙` 섹션을 앱에 맞게 직접 채워야 한다.

---

## lib/src/ — 생성 결과물 참조용 예시

`lib/src/`의 Dart 파일들은 `gen_dart.py`가 생성하는 코드의 **참조 예시**다.
실제 앱 프로젝트에는 `init` 스킬이 앱 경로에 직접 생성한다.

```
lib/src/
├── semantic_color_palette.dart  # Layer 1 — 팔레트 원시값 (seed #E91E63 예시)
├── theme_colors.dart            # Layer 2 — ColorScheme 6개 variant
├── theme.dart                   # Layer 3 — AppTheme (ThemeData)
└── tokens.dart                  # Spacing / Radius / Elevation / IconSize / Opacity
```

### 생성된 코드 사용법

```dart
// MaterialApp 세팅
MaterialApp(
  theme:     AppTheme.light,
  darkTheme: AppTheme.dark,
  themeMode: ThemeMode.system,
)

// 색상 접근
final cs = Theme.of(context).colorScheme;
cs.primary      // 브랜드 컬러
cs.surface      // 배경
cs.onSurface    // 텍스트

// 디자인 토큰
EdgeInsets.all(AppSpacing.base)         // 12dp
BorderRadius.circular(AppRadius.md)     // 16dp
AppElevation.level1                     // 1dp
AppIconSize.md                          // 24dp
```

### 의존성

생성된 `theme.dart`는 `google_fonts`를 사용한다:

```yaml
dependencies:
  google_fonts: ^6.2.1
```

---

## Pencil 가이드

`pencil/guide/` 폴더에 31개 M3 컴포넌트 + 8개 토큰 시스템 가이드가 있다.
각 파일에는 컴포넌트 사용 규칙과 Flutter 코드 연동 방법이 포함되어 있다.

`pencil/guide/_overview.md` 참조.
