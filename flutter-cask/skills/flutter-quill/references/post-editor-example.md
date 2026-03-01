# PostEditor 전체 예시

```dart
class PostEditor extends StatefulWidget {
  final String? initialContent;
  final void Function(String json) onSave;

  const PostEditor({this.initialContent, required this.onSave});

  @override
  State<PostEditor> createState() => _PostEditorState();
}

class _PostEditorState extends State<PostEditor> {
  late QuillController _controller;

  @override
  void initState() {
    super.initState();
    if (widget.initialContent != null) {
      final json = jsonDecode(widget.initialContent!);
      _controller = QuillController(
        document: Document.fromJson(json),
        selection: TextSelection.collapsed(offset: 0),
      );
    } else {
      _controller = QuillController.basic();
    }
  }

  void _save() {
    final json = jsonEncode(_controller.document.toDelta().toJson());
    widget.onSave(json);
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        QuillSimpleToolbar(controller: _controller),
        Expanded(child: QuillEditor.basic(controller: _controller)),
        ElevatedButton(onPressed: _save, child: Text('저장')),
      ],
    );
  }
}
```
