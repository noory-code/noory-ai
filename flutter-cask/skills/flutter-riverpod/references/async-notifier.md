# AsyncNotifier Pattern

Class-based Provider for async state management.

## Basic Structure

```dart
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'todo_list.g.dart';

@riverpod
class TodoList extends _$TodoList {
  @override
  Future<List<Todo>> build() async {
    // load initial data
    final response = await dio.get('/todos');
    return response.data.map(Todo.fromJson).toList();
  }
}
```

**Key points:**
- `build()`: returns `Future<T>`
- `state`: type is `AsyncValue<T>`
- Automatically manages loading/error states

---

## State Changes

```dart
@riverpod
class TodoList extends _$TodoList {
  @override
  Future<List<Todo>> build() async {
    return await _fetchTodos();
  }

  Future<void> addTodo(String title) async {
    // switch to loading state
    state = const AsyncLoading();

    // execute safely (error handled automatically)
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

## Usage in Widget

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

## AsyncValue Patterns

```dart
// check state
if (state.isLoading) { ... }
if (state.hasError) { ... }
if (state.hasValue) { ... }

// access value
state.value           // T? (can be null)
state.valueOrNull     // T? (same)
state.requireValue    // T (throws if null)

// transform
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

## Refresh

```dart
// from widget
ref.invalidate(todoListProvider);  // reload
ref.refresh(todoListProvider);     // reload + return value

// from inside Notifier
Future<void> refresh() async {
  state = const AsyncLoading();
  state = await AsyncValue.guard(() => _fetchTodos());
}
```
