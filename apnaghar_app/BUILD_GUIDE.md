# 📱 ApnaGhar Flutter Mobile App — Production Build Guide (Task 10)

This guide provides the complete procedure for generating cryptographically signed production builds (APK and Android App Bundle) of the ApnaGhar smart home mobile app for release on the Google Play Store.

---

## 1. Prerequisites

- Flutter SDK (v3.19.0 or higher)
- Android Studio / Android SDK with Command-line Tools & Build Tools 34.0.0
- OpenJDK 17 or higher
- Connected Android device or configured Android Virtual Device (AVD)

Verify environment:
```bash
flutter doctor -v
```

---

## 2. Generating the Release Signing Keystore

Execute the following `keytool` command inside `apnaghar_app/android/app/`:

```bash
cd apnaghar_app/android/app

keytool -genkey -v \
  -keystore apnaghar-release-key.jks \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000 \
  -alias apnaghar \
  -storepass ApnaGhar@2026 \
  -keypass ApnaGhar@2026 \
  -dname "CN=Mohammad Sakib Ahmad, OU=Mobile IoT, O=ApnaGhar, L=Delhi, ST=Delhi, C=IN"
```

> [!CAUTION]
> Back up your `apnaghar-release-key.jks` in a secure, encrypted offline vault. If you lose this key, you will not be able to push updates to the Google Play Store!

---

## 3. Dependency Resolution

From the `apnaghar_app/` directory:

```bash
flutter clean
flutter pub get
```

---

## 4. Building the Production Artifacts

### A. Universal Release APK (For Direct Sideloading & Testing)
```bash
flutter build apk --release
```
- Output location: `build/app/outputs/flutter-apk/app-release.apk`
- Features: 64-bit ARM (`arm64-v8a`) + 32-bit ARM (`armeabi-v7a`) optimized.

### B. Android App Bundle (AAB - Mandatory for Google Play Store)
```bash
flutter build appbundle --release
```
- Output location: `build/app/outputs/bundle/release/app-release.aab`
- Size optimization: Google Play dynamically generates optimized split APKs tailored to each user's device screen density and CPU architecture (typically reduces app install size by 40%).

---

## 5. Google Play Console Submission Steps

1. Log into [Google Play Console](https://play.google.com/console).
2. Create Application $\rightarrow$ Name: **ApnaGhar - Smart Home Control**.
3. Under **Release $\rightarrow$ Production**, create a new release.
4. Upload `app-release.aab`.
5. Enter release notes:
   - *"Initial v2.0.0 release with real-time Firebase streaming, live PZEM voltage & power monitoring, automation schedules, and direct offline hotspot connectivity."*
6. Review permissions:
   - `android.permission.INTERNET`
   - `android.permission.ACCESS_NETWORK_STATE`
   - `android.permission.ACCESS_WIFI_STATE`
7. Save and publish to Closed Testing or Production review.
