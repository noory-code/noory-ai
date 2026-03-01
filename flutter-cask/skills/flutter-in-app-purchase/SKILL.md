---
name: flutter-in-app-purchase
description: 인앱 결제 (구독, 소모품, 비소모품)
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [in_app_purchase, IAP, 인앱 결제, 구독, 구매]
---

# Flutter In-App Purchase

앱스토어/플레이스토어 인앱 결제. 구독, 소모품, 비소모품 지원.

---

## 설치

```bash
flutter pub add in_app_purchase
```

## 사전 요구사항

- App Store Connect: 인앱 상품 등록, 계약 완료
- Google Play Console: 인앱 상품 등록, 라이선스 키 설정

---

## Quick Reference

### 초기화

```dart
import 'package:in_app_purchase/in_app_purchase.dart';

class IAPService {
  final _iap = InAppPurchase.instance;
  late StreamSubscription<List<PurchaseDetails>> _subscription;

  Future<void> init() async {
    final available = await _iap.isAvailable();
    if (!available) return;

    // 구매 스트림 리스닝
    _subscription = _iap.purchaseStream.listen(
      _handlePurchaseUpdates,
      onError: (error) => print('구매 에러: $error'),
    );

    // 미완료 구매 복원
    await _iap.restorePurchases();
  }

  void dispose() {
    _subscription.cancel();
  }
}
```

### 상품 조회

```dart
Future<List<ProductDetails>> loadProducts() async {
  const productIds = {'premium_monthly', 'premium_yearly', 'coins_100'};
  final response = await _iap.queryProductDetails(productIds);

  if (response.notFoundIDs.isNotEmpty) {
    print('상품 못찾음: ${response.notFoundIDs}');
  }

  return response.productDetails;
}
```

### 구매 처리

```dart
Future<void> buyProduct(ProductDetails product) async {
  final purchaseParam = PurchaseParam(productDetails: product);

  if (product.id.contains('subscription')) {
    // 구독 상품
    await _iap.buyNonConsumable(purchaseParam: purchaseParam);
  } else {
    // 소모품
    await _iap.buyConsumable(purchaseParam: purchaseParam);
  }
}
```

### 구매 업데이트 처리

```dart
void _handlePurchaseUpdates(List<PurchaseDetails> purchases) {
  for (final purchase in purchases) {
    switch (purchase.status) {
      case PurchaseStatus.pending:
        // 결제 진행 중 UI
        break;

      case PurchaseStatus.purchased:
      case PurchaseStatus.restored:
        // 서버 검증 후 기능 활성화
        _verifyAndDeliver(purchase);
        break;

      case PurchaseStatus.error:
        _handleError(purchase.error!);
        break;

      case PurchaseStatus.canceled:
        // 사용자 취소
        break;
    }

    // 구매 완료 처리 (필수!)
    if (purchase.pendingCompletePurchase) {
      _iap.completePurchase(purchase);
    }
  }
}
```

### 서버 검증

```dart
Future<void> _verifyAndDeliver(PurchaseDetails purchase) async {
  // 서버에서 영수증 검증
  final verified = await verifyOnServer(
    productId: purchase.productID,
    receipt: purchase.verificationData.serverVerificationData,
    source: purchase.verificationData.source,  // 'app_store' or 'google_play'
  );

  if (verified) {
    // 프리미엄 기능 활성화
    await enablePremium(purchase.productID);
  }
}
```

### 구매 복원

```dart
Future<void> restorePurchases() async {
  await _iap.restorePurchases();
  // purchaseStream에서 restored 상태로 수신됨
}
```

### UI 예시

```dart
class SubscriptionPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<ProductDetails>>(
      future: iapService.loadProducts(),
      builder: (context, snapshot) {
        if (!snapshot.hasData) return CircularProgressIndicator();

        return ListView(
          children: snapshot.data!.map((product) => ListTile(
            title: Text(product.title),
            subtitle: Text(product.description),
            trailing: ElevatedButton(
              onPressed: () => iapService.buyProduct(product),
              child: Text(product.price),
            ),
          )).toList(),
        );
      },
    );
  }
}
```

---

## 주의사항

| 상황 | 해결 |
|------|------|
| 상품 안나옴 | 스토어 상품 등록 상태, 심사 완료 확인 |
| 테스트 불가 | 샌드박스/테스트 계정 사용 |
| 영수증 검증 | 서버에서 검증 필수 (클라이언트 신뢰 X) |
| completePurchase 누락 | 반드시 호출, 안하면 환불됨 |
| 구독 갱신 | 서버 웹훅으로 상태 동기화 |
