# Switch

## M3 링크

| 페이지 | URL |
|--------|-----|
| Overview | https://m3.material.io/components/switch/overview |
| Guidelines | https://m3.material.io/components/switch/guidelines |
| Specs | https://m3.material.io/components/switch/specs |

## Flutter 위젯 매핑

| M3 Variant | Flutter 위젯 |
|-----------|-------------|
| Switch | `Switch` |
| Adaptive | `Switch.adaptive()` |
| With label | `SwitchListTile` |

## 언제 사용하나요?

- 기능 켜기/끄기처럼 즉각 반영되는 이진 설정
- 확인 버튼 없이 즉시 상태가 변경되어야 할 때
- 설정 화면에서 여러 독립 옵션을 On/Off로 제어할 때
- Checkbox보다 On/Off 의미가 더 명확할 때

## 반응형 가이드라인

| 화면 크기 | 권장 사항 |
|----------|---------|
| Mobile (compact) | 전체 너비 SwitchListTile, 우측 트레일링 배치 |
| Tablet (medium) | 동일, 2열 설정 레이아웃 가능 |
| Desktop/Web (expanded) | 인라인 레이블 + Switch, 호버 상태 지원 |

## Variants

- **Standard** — 기본 Switch
- **With icon** — 썸 내부에 아이콘 표시
- **Adaptive** — 플랫폼에 맞는 네이티브 스타일

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---


다음 지시에 따라 Pencil에 "Switch Guide" 프레임을 만들어주세요.

모든 내용은 이 "Switch Guide" 프레임 하나 안에 그린다. 섹션 7의 컴포넌트도 이 프레임 안에 직접 그린다.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)
참고: https://m3.material.io/components/switch/overview

---

## 프레임 설정
- 이름: "Switch Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Switch"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · switch"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/components/switch/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — When to use
- 소제목: "When to use"  (20px, 600)
- 불릿 리스트:
  · 기능 켜기/끄기처럼 즉각 반영되는 이진 설정
  · 확인 버튼 없이 즉시 상태가 변경되어야 할 때
  · 설정 화면에서 여러 독립 옵션을 On/Off로 제어할 때

---

## 섹션 3 — Variants
- 소제목: "Variants"  (20px, 600)
- Off/On 상태 쌍을 가로 나열, gap 24px

  ┌─ Off ──────────────────────┐
  │  track: 52×32dp, corner 16dp│
  │  track: surfaceContainerHighest│
  │  border: 2dp, outline       │
  │  thumb: 16dp, outline       │
  │  thumb 위치: 좌측           │
  └─────────────────────────────┘

  ┌─ On ───────────────────────┐
  │  track: 52×32dp, corner 16dp│
  │  track: primary             │
  │  thumb: 24dp, onPrimary    │
  │  thumb 위치: 우측           │
  └─────────────────────────────┘

  ┌─ With Icon (On) ───────────┐
  │  동일 구조                  │
  │  thumb 내부: check 16dp     │
  │  아이콘: onPrimaryContainer │
  └─────────────────────────────┘

---

## 섹션 4 — Anatomy
- 소제목: "Anatomy"  (20px, 600)
- On 상태 Switch를 크게 그리고 번호 레이블 연결:
  1. Track — 52×32dp, corner 16dp (on: primary / off: surfaceContainerHighest)
  2. Thumb — 24dp (on: onPrimary) / 16dp (off: outline)
  3. Icon (선택) — 16dp, thumb 중앙 (thumbIcon 파라미터)
  4. Touch target — 48dp 높이

---

## 섹션 5 — Specs
- 소제목: "Specs"  (20px, 600)
- 테이블:
  | 속성                   | 값 (Off)                 | 값 (On)                 | 토큰                                    |
  |-----------------------|--------------------------|-------------------------|-----------------------------------------|
  | Track size            | 52 × 32 dp               | 52 × 32 dp              | —                                       |
  | Track corner          | 16 dp                    | 16 dp                   | —                                       |
  | Track bg              | surfaceContainerHighest  | primary                 | colorScheme.surfaceContainerHighest / .primary |
  | Track border          | outline 2dp              | 없음                    | colorScheme.outline                     |
  | Thumb size            | 16 dp                    | 24 dp                   | —                                       |
  | Thumb color           | outline                  | onPrimary               | colorScheme.outline / .onPrimary        |
  | Touch target          | 48 dp                    | 동일                    | —                                       |
  | Icon size (선택)      | 16 dp                    | 16 dp                   | —                                       |

