# StreamProvider

Real-time data stream handling.

## Basic Usage

```dart
@riverpod
Stream<int> counter(Ref ref) async* {
  int count = 0;
  while (true) {
    await Future.delayed(const Duration(seconds: 1));
    yield count++;
  }
}

// usage
final counterAsync = ref.watch(counterProvider);
counterAsync.when(
  data: (count) => Text('$count'),
  loading: () => CircularProgressIndicator(),
  error: (e, st) => Text('Error: $e'),
);
```

---

## Supabase Realtime Example

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

// usage
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

## Using StreamController

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

## Stream -> AsyncValue

```dart
// Streams are automatically wrapped as AsyncValue
final streamAsync = ref.watch(counterProvider);

// type: AsyncValue<int>
streamAsync.value      // int?
streamAsync.isLoading  // bool
streamAsync.hasError   // bool
```
