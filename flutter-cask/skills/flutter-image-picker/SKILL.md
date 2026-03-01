---
name: flutter-image-picker
description: Pick images from gallery or camera
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [image_picker, photo picker, camera, gallery, image upload]
---

# Flutter Image Picker

Pick images and videos from the gallery or camera. Commonly used for profile photos and photo uploads.

---

## Installation

```bash
flutter pub add image_picker
```

## Platform Setup

### iOS (ios/Runner/Info.plist)

```xml
<key>NSPhotoLibraryUsageDescription</key>
<string>Gallery access is required to select a profile photo.</string>
<key>NSCameraUsageDescription</key>
<string>Camera access is required to take a profile photo.</string>
<key>NSMicrophoneUsageDescription</key>
<string>Microphone access is required for video recording.</string>
```

### Android

Android 13 and above are supported automatically. No additional setup is required.

---

## Quick Reference

### Single Image Selection

```dart
import 'package:image_picker/image_picker.dart';

final picker = ImagePicker();

// pick from gallery
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
    // upload or display
  }
}

// take a photo with the camera
Future<void> takePhoto() async {
  final XFile? image = await picker.pickImage(
    source: ImageSource.camera,
    preferredCameraDevice: CameraDevice.front,  // front/rear
  );
}
```

### Multiple Image Selection

```dart
Future<void> pickMultipleImages() async {
  final List<XFile> images = await picker.pickMultiImage(
    maxWidth: 1024,
    maxHeight: 1024,
    imageQuality: 80,
  );

  for (final image in images) {
    // process each image
  }
}
```

### Video Selection

```dart
Future<void> pickVideo() async {
  final XFile? video = await picker.pickVideo(
    source: ImageSource.gallery,
    maxDuration: Duration(minutes: 5),
  );
}
```

### Display Selected Image

```dart
XFile? _selectedImage;

// after selection
setState(() => _selectedImage = image);

// display
if (_selectedImage != null)
  Image.file(
    File(_selectedImage!.path),
    fit: BoxFit.cover,
  )
```

### Upload to Supabase Storage

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

### Source Selection Dialog

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
            title: Text('Choose from Gallery'),
            onTap: () {
              Navigator.pop(context);
              pickFromGallery();
            },
          ),
          ListTile(
            leading: Icon(Icons.camera_alt),
            title: Text('Take Photo'),
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

## Common Issues

| Issue | Fix |
|------|------|
| iOS permission denied | Add the Usage Description keys to Info.plist |
| Image is null | The user cancelled the picker (expected behavior) |
| Out of memory | Set maxWidth, maxHeight, and imageQuality |
| Simulator camera | Test on a real device |
| HEIC format | Automatically converted to JPEG on iOS |
