# Time Pickers

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/time-pickers/overview |
| Guidelines | https://m3.material.io/components/time-pickers/guidelines |
| Specs | https://m3.material.io/components/time-pickers/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| Dial picker | `showTimePicker()` → `TimePickerDialog` |
| Input picker | `showTimePicker(initialEntryMode: TimePickerEntryMode.input)` |

## 언제 사용하나요?

- 알람 설정, 예약 시간처럼 특정 시각을 선택해야 할 때
- 직관적인 다이얼 UI로 시/분을 선택해야 할 때
- 키보드 입력 모드를 대안으로 제공해 접근성을 높여야 할 때
- 12시간/24시간 포맷 중 지역 설정에 맞는 형식이 필요할 때

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | Dial 타임피커 (Modal 다이얼로그) |
| Tablet (medium) | Dial 또는 Input 타임피커 |
| Desktop/Web (expanded) | Input 타임피커 권장 (마우스 환경에서 다이얼 사용성 낮음) |

## Variants

- **Dial** — 시계 다이얼 형태로 선택 (기본, 터치 최적화)
- **Input** — 텍스트 필드 직접 입력 (키보드 환경 최적화)

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Time Pickers Guide" 프레임을 만들어주세요.

모든 내용은 이 "Time Pickers Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)
참고: https://m3.material.io/components/time-pickers/overview

---

## 프레임 설정
- 이름: "Time Pickers Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Time Pickers"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · time-pickers"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/time-pickers/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 알람 설정, 예약 시간처럼 특정 시각을 선택해야 할 때
  · 직관적인 다이얼 UI로 시/분을 선택해야 할 때
  · 키보드 입력 모드를 대안으로 제공해 접근성을 높여야 할 때

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Variant 2개를 가로 나란히 배치, gap 24px

  ┌─ Dial Picker ──────────────────────┐
  │  다이얼로그 (280×400dp)             │
  │  배경: Surface Container High       │
  │  corner: 28dp                      │
  │  상단: "Select time" (14sp)         │
  │  시:분 표시 (48sp bold):            │
  │    "09" (selected, Primary bg)     │
  │    " : "                           │
  │    "30" (Secondary Container bg)   │
  │  시계 다이얼: 원형 200dp            │
  │    track: Surface Container        │
  │    선택 핸드: Primary               │
  │    AM/PM 토글                       │
  │  하단: 취소/확인 버튼               │
  └────────────────────────────────────┘

  ┌─ Input Picker ─────────────────────┐
  │  다이얼로그 (280×220dp)             │
  │  배경: Surface Container High       │
  │  corner: 28dp                      │
  │  상단: "Enter time" (14sp)          │
  │  시:분 입력 필드:                   │
  │    Outlined TextField × 2         │
  │    "09" "30"                       │
  │  AM/PM 선택 (SegmentedButton)       │
  │  하단: 취소/확인 버튼               │
  └────────────────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- Dial Picker를 크게 그리고 번호 레이블 연결:
  1. Dialog container — corner 28dp, Surface Container High
  2. Time display — Hour:Minute (48sp, 선택된 항목 Primary bg)
  3. AM/PM selector
  4. Clock dial — 원형 다이얼, 숫자 배치
  5. Selection handle — Primary 색상 핸드
  6. Action buttons — 취소/확인

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성                | 값                  |
  |--------------------|---------------------|
  | Dialog corner      | 28 dp               |
  | Time display font  | 48sp                |
  | Dial diameter      | 200 dp              |
  | Color (bg)         | Surface Container High|
  | Color (selected)   | Primary             |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  Dial 타임피커 (Modal)      │
  │  → showTimePicker()        │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  Dial 또는 Input           │
  │  → showTimePicker()        │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  Input 타임피커 권장        │
  │  → showTimePicker(         │
  │      initialEntryMode:     │
  │      TimePickerEntryMode.input) │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Time Pickers Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트 2개를 가로 나란히 배치, gap 24px:

  TimePicker/Dial — 시계 다이얼형:
  · 컴포넌트 이름: "TimePicker/Dial"
  · 다이얼로그: 280×400dp, corner 28dp
  · 배경: Surface Container High
  · 시:분 표시: 48sp bold, 선택 배경 Primary Container
  · 다이얼: 256dp 지름, 선택 핸드 Primary
  · AM/PM 토글 포함

  TimePicker/Input — 텍스트 입력형:
  · 컴포넌트 이름: "TimePicker/Input"
  · 다이얼로그: 280×220dp, corner 28dp
  · 배경: Surface Container High
  · 시:분 Outlined TextField × 2
  · AM/PM SegmentedButton 포함


---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (배경: surfaceContainerHighest, radius 8px, padding 16px):
  // Dial (기본)
  final time = await showTimePicker(
    context: context,
    initialTime: TimeOfDay.now(),
  );

  // Input mode
  final time = await showTimePicker(
    context: context,
    initialTime: TimeOfDay.now(),
    initialEntryMode: TimePickerEntryMode.input,
  );

---

## Flutter Usage

```dart
import 'package:flutter_design/flutter_design.dart';

final cs = Theme.of(context).colorScheme;

// Dial Time Picker (기본)
Future<void> _pickTime(BuildContext context) async {
  final TimeOfDay? time = await showTimePicker(
    context: context,
    initialTime: TimeOfDay.now(),
    builder: (context, child) => Theme(
      data: Theme.of(context).copyWith(
        colorScheme: cs.copyWith(
          primary: cs.primary,
          onPrimary: cs.onPrimary,
          surface: cs.surfaceContainerHigh,
        ),
      ),
      child: child!,
    ),
  );
  if (time != null) {
    // time.hour, time.minute 사용
  }
}

// Input Mode Time Picker
final TimeOfDay? time = await showTimePicker(
  context: context,
  initialTime: TimeOfDay.now(),
  initialEntryMode: TimePickerEntryMode.input,
);
```
