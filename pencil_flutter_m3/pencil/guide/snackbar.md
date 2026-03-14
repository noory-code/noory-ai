# Snackbar

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/snackbar/overview |
| Guidelines | https://m3.material.io/components/snackbar/guidelines |
| Specs | https://m3.material.io/components/snackbar/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| Snackbar | `SnackBar` |
| 표시 방법 | `ScaffoldMessenger.of(context).showSnackBar()` |

## 언제 사용하나요?

- 사용자 액션 결과를 간단히 피드백할 때 (저장됨, 삭제됨 등)
- 실행 취소(Undo)처럼 단일 액션 버튼을 함께 제공할 때
- 중요하지 않아 다이얼로그가 필요 없는 일시적 알림
- 4초 후 자동으로 사라지는 비방해 방식의 메시지

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | 화면 하단 전체 너비 Snackbar |
| Tablet (medium) | 하단 중앙 고정 너비 (최대 640dp) |
| Desktop/Web (expanded) | 좌하단 또는 중앙 하단 고정 너비, 여러 개 스택 가능 |

## Variants

- **Text only** — 메시지만 표시
- **With action** — 메시지 + 단일 액션 버튼 (예: 실행취소)

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Snackbar Guide" 프레임을 만들어주세요.

모든 내용은 이 "Snackbar Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)
참고: https://m3.material.io/components/snackbar/overview

---

## 프레임 설정
- 이름: "Snackbar Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Snackbar"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · snackbar"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/snackbar/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 사용자 액션 결과를 간단히 피드백할 때 (저장됨, 삭제됨)
  · 실행 취소(Undo)처럼 단일 액션 버튼을 함께 제공할 때
  · 4초 후 자동으로 사라지는 비방해 방식의 메시지

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Variant 2개를 세로 나열 (너비 320dp), gap 16px

  ┌─ Text only (너비 320dp) ─────────────────────────┐
  │  height: 48dp                                      │
  │  배경: Inverse Surface (어두운 배경)               │
  │  corner: 4dp                                       │
  │  텍스트: "Message sent"  (14sp, Inverse On-Surface)│
  │  좌우 패딩: 16dp                                   │
  └───────────────────────────────────────────────────┘

  ┌─ With action (너비 320dp) ───────────────────────┐
  │  height: 48dp                                      │
  │  배경: Inverse Surface                             │
  │  corner: 4dp                                       │
  │  텍스트: "Email deleted"  (14sp, Inverse On-Surface)│
  │  우측: "UNDO" 버튼  (14sp, Inverse Primary)       │
  └───────────────────────────────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- With action Snackbar를 크게 그리고 번호 레이블 연결:
  1. Container — inverseSurface, corner 4dp, elevation 3
  2. Supporting text — bodyMedium (onInverseSurface)
  3. Action button — labelLarge (inversePrimary), TextButton
  4. Icon button (선택) — 닫기 X 아이콘 (onInverseSurface)

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성              | 값                    | 토큰                              |
  |------------------|-----------------------|-----------------------------------|
  | Min height       | 48 dp                 | —                                 |
  | Corner radius    | 4 dp                  | —                                 |
  | Horizontal pad   | 16 dp                 | —                                 |
  | Text TextStyle   | bodyMedium            | textTheme.bodyMedium              |
  | Action TextStyle | labelLarge            | textTheme.labelLarge              |
  | Elevation        | Level 3               | AppElevation.level3               |
  | Container bg     | inverseSurface        | colorScheme.inverseSurface        |
  | Text color       | onInverseSurface      | colorScheme.onInverseSurface      |
  | Action color     | inversePrimary        | colorScheme.inversePrimary        |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  하단 전체 너비             │
  │  → ScaffoldMessenger       │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  하단 중앙, 최대 640dp      │
  │  → ScaffoldMessenger       │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  좌하단 또는 중앙 하단       │
  │  → ScaffoldMessenger       │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Snackbar Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트 2개를 가로 나란히 배치, gap 24px:

  Snackbar/TextOnly — 메시지만 표시:
  · 컴포넌트 이름: "Snackbar/TextOnly"
  · 높이: 48dp, 너비: 320dp, corner: 4dp
  · 배경: Inverse Surface, Elevation Level 3
  · 텍스트: 14sp, Inverse On-Surface
  · 수평 패딩: 16dp

  Snackbar/WithAction — 메시지 + 액션 버튼:
  · 컴포넌트 이름: "Snackbar/WithAction"
  · 동일 구조
  · Action 버튼: 14sp medium, Inverse Primary (우측 정렬)


  State 없음 — 단일 상태로만 표시

---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (배경: surfaceContainerHighest, radius 8px, padding 16px):
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(
      content: Text('Email deleted'),
      action: SnackBarAction(
        label: 'UNDO',
        onPressed: () {},
      ),
    ),
  );

---

## Flutter Usage

```dart
import 'package:flutter_design/flutter_design.dart';

final cs = Theme.of(context).colorScheme;

// Text only — 기본 (테마 자동 적용)
ScaffoldMessenger.of(context).showSnackBar(
  const SnackBar(
    content: Text('메시지가 전송되었습니다.'),
  ),
);

// With action (Undo) — 실행취소 버튼
ScaffoldMessenger.of(context).showSnackBar(
  SnackBar(
    content: const Text('이메일이 삭제되었습니다.'),
    action: SnackBarAction(
      label: '실행취소',
      onPressed: () {},
    ),
  ),
);

// behavior: floating — 화면 위에 떠서 표시 (M3 기본)
ScaffoldMessenger.of(context).showSnackBar(
  SnackBar(
    content: const Text('저장되었습니다.'),
    behavior: SnackBarBehavior.floating,
    width: 320,  // 너비 고정 (floating 시 사용)
  ),
);

// duration — 표시 시간 조정 (기본 4초)
ScaffoldMessenger.of(context).showSnackBar(
  SnackBar(
    content: const Text('완료'),
    duration: const Duration(seconds: 2),
  ),
);
```
