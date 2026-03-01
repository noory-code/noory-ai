---
name: flutter-svg
description: SVG 벡터 이미지 렌더링
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [SVG, flutter_svg, 벡터 이미지, 아이콘, 스케일러블]
---

# Flutter SVG

SVG 벡터 이미지 렌더링. 해상도 독립적 아이콘/로고에 최적.

---

## 설치

```bash
flutter pub add flutter_svg
```

---

## Quick Reference

### 기본 사용

```dart
import 'package:flutter_svg/flutter_svg.dart';

// Asset에서 로드
SvgPicture.asset(
  'assets/icons/logo.svg',
  width: 100,
  height: 100,
)

// 네트워크에서 로드
SvgPicture.network(
  'https://example.com/icon.svg',
  placeholderBuilder: (context) => CircularProgressIndicator(),
)

// 문자열에서 로드
SvgPicture.string(
  '<svg viewBox="0 0 100 100">...</svg>',
)
```

### 색상 변경

```dart
SvgPicture.asset(
  'assets/icons/heart.svg',
  colorFilter: ColorFilter.mode(
    Colors.red,
    BlendMode.srcIn,
  ),
)

// 테마 색상 사용
SvgPicture.asset(
  'assets/icons/menu.svg',
  colorFilter: ColorFilter.mode(
    Theme.of(context).iconTheme.color!,
    BlendMode.srcIn,
  ),
)
```

### 크기 조절

```dart
// 고정 크기
SvgPicture.asset(
  'assets/logo.svg',
  width: 200,
  height: 100,
)

// 부모에 맞춤
SvgPicture.asset(
  'assets/logo.svg',
  fit: BoxFit.contain,  // contain, cover, fill, fitWidth, fitHeight
)

// 종횡비 유지
SizedBox(
  width: 100,
  child: SvgPicture.asset(
    'assets/logo.svg',
    fit: BoxFit.fitWidth,
  ),
)
```

### Asset 등록 (pubspec.yaml)

```yaml
flutter:
  assets:
    - assets/icons/
    - assets/images/
```

### 캐싱 (precache)

```dart
// 앱 시작 시 미리 로드
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

## 주의사항

| 상황 | 해결 |
|------|------|
| SVG 안보임 | pubspec.yaml에 assets 경로 등록 |
| 색상 변경 안됨 | SVG 내 fill/stroke 속성이 currentColor인지 확인 |
| 복잡한 SVG 느림 | 간단한 SVG 사용 또는 PNG로 대체 |
| 그라디언트 깨짐 | flutter_svg 지원 확인 (일부 제한) |
| Web에서 CORS | 같은 도메인 또는 CORS 설정 필요 |

---

## SVG 최적화 팁

```dart
// 1. 아이콘은 24x24 또는 48x48 viewBox 사용
// 2. 불필요한 메타데이터 제거 (SVGO 도구)
// 3. 단색 아이콘은 path만 남기고 fill="currentColor"
// 4. 복잡한 일러스트는 PNG 고려
```
