# AdMob Ad Type Implementations

## Interstitial Ad

```dart
class InterstitialAdService {
  InterstitialAd? _ad;

  void loadAd() {
    InterstitialAd.load(
      adUnitId: AdHelper.interstitialAdUnitId,
      request: AdRequest(),
      adLoadCallback: InterstitialAdLoadCallback(
        onAdLoaded: (ad) => _ad = ad,
        onAdFailedToLoad: (error) => print('Interstitial ad load failed: $error'),
      ),
    );
  }

  void showAd({VoidCallback? onAdClosed}) {
    if (_ad == null) return;

    _ad!.fullScreenContentCallback = FullScreenContentCallback(
      onAdDismissedFullScreenContent: (ad) {
        ad.dispose();
        onAdClosed?.call();
        loadAd();  // preload next ad
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

## Rewarded Ad

```dart
class RewardedAdService {
  RewardedAd? _ad;

  void loadAd() {
    RewardedAd.load(
      adUnitId: AdHelper.rewardedAdUnitId,
      request: AdRequest(),
      rewardedAdLoadCallback: RewardedAdLoadCallback(
        onAdLoaded: (ad) => _ad = ad,
        onAdFailedToLoad: (error) => print('Rewarded ad load failed'),
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
