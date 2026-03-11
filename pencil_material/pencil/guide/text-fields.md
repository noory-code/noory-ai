# Text Fields

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/text-fields/overview |
| Guidelines | https://m3.material.io/components/text-fields/guidelines |
| Specs | https://m3.material.io/components/text-fields/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| Filled text field | `TextField` / `TextFormField` (filled InputDecoration) |
| Outlined text field | `TextField` / `TextFormField` (outlined InputDecoration) |

## 언제 사용하나요?

- 사용자로부터 이름, 이메일, 비밀번호 등 텍스트 입력을 받을 때
- 폼(Form) 내에서 유효성 검사와 에러 메시지가 필요할 때
- 힌트, 레이블, 도우미 텍스트, 문자 카운터가 필요할 때
- 검색 입력, 댓글 작성, 채팅 입력처럼 자유 텍스트 입력

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | 전체 너비, 키보드 올라올 때 스크롤 보장 |
| Tablet (medium) | 고정 너비 (최대 480dp) 또는 2열 폼 |
| Desktop/Web (expanded) | 고정 너비 폼, 탭 키 네비게이션 지원 필수 |

## Variants

- **Filled** — 배경이 채워진 형태 (기본 권장)
- **Outlined** — 테두리로만 구분된 형태

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Text Fields Guide" 프레임을 만들어주세요.

모든 내용은 이 "Text Fields Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)
참고: https://m3.material.io/components/text-fields/overview

---

