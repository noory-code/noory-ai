---
name: flutter-screenutil
description: 반응형 UI를 위한 화면 크기 적응형 유틸리티
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [screenutil, 반응형, 화면 크기, 적응형 UI, 스케일링]
---

# Flutter ScreenUtil

디자인 기준 크기로 UI를 반응형으로 스케일링. Figma 디자인 그대로 구현 가능.

---

## 설치

```bash
flutter pub add flutter_screenutil
```

---

## Quick Reference

### 초기화

```dart
import 'package:flutter_screenutil/flutter_screenutil.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return ScreenUtilInit(
      // Figma 디자인 기준 크기
      designSize: Size(375, 812),  // iPhone X 기준
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

### 크기 단위

```dart
// 너비 기준 스케일 (w)
Container(
  width: 100.w,   // 디자인에서 100px → 화면에 맞게 스케일
  height: 50.h,  // 높이 기준 스케일 (h)
)

// 반지름 (r) - 원형, 둥근 모서리
Container(
  decoration: BoxDecoration(
    borderRadius: BorderRadius.circular(8.r),
  ),
)

// 최소값 기준 (sp) - 폰트에 주로 사용
Text(
  'Hello',
  style: TextStyle(fontSize: 16.sp),
)

// 정사각형 (sp보다 더 일관된 스케일링)
Container(
  width: 50.w,
  height: 50.w,  // 정사각형은 w만 사용
)
```

### 폰트 스케일링

```dart
Text(
  '제목',
  style: TextStyle(
    fontSize: 24.sp,
    fontWeight: FontWeight.bold,
  ),
)

Text(
  '본문',
  style: TextStyle(
    fontSize: 14.sp,
    height: 1.5,
  ),
)
```

### 여백/패딩

```dart
Padding(
  padding: EdgeInsets.symmetric(
    horizontal: 16.w,
    vertical: 12.h,
  ),
  child: ...,
)

// 모든 방향 동일
Padding(
  padding: EdgeInsets.all(16.r),
  child: ...,
)

SizedBox(height: 24.h)
SizedBox(width: 16.w)
```

### 화면 정보

```dart
// 화면 너비/높이
final screenWidth = 1.sw;  // 100% 너비
final screenHeight = 1.sh;  // 100% 높이

// 절반
Container(width: 0.5.sw)  // 화면 너비의 50%

// 상태바/하단바 높이
final statusBarHeight = ScreenUtil().statusBarHeight;
final bottomBarHeight = ScreenUtil().bottomBarHeight;
```

### 조건부 레이아웃

```dart
// 태블릿 감지
if (1.sw > 600) {
  // 태블릿 레이아웃
} else {
  // 폰 레이아웃
}

// 가로/세로 모드
if (1.sw > 1.sh) {
  // 가로 모드
}
```

### Extension 활용

```dart
// int, double 모두 지원
100.w
100.0.h
16.sp
8.r

// EdgeInsets 확장
EdgeInsets.symmetric(horizontal: 16.w, vertical: 8.h)

// 또는 직접 사용
EdgeInsets.only(
  left: 16.w,
  right: 16.w,
  top: 8.h,
  bottom: 8.h,
)
```

---

## 주의사항

| 상황 | 해결 |
|------|------|
| 초기화 전 사용 | ScreenUtilInit 내부에서만 사용 |
| 텍스트 너무 작음 | minTextAdapt: true 설정 |
| 태블릿에서 너무 큼 | maxWidth 제한 또는 조건부 레이아웃 |
| 핫 리로드 깨짐 | 앱 재시작 |
| 분할화면 깨짐 | splitScreenMode: true 설정 |

---

## 디자인 시스템 통합

→ [references/design-system.md](references/design-system.md) 참조
