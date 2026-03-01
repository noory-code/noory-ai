---
name: flutter-cached-image
description: Image caching using cached_network_image
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [cached_network_image, image caching, network image]
---

# Flutter Cached Image

Network image caching with placeholder and error widget support.

---

## Installation

```bash
flutter pub add cached_network_image
```

---

## Quick Reference

```dart
import 'package:cached_network_image/cached_network_image.dart';

// basic usage
CachedNetworkImage(
  imageUrl: 'https://example.com/image.jpg',
  placeholder: (context, url) => const CircularProgressIndicator(),
  errorWidget: (context, url, error) => const Icon(Icons.error),
)

// progress indicator
CachedNetworkImage(
  imageUrl: 'https://example.com/image.jpg',
  progressIndicatorBuilder: (context, url, progress) {
    return CircularProgressIndicator(value: progress.progress);
  },
)

// custom image builder
CachedNetworkImage(
  imageUrl: 'https://example.com/avatar.jpg',
  imageBuilder: (context, imageProvider) {
    return CircleAvatar(
      backgroundImage: imageProvider,
      radius: 40,
    );
  },
)

// BoxFit and size
CachedNetworkImage(
  imageUrl: 'https://example.com/image.jpg',
  width: 200,
  height: 200,
  fit: BoxFit.cover,
)
```

### Using as ImageProvider

```dart
// with Image widget
Image(
  image: CachedNetworkImageProvider(imageUrl),
)

// with DecorationImage
Container(
  decoration: BoxDecoration(
    image: DecorationImage(
      image: CachedNetworkImageProvider(imageUrl),
      fit: BoxFit.cover,
    ),
  ),
)
```

### Cache Management

```dart
import 'package:flutter_cache_manager/flutter_cache_manager.dart';

// remove a specific image from cache
await DefaultCacheManager().removeFile(imageUrl);

// clear all cached images
await DefaultCacheManager().emptyCache();
```

---

## Common Issues

| Issue | Fix |
|------|------|
| Image not showing | Verify the URL is valid and check CORS settings |
| Image not cached | Check the Cache-Control header on the response |
| Out of memory | Resize with memCacheWidth/Height |
| Placeholder has wrong size | Specify width/height explicitly |

---

## Additional Options

| Property | Description |
|------|------|
| `fadeInDuration` | Fade-in animation duration |
| `fadeOutDuration` | Fade-out animation duration |
| `memCacheWidth` | Memory cache image width |
| `memCacheHeight` | Memory cache image height |
| `maxWidthDiskCache` | Disk cache maximum width |
| `maxHeightDiskCache` | Disk cache maximum height |
| `cacheManager` | Custom cache manager |
