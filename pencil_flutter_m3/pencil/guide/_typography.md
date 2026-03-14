# Typography

## M3 링크

| 페이지 | URL |
|--------|-----|
| Type Scale | https://m3.material.io/styles/typography/overview |
| Type Tokens | https://m3.material.io/styles/typography/fonts |

---

## 토큰 정의

펜슬 `typography/` 토큰 → Flutter `TextTheme` 1:1 대응.

| Pencil 토큰 | Flutter | size | lineHeight | weight |
|------------|---------|------|-----------|--------|
| `typography/display/large` | `displayLarge` | 57sp | 1.12 | w300 |
| `typography/display/medium` | `displayMedium` | 45sp | 1.16 | w300 |
| `typography/display/small` | `displaySmall` | 36sp | 1.22 | w400 |
| `typography/headline/large` | `headlineLarge` | 32sp | 1.25 | w400 |
| `typography/headline/medium` | `headlineMedium` | 28sp | 1.29 | w400 |
| `typography/headline/small` | `headlineSmall` | 24sp | 1.33 | w400 |
| `typography/title/large` | `titleLarge` | 22sp | 1.27 | w400 |
| `typography/title/medium` | `titleMedium` | 16sp | 1.50 | w500 |
| `typography/title/small` | `titleSmall` | 14sp | 1.43 | w500 |
| `typography/body/large` | `bodyLarge` | 16sp | 1.50 | w400 |
| `typography/body/medium` | `bodyMedium` | 14sp | 1.43 | w400 |
| `typography/body/small` | `bodySmall` | 12sp | 1.33 | w400 |
| `typography/label/large` | `labelLarge` | 14sp | 1.43 | w500 |
| `typography/label/medium` | `labelMedium` | 12sp | 1.33 | w500 |
| `typography/label/small` | `labelSmall` | 11sp | 1.45 | w500 |

---

## Flutter 사용법

### 1. ThemeData 세팅 (AppTheme)

**파일**: `lib/src/theme.dart` → `AppTheme`

`AppTheme.light` / `AppTheme.dark` 안에 `TextTheme`이 이미 세팅되어 있다.
별도로 할 작업 없음.

```dart
// MaterialApp 세팅
MaterialApp(
  theme: AppTheme.light,
  darkTheme: AppTheme.dark,
  themeMode: ThemeMode.system,
)
```

### 2. 위젯에서 텍스트 스타일 접근

```dart
// 기본 접근법
Theme.of(context).textTheme.bodyMedium      // 14sp, w400
Theme.of(context).textTheme.titleLarge      // 22sp, w400
Theme.of(context).textTheme.labelSmall      // 11sp, w500

// 실제 사용 예시
Text(
  '제목',
  style: Theme.of(context).textTheme.headlineMedium,
)

Text(
  '본문',
  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
    color: Theme.of(context).colorScheme.onSurfaceVariant,
  ),
)
```

### 3. 언제 어떤 스타일을 쓰나?

| 용도 | TextTheme | Pencil 토큰 |
|------|-----------|------------|
| 화면 최상단 대형 타이틀 | `displayLarge` | display/large |
| 페이지 제목 | `headlineLarge` | headline/large |
| 카드 제목 | `titleMedium` | title/medium |
| 본문 텍스트 | `bodyMedium` | body/medium |
| 설명 텍스트 | `bodySmall` | body/small |
| 버튼 레이블 | `labelLarge` | label/large |
| 캡션, 뱃지 | `labelSmall` | label/small |

---

## Pencil 프롬프트

아래 프롬프트를 Pencil AI에 입력해서 가이드 프레임을 생성한다.

---

다음 지시에 따라 Pencil에 "Typography Guide" 프레임을 만들어주세요.
색상: material-design-guide.lib.pen 의 M3 Color Scheme 토큰 참조 ($primary, $surface, $onSurface, $outlineVariant 등)

참고: https://m3.material.io/styles/typography/overview

---

## 프레임 설정
- 이름: "Typography Guide"
- 배경: Surface
- 레이아웃: 수직, 섹션 간격 48px, 좌우 패딩 40px

---

## 섹션 1 — Header
- 제목: "Typography"  (32px, bold, On-Surface)
- 부제목: "Material Design 3 · Type Scale"  (14px, On-Surface-Variant)
- 링크: "m3.material.io/styles/typography/overview"  (12px, Primary)
- 구분선: 전체 너비, 1px, Outline Variant

---

## 섹션 2 — Type Scale
- 소제목: "Type Scale"  (20px, 600)
- 15개 스타일을 수직 나열, 각 행:

  [카테고리 태그 80px] [샘플 텍스트 "The quick brown fox"] [크기·굵기 정보]

  · Display Large   — 57sp, w300 — "The quick brown fox"  (57px)
  · Display Medium  — 45sp, w300 — "The quick brown fox"  (45px)
  · Display Small   — 36sp, w400 — "The quick brown fox"  (36px)
  · Headline Large  — 32sp, w400 — "The quick brown fox"  (32px)
  · Headline Medium — 28sp, w400 — "The quick brown fox"  (28px)
  · Headline Small  — 24sp, w400 — "The quick brown fox"  (24px)
  · Title Large     — 22sp, w400 — "The quick brown fox"  (22px)
  · Title Medium    — 16sp, w500 — "The quick brown fox"  (16px)
  · Title Small     — 14sp, w500 — "The quick brown fox"  (14px)
  · Body Large      — 16sp, w400 — "The quick brown fox"  (16px)
  · Body Medium     — 14sp, w400 — "The quick brown fox"  (14px)
  · Body Small      — 12sp, w400 — "The quick brown fox"  (12px)
  · Label Large     — 14sp, w500 — "The quick brown fox"  (14px)
  · Label Medium    — 12sp, w500 — "The quick brown fox"  (12px)
  · Label Small     — 11sp, w500 — "The quick brown fox"  (11px)

  모든 텍스트: On-Surface 색상

---

## 섹션 3 — Usage Guide
- 소제목: "Usage Guide"  (20px, 600)
- 테이블:
  | 용도 | Style | Pencil 토큰 |
  |------|-------|------------|
  | 화면 최상단 대형 타이틀 | displayLarge | typography/display/large |
  | 페이지 제목 | headlineLarge | typography/headline/large |
  | 카드 제목 | titleMedium | typography/title/medium |
  | 본문 텍스트 | bodyMedium | typography/body/medium |
  | 설명 텍스트 | bodySmall | typography/body/small |
  | 버튼 레이블 | labelLarge | typography/label/large |
  | 캡션, 뱃지 | labelSmall | typography/label/small |

---

## 섹션 4 — Flutter Usage
- 소제목: "Flutter Usage"  (20px, 600)
- 코드 박스 (background surfaceContainerHighest, radius 8px, padding 16px):
  // TextTheme 접근
  final tt = Theme.of(context).textTheme;

  Text('페이지 제목', style: tt.headlineLarge)
  Text('카드 제목',  style: tt.titleMedium)
  Text('본문',       style: tt.bodyMedium)
  Text('캡션',       style: tt.labelSmall)

  // 색상 조합
  Text(
    '보조 설명',
    style: tt.bodySmall?.copyWith(
      color: Theme.of(context).colorScheme.onSurfaceVariant,
    ),
  )
