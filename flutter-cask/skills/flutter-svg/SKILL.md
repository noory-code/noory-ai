---
name: flutter-svg
description: SVG vector image rendering
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [SVG, flutter_svg, vector image, icon, scalable]
---

# Flutter SVG

SVG vector image rendering. Ideal for resolution-independent icons and logos.

---

## Installation

```bash
flutter pub add flutter_svg
```

---

## Quick Reference

### Basic Usage

```dart
import 'package:flutter_svg/flutter_svg.dart';

// load from assets
SvgPicture.asset(
  'assets/icons/logo.svg',
  width: 100,
  height: 100,
)

// load from network
SvgPicture.network(
  'https://example.com/icon.svg',
  placeholderBuilder: (context) => CircularProgressIndicator(),
)

// load from string
SvgPicture.string(
  '<svg viewBox="0 0 100 100">...</svg>',
)
```

### Change Color

```dart
SvgPicture.asset(
  'assets/icons/heart.svg',
  colorFilter: ColorFilter.mode(
    Colors.red,
    BlendMode.srcIn,
  ),
)

// use theme color
SvgPicture.asset(
  'assets/icons/menu.svg',
  colorFilter: ColorFilter.mode(
    Theme.of(context).iconTheme.color!,
    BlendMode.srcIn,
  ),
)
```

### Resize

```dart
// fixed size
SvgPicture.asset(
  'assets/logo.svg',
  width: 200,
  height: 100,
)

// fit to parent
SvgPicture.asset(
  'assets/logo.svg',
  fit: BoxFit.contain,  // contain, cover, fill, fitWidth, fitHeight
)

// maintain aspect ratio
SizedBox(
  width: 100,
  child: SvgPicture.asset(
    'assets/logo.svg',
    fit: BoxFit.fitWidth,
  ),
)
```

### Register Assets (pubspec.yaml)

```yaml
flutter:
  assets:
    - assets/icons/
    - assets/images/
```

### Caching (precache)

```dart
// preload at app startup
Future<void> precacheSvgs(BuildContext context) async {
  await Future.wait([
    precachePicture(
      ExactAssetPicture(SvgPicture.svgStringDecoderBuilder, 'assets/icons/logo.svg'),
      context,
    ),
  ]);
}
```

---

## Common Issues

| Issue | Fix |
|------|------|
| SVG not showing | Register the assets path in pubspec.yaml |
| Color not changing | Check if the fill/stroke attribute in the SVG uses currentColor |
| Complex SVG is slow | Simplify the SVG or replace with a PNG |
| Gradient broken | Some gradients have limited support in flutter_svg |
| CORS on web | Use the same domain or configure CORS headers |

---

## SVG Optimization Tips

```dart
// 1. Use a 24x24 or 48x48 viewBox for icons
// 2. Remove unnecessary metadata (use SVGO)
// 3. For monochrome icons, keep only the path and set fill="currentColor"
// 4. Consider PNG for complex illustrations
```

---

## Changelog

### [1.1.0] - 2026-03-01
- 초기 릴리스
