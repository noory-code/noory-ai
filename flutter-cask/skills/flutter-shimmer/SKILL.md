---
name: flutter-shimmer
description: 로딩 스켈레톤 애니메이션
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [shimmer, 스켈레톤, 로딩 UI, placeholder, 로딩 애니메이션]
---

# Flutter Shimmer

로딩 중 스켈레톤 애니메이션. 데이터 로딩 UX 개선.

---

## 설치

```bash
flutter pub add shimmer
```

---

## Quick Reference

### 기본 사용

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

### 스켈레톤 카드

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
            // 아바타
            CircleAvatar(radius: 24, backgroundColor: Colors.white),
            SizedBox(height: 12),
            // 제목
            Container(width: 150, height: 16, color: Colors.white),
            SizedBox(height: 8),
            // 설명
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

### 리스트 스켈레톤

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

### 조건부 Shimmer

```dart
Widget buildContent({required bool isLoading, required Widget child}) {
  if (isLoading) {
    return Shimmer.fromColors(
      baseColor: Colors.grey[300]!,
      highlightColor: Colors.grey[100]!,
      child: child,  // 실제 레이아웃과 동일한 구조
    );
  }
  return child;
}
```

### 다크 모드 대응

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

### 재사용 위젯

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

// 사용
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

## 주의사항

| 상황 | 해결 |
|------|------|
| 애니메이션 안됨 | child에 배경색 있는 위젯 필요 |
| 성능 이슈 | 리스트 아이템 수 제한 (5-10개) |
| 레이아웃 다름 | 실제 콘텐츠와 동일한 구조 유지 |
| 다크모드 어색함 | baseColor/highlightColor 테마별 설정 |
