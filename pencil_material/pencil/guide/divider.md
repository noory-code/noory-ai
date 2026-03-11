# Divider

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/divider/overview |
| Guidelines | https://m3.material.io/components/divider/guidelines |
| Specs | https://m3.material.io/components/divider/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| Horizontal | `Divider` |
| Vertical | `VerticalDivider` |

## 언제 사용하나요?

- 목록이나 컨테이너 내에서 콘텐츠 그룹을 구분할 때
- 공백만으로 그룹을 구분하기 어려울 때 시각적 선을 추가할 때
- 개별 항목 분리가 아닌 섹션/그룹을 구분하는 용도로 사용할 때
- ListTile 사이, 설정 메뉴 섹션 구분에 사용할 때

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | 전체 너비 Divider 또는 inset Divider |
| Tablet (medium) | 동일, 다중 열 레이아웃에서 VerticalDivider로 열 구분 |
| Desktop/Web (expanded) | VerticalDivider로 사이드 패널 구분, 섹션 간 Divider |

## Variants

- **Horizontal** — 가로 구분선
- **Vertical** — 세로 구분선

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Divider Guide" 프레임을 만들어주세요.
모든 내용은 이 "Divider Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/components/divider/overview

---

## 프레임 설정
- 이름: "Divider Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Divider"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · divider"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/divider/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 목록이나 컨테이너 내에서 콘텐츠 그룹을 구분할 때
  · 공백만으로 그룹을 구분하기 어려울 때 시각적 선을 추가할 때
  · 설정 메뉴 섹션 구분, ListTile 사이에 사용할 때

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Variant 3개를 가로 나란히 배치, gap 24px

  ┌─ Full-width Divider ───────────────┐
  │  너비: 320dp                        │
  │  높이: 1dp                          │
  │  색상: Outline Variant (Outline Variant)   │
  │  위아래에 텍스트 리스트 아이템 2개  │
  └────────────────────────────────────┘

  ┌─ Inset Divider ────────────────────┐
  │  너비: 320dp (왼쪽 72dp inset)      │
  │  높이: 1dp                          │
  │  색상: Outline Variant                     │
  │  좌측 아이콘 공간(48dp) + inset     │
  └────────────────────────────────────┘

  ┌─ Vertical Divider ─────────────────┐
  │  너비: 1dp, 높이: 120dp             │
  │  색상: Outline Variant                     │
  │  양쪽에 콘텐츠 배치               │
  └────────────────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- Inset Divider를 크게 그리고 번호 레이블 연결:
  1. Line — 1dp, Outline Variant 색상
  2. Inset start — 왼쪽 여백 (72dp 기본)
  3. Inset end — 오른쪽 여백 (0 기본)

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성                        | Horizontal (Divider)      | Vertical (VerticalDivider) | 토큰                         |
  |----------------------------|---------------------------|----------------------------|------------------------------|
  | Thickness (실제 선 두께)    | 1 dp                      | 1 dp                       | —                            |
  | height / width (박스 크기)  | height: 16 dp (기본)      | width: 16 dp (기본)        | —                            |
  | Color                      | outlineVariant            | outlineVariant             | colorScheme.outlineVariant   |
  | indent (시작 여백)          | 0 dp (full) / 72 dp (inset)| 0 dp                      | —                            |
  | endIndent (끝 여백)         | 0 dp                      | 0 dp                       | —                            |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  Full-width 또는 inset       │
  │  → Divider                 │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  다중 열에서 VerticalDivider │
  │  → VerticalDivider         │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  사이드 패널 구분            │
  │  → VerticalDivider         │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Divider Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트 3개를 가로 나란히 배치, gap 24px:

  Divider/Full — 전체 너비 구분선:
  · 컴포넌트 이름: "Divider/Full"
  · 너비: 360dp, 두께: 1dp
  · 색상: Outline Variant

  Divider/Inset — 들여쓰기 구분선:
  · 컴포넌트 이름: "Divider/Inset"
  · 너비: 360dp (좌측 72dp 오프셋), 두께: 1dp
  · 색상: Outline Variant

  Divider/Vertical — 세로 구분선:
  · 컴포넌트 이름: "Divider/Vertical"
  · 두께: 1dp, 높이: 컨텍스트에 따라
  · 색상: Outline Variant

  State 없음 — 단일 상태로만 표시

---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  // Horizontal — full width
  Divider(thickness: 1)

  // Horizontal — inset (ListTile 아이콘 기준)
  Divider(thickness: 1, indent: 72)

  // Vertical — Row 내 열 구분 (width=총 가로 공간, thickness=선 두께)
  SizedBox(
    height: 24,
    child: VerticalDivider(width: 16, thickness: 1),
  )

---

## Flutter Usage

```dart
import 'package:flutter_design/flutter_design.dart';

final cs = Theme.of(context).colorScheme;

// [Divider 파라미터]
// height   — 위젯이 차지하는 총 세로 공간 (기본 16dp). 선 위아래 여백 포함. 선 두께 아님.
// thickness — 실제 보이는 선의 두께 (기본 0 → hairline)
// indent    — 선 시작(왼쪽) 여백
// endIndent — 선 끝(오른쪽) 여백
// color     — 선 색상

// Full-width Divider — M3 기본 (테마 자동 적용)
const Divider()

// Full-width Divider — 명시적 토큰 사용
Divider(
  height: 1,        // 여백 없이 선만 (tight layout)
  thickness: 1,
  color: cs.outlineVariant,
)

// Inset Divider — ListTile 아이콘 영역 기준 72dp 들여쓰기
Divider(
  thickness: 1,
  indent: 72.0,     // 왼쪽 여백 (아이콘 너비 + 패딩)
  endIndent: 0,
  color: cs.outlineVariant,
)

// Middle Inset Divider — 양쪽 패딩 적용
Divider(
  thickness: 1,
  indent: AppSpacing.base,
  endIndent: AppSpacing.base,
  color: cs.outlineVariant,
)

// [VerticalDivider 파라미터]
// width     — 위젯이 차지하는 총 가로 공간 (기본 16dp). 선 좌우 여백 포함. 선 두께 아님.
// thickness — 실제 보이는 선의 두께 (기본 0 → hairline)
// indent    — 선 시작(위쪽) 여백
// endIndent — 선 끝(아래쪽) 여백
// color     — 선 색상

// Vertical Divider — Row 내에서 열 구분 (SizedBox로 높이 제한)
SizedBox(
  height: 24,  // IntrinsicHeight 또는 Row 높이에 맞춤
  child: VerticalDivider(
    width: 16,        // 위젯 총 너비 (기본값 유지 권장)
    thickness: 1,     // 실제 선 두께
    color: cs.outlineVariant,
  ),
)

// Vertical Divider — IntrinsicHeight로 부모 높이 자동 맞춤
IntrinsicHeight(
  child: Row(
    children: [
      Text('Left'),
      VerticalDivider(thickness: 1, color: cs.outlineVariant),
      Text('Right'),
    ],
  ),
)

// Vertical Divider — 사이드 패널 전체 높이 구분선
VerticalDivider(
  width: 1,         // 공간 최소화 (패널 레이아웃에서 tight하게)
  thickness: 1,
  color: cs.outlineVariant,
)
```
