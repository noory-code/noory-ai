---
name: flutter-share
description: Share content via the native share sheet
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [share_plus, share, native share, share sheet, SNS share]
---

# Flutter Share Plus

Share text, URLs, and files via the native share sheet.

---

## Installation

```bash
flutter pub add share_plus
```

---

## Quick Reference

### Share Text

```dart
import 'package:share_plus/share_plus.dart';

// plain text
await Share.share('Text to share');

// with subject
await Share.share(
  'Text to share',
  subject: 'Share title',  // used for email subject, etc.
);
```

### Share URL

```dart
await Share.shareUri(Uri.parse('https://example.com'));

// text and URL together
await Share.share('Check out this link!\nhttps://example.com');
```

### Share Files

```dart
// single file
await Share.shareXFiles(
  [XFile('/path/to/image.png')],
  text: 'Sharing a photo',
);

// multiple files
await Share.shareXFiles([
  XFile('/path/to/image1.png'),
  XFile('/path/to/image2.png'),
]);

// share directly from memory
final bytes = await generateImage();
await Share.shareXFiles(
  [XFile.fromData(bytes, name: 'image.png', mimeType: 'image/png')],
);
```

### Check Share Result

```dart
final result = await Share.shareWithResult(
  'Text to share',
);

switch (result.status) {
  case ShareResultStatus.success:
    print('Share successful');
    break;
  case ShareResultStatus.dismissed:
    print('User dismissed');
    break;
  case ShareResultStatus.unavailable:
    print('Share unavailable');
    break;
}
```

### Specify Position (iPad)

```dart
// specify popover position on iPad
await Share.share(
  'Text to share',
  sharePositionOrigin: Rect.fromLTWH(0, 0, 100, 100),
);

// based on button position
final box = context.findRenderObject() as RenderBox;
await Share.share(
  'Text to share',
  sharePositionOrigin: box.localToGlobal(Offset.zero) & box.size,
);
```

### Share Button Example

```dart
IconButton(
  icon: Icon(Icons.share),
  onPressed: () async {
    final box = context.findRenderObject() as RenderBox;
    await Share.share(
      'Sharing from app: https://example.com',
      sharePositionOrigin: box.localToGlobal(Offset.zero) & box.size,
    );
  },
)
```

---

## Common Issues

| Situation | Solution |
|------|------|
| iPad crash | sharePositionOrigin is required |
| File share not working | Check file path permissions and MIME type |
| Korean text garbled | Check UTF-8 encoding |
| Result always dismissed | Tracking results on Android is limited (normal) |
