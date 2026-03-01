# Notifier 패턴

동기식 상태 관리를 위한 클래스 기반 Provider.

## 기본 구조

```dart
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'counter.g.dart';

@riverpod
class Counter extends _$Counter {
  @override
  int build() => 0;  // 초기 상태

  void increment() => state++;
  void decrement() => state--;
  void reset() => state = 0;
}
```

**핵심:**
- `build()`: 초기 상태 반환 (생성자 대신 사용)
- `state`: 현재 상태 (읽기/쓰기 가능)
- 메서드: 상태 변경 로직

---

## 복잡한 상태

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

## 의존성 주입

```dart
@riverpod
class TodoList extends _$TodoList {
  @override
  List<Todo> build() {
    // 다른 Provider 의존
    final filter = ref.watch(filterProvider);
    final todos = ref.watch(allTodosProvider);

    return todos.where((t) => matchesFilter(t, filter)).toList();
  }
}
```

---

## 라이프사이클

```dart
@riverpod
class TimerNotifier extends _$TimerNotifier {
  @override
  int build() {
    // 리소스 초기화
    final timer = Timer.periodic(
      const Duration(seconds: 1),
      (_) => state++,
    );

    // 정리 (dispose)
    ref.onDispose(() {
      timer.cancel();
    });

    return 0;
  }
}
```

---

## keepAlive 옵션

```dart
// 기본: autoDispose (사용 안하면 자동 해제)
@riverpod
class Counter extends _$Counter { ... }

// keepAlive: 앱 생명주기 동안 유지
@Riverpod(keepAlive: true)
class AppState extends _$AppState { ... }
```
