---
name: flutter-in-app-purchase
description: In-app purchases (subscriptions, consumables, non-consumables)
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [in_app_purchase, IAP, in-app purchase, subscription, purchase]
---

# Flutter In-App Purchase

In-app purchases on App Store/Play Store. Supports subscriptions, consumables, and non-consumables.

---

## Installation

```bash
flutter pub add in_app_purchase
```

## Prerequisites

- App Store Connect: register in-app products, complete agreements
- Google Play Console: register in-app products, configure license key

---

## Quick Reference

### Initialization

```dart
import 'package:in_app_purchase/in_app_purchase.dart';

class IAPService {
  final _iap = InAppPurchase.instance;
  late StreamSubscription<List<PurchaseDetails>> _subscription;

  Future<void> init() async {
    final available = await _iap.isAvailable();
    if (!available) return;

    // listen to purchase stream
    _subscription = _iap.purchaseStream.listen(
      _handlePurchaseUpdates,
      onError: (error) => print('Purchase error: $error'),
    );

    // restore incomplete purchases
    await _iap.restorePurchases();
  }

  void dispose() {
    _subscription.cancel();
  }
}
```

### Load Products

```dart
Future<List<ProductDetails>> loadProducts() async {
  const productIds = {'premium_monthly', 'premium_yearly', 'coins_100'};
  final response = await _iap.queryProductDetails(productIds);

  if (response.notFoundIDs.isNotEmpty) {
    print('Products not found: ${response.notFoundIDs}');
  }

  return response.productDetails;
}
```

### Handle Purchase

```dart
Future<void> buyProduct(ProductDetails product) async {
  final purchaseParam = PurchaseParam(productDetails: product);

  if (product.id.contains('subscription')) {
    // subscription product
    await _iap.buyNonConsumable(purchaseParam: purchaseParam);
  } else {
    // consumable
    await _iap.buyConsumable(purchaseParam: purchaseParam);
  }
}
```

### Handle Purchase Updates

```dart
void _handlePurchaseUpdates(List<PurchaseDetails> purchases) {
  for (final purchase in purchases) {
    switch (purchase.status) {
      case PurchaseStatus.pending:
        // payment in progress UI
        break;

      case PurchaseStatus.purchased:
      case PurchaseStatus.restored:
        // verify on server then enable features
        _verifyAndDeliver(purchase);
        break;

      case PurchaseStatus.error:
        _handleError(purchase.error!);
        break;

      case PurchaseStatus.canceled:
        // user cancelled
        break;
    }

    // complete purchase (required!)
    if (purchase.pendingCompletePurchase) {
      _iap.completePurchase(purchase);
    }
  }
}
```

### Server Verification

```dart
Future<void> _verifyAndDeliver(PurchaseDetails purchase) async {
  // verify receipt on server
  final verified = await verifyOnServer(
    productId: purchase.productID,
    receipt: purchase.verificationData.serverVerificationData,
    source: purchase.verificationData.source,  // 'app_store' or 'google_play'
  );

  if (verified) {
    // enable premium features
    await enablePremium(purchase.productID);
  }
}
```

### Restore Purchases

```dart
Future<void> restorePurchases() async {
  await _iap.restorePurchases();
  // received as restored status in purchaseStream
}
```

### UI Example

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

## Common Issues

| Situation | Solution |
|------|------|
| Products not showing | Check store product registration status and review completion |
| Cannot test | Use sandbox/test accounts |
| Receipt verification | Must verify on server (do not trust client) |
| Missing completePurchase | Must call it, otherwise refund will occur |
| Subscription renewal | Sync status via server webhooks |
