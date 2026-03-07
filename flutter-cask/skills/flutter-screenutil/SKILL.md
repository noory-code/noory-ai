---
name: flutter-screenutil
description: Screen size adaptive utility for responsive UI
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [screenutil, responsive, screen size, adaptive UI, scaling]
---

# Flutter ScreenUtil

Scale UI responsively based on a design reference size. Enables pixel-perfect reproduction of Figma designs across devices.

---

## Installation

```bash
flutter pub add flutter_screenutil
```

---

## Quick Reference

### Initialization

```dart
import 'package:flutter_screenutil/flutter_screenutil.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return ScreenUtilInit(
      // Figma design reference size
      designSize: Size(375, 812),  // based on iPhone X
      minTextAdapt: true,
      splitScreenMode: true,
      builder: (context, child) {
        return MaterialApp(
          home: HomePage(),
        );
      },
    );
  }
}
```

### Size Units

```dart
// width-based scale (w)
Container(
  width: 100.w,   // 100px in the design, scaled to fit the screen
  height: 50.h,  // height-based scale (h)
)

// radius (r) — for circles and rounded corners
Container(
  decoration: BoxDecoration(
    borderRadius: BorderRadius.circular(8.r),
  ),
)

// scale-independent pixels (sp) — primarily for font sizes
Text(
  'Hello',
  style: TextStyle(fontSize: 16.sp),
)

// use .w for both dimensions when a square is needed
Container(
  width: 50.w,
  height: 50.w,
)
```

### Font Scaling

```dart
Text(
  'Title',
  style: TextStyle(
    fontSize: 24.sp,
    fontWeight: FontWeight.bold,
  ),
)

Text(
  'Body',
  style: TextStyle(
    fontSize: 14.sp,
    height: 1.5,
  ),
)
```

### Margin and Padding

```dart
Padding(
  padding: EdgeInsets.symmetric(
    horizontal: 16.w,
    vertical: 12.h,
  ),
  child: ...,
)

// same in all directions
Padding(
  padding: EdgeInsets.all(16.r),
  child: ...,
)

SizedBox(height: 24.h)
SizedBox(width: 16.w)
```

### Screen Info

```dart
// screen width/height
final screenWidth = 1.sw;   // 100% of screen width
final screenHeight = 1.sh;  // 100% of screen height

// half screen width
Container(width: 0.5.sw)

// status bar and bottom bar heights
final statusBarHeight = ScreenUtil().statusBarHeight;
final bottomBarHeight = ScreenUtil().bottomBarHeight;
```

### Conditional Layout

```dart
// detect tablet
if (1.sw > 600) {
  // tablet layout
} else {
  // phone layout
}

// landscape/portrait
if (1.sw > 1.sh) {
  // landscape mode
}
```

### Extension Usage

```dart
// supports both int and double
100.w
100.0.h
16.sp
8.r

// EdgeInsets extension
EdgeInsets.symmetric(horizontal: 16.w, vertical: 8.h)

// or use directly
EdgeInsets.only(
  left: 16.w,
  right: 16.w,
  top: 8.h,
  bottom: 8.h,
)
```

---

## Common Issues

| Issue | Fix |
|------|------|
| Used before initialization | Use size extensions only inside ScreenUtilInit |
| Text too small | Set minTextAdapt: true |
| Too large on tablet | Limit maxWidth or use a conditional layout |
| Hot reload broken | Restart the app |
| Split screen broken | Set splitScreenMode: true |

---

## Design System Integration

See [references/design-system.md](references/design-system.md)

---

## Changelog

### [1.1.0] - 2026-03-01
- 초기 릴리스
