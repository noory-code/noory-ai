# Family Provider

파라미터를 받는 Provider. riverpod_generator에서는 함수 인자로 자동 처리.

## 함수 기반 (단순)

```dart
@riverpod
String greeting(Ref ref, String name) {
  return 'Hello, $name';
}

// 사용
final msg = ref.watch(greetingProvider('Kim'));
```

## Notifier 기반

```dart
@riverpod
class TodoDetail extends _$TodoDetail {
  @override
  Future<Todo> build(String todoId) async {
    return await fetchTodo(todoId);
  }

  Future<void> update(String title) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      return await updateTodo(todoId, title);  // todoId 접근 가능
    });
  }
}

// 사용
final todo = ref.watch(todoDetailProvider('todo-123'));
```

---

## 여러 파라미터

```dart
@riverpod
Future<List<Post>> userPosts(
  Ref ref,
  String userId,
  {int page = 1, int limit = 20}
) async {
  return await fetchPosts(userId, page: page, limit: limit);
}

// 사용
final posts = ref.watch(
  userPostsProvider('user-1', page: 2, limit: 10),
);
```

---

## 캐싱 동작

```dart
// 같은 파라미터 = 같은 인스턴스 (캐시됨)
ref.watch(todoDetailProvider('todo-1'));
ref.watch(todoDetailProvider('todo-1'));  // 캐시 hit

// 다른 파라미터 = 다른 인스턴스
ref.watch(todoDetailProvider('todo-1'));
ref.watch(todoDetailProvider('todo-2'));  // 별도 인스턴스
```
