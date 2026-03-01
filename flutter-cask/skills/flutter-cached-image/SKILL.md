---
name: flutter-cached-image
description: cached_network_image를 사용한 이미지 캐싱
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [cached_network_image, 이미지 캐싱, network image, 네트워크 이미지]
---

# Flutter Cached Image

네트워크 이미지 캐싱 및 플레이스홀더 처리.

---

## 설치

```bash
flutter pub add cached_network_image
```

---

## Quick Reference

```dart
import 'package:cached_network_image/cached_network_image.dart';

// 기본 사용
CachedNetworkImage(
  imageUrl: 'https://example.com/image.jpg',
  placeholder: (context, url) => const CircularProgressIndicator(),
  errorWidget: (context, url, error) => const Icon(Icons.error),
)

// 프로그레스 표시
CachedNetworkImage(
  imageUrl: 'https://example.com/image.jpg',
  progressIndicatorBuilder: (context, url, progress) {
    return CircularProgressIndicator(value: progress.progress);
  },
)

// 커스텀 이미지 빌더
CachedNetworkImage(
  imageUrl: 'https://example.com/avatar.jpg',
  imageBuilder: (context, imageProvider) {
    return CircleAvatar(
      backgroundImage: imageProvider,
      radius: 40,
    );
  },
)

// BoxFit 및 크기 지정
CachedNetworkImage(
  imageUrl: 'https://example.com/image.jpg',
  width: 200,
  height: 200,
  fit: BoxFit.cover,
)
```

### ImageProvider로 사용

```dart
// Image 위젯과 함께
Image(
  image: CachedNetworkImageProvider(imageUrl),
)

// DecorationImage와 함께
Container(
  decoration: BoxDecoration(
    image: DecorationImage(
      image: CachedNetworkImageProvider(imageUrl),
      fit: BoxFit.cover,
    ),
  ),
)
```

### 캐시 관리

```dart
import 'package:flutter_cache_manager/flutter_cache_manager.dart';

// 특정 이미지 캐시 삭제
await DefaultCacheManager().removeFile(imageUrl);

// 전체 캐시 삭제
await DefaultCacheManager().emptyCache();
```

---

## 주의사항

| 상황 | 해결 |
|------|------|
| 이미지 안 뜸 | URL 유효성 확인, CORS 설정 확인 |
| 캐시 안됨 | Cache-Control 헤더 확인 |
| 메모리 부족 | memCacheWidth/Height로 리사이즈 |
| 플레이스홀더 크기 | width/height 명시적 지정 |

---

## 추가 옵션

| 속성 | 설명 |
|------|------|
| `fadeInDuration` | 페이드인 애니메이션 시간 |
| `fadeOutDuration` | 페이드아웃 애니메이션 시간 |
| `memCacheWidth` | 메모리 캐시 이미지 너비 |
| `memCacheHeight` | 메모리 캐시 이미지 높이 |
| `maxWidthDiskCache` | 디스크 캐시 최대 너비 |
| `maxHeightDiskCache` | 디스크 캐시 최대 높이 |
| `cacheManager` | 커스텀 캐시 매니저 |
