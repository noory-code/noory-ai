# MFA 페이지 예시

```dart
class MfaVerifyPage extends StatefulWidget {
  @override
  State<MfaVerifyPage> createState() => _MfaVerifyPageState();
}

class _MfaVerifyPageState extends State<MfaVerifyPage> {
  final controller = TextEditingController();
  final focusNode = FocusNode();
  bool isLoading = false;
  bool hasError = false;

  @override
  void dispose() {
    controller.dispose();
    focusNode.dispose();
    super.dispose();
  }

  Future<void> verify(String code) async {
    setState(() {
      isLoading = true;
      hasError = false;
    });
    // 검증 로직
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text('인증 코드 6자리를 입력하세요'),
        SizedBox(height: 24),
        Pinput(
          length: 6,
          controller: controller,
          focusNode: focusNode,
          forceErrorState: hasError,
          enabled: !isLoading,
          onCompleted: verify,
        ),
      ],
    );
  }
}
```
