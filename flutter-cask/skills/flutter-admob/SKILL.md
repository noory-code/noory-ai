---
name: flutter-admob
description: Google AdMob ads (banner, interstitial, rewarded)
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [google_mobile_ads, admob, ads, banner ad, rewarded ad, monetization]
---

# Flutter AdMob

Google AdMob mobile advertising. Supports banner, interstitial, and rewarded ads.

---

## Installation

```bash
flutter pub add google_mobile_ads
```

## Platform Setup

### iOS (ios/Runner/Info.plist)

```xml
<key>GADApplicationIdentifier</key>
<string>ca-app-pub-XXXXXXXXXXXXXXXX~XXXXXXXXXX</string>
<key>SKAdNetworkItems</key>
<array>
  <dict>
    <key>SKAdNetworkIdentifier</key>
    <string>cstr6suwn9.skadnetwork</string>
  </dict>
</array>
```

### Android (android/app/src/main/AndroidManifest.xml)

```xml
<meta-data
    android:name="com.google.android.gms.ads.APPLICATION_ID"
    android:value="ca-app-pub-XXXXXXXXXXXXXXXX~XXXXXXXXXX"/>
```

---

## Quick Reference

### Initialization

```dart
import 'package:google_mobile_ads/google_mobile_ads.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await MobileAds.instance.initialize();
  runApp(MyApp());
}
```

### Test Ad IDs

```dart
class AdHelper {
  static String get bannerAdUnitId {
    if (Platform.isAndroid) {
      return 'ca-app-pub-3940256099942544/6300978111';  // test
    } else {
      return 'ca-app-pub-3940256099942544/2934735716';  // test
    }
  }

  static String get interstitialAdUnitId {
    if (Platform.isAndroid) {
      return 'ca-app-pub-3940256099942544/1033173712';
    } else {
      return 'ca-app-pub-3940256099942544/4411468910';
    }
  }

  static String get rewardedAdUnitId {
    if (Platform.isAndroid) {
      return 'ca-app-pub-3940256099942544/5224354917';
    } else {
      return 'ca-app-pub-3940256099942544/1712485313';
    }
  }
}
```

### Banner Ad

```dart
class BannerAdWidget extends StatefulWidget {
  @override
  State<BannerAdWidget> createState() => _BannerAdWidgetState();
}

class _BannerAdWidgetState extends State<BannerAdWidget> {
  BannerAd? _bannerAd;

  @override
  void initState() {
    super.initState();
    _loadAd();
  }

  void _loadAd() {
    _bannerAd = BannerAd(
      adUnitId: AdHelper.bannerAdUnitId,
      size: AdSize.banner,
      request: AdRequest(),
      listener: BannerAdListener(
        onAdLoaded: (_) => setState(() {}),
        onAdFailedToLoad: (ad, error) {
          ad.dispose();
          print('Banner load failed: $error');
        },
      ),
    )..load();
  }

  @override
  void dispose() {
    _bannerAd?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_bannerAd == null) return SizedBox(height: 50);
    return SizedBox(
      height: _bannerAd!.size.height.toDouble(),
      width: _bannerAd!.size.width.toDouble(),
      child: AdWidget(ad: _bannerAd!),
    );
  }
}
```

### Interstitial Ad / Rewarded Ad

→ See [references/ad-types.md](references/ad-types.md)

---

## Common Issues

| Situation | Solution |
|------|------|
| Ad not showing | Use test ID, verify AdMob account approval |
| Test device | Set addTestDeviceIds() or use test ID |
| Policy violation | Auto-clicking and excessive ads are prohibited |
| Not working in release | Replace with real ad ID, activate account |
| Low revenue | Use higher eCPM ad formats (rewarded > interstitial > banner) |
