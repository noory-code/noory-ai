---
name: flutter-shimmer
description: Loading skeleton animation
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [shimmer, skeleton, loading UI, placeholder, loading animation]
---

# Flutter Shimmer

Skeleton animation while loading. Improves data loading UX.

---

## Installation

```bash
flutter pub add shimmer
```

---

## Quick Reference

### Basic Usage

```dart
import 'package:shimmer/shimmer.dart';

Shimmer.fromColors(
  baseColor: Colors.grey[300]!,
  highlightColor: Colors.grey[100]!,
  child: Container(
    width: 200,
    height: 100,
    color: Colors.white,
  ),
)
```

### Skeleton Card

```dart
Widget buildShimmerCard() {
  return Shimmer.fromColors(
    baseColor: Colors.grey[300]!,
    highlightColor: Colors.grey[100]!,
    child: Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // avatar
            CircleAvatar(radius: 24, backgroundColor: Colors.white),
            SizedBox(height: 12),
            // title
            Container(width: 150, height: 16, color: Colors.white),
            SizedBox(height: 8),
            // description
            Container(width: double.infinity, height: 12, color: Colors.white),
            SizedBox(height: 4),
            Container(width: 200, height: 12, color: Colors.white),
          ],
        ),
      ),
    ),
  );
}
```

### List Skeleton

```dart
Widget buildShimmerList({int itemCount = 5}) {
  return ListView.builder(
    itemCount: itemCount,
    itemBuilder: (context, index) => Shimmer.fromColors(
      baseColor: Colors.grey[300]!,
      highlightColor: Colors.grey[100]!,
      child: ListTile(
        leading: CircleAvatar(backgroundColor: Colors.white),
        title: Container(height: 14, width: 100, color: Colors.white),
        subtitle: Container(height: 10, width: 150, color: Colors.white),
      ),
    ),
  );
}
```

### Conditional Shimmer

```dart
Widget buildContent({required bool isLoading, required Widget child}) {
  if (isLoading) {
    return Shimmer.fromColors(
      baseColor: Colors.grey[300]!,
      highlightColor: Colors.grey[100]!,
      child: child,  // same structure as actual layout
    );
  }
  return child;
}
```

### Dark Mode Support

```dart
Shimmer.fromColors(
  baseColor: Theme.of(context).brightness == Brightness.dark
      ? Colors.grey[700]!
      : Colors.grey[300]!,
  highlightColor: Theme.of(context).brightness == Brightness.dark
      ? Colors.grey[600]!
      : Colors.grey[100]!,
  child: ...,
)
```

### Reusable Widget

```dart
class ShimmerBox extends StatelessWidget {
  final double width;
  final double height;
  final double radius;

  const ShimmerBox({
    this.width = double.infinity,
    required this.height,
    this.radius = 4,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(radius),
      ),
    );
  }
}

// usage
Shimmer.fromColors(
  baseColor: Colors.grey[300]!,
  highlightColor: Colors.grey[100]!,
  child: Column(
    children: [
      ShimmerBox(height: 200, radius: 8),
      SizedBox(height: 8),
      ShimmerBox(width: 150, height: 16),
      SizedBox(height: 4),
      ShimmerBox(height: 12),
    ],
  ),
)
```

---

## Common Issues

| Situation | Solution |
|------|------|
| Animation not working | Child widget needs a background color |
| Performance issues | Limit list item count (5-10) |
| Different layout | Keep same structure as actual content |
| Awkward in dark mode | Set baseColor/highlightColor per theme |
