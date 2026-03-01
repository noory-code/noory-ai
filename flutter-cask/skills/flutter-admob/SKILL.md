---
name: flutter-admob
description: Google AdMob 광고 (배너, 전면, 보상형)
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [google_mobile_ads, admob, 광고, 배너 광고, 보상형 광고, 수익화]
---

# Flutter AdMob

Google AdMob 모바일 광고. 배너, 전면, 보상형 광고 지원.

---

## 설치

```bash
flutter pub add google_mobile_ads
```

## 플랫폼 설정

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

### 초기화

```dart
import 'package:google_mobile_ads/google_mobile_ads.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await MobileAds.instance.initialize();
  runApp(MyApp());
}
```

### 테스트 광고 ID

```dart
class AdHelper {
  static String get bannerAdUnitId {
    if (Platform.isAndroid) {
      return 'ca-app-pub-3940256099942544/6300978111';  // 테스트
    } else {
      return 'ca-app-pub-3940256099942544/2934735716';  // 테스트
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

### 배너 광고

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
          print('배너 로드 실패: $error');
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

### 전면 광고 / 보상형 광고

→ [references/ad-types.md](references/ad-types.md) 참조

---

## 주의사항

| 상황 | 해결 |
|------|------|
| 광고 안나옴 | 테스트 ID 사용, AdMob 계정 승인 확인 |
| 테스트 기기 | addTestDeviceIds() 설정 또는 테스트 ID |
| 정책 위반 | 자동 클릭, 과도한 광고 금지 |
| 릴리스에서 안됨 | 실제 광고 ID로 교체, 계정 활성화 |
| 수익 낮음 | eCPM 높은 광고 형식 사용 (보상형 > 전면 > 배너) |
