# Date Pickers

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/date-pickers/overview |
| Guidelines | https://m3.material.io/components/date-pickers/guidelines |
| Specs | https://m3.material.io/components/date-pickers/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 | 비고 |
|-----------|-------------|------|
| Modal calendar | `showDatePicker()` | 내부적으로 `DatePickerDialog` 사용 |
| Modal input | `showDatePicker(initialEntryMode: DatePickerEntryMode.input)` | 텍스트 입력 모드 |
| Docked | `CalendarDatePicker` (직접 구현 필요) | ⚠️ M3 Docked는 Flutter 미지원 |
| Date range | `showDateRangePicker()` | |

> ⚠️ **Docked DatePicker**: Material Design 3 스펙에 정의돼 있으나 Flutter 공식 미지원 (GitHub Issue #114088). `CalendarDatePicker` 위젯을 직접 배치하는 방식으로 대체한다.

## 언제 사용하나요?

- 사용자가 특정 날짜(단일 또는 범위)를 선택해야 할 때
- 항공권 예약, 호텔 체크인 등 날짜 범위 입력이 필요할 때
- 가까운 날짜는 캘린더 UI, 먼 날짜는 입력 모드를 함께 제공할 때
- 현재·과거·미래 날짜 중 허용 범위를 제한해야 할 때

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | Modal 캘린더 다이얼로그 (`showDatePicker`) |
| Tablet (medium) | Docked (인라인) 캘린더 — `CalendarDatePicker` 직접 구현 |
| Desktop/Web (expanded) | Docked 캘린더, 폼 내 인라인 배치 — `CalendarDatePicker` 직접 구현 |

## Variants

- **Modal calendar** — 캘린더 다이얼로그
- **Modal input** — 텍스트 직접 입력 (모드 전환 아이콘)
- **Docked** — ⚠️ M3 스펙이나 Flutter 미지원. `CalendarDatePicker` 위젯으로 인라인 구현
- **Date range** — 시작~종료 날짜 선택

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Date Pickers Guide" 프레임을 만들어주세요.
모든 내용은 이 "Date Pickers Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/components/date-pickers/overview

---

## 프레임 설정
- 이름: "Date Pickers Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Date Pickers"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · date-pickers"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/date-pickers/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 사용자가 특정 날짜(단일 또는 범위)를 선택해야 할 때
  · 항공권 예약, 호텔 체크인 등 날짜 범위 입력이 필요할 때
  · 현재·과거·미래 날짜 중 허용 범위를 제한해야 할 때

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Variant 2개를 가로 나란히 배치, gap 24px

  ┌─ Modal Calendar ───────────────────┐
  │  다이얼로그 (360×560dp)             │
  │  배경: Surface Container High, corner 28dp │
  │  상단 헤더: "Select date" (24sp)    │
  │  연도/월 네비게이션 바              │
  │  7×6 날짜 그리드                   │
  │  선택일: 원형 강조 (Primary, 40dp)  │
  │  하단: 취소/확인 버튼 (TextButton)  │
  └────────────────────────────────────┘

  ┌─ Modal Input ──────────────────────┐
  │  다이얼로그 (360×240dp)             │
  │  배경: Surface Container High, corner 28dp │
  │  상단: "Enter date"                │
  │  텍스트 필드: "mm/dd/yyyy"          │
  │  우상단: 캘린더 아이콘 (모드 전환)   │
  │  하단: 취소/확인 버튼               │
  └────────────────────────────────────┘

  ┌─ Date Range ───────────────────────┐
  │  전체화면 (Mobile) 또는 다이얼로그   │
  │  상단: "Select range"              │
  │  시작일~종료일 강조 (Primary범위)    │
  │  하단: Save 버튼                   │
  └────────────────────────────────────┘

  ┌─ Docked ─────────────────────────┐
  │  ⚠️ M3 스펙 / Flutter 미지원       │
  │  CalendarDatePicker 직접 배치로 구현│
  │  인라인 캘린더 그리드              │
  │  선택일: Primary 배경 원형 40dp    │
  └────────────────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- Modal Calendar를 크게 그리고 번호 레이블 연결:
  1. Dialog container — corner 28dp, surfaceContainerHigh
  2. Header — labelSmall, onSurfaceVariant ("Select date")
  3. Month/year navigation — labelLarge, onSurfaceVariant
  4. Day of week labels — bodySmall, onSurface
  5. Date grid — 날짜 셀 40×40dp, bodySmall
  6. Selected date — primary 배경 원형 40dp, onPrimary 텍스트
  7. Today (미선택) — primary 테두리 원형
  8. Action buttons — TextButton (취소/확인)

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성                    | 값                     | 토큰                              |
  |------------------------|------------------------|-----------------------------------|
  | Dialog corner          | 28 dp                  | AppRadius.xl                      |
  | Selected circle        | 40 dp                  | —                                 |
  | Date cell size         | 40 × 40 dp             | —                                 |
  | Header TextStyle       | labelSmall             | textTheme.labelSmall              |
  | Day label TextStyle    | bodySmall              | textTheme.bodySmall               |
  | Selected bg            | primary                | colorScheme.primary               |
  | Selected text          | onPrimary              | colorScheme.onPrimary             |
  | Today ring             | primary                | colorScheme.primary               |
  | Container bg           | surfaceContainerHigh   | colorScheme.surfaceContainerHigh  |
  | Entry mode toggle      | DatePickerEntryMode    | —                                 |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  Modal 캘린더 다이얼로그     │
  │  → showDatePicker()        │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  Docked (인라인) 구현       │
  │  → CalendarDatePicker      │
  │  ⚠️ Flutter 직접 구현 필요  │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  Docked 캘린더, 폼 내 인라인│
  │  → CalendarDatePicker      │
  │  ⚠️ Flutter 직접 구현 필요  │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Date Pickers Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트 4개를 가로 나란히 배치, gap 24px:

  DatePicker/Modal — 캘린더 다이얼로그:
  · 컴포넌트 이름: "DatePicker/Modal"
  · 너비: 360dp, 배경: Surface Container High, corner: 28dp
  · 헤더 높이: 120dp, 헤더 배경: Primary Container
  · 날짜 셀: 40×40dp
  · 선택 날짜: Primary 배경 (corner 20dp), On-Primary 텍스트

  DatePicker/Input — 텍스트 입력형:
  · 컴포넌트 이름: "DatePicker/Input"
  · 너비: 360dp, 배경: Surface Container High, corner: 28dp
  · 텍스트 필드 입력 "mm/dd/yyyy"
  · 우상단 캘린더 아이콘 (모드 전환)

  DatePicker/Range — 범위 선택형:
  · 컴포넌트 이름: "DatePicker/Range"
  · 시작일~종료일 범위 강조 (Primary Container 배경)
  · 시작/종료일: Primary 원형
  · Save 버튼 (On-Surface)

  DatePicker/Docked — 인라인 캘린더 (CalendarDatePicker):
  · 컴포넌트 이름: "DatePicker/Docked"
  · ⚠️ M3 스펙 / Flutter showDatePicker 미지원 → CalendarDatePicker 직접 배치
  · 캘린더 그리드 표시, 배경: Surface Container High
  · 선택 날짜: Primary 배경, On-Primary 텍스트

---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  // Modal calendar (기본)
  final date = await showDatePicker(
    context: context,
    initialDate: DateTime.now(),
    firstDate: DateTime(2000),
    lastDate: DateTime(2100),
  );

  // Input 모드
  final date = await showDatePicker(
    context: context,
    initialDate: DateTime.now(),
    firstDate: DateTime(2000),
    lastDate: DateTime(2100),
    initialEntryMode: DatePickerEntryMode.input,
  );

  // Date range
  final range = await showDateRangePicker(
    context: context,
    firstDate: DateTime(2000),
    lastDate: DateTime(2100),
  );

  // Docked/인라인 (CalendarDatePicker)
  CalendarDatePicker(
    initialDate: DateTime.now(),
    firstDate: DateTime(2000),
    lastDate: DateTime(2100),
    onDateChanged: (date) {},
  )

---

## Flutter Usage

```dart
import 'package:flutter_design/flutter_design.dart';

final cs = Theme.of(context).colorScheme;

// Modal Calendar — 단일 날짜 선택 (기본)
final date = await showDatePicker(
  context: context,
  initialDate: DateTime.now(),
  firstDate: DateTime(2000),
  lastDate: DateTime(2100),
  helpText: '날짜 선택',
  builder: (context, child) => Theme(
    data: Theme.of(context).copyWith(
      colorScheme: cs.copyWith(surface: cs.surfaceContainerHigh),
      dialogTheme: DialogThemeData(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadius.xl), // 28dp
        ),
      ),
    ),
    child: child!,
  ),
);

// Input 모드 — 키보드로 직접 날짜 입력
final date = await showDatePicker(
  context: context,
  initialDate: DateTime.now(),
  firstDate: DateTime(2000),
  lastDate: DateTime(2100),
  initialEntryMode: DatePickerEntryMode.input,
  helpText: '날짜 입력',
  fieldHintText: 'mm/dd/yyyy',
);

// selectableDayPredicate — 날짜 제한 (오늘 이후만 선택 가능)
final date = await showDatePicker(
  context: context,
  initialDate: DateTime.now(),
  firstDate: DateTime.now(),
  lastDate: DateTime(2100),
  selectableDayPredicate: (DateTime day) {
    // 오늘 포함 미래 날짜만 선택 가능
    final today = DateTime.now();
    return !day.isBefore(DateTime(today.year, today.month, today.day));
  },
);

// Date Range Picker — 범위 선택
final range = await showDateRangePicker(
  context: context,
  firstDate: DateTime(2000),
  lastDate: DateTime(2100),
  saveText: '선택',
  builder: (context, child) => child!,
);
// range?.start, range?.end 로 시작/종료 날짜 접근

// CalendarDatePicker — Docked/인라인 구현
// ⚠️ M3 Docked DatePicker를 Flutter에서 구현하려면 이 위젯을 직접 배치
CalendarDatePicker(
  initialDate: DateTime.now(),
  firstDate: DateTime(2000),
  lastDate: DateTime(2100),
  onDateChanged: (DateTime date) {
    // 날짜 변경 처리
  },
)
```
