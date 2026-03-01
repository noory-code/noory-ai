---
name: flutter-quill
description: 리치텍스트 에디터 (WYSIWYG)
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [flutter_quill, 리치텍스트, 에디터, WYSIWYG, 텍스트 편집기]
---

# Flutter Quill

리치텍스트 에디터. 볼드, 이탤릭, 리스트, 이미지 삽입 지원.

---

## 설치

```bash
flutter pub add flutter_quill
```

---

## Quick Reference

### 기본 에디터

```dart
import 'package:flutter_quill/flutter_quill.dart';

class RichTextEditor extends StatefulWidget {
  @override
  State<RichTextEditor> createState() => _RichTextEditorState();
}

class _RichTextEditorState extends State<RichTextEditor> {
  final QuillController _controller = QuillController.basic();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        QuillSimpleToolbar(controller: _controller),
        Expanded(
          child: QuillEditor.basic(controller: _controller),
        ),
      ],
    );
  }
}
```

### 초기 콘텐츠 로드

```dart
// Delta JSON에서 로드
final json = jsonDecode(savedContent);
final document = Document.fromJson(json);
final controller = QuillController(
  document: document,
  selection: TextSelection.collapsed(offset: 0),
);

// 일반 텍스트에서 로드
final document = Document()..insert(0, '초기 텍스트');
```

### 콘텐츠 저장

```dart
// Delta JSON으로 저장
final json = jsonEncode(_controller.document.toDelta().toJson());
await saveToDatabase(json);

// 일반 텍스트로 변환
final plainText = _controller.document.toPlainText();
```

### 커스텀 툴바

```dart
QuillSimpleToolbar(
  controller: _controller,
  configurations: QuillSimpleToolbarConfigurations(
    showBoldButton: true,
    showItalicButton: true,
    showUnderLineButton: true,
    showStrikeThrough: false,
    showListBullets: true,
    showListNumbers: true,
    showQuote: true,
    showLink: true,
    showSearchButton: false,
    showCodeBlock: false,
  ),
)
```

### 읽기 전용 모드

```dart
QuillEditor.basic(
  controller: _controller,
  configurations: QuillEditorConfigurations(
    readOnly: true,
    showCursor: false,
  ),
)
```

### 플레이스홀더

```dart
QuillEditor.basic(
  controller: _controller,
  configurations: QuillEditorConfigurations(
    placeholder: '내용을 입력하세요...',
  ),
)
```

### 에디터 스타일링

```dart
QuillEditor.basic(
  controller: _controller,
  configurations: QuillEditorConfigurations(
    padding: EdgeInsets.all(16),
    customStyles: DefaultStyles(
      paragraph: DefaultTextBlockStyle(
        TextStyle(fontSize: 16, height: 1.5),
        VerticalSpacing(8, 0),
        VerticalSpacing(0, 0),
        null,
      ),
      h1: DefaultTextBlockStyle(
        TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
        VerticalSpacing(16, 8),
        VerticalSpacing(0, 0),
        null,
      ),
    ),
  ),
)
```

### 변경 감지

```dart
@override
void initState() {
  super.initState();
  _controller.addListener(() {
    setState(() {
      _hasChanges = true;
    });
  });
}
```

### 전체 예시

→ [references/post-editor-example.md](references/post-editor-example.md) 참조

---

## 주의사항

| 상황 | 해결 |
|------|------|
| 한글 입력 이슈 | 최신 버전 사용, IME 관련 이슈 확인 |
| 키보드 가림 | SingleChildScrollView 또는 padding 조정 |
| 이미지 삽입 | flutter_quill_extensions 패키지 추가 |
| Delta 포맷 | 서버 저장 시 JSON 문자열로 변환 |
| 성능 이슈 | 긴 문서는 페이지네이션 고려 |
