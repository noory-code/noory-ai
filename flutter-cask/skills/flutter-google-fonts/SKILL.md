---
name: flutter-google-fonts
description: google_fonts를 사용한 폰트 적용
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [google_fonts, 폰트, font, 구글 폰트, typography]
---

# Flutter Google Fonts

Google Fonts를 런타임에 다운로드하여 적용.

---

## 설치

```bash
flutter pub add google_fonts
```

---

## Quick Reference

```dart
import 'package:google_fonts/google_fonts.dart';

// 기본 사용 (정적 메서드)
Text(
  'Hello World',
  style: GoogleFonts.lato(),
)

// 스타일 커스터마이징
Text(
  'Hello World',
  style: GoogleFonts.lato(
    fontSize: 24,
    fontWeight: FontWeight.bold,
    color: Colors.black,
  ),
)

// 동적 폰트 이름
Text(
  'Hello World',
  style: GoogleFonts.getFont('Noto Sans KR'),
)

// 기존 TextStyle에 폰트만 적용
Text(
  'Hello World',
  style: GoogleFonts.lato(textStyle: existingStyle),
)
```

### 앱 전역 적용

```dart
MaterialApp(
  theme: ThemeData(
    textTheme: GoogleFonts.latoTextTheme(),
  ),
)

// 기존 테마에 폰트만 적용
MaterialApp(
  theme: ThemeData(
    textTheme: GoogleFonts.latoTextTheme(
      Theme.of(context).textTheme,
    ),
  ),
)
```

### 폰트 프리로딩

```dart
// main.dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // 폰트 미리 로드
  await GoogleFonts.pendingFonts([
    GoogleFonts.lato(),
    GoogleFonts.notoSansKr(),
  ]);

  runApp(MyApp());
}
```

### 오프라인 사용 (에셋 번들링)

```yaml
# pubspec.yaml
flutter:
  assets:
    - google_fonts/
```

```
# 폴더 구조
assets/
└── google_fonts/
    ├── Lato-Regular.ttf
    ├── Lato-Bold.ttf
    └── NotoSansKR-Regular.otf
```

> 앱 번들에 포함하면 런타임 다운로드 없이 즉시 사용

---

## 주의사항

| 상황 | 해결 |
|------|------|
| 폰트 안 보임 | 인터넷 연결 확인 또는 에셋 번들링 |
| 한글 깨짐 | `Noto Sans KR` 등 한글 지원 폰트 사용 |
| 첫 로드 느림 | `pendingFonts()`로 프리로딩 |
| 앱 용량 증가 | 필요한 weight만 에셋에 포함 |

---

## 자주 쓰는 폰트

| 용도 | 폰트 |
|------|------|
| 영문 본문 | Lato, Roboto, Open Sans |
| 영문 제목 | Montserrat, Poppins |
| 한글 | Noto Sans KR, Pretendard |
| 코드 | Fira Code, JetBrains Mono |