---

## 섹션 6 — Responsive
- 소제목: "Responsive"  (20px, 600)
- 세 박스 가로 배치 (너비 균등):

  ┌─ Mobile / compact ─────────┐
  │  전체 너비 SwitchListTile   │
  │  → SwitchListTile          │
  └─────────────────────────────┘

  ┌─ Tablet / medium ──────────┐
  │  2열 설정 레이아웃 가능      │
  │  → SwitchListTile          │
  └─────────────────────────────┘

  ┌─ Desktop / expanded ───────┐
  │  인라인 레이블 + Switch     │
  │  → Switch + label Row      │
  └─────────────────────────────┘

---

## 섹션 7 — Component
- 소제목: "Component"  (20px, 600)
- 이 "Switch Guide" 프레임 안에 아래 컴포넌트들을 그리고, 각각 리유저블 컴포넌트로 등록한다
- 컴포넌트 4개를 가로 나란히 배치, gap 24px:

  Switch/Off — 꺼진 상태:
  · 컴포넌트 이름: "Switch/Off"
  · Track: 52×32dp, corner 16dp, Surface Container Highest
  · Track 테두리: Outline 2dp
  · Thumb: 16×16dp, Outline 색상, 좌측 위치
  · 터치 타겟: 48dp 높이

  Switch/On — 켜진 상태:
  · 컴포넌트 이름: "Switch/On"
  · Track: 52×32dp, corner 16dp, Primary
  · Thumb: 24×24dp, On-Primary 색상, 우측 위치

  Switch/Off/WithIcon — 꺼진 상태 + 아이콘:
  · 컴포넌트 이름: "Switch/Off/WithIcon"
  · Off 구조 + Thumb 내부 아이콘 16dp, Surface-Variant

  Switch/On/WithIcon — 켜진 상태 + 아이콘:
  · 컴포넌트 이름: "Switch/On/WithIcon"
  · On 구조 + Thumb 내부 check 아이콘 16dp, On-Primary-Container


---

## 섹션 8 — Flutter Widget
- 소제목: "Flutter Widget"  (20px, 600)
- 코드 박스 (배경: surfaceContainerHighest, radius 8px, padding 16px):
  Switch(value: isOn, onChanged: (v) => setState(() => isOn = v))
  Switch.adaptive(value: isOn, onChanged: (v) => setState(() => isOn = v))
  SwitchListTile(
    title: Text('Notifications'),
    value: isOn,
    onChanged: (v) => setState(() => isOn = v),
  )

---

## Flutter Usage

```dart
import 'package:flutter_design/flutter_design.dart';

final cs = Theme.of(context).colorScheme;

// SwitchListTile — 설정 화면 (기본, 테마 자동 적용)
SwitchListTile(
  title: const Text('알림'),
  subtitle: const Text('앱 알림을 받습니다.'),
  value: _isOn,
  onChanged: (bool val) => setState(() => _isOn = val),
)

// Switch 단독 — 인라인 배치
Row(
  mainAxisAlignment: MainAxisAlignment.spaceBetween,
  children: [
    const Text('다크 모드'),
    Switch(
      value: _isDark,
      onChanged: (bool val) => setState(() => _isDark = val),
    ),
  ],
)

// thumbIcon — 아이콘 포함 썸
Switch(
  value: _isOn,
  thumbIcon: WidgetStateProperty.resolveWith<Icon?>((states) {
    if (states.contains(WidgetState.selected)) {
      return const Icon(Icons.check);  // On: 체크
    }
    return const Icon(Icons.close);  // Off: X
  }),
  onChanged: (val) => setState(() => _isOn = val),
)

// Switch.adaptive — 플랫폼별 네이티브 스타일 (iOS: Cupertino)
Switch.adaptive(
  value: _isOn,
  onChanged: (val) => setState(() => _isOn = val),
)

// Disabled — onChanged: null
Switch(value: false, onChanged: null)
SwitchListTile(title: const Text('비활성'), value: false, onChanged: null)
```
