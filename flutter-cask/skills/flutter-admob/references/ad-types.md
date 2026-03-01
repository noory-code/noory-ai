# AdMob 광고 유형별 구현

## 전면 광고

```dart
class InterstitialAdService {
  InterstitialAd? _ad;

  void loadAd() {
    InterstitialAd.load(
      adUnitId: AdHelper.interstitialAdUnitId,
      request: AdRequest(),
      adLoadCallback: InterstitialAdLoadCallback(
        onAdLoaded: (ad) => _ad = ad,
        onAdFailedToLoad: (error) => print('전면 광고 로드 실패: $error'),
      ),
    );
  }

  void showAd({VoidCallback? onAdClosed}) {
    if (_ad == null) return;

    _ad!.fullScreenContentCallback = FullScreenContentCallback(
      onAdDismissedFullScreenContent: (ad) {
        ad.dispose();
        onAdClosed?.call();
        loadAd();  // 다음 광고 미리 로드
      },
      onAdFailedToShowFullScreenContent: (ad, error) {
        ad.dispose();
        loadAd();
      },
    );

    _ad!.show();
    _ad = null;
  }
}
```

## 보상형 광고

```dart
class RewardedAdService {
  RewardedAd? _ad;

  void loadAd() {
    RewardedAd.load(
      adUnitId: AdHelper.rewardedAdUnitId,
      request: AdRequest(),
      rewardedAdLoadCallback: RewardedAdLoadCallback(
        onAdLoaded: (ad) => _ad = ad,
        onAdFailedToLoad: (error) => print('보상형 광고 로드 실패'),
      ),
    );
  }

  void showAd({required void Function(int amount) onRewarded}) {
    if (_ad == null) return;

    _ad!.fullScreenContentCallback = FullScreenContentCallback(
      onAdDismissedFullScreenContent: (ad) {
        ad.dispose();
        loadAd();
      },
    );

    _ad!.show(
      onUserEarnedReward: (ad, reward) {
        onRewarded(reward.amount.toInt());
      },
    );

    _ad = null;
  }

  bool get isReady => _ad != null;
}
```
