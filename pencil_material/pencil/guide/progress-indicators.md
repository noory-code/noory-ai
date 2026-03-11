# Progress Indicators

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/progress-indicators/overview |
| Guidelines | https://m3.material.io/components/progress-indicators/guidelines |
| Specs | https://m3.material.io/components/progress-indicators/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| Linear | `LinearProgressIndicator` |
| Circular | `CircularProgressIndicator` |
| Determinate | value: 0.0~1.0 전달 |
| Indeterminate | value: null (기본값) |

## 언제 사용하나요?

- 파일 업로드/다운로드처럼 진행률을 알 수 있는 작업에 Linear 사용
- 로딩 중 소요 시간을 모를 때 Circular indeterminate 사용
- 화면 상단 전체 너비로 페이지 로딩 진행을 표시할 때
- 버튼 또는 아이콘 자리에 소형 원형 인디케이터를 사용할 때

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | Circular (전체 화면 로딩), Linear (콘텐츠 상단) |
| Tablet (medium) | 동일 |
| Desktop/Web (expanded) | Linear (상단 바), Circular (로컬 영역 로딩) |

## Variants

- **Linear determinate** — 진행률 바
- **Linear indeterminate** — 애니메이션 진행 바
- **Circular determinate** — 원형 진행률
- **Circular indeterminate** — 스피너

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Progress Indicators Guide" 프레임을 만들어주세요.
모든 내용은 이 "Progress Indicators Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/components/progress-indicators/overview

---

## 프레임 설정
- 이름: "Progress Indicators Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Progress Indicators"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · progress-indicators"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/progress-indicators/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 파일 업로드/다운로드처럼 진행률을 알 수 있는 작업에 Linear 사용
  · 로딩 중 소요 시간을 모를 때 Circular indeterminate 사용
  · 화면 상단 전체 너비로 페이지 로딩 진행을 표시할 때

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Variant 4개를 배치 (Linear 2개 세로, Circular 2개 가로)

  Linear — 가로 전체 너비로 2개 배치:

  ┌─ Linear Determinate (너비 320dp) ───────────────────┐
  │  track: 4dp 높이, bg: Secondary Container (Secondary Container) │
  │  indicator: 60% 채움, Primary (Primary)             │
  │  양쪽 끝 cap: rounded                               │
  └──────────────────────────────────────────────────────┘

  ┌─ Linear Indeterminate (너비 320dp) ─────────────────┐
  │  track: 4dp 높이, bg: Secondary Container                       │
  │  indicator: 애니메이션 표시 (물결 표현)              │
  │  (화살표로 "animating" 표기)                        │
  └──────────────────────────────────────────────────────┘

  Circular — 2개 가로 나란히:

  ┌─ Circular Determinate ─┐   ┌─ Circular Indeterminate ──┐
  │  지름: 48dp             │   │  지름: 48dp               │
  │  stroke: 4dp            │   │  stroke: 4dp              │
  │  track: Secondary Container         │   │  track: 투명              │
  │  indicator: 75% 호      │   │  indicator: 스피너 호      │
  │  색상: Primary          │   │  색상: Primary            │
  └─────────────────────────┘   └───────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- Linear Determinate를 크게 그리고 번호 레이블 연결:
  1. Track — 전체 너비, 4dp 높이, secondaryContainer 배경
  2. Indicator — primary 색상, 진행률만큼 채움
  3. Stop indicator (선택) — 끝점 도형 (determinate 전용)

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성                   | Linear              | Circular            | 토큰                          |
  |-----------------------|---------------------|---------------------|-------------------------------|
  | Track height / stroke | 4 dp                | 4 dp                | —                             |
  | Circle diameter       | —                   | 48 dp               | —                             |
  | Indicator color       | primary             | primary             | colorScheme.primary           |
  | Track bg color        | secondaryContainer  | —                   | colorScheme.secondaryContainer|
  | Stroke cap            | rounded             | rounded             | StrokeCap.round               |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  Circular (전체 화면 로딩)  │
  │  Linear (콘텐츠 상단)       │
  │  → CircularProgressIndicator │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  동일                       │
  │  → LinearProgressIndicator │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  Linear (상단 바)           │
  │  Circular (로컬 영역)       │
  │  → LinearProgressIndicator │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Progress Indicators Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트 4개를 가로 나란히 배치, gap 24px:

  ProgressIndicators/LinearDeterminate — 진행률 표시:
  · 컴포넌트 이름: "ProgressIndicators/LinearDeterminate"
  · 너비: 360dp, 높이: 4dp
  · Track: Secondary Container
  · Indicator: Primary (60% 채움 예시)
  · 양쪽 끝 cap: rounded

  ProgressIndicators/LinearIndeterminate — 애니메이션 (정적 표현):
  · 컴포넌트 이름: "ProgressIndicators/LinearIndeterminate"
  · 너비: 360dp, 높이: 4dp
  · Track: Secondary Container
  · Indicator: Primary (물결 표현)

  ProgressIndicators/CircularDeterminate — 원형 진행률:
  · 컴포넌트 이름: "ProgressIndicators/CircularDeterminate"
  · 크기: 48×48dp, stroke: 4dp
  · Track: Secondary Container
  · Indicator: Primary (75% 호)

  ProgressIndicators/CircularIndeterminate — 원형 로딩:
  · 컴포넌트 이름: "ProgressIndicators/CircularIndeterminate"
  · 크기: 48×48dp, stroke: 4dp
  · Indicator: Primary (스피너)


  State 없음 — 단일 상태로만 표시

---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  // Linear determinate
  LinearProgressIndicator(value: 0.6)

  // Linear indeterminate
  LinearProgressIndicator()

  // Circular determinate
  CircularProgressIndicator(value: 0.75)

  // Circular indeterminate (spinner)
  CircularProgressIndicator()

---

## Flutter Usage

```dart
import 'package:flutter_design/flutter_design.dart';

final cs = Theme.of(context).colorScheme;

// Linear determinate — 진행률 표시 (기본, 테마 자동 적용)
LinearProgressIndicator(
  value: 0.6,  // 0.0 ~ 1.0
  color: cs.primary,
  backgroundColor: cs.secondaryContainer,
  borderRadius: BorderRadius.circular(4), // M3 rounded cap
)

// Linear indeterminate — 로딩 중 (소요 시간 불명)
const LinearProgressIndicator()

// Circular indeterminate — 스피너 (기본)
const CircularProgressIndicator()

// Circular determinate — 원형 진행률
CircularProgressIndicator(
  value: 0.75,
  strokeWidth: 4,        // M3 기본 4dp
  strokeCap: StrokeCap.round,
  color: cs.primary,
  backgroundColor: cs.secondaryContainer,
)

// 소형 Circular — 버튼/아이콘 자리 (compact)
const SizedBox(
  width: 24,
  height: 24,
  child: CircularProgressIndicator(strokeWidth: 3),
)
```
