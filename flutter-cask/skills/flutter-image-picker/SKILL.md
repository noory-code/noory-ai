---
name: flutter-image-picker
description: 갤러리/카메라에서 이미지 선택
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [image_picker, 사진 선택, 카메라, 갤러리, 이미지 업로드]
---

# Flutter Image Picker

갤러리/카메라에서 이미지/비디오 선택. 프로필 이미지, 사진 업로드에 사용.

---

## 설치

```bash
flutter pub add image_picker
```

## 플랫폼 설정

### iOS (ios/Runner/Info.plist)

```xml
<key>NSPhotoLibraryUsageDescription</key>
<string>프로필 사진을 선택하기 위해 갤러리 접근이 필요합니다.</string>
<key>NSCameraUsageDescription</key>
<string>프로필 사진을 촬영하기 위해 카메라 접근이 필요합니다.</string>
<key>NSMicrophoneUsageDescription</key>
<string>비디오 촬영을 위해 마이크 접근이 필요합니다.</string>
```

### Android

Android 13+ 자동 지원. 추가 설정 불필요.

---

## Quick Reference

### 단일 이미지 선택

```dart
import 'package:image_picker/image_picker.dart';

final picker = ImagePicker();

// 갤러리에서 선택
Future<void> pickFromGallery() async {
  final XFile? image = await picker.pickImage(
    source: ImageSource.gallery,
    maxWidth: 1024,
    maxHeight: 1024,
    imageQuality: 80,  // 0-100
  );

  if (image != null) {
    final bytes = await image.readAsBytes();
    final path = image.path;
    // 업로드 또는 표시
  }
}

// 카메라로 촬영
Future<void> takePhoto() async {
  final XFile? image = await picker.pickImage(
    source: ImageSource.camera,
    preferredCameraDevice: CameraDevice.front,  // 전면/후면
  );
}
```

### 다중 이미지 선택

```dart
Future<void> pickMultipleImages() async {
  final List<XFile> images = await picker.pickMultiImage(
    maxWidth: 1024,
    maxHeight: 1024,
    imageQuality: 80,
  );

  for (final image in images) {
    // 각 이미지 처리
  }
}
```

### 비디오 선택

```dart
Future<void> pickVideo() async {
  final XFile? video = await picker.pickVideo(
    source: ImageSource.gallery,
    maxDuration: Duration(minutes: 5),
  );
}
```

### 선택한 이미지 표시

```dart
XFile? _selectedImage;

// 선택 후
setState(() => _selectedImage = image);

// 표시
if (_selectedImage != null)
  Image.file(
    File(_selectedImage!.path),
    fit: BoxFit.cover,
  )
```

### Supabase Storage 업로드

```dart
Future<String?> uploadToSupabase(XFile image) async {
  final bytes = await image.readAsBytes();
  final fileName = '${DateTime.now().millisecondsSinceEpoch}.jpg';
  final path = 'profiles/$fileName';

  await Supabase.instance.client.storage
      .from('avatars')
      .uploadBinary(path, bytes);

  return Supabase.instance.client.storage
      .from('avatars')
      .getPublicUrl(path);
}
```

### 선택 다이얼로그

```dart
Future<void> showImageSourceDialog(BuildContext context) async {
  showModalBottomSheet(
    context: context,
    builder: (context) => SafeArea(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          ListTile(
            leading: Icon(Icons.photo_library),
            title: Text('갤러리에서 선택'),
            onTap: () {
              Navigator.pop(context);
              pickFromGallery();
            },
          ),
          ListTile(
            leading: Icon(Icons.camera_alt),
            title: Text('카메라로 촬영'),
            onTap: () {
              Navigator.pop(context);
              takePhoto();
            },
          ),
        ],
      ),
    ),
  );
}
```

---

## 주의사항

| 상황 | 해결 |
|------|------|
| iOS 권한 거부 | Info.plist에 Usage Description 추가 |
| 이미지 null | 사용자가 취소한 경우 (정상) |
| 메모리 부족 | maxWidth/maxHeight/imageQuality 설정 |
| 시뮬레이터 카메라 | 실제 기기에서 테스트 |
| HEIC 형식 | iOS에서 자동 JPEG 변환됨 |
