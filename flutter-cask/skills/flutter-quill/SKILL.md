---
name: flutter-quill
user-invocable: true
description: Rich text editor (WYSIWYG)
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [flutter_quill, rich text, editor, WYSIWYG, text editor]
---

# Flutter Quill

A rich text editor with support for bold, italic, lists, and image insertion.

---

## Installation

```bash
flutter pub add flutter_quill
```

---

## Quick Reference

### Basic Editor

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

### Load Initial Content

```dart
// load from Delta JSON
final json = jsonDecode(savedContent);
final document = Document.fromJson(json);
final controller = QuillController(
  document: document,
  selection: TextSelection.collapsed(offset: 0),
);

// load from plain text
final document = Document()..insert(0, 'Initial text');
```

### Save Content

```dart
// save as Delta JSON
final json = jsonEncode(_controller.document.toDelta().toJson());
await saveToDatabase(json);

// convert to plain text
final plainText = _controller.document.toPlainText();
```

### Custom Toolbar

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

### Read-only Mode

```dart
QuillEditor.basic(
  controller: _controller,
  configurations: QuillEditorConfigurations(
    readOnly: true,
    showCursor: false,
  ),
)
```

### Placeholder

```dart
QuillEditor.basic(
  controller: _controller,
  configurations: QuillEditorConfigurations(
    placeholder: 'Enter content...',
  ),
)
```

### Editor Styling

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

### Change Detection

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

### Full Example

See [references/post-editor-example.md](references/post-editor-example.md)

---

## Common Issues

| Issue | Fix |
|------|------|
| Korean input issues | Use the latest version and check for IME-related issues |
| Keyboard obstructing content | Adjust SingleChildScrollView or padding |
| Image insertion | Add the flutter_quill_extensions package |
| Delta format | Convert to a JSON string when saving to the server |
| Performance issues | Consider pagination for long documents |

---

## Changelog

### [1.1.0] - 2026-03-01
- Initial release
