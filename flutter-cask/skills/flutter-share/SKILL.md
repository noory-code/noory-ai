---
name: flutter-share
description: 네이티브 공유 시트로 콘텐츠 공유
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [share_plus, 공유, 네이티브 공유, 공유 시트, SNS 공유]
---

# Flutter Share Plus

네이티브 공유 시트로 텍스트, URL, 파일 공유.

---

## 설치

```bash
flutter pub add share_plus
```

---

## Quick Reference

### 텍스트 공유

```dart
import 'package:share_plus/share_plus.dart';

// 단순 텍스트
await Share.share('공유할 텍스트');

// 제목 포함
await Share.share(
  '공유할 텍스트',
  subject: '공유 제목',  // 이메일 제목 등에 사용
);
```

### URL 공유

```dart
await Share.shareUri(Uri.parse('https://example.com'));

// 텍스트와 URL 함께
await Share.share('이 링크 확인해보세요!\nhttps://example.com');
```

### 파일 공유

```dart
// 단일 파일
await Share.shareXFiles(
  [XFile('/path/to/image.png')],
  text: '사진 공유합니다',
);

// 다중 파일
await Share.shareXFiles([
  XFile('/path/to/image1.png'),
  XFile('/path/to/image2.png'),
]);

// 메모리에서 직접 공유
final bytes = await generateImage();
await Share.shareXFiles(
  [XFile.fromData(bytes, name: 'image.png', mimeType: 'image/png')],
);
```

### 공유 결과 확인

```dart
final result = await Share.shareWithResult(
  '공유할 텍스트',
);

switch (result.status) {
  case ShareResultStatus.success:
    print('공유 성공');
    break;
  case ShareResultStatus.dismissed:
    print('사용자가 취소');
    break;
  case ShareResultStatus.unavailable:
    print('공유 불가');
    break;
}
```

### 위치 지정 (iPad)

```dart
// iPad에서 팝오버 위치 지정
await Share.share(
  '공유할 텍스트',
  sharePositionOrigin: Rect.fromLTWH(0, 0, 100, 100),
);

// 버튼 위치 기준
final box = context.findRenderObject() as RenderBox;
await Share.share(
  '공유할 텍스트',
  sharePositionOrigin: box.localToGlobal(Offset.zero) & box.size,
);
```

### 공유 버튼 예시

```dart
IconButton(
  icon: Icon(Icons.share),
  onPressed: () async {
    final box = context.findRenderObject() as RenderBox;
    await Share.share(
      '앱에서 공유합니다: https://example.com',
      sharePositionOrigin: box.localToGlobal(Offset.zero) & box.size,
    );
  },
)
```

---

## 주의사항

| 상황 | 해결 |
|------|------|
| iPad 크래시 | sharePositionOrigin 필수 지정 |
| 파일 공유 안됨 | 파일 경로 권한, MIME 타입 확인 |
| 한글 깨짐 | UTF-8 인코딩 확인 |
| 결과 항상 dismissed | Android에서 결과 추적 제한 (정상) |
