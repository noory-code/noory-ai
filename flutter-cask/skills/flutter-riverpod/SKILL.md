---
name: flutter-riverpod
description: State management using Riverpod + riverpod_generator
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [riverpod, provider, state management, notifier]
---

# Flutter Riverpod

Code-generation-based state management using riverpod_generator.

---

## Installation

```bash
# required
flutter pub add flutter_riverpod
flutter pub add riverpod_annotation
flutter pub add dev:riverpod_generator
flutter pub add dev:build_runner
```

## Code Generation

```bash
# one-time build
dart run build_runner build --delete-conflicting-outputs

# watch mode
dart run build_runner watch -d
```

---

## Quick Reference

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'example.g.dart';

// simple Provider (function)
@riverpod
String helloWorld(Ref ref) => 'Hello world';

// Notifier (class-based, state can be changed)
@riverpod
class Counter extends _$Counter {
  @override
  int build() => 0;

  void increment() => state++;
  void decrement() => state--;
}

// AsyncNotifier (async)
@riverpod
class TodoList extends _$TodoList {
  @override
  Future<List<Todo>> build() async {
    return await fetchTodos();
  }

  Future<void> addTodo(Todo todo) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      await saveTodo(todo);
      return [...state.value ?? [], todo];
    });
  }
}
```

### Widget Usage

```dart
void main() {
  runApp(ProviderScope(child: MyApp()));
}

class MyPage extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final count = ref.watch(counterProvider);

    return TextButton(
      onPressed: () => ref.read(counterProvider.notifier).increment(),
      child: Text('Count: $count'),
    );
  }
}
```

---

## Common Issues

| Issue | Fix |
|------|------|
| Provider not found | Wrap the app with `ProviderScope` |
| State not updating | Use `ref.read(provider.notifier).method()` |
| Build error | Run `dart run build_runner build` |
| Disable autoDispose | Use `@Riverpod(keepAlive: true)` |

---

## References

| File | Description |
|------|------|
| [notifier.md](references/notifier.md) | Notifier pattern, state changes, lifecycle |
| [async-notifier.md](references/async-notifier.md) | AsyncNotifier, loading/error handling |
| [widgets.md](references/widgets.md) | ConsumerWidget, ref.watch/read/listen |
| [family.md](references/family.md) | Providers with parameters, caching |
| [stream.md](references/stream.md) | StreamProvider, Supabase Realtime |
| [testing.md](references/testing.md) | Provider override, mocking, unit tests |

---

## Changelog

### [1.1.0] - 2026-03-01
- Initial release
