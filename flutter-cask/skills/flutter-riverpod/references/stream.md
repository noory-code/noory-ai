# StreamProvider

실시간 데이터 스트림 처리.

## 기본 사용

```dart
@riverpod
Stream<int> counter(Ref ref) async* {
  int count = 0;
  while (true) {
    await Future.delayed(const Duration(seconds: 1));
    yield count++;
  }
}

// 사용
final counterAsync = ref.watch(counterProvider);
counterAsync.when(
  data: (count) => Text('$count'),
  loading: () => CircularProgressIndicator(),
  error: (e, st) => Text('Error: $e'),
);
```

---

## Supabase Realtime 예제

```dart
@riverpod
Stream<List<Message>> chatMessages(Ref ref, String roomId) {
  final supabase = ref.watch(supabaseProvider);

  return supabase
      .from('messages')
      .stream(primaryKey: ['id'])
      .eq('room_id', roomId)
      .order('created_at')
      .map((data) => data.map(Message.fromJson).toList());
}

// 사용
class ChatPage extends ConsumerWidget {
  final String roomId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final messagesAsync = ref.watch(chatMessagesProvider(roomId));

    return messagesAsync.when(
      data: (messages) => ListView.builder(
        itemCount: messages.length,
        itemBuilder: (_, i) => MessageTile(messages[i]),
      ),
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, st) => Center(child: Text('Error: $e')),
    );
  }
}
```

---

## StreamController 사용

```dart
@riverpod
class NotificationStream extends _$NotificationStream {
  StreamController<Notification>? _controller;

  @override
  Stream<Notification> build() {
    _controller = StreamController<Notification>.broadcast();

    ref.onDispose(() {
      _controller?.close();
    });

    return _controller!.stream;
  }

  void push(Notification notification) {
    _controller?.add(notification);
  }
}
```

---

## Stream → AsyncValue

```dart
// Stream은 자동으로 AsyncValue로 래핑됨
final streamAsync = ref.watch(counterProvider);

// 타입: AsyncValue<int>
streamAsync.value      // int?
streamAsync.isLoading  // bool
streamAsync.hasError   // bool
```
