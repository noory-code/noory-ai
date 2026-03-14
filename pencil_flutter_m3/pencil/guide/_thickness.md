# Thickness

## M3 링크

| 페이지 | URL |
|--------|-----|
| Divider | https://m3.material.io/components/divider/overview |
| Text Field | https://m3.material.io/components/text-fields/overview |

## 토큰 정의

| 토큰 | 값 | 용도 |
|------|-----|------|
| $thickness/thin | 0.5 dp | 보조 Divider, 얇은 구분선 |
| $thickness/md | 1 dp | 기본 Divider, OutlinedButton, TextField outline |
| $thickness/thick | 2 dp | Focused TextField, Focused OutlinedButton, 강조 border |

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 Design Token 변수를 등록하고 "Thickness Guide" 프레임을 만들어주세요.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/components/divider/overview

---

## 변수 등록 (Variables)

먼저 material-design-guide.lib.pen 의 Variables 패널에서 "Design Tokens" 테마 > Default에 다음 변수를 number 타입으로 등록한다. 이미 등록되어 있다면 그대로 사용한다:

| 변수명 | 값 |
|--------|-----|
| $thickness/thin | 0.5 |
| $thickness/md | 1 |
| $thickness/thick | 2 |

---

## 프레임 설정
- 이름: "Thickness Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Thickness"  (32px, bold, On-Surface)
- 부제목: "선 두께 토큰 — Divider · Border · Outline"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/divider/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · thin (0.5dp) — 보조 구분선, 미세한 영역 분리
  · md (1dp) — 기본 Divider, OutlinedButton, TextField 기본 outline
  · thick (2dp) — Focused TextField, Focused OutlinedButton, 강조 border

---

## 섹션 3 — Thickness Scale
- 소제목: "Thickness Scale"  (20px, 600)
- 3개 행 수직 나열, 각 행:

  [토큰명 레이블 140px] [가로선 (길이 200px, 높이=값dp, bg=On-Surface)] [값 텍스트 (Primary)]

  · $thickness/thin  → 0.5dp → 선 높이 0.5px (점선으로 표현)
  · $thickness/md    → 1dp   → 선 높이 1px
  · $thickness/thick → 2dp   → 선 높이 2px

---

## 섹션 4 — Context Examples
- 소제목: "Context Examples"  (20px, 600)
- 3개 예시 카드 가로 배치, gap 24px:

  ┌─ Divider ──────────────────────┐
  │  텍스트                         │
  │  ────────────────── (1dp)       │
  │  텍스트                         │
  │  $thickness/md = 1dp            │
  └─────────────────────────────────┘

  ┌─ OutlinedButton ───────────────┐
  │  ┌─────────────────────┐       │
  │  │      Label          │ 1dp   │
  │  └─────────────────────┘       │
  │  $thickness/md = 1dp            │
  └─────────────────────────────────┘

  ┌─ Focused TextField ────────────┐
  │  ══════════════════════ (2dp)  │
  │  Label                         │
  │  $thickness/thick = 2dp        │
  └─────────────────────────────────┘

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 토큰 | 값 | 주요 용도 |
  |------|-----|----------|
  | $thickness/thin | 0.5 dp | 보조 구분선 |
  | $thickness/md | 1 dp | Divider, OutlinedButton, TextField |
  | $thickness/thick | 2 dp | Focused 상태 |

---

## 섹션 6 — Flutter Usage
- 소제목: "Flutter Usage"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  // AppThickness 토큰 사용 (lib/src/tokens.dart)
  import 'package:flutter_design/flutter_design.dart';

  // Divider
  Divider(thickness: AppThickness.md)         // 1dp
  Divider(thickness: AppThickness.thin)        // 0.5dp

  // OutlinedButton border
  OutlinedButton(
    style: OutlinedButton.styleFrom(
      side: BorderSide(width: AppThickness.md), // 1dp
    ),
    onPressed: () {},
    child: Text('Label'),
  )

  // TextField focused border
  TextField(
    decoration: InputDecoration(
      enabledBorder: OutlineInputBorder(
        borderSide: BorderSide(width: AppThickness.md),    // 1dp
      ),
      focusedBorder: OutlineInputBorder(
        borderSide: BorderSide(width: AppThickness.thick), // 2dp
      ),
    ),
  )

  // Container border
  Container(
    decoration: BoxDecoration(
      border: Border.all(width: AppThickness.md),
      borderRadius: BorderRadius.circular(AppRadius.sm),
    ),
  )
