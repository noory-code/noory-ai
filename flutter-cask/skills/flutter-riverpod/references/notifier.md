# Notifier Pattern

Class-based Provider for synchronous state management.

## Basic Structure

```dart
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'counter.g.dart';

@riverpod
class Counter extends _$Counter {
  @override
  int build() => 0;  // initial state

  void increment() => state++;
  void decrement() => state--;
  void reset() => state = 0;
}
```

**Key points:**
- `build()`: returns initial state (replaces constructor)
- `state`: current state (readable and writable)
- Methods: state change logic

---

## Complex State

```dart
@freezed
abstract class AuthState with _$AuthState {
  const factory AuthState({
    required bool isLoggedIn,
    User? user,
  }) = _AuthState;
}

@riverpod
class Auth extends _$Auth {
  @override
  AuthState build() => const AuthState(isLoggedIn: false);

  void login(User user) {
    state = state.copyWith(isLoggedIn: true, user: user);
  }

  void logout() {
    state = const AuthState(isLoggedIn: false);
  }
}
```

---

## Dependency Injection

```dart
@riverpod
class TodoList extends _$TodoList {
  @override
  List<Todo> build() {
    // depend on other providers
    final filter = ref.watch(filterProvider);
    final todos = ref.watch(allTodosProvider);

    return todos.where((t) => matchesFilter(t, filter)).toList();
  }
}
```

---

## Lifecycle

```dart
@riverpod
class TimerNotifier extends _$TimerNotifier {
  @override
  int build() {
    // initialize resources
    final timer = Timer.periodic(
      const Duration(seconds: 1),
      (_) => state++,
    );

    // cleanup (dispose)
    ref.onDispose(() {
      timer.cancel();
    });

    return 0;
  }
}
```

---

## keepAlive Option

```dart
// default: autoDispose (released automatically when not used)
@riverpod
class Counter extends _$Counter { ... }

// keepAlive: persists for app lifecycle
@Riverpod(keepAlive: true)
class AppState extends _$AppState { ... }
```
