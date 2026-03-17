---
name: flutter-google-fonts
description: Applying fonts using google_fonts
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [google_fonts, font, google fonts, typography]
---

# Flutter Google Fonts

Download and apply Google Fonts at runtime.

---

## Installation

```bash
flutter pub add google_fonts
```

---

## Quick Reference

```dart
import 'package:google_fonts/google_fonts.dart';

// basic usage (static method)
Text(
  'Hello World',
  style: GoogleFonts.lato(),
)

// customize style
Text(
  'Hello World',
  style: GoogleFonts.lato(
    fontSize: 24,
    fontWeight: FontWeight.bold,
    color: Colors.black,
  ),
)

// dynamic font name
Text(
  'Hello World',
  style: GoogleFonts.getFont('Noto Sans KR'),
)

// apply font on top of an existing TextStyle
Text(
  'Hello World',
  style: GoogleFonts.lato(textStyle: existingStyle),
)
```

### App-wide Application

```dart
MaterialApp(
  theme: ThemeData(
    textTheme: GoogleFonts.latoTextTheme(),
  ),
)

// apply font while preserving the existing theme's styles
MaterialApp(
  theme: ThemeData(
    textTheme: GoogleFonts.latoTextTheme(
      Theme.of(context).textTheme,
    ),
  ),
)
```

### Font Preloading

```dart
// main.dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // preload fonts before the app starts
  await GoogleFonts.pendingFonts([
    GoogleFonts.lato(),
    GoogleFonts.notoSansKr(),
  ]);

  runApp(MyApp());
}
```

### Offline Usage (Asset Bundling)

```yaml
# pubspec.yaml
flutter:
  assets:
    - google_fonts/
```

```
# folder structure
assets/
└── google_fonts/
    ├── Lato-Regular.ttf
    ├── Lato-Bold.ttf
    └── NotoSansKR-Regular.otf
```

> When included in the app bundle, fonts are available immediately without a runtime download.

---

## Common Issues

| Issue | Fix |
|------|------|
| Font not visible | Check internet connection or use asset bundling |
| Korean text broken | Use a Korean-supporting font such as `Noto Sans KR` |
| Slow first load | Preload with `pendingFonts()` |
| App size increase | Include only the needed weights in assets |

---

## Commonly Used Fonts

| Use Case | Font |
|------|------|
| English body | Lato, Roboto, Open Sans |
| English heading | Montserrat, Poppins |
| Korean | Noto Sans KR, Pretendard |
| Code | Fira Code, JetBrains Mono |

---

## Changelog

### [1.1.0] - 2026-03-01
- Initial release