## 프레임 설정
- 이름: "Text Fields Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Text Fields"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · text-fields"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/text-fields/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 사용자로부터 이름, 이메일, 비밀번호 등 텍스트 입력을 받을 때
  · 폼 내에서 유효성 검사와 에러 메시지가 필요할 때
  · 힌트, 레이블, 도우미 텍스트, 문자 카운터가 필요할 때

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Filled / Outlined 각각 4개 States를 2행으로 배치

  Filled 행 (너비 180dp씩):
  ┌─ Enabled ─────┐  ┌─ Focused ─────┐  ┌─ Error ───────┐  ┌─ Disabled ────┐
  │ height: 56dp   │  │ height: 56dp   │  │ height: 56dp   │  │ height: 56dp   │
  │ bg: Surface-Var│  │ bg: Surface-Var│  │ bg: Surface-Var│  │ bg: 38% opaque │
  │ corner top 4dp │  │ 하단: 2dp Pri  │  │ 하단: 2dp Error│  │ 하단: 1dp Off  │
  │ label: 12sp    │  │ label: Primary │  │ label: Error   │  │ label: disabled│
  │ hpad: 16dp     │  │ hpad: 16dp     │  │ error msg 아래 │  │ hpad: 16dp     │
  └────────────────┘  └────────────────┘  └────────────────┘  └────────────────┘

  Outlined 행:
  ┌─ Enabled ─────┐  ┌─ Focused ─────┐  ┌─ Error ───────┐  ┌─ Disabled ────┐
  │ height: 56dp   │  │ height: 56dp   │  │ height: 56dp   │  │ height: 56dp   │
  │ border: 1dp    │  │ border: 2dp Pri│  │ border: 2dp Err│  │ border: 1dp    │
  │ Outline color  │  │ label: Primary │  │ label: Error   │  │ 38% opacity    │
  │ corner: 4dp    │  │ corner: 4dp    │  │ corner: 4dp    │  │ corner: 4dp    │
  └────────────────┘  └────────────────┘  └────────────────┘  └────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- Filled Text Field (Focused, with prefix/suffix)를 크게 그리고 번호 레이블 연결:
  1. Container — surfaceContainerHighest bg, top corner 4dp
  2. Active indicator — 하단 2dp, primary (focused) / onSurfaceVariant (enabled)
  3. Label — bodySmall 12sp (위로 올라간 상태) / bodyLarge 16sp (placeholder)
  4. Input text — bodyLarge 16sp, onSurface
  5. Leading icon (선택) — 24dp, onSurfaceVariant
  6. Trailing icon (선택) — 24dp, onSurfaceVariant (clear/visibility toggle 등)
  7. Prefix text (선택) — bodyLarge, onSurface (예: "$", "+82")
  8. Suffix text (선택) — bodyLarge, onSurface (예: "kg", ".com")
  9. Supporting text — bodySmall 12sp, 하단 (helper / error / counter)

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성                        | Filled                | Outlined              | 토큰                                    |
  |----------------------------|-----------------------|-----------------------|-----------------------------------------|
  | Height                     | 56 dp                 | 56 dp                 | —                                       |
  | Corner radius              | 4dp (top)             | 4 dp (all)            | —                                       |
  | Border (enabled)           | 1dp bottom            | 1dp all               | —                                       |
  | Border (focused)           | 2dp bottom, Primary   | 2dp all, Primary      | colorScheme.primary                     |
  | Border (error)             | 2dp bottom, Error     | 2dp all, Error        | colorScheme.error                       |
  | Horizontal pad             | 16 dp                 | 16 dp                 | —                                       |
  | Container bg               | surfaceContainerHighest| transparent          | colorScheme.surfaceContainerHighest     |
  | Label (floating) TextStyle | bodySmall 12sp        | bodySmall 12sp        | textTheme.bodySmall                     |
  | Label (resting) TextStyle  | bodyLarge 16sp        | bodyLarge 16sp        | textTheme.bodyLarge                     |
  | Input TextStyle            | bodyLarge 16sp        | bodyLarge 16sp        | textTheme.bodyLarge                     |
  | Prefix / Suffix text color | onSurface             | onSurface             | colorScheme.onSurface                   |
  | Icon size                  | 24 dp                 | 24 dp                 | —                                       |
  | Supporting text TextStyle  | bodySmall 12sp        | bodySmall 12sp        | textTheme.bodySmall                     |
  | Error color                | error                 | error                 | colorScheme.error                       |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  전체 너비, 키보드 스크롤 보장│
  │  → TextField / TextFormField│
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  고정 너비 최대 480dp, 2열  │
  │  → TextField               │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  고정 너비, 탭 네비게이션   │
  │  → TextField               │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Text Fields Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트를 2행으로 배치, 각 행 gap 24px, 행 간격 32px:

  [행 1 — Filled 계열]

  TextFields/Filled/Empty — Filled 빈 상태:
  · 컴포넌트 이름: "TextFields/Filled/Empty"
  · 높이: 56dp, 너비: 280dp
  · 배경: Surface Container Highest, 상단 corner: 4dp
  · 하단선: On-Surface-Variant 1dp
  · Label: 16sp, On-Surface-Variant (placeholder 위치)
  · 수평 패딩: 16dp

  TextFields/Filled/Focused — Filled 입력 상태:
  · 컴포넌트 이름: "TextFields/Filled/Focused"
  · 동일 구조, 하단선: Primary 2dp
  · Label: 12sp floating (상단), Primary 색상
  · 입력 텍스트: 16sp, On-Surface

  TextFields/Filled/WithIcons — Leading/Trailing 아이콘:
  · 컴포넌트 이름: "TextFields/Filled/WithIcons"
  · Leading icon: 24dp, On-Surface-Variant (좌측)
  · Trailing icon: 24dp, On-Surface-Variant (우측, X 또는 visibility)

  TextFields/Filled/WithPrefixSuffix — Prefix/Suffix 텍스트:
  · 컴포넌트 이름: "TextFields/Filled/WithPrefixSuffix"
  · Prefix text: "₩" 또는 "+82" (bodyLarge, On-Surface)
  · Suffix text: "kg" 또는 ".com" (bodyLarge, On-Surface)

  [행 2 — Outlined 계열]

  TextFields/Outlined/Empty — Outlined 빈 상태:
  · 컴포넌트 이름: "TextFields/Outlined/Empty"
  · 높이: 56dp, 너비: 280dp, 배경: 투명
  · 테두리: Outline 1dp, corner 4dp
  · Label: 16sp, On-Surface-Variant

  TextFields/Outlined/Focused — Outlined 입력 상태:
  · 컴포넌트 이름: "TextFields/Outlined/Focused"
  · 테두리: Primary 2dp
  · Label: 12sp floating, Primary 색상

---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (배경: surfaceContainerHighest, radius 8px, padding 16px):
  // Filled — prefixIcon + suffixIcon
  TextField(
    decoration: InputDecoration(
      filled: true,
      labelText: 'Email',
      hintText: 'user@example.com',
      prefixIcon: Icon(Icons.email_outlined),
      suffixIcon: Icon(Icons.clear),
    ),
  )

  // Outlined — prefixText + suffixText
  TextField(
    decoration: InputDecoration(
      border: OutlineInputBorder(),
      labelText: '금액',
      prefixText: '₩ ',
      suffixText: 'KRW',
    ),
  )

  // Error state + helperText
  TextField(
    decoration: InputDecoration(
      border: OutlineInputBorder(),
      labelText: '이메일',
      errorText: '올바른 이메일을 입력하세요',
      helperText: '예: user@example.com',
    ),
  )

