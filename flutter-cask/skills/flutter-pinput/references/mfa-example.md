# MFA Page Example

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
    // verification logic
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text('Enter your 6-digit verification code'),
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
