# Riverpod Widgets

Flutter에서 Provider 사용을 위한 위젯들.

## ProviderScope

앱 최상위에서 Provider 상태 저장소 제공.

```dart
void main() {
  runApp(
    ProviderScope(
      // 오버라이드 (테스트용)
      overrides: [
        authRepositoryProvider.overrideWithValue(MockAuthRepository()),
      ],
      child: MyApp(),
    ),
  );
}
```

---

## ConsumerWidget

Provider를 사용하는 StatelessWidget.

```dart
class HomePage extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(userProvider);

    return Text('Hello, ${user.name}');
  }
}
```

---

## ConsumerStatefulWidget

상태가 필요한 경우.

```dart
class HomePage extends ConsumerStatefulWidget {
  @override
  ConsumerState<HomePage> createState() => _HomePageState();
}

class _HomePageState extends ConsumerState<HomePage> {
  @override
  void initState() {
    super.initState();
    // ref 사용 가능
    ref.read(analyticsProvider).logPageView('home');
  }

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(userProvider);
    return Text('Hello, ${user.name}');
  }
}
```

---

## Consumer

위젯 트리 일부만 리빌드.

```dart
class HomePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const Header(),  // 리빌드 안됨
        Consumer(
          builder: (context, ref, child) {
            final count = ref.watch(counterProvider);
            return Text('Count: $count');  // 여기만 리빌드
          },
        ),
        const Footer(),  // 리빌드 안됨
      ],
    );
  }
}
```

---

## ref 메서드

| 메서드 | 용도 | 리빌드 |
|--------|------|--------|
| `ref.watch(p)` | 값 구독 + 변경 시 리빌드 | O |
| `ref.read(p)` | 값 1회 읽기 (이벤트 핸들러) | X |
| `ref.listen(p, cb)` | 변경 시 콜백 실행 | X |

### 사용 예시

```dart
class MyWidget extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // watch: 빌드에서 사용
    final count = ref.watch(counterProvider);

    // listen: 사이드 이펙트 (스낵바 등)
    ref.listen(errorProvider, (prev, next) {
      if (next != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(next)),
        );
      }
    });

    return TextButton(
      // read: 이벤트 핸들러에서
      onPressed: () => ref.read(counterProvider.notifier).increment(),
      child: Text('Count: $count'),
    );
  }
}
```

---

## select (부분 구독)

특정 필드만 구독하여 불필요한 리빌드 방지.

```dart
// 전체 구독 (user 변경 시마다 리빌드)
final user = ref.watch(userProvider);

// 부분 구독 (name 변경 시에만 리빌드)
final name = ref.watch(userProvider.select((u) => u.name));
```