---

## Flutter Usage

```dart
import 'package:flutter_design/flutter_design.dart';

final cs = Theme.of(context).colorScheme;

// [InputDecoration prefix/suffix 종류]
// prefixIcon   — 좌측 아이콘 위젯 (Icon, 24dp)
// prefixText   — 좌측 텍스트 (예: "₩", "+82")
// prefix       — 좌측 커스텀 위젯 (prefixText/prefixIcon 대신)
// suffixIcon   — 우측 아이콘 위젯 (clear, visibility 등)
// suffixText   — 우측 텍스트 (예: "kg", ".com")
// suffix       — 우측 커스텀 위젯
// ⚠️ prefixIcon과 prefix 동시 사용 불가, suffix도 동일

// Filled TextField — Leading icon
TextField(
  decoration: InputDecoration(
    filled: true,
    labelText: '이메일',
    hintText: 'user@example.com',
    prefixIcon: Icon(Icons.email_outlined, size: AppIconSize.md), // 24dp
    border: UnderlineInputBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(AppRadius.xs)), // 4dp
    ),
  ),
)

// Filled TextField — Trailing icon (clear 버튼)
TextField(
  controller: _controller,
  decoration: InputDecoration(
    filled: true,
    labelText: '검색',
    suffixIcon: _controller.text.isEmpty
        ? null
        : IconButton(
            icon: const Icon(Icons.clear),
            onPressed: () => _controller.clear(),
          ),
  ),
)

// Outlined TextField — prefixText (통화, 단위)
TextField(
  decoration: InputDecoration(
    border: const OutlineInputBorder(
      borderRadius: BorderRadius.all(Radius.circular(AppRadius.xs)), // 4dp
    ),
    labelText: '금액',
    prefixText: '₩ ',             // 입력 영역 왼쪽에 텍스트 고정
    suffixText: 'KRW',            // 입력 영역 오른쪽에 텍스트 고정
    prefixStyle: TextStyle(color: cs.onSurface),
    suffixStyle: TextStyle(color: cs.onSurfaceVariant),
  ),
  keyboardType: TextInputType.number,
)

// Outlined TextField — prefixText (국제전화 코드)
TextField(
  decoration: InputDecoration(
    border: const OutlineInputBorder(),
    labelText: '전화번호',
    prefixText: '+82 ',
    hintText: '010-0000-0000',
  ),
  keyboardType: TextInputType.phone,
)

// Outlined TextField — prefix 커스텀 위젯 (드롭다운 등)
TextField(
  decoration: InputDecoration(
    border: const OutlineInputBorder(),
    labelText: '도메인',
    suffix: DropdownButton<String>(
      value: _domain,
      underline: const SizedBox.shrink(),
      items: const [
        DropdownMenuItem(value: '.com', child: Text('.com')),
        DropdownMenuItem(value: '.co.kr', child: Text('.co.kr')),
      ],
      onChanged: (v) => setState(() => _domain = v!),
    ),
  ),
)

// Outlined TextField — Password (visibility toggle)
TextField(
  obscureText: _obscure,
  decoration: InputDecoration(
    border: const OutlineInputBorder(),
    labelText: '비밀번호',
    prefixIcon: const Icon(Icons.lock_outline),
    suffixIcon: IconButton(
      icon: Icon(_obscure ? Icons.visibility_off : Icons.visibility),
      onPressed: () => setState(() => _obscure = !_obscure),
    ),
    focusedBorder: OutlineInputBorder(
      borderSide: BorderSide(color: cs.primary, width: 2),
    ),
    errorBorder: OutlineInputBorder(
      borderSide: BorderSide(color: cs.error, width: 2),
    ),
  ),
)

// Error + Helper + Counter
TextField(
  maxLength: 50,
  decoration: InputDecoration(
    border: const OutlineInputBorder(),
    labelText: '닉네임',
    helperText: '특수문자 제외, 2–20자',       // 정상 상태 안내
    errorText: _error,                          // null이면 helperText 표시
    counterText: '${_value.length}/50',         // 직접 제어 시
  ),
)
```
