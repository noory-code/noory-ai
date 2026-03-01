---
name: flutter-riverpod
description: Riverpod + riverpod_generator를 사용한 상태 관리
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [riverpod, provider, 상태관리, state management, notifier]
---

# Flutter Riverpod

riverpod_generator를 사용한 코드 생성 기반 상태 관리.

---

## 설치

```bash
# 필수
flutter pub add flutter_riverpod
flutter pub add riverpod_annotation
flutter pub add dev:riverpod_generator
flutter pub add dev:build_runner
```

## 코드 생성

```bash
# 일회성 빌드
dart run build_runner build --delete-conflicting-outputs

# 감시 모드
dart run build_runner watch -d
```

---

## Quick Reference

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'example.g.dart';

// 단순 Provider (함수)
@riverpod
String helloWorld(Ref ref) => 'Hello world';

// Notifier (클래스 - 상태 변경 가능)
@riverpod
class Counter extends _$Counter {
  @override
  int build() => 0;

  void increment() => state++;
  void decrement() => state--;
}

// AsyncNotifier (비동기)
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

### Widget 사용

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

## 주의사항

| 상황 | 해결 |
|------|------|
| Provider 찾을 수 없음 | `ProviderScope`로 앱 감싸기 |
| 상태 변경 안됨 | `ref.read(provider.notifier).method()` 사용 |
| 빌드 에러 | `dart run build_runner build` 실행 |
| autoDispose 비활성화 | `@Riverpod(keepAlive: true)` 사용 |

---

## References

| 파일 | 내용 |
|------|------|
| [notifier.md](references/notifier.md) | Notifier 패턴, 상태 변경, 라이프사이클 |
| [async-notifier.md](references/async-notifier.md) | AsyncNotifier, 로딩/에러 처리 |
| [widgets.md](references/widgets.md) | ConsumerWidget, ref.watch/read/listen |
| [family.md](references/family.md) | 파라미터 받는 Provider, 캐싱 |
| [stream.md](references/stream.md) | StreamProvider, Supabase Realtime |
| [testing.md](references/testing.md) | Provider 오버라이드, 모킹, Unit 테스트 |
