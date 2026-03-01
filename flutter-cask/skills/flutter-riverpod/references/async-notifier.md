# AsyncNotifier 패턴

비동기 상태 관리를 위한 클래스 기반 Provider.

## 기본 구조

```dart
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'todo_list.g.dart';

@riverpod
class TodoList extends _$TodoList {
  @override
  Future<List<Todo>> build() async {
    // 초기 데이터 로드
    final response = await dio.get('/todos');
    return response.data.map(Todo.fromJson).toList();
  }
}
```

**핵심:**
- `build()`: `Future<T>` 반환
- `state`: `AsyncValue<T>` 타입
- 자동으로 로딩/에러 상태 관리

---

## 상태 변경

```dart
@riverpod
class TodoList extends _$TodoList {
  @override
  Future<List<Todo>> build() async {
    return await _fetchTodos();
  }

  Future<void> addTodo(String title) async {
    // 로딩 상태로 전환
    state = const AsyncLoading();

    // 안전하게 실행 (에러 자동 처리)
    state = await AsyncValue.guard(() async {
      final newTodo = await _createTodo(title);
      return [...state.value ?? [], newTodo];
    });
  }

  Future<void> removeTodo(String id) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      await _deleteTodo(id);
      return state.value!.where((t) => t.id != id).toList();
    });
  }
}
```

---

## Widget에서 사용

```dart
class TodoListPage extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final todosAsync = ref.watch(todoListProvider);

    return todosAsync.when(
      data: (todos) => ListView.builder(
        itemCount: todos.length,
        itemBuilder: (_, i) => TodoTile(todos[i]),
      ),
      loading: () => const CircularProgressIndicator(),
      error: (e, st) => Text('Error: $e'),
    );
  }
}
```

---

## AsyncValue 패턴

```dart
// 상태 확인
if (state.isLoading) { ... }
if (state.hasError) { ... }
if (state.hasValue) { ... }

// 값 접근
state.value           // T? (null 가능)
state.valueOrNull     // T? (동일)
state.requireValue    // T (null이면 에러)

// 변환
state.when(
  data: (value) => ...,
  loading: () => ...,
  error: (e, st) => ...,
);

state.maybeWhen(
  data: (value) => ...,
  orElse: () => ...,
);
```

---

## 새로고침

```dart
// Widget에서
ref.invalidate(todoListProvider);  // 다시 로드
ref.refresh(todoListProvider);     // 다시 로드 + 값 반환

// Notifier 내부에서
Future<void> refresh() async {
  state = const AsyncLoading();
  state = await AsyncValue.guard(() => _fetchTodos());
}
```
