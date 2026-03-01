# Design System Integration

```dart
// theme/dimensions.dart
class Dimensions {
  // Spacing
  static double get xs => 4.w;
  static double get sm => 8.w;
  static double get md => 16.w;
  static double get lg => 24.w;
  static double get xl => 32.w;

  // Font sizes
  static double get fontXs => 12.sp;
  static double get fontSm => 14.sp;
  static double get fontMd => 16.sp;
  static double get fontLg => 20.sp;
  static double get fontXl => 24.sp;

  // Radius
  static double get radiusSm => 4.r;
  static double get radiusMd => 8.r;
  static double get radiusLg => 16.r;
}

// usage
Container(
  padding: EdgeInsets.all(Dimensions.md),
  decoration: BoxDecoration(
    borderRadius: BorderRadius.circular(Dimensions.radiusMd),
  ),
  child: Text(
    'Hello',
    style: TextStyle(fontSize: Dimensions.fontMd),
  ),
)
```
