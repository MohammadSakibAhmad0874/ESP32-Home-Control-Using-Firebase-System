# ApnaGhar v2.0 — Production Release & Live Execution Guide

**Project:** ESP32 Home Control Using Firebase System  
**Version:** 2.0.0 Production  
**Author:** Mohammad Sakib Ahmad (@MohammadSakibAhmad0874)  
**Date:** October 2026  

---

## 📌 Executive Summary

ApnaGhar v2.0 is a complete, enterprise-grade IoT smart home automation platform featuring a 3-mode hybrid fallback architecture (Cloud Firebase + Local mDNS Web Server + Offline Access Point), real-time power monitoring (PZEM-004T), hardware safety snubbers, cross-platform Flutter mobile app, web dashboard, and voice assistants (Amazon Alexa + Google Home).

---

## 🌐 1. Web Dashboard

### A. Live Deployment (Vercel)
- **Live URL:** [https://web-iota-ruddy-37.vercel.app](https://web-iota-ruddy-37.vercel.app)
- **Alternative URL:** [https://web-e4ev4gvmw-ahmadsakib263-4202s-projects.vercel.app](https://web-e4ev4gvmw-ahmadsakib263-4202s-projects.vercel.app)
- **GitHub Repository:** [https://github.com/MohammadSakibAhmad0874/ESP32-Home-Control-Using-Firebase-System](https://github.com/MohammadSakibAhmad0874/ESP32-Home-Control-Using-Firebase-System)

### B. Running Web Dashboard Locally
To preview or run the dashboard on your machine:
```bash
# Option 1: Serve directly with npx
npx serve web -l 5173

# Option 2: Using python static server
python -m http.server 5173 --directory web
```
Open your browser at `http://localhost:5173` or `http://localhost:3000`.

### C. Deploying to Vercel
```bash
# Install Vercel CLI globally (if not installed)
npm install -g vercel

# Deploy directly
cd web
vercel --prod --yes
```

---

## 📱 2. Mobile App (Android APK & AAB)

### A. APK Location & Installation
- **Signed APK file:** `ApnaGhar-v2.0-release.apk` (or `apnaghar_app/build/app/outputs/flutter-apk/app-release.apk`)
- **Keystore:** `apnaghar_app/android/app/apnaghar-release-key.jks` (RSA 2048-bit, 10,000 days validity, alias: `apnaghar`)
- **How to Install on Android:**
  1. Transfer `ApnaGhar-v2.0-release.apk` to your phone via USB cable, WhatsApp document, or Google Drive.
  2. In Android Settings: Go to **Security & Privacy** -> **Install Unknown Apps** -> Allow your file manager / browser.
  3. Tap the APK file and select **Install**.
  4. Launch ApnaGhar, log in with your Firebase credentials, and control appliances with real-time feedback.

### B. Building APK & AAB from Source
```bash
cd apnaghar_app

# 1. Fetch dependencies
flutter pub get

# 2. Build signed release APK
flutter build apk --release --no-tree-shake-icons

# 3. Build Google Play Store bundle (AAB)
flutter build appbundle --release --no-tree-shake-icons
```

---

## 🔥 3. Firebase Configuration & Deployment

### Project Credentials
- **Firebase Project ID:** `apnaghar-3f865`
- **Realtime Database URL:** `https://apnaghar-3f865-default-rtdb.firebaseio.com`
- **Console Link:** [https://console.firebase.google.com/project/apnaghar-3f865](https://console.firebase.google.com/project/apnaghar-3f865)

### Deploying Security Rules & Functions
```bash
# 1. Deploy Realtime Database rules (prevents unauthorized read/write)
firebase deploy --only database --project apnaghar-3f865

# 2. Deploy FCM Push Notification Cloud Functions
cd backend/fcm
npm install --legacy-peer-deps
firebase deploy --only functions --project apnaghar-3f865

# 3. Deploy Google Home Smart Home Fulfillment
cd google-action/fulfillment
npm install --legacy-peer-deps
firebase deploy --only functions:smarthome --project apnaghar-3f865
```

---

## ⚡ 4. ESP32 Firmware Flashing & Hardware Setup

### Firmware Specifications
- **Board:** ESP32 DevKit V1 (ESP32-WROOM-32, Dual-core 240MHz, 4MB Flash)
- **Framework:** Arduino / PlatformIO
- **Relay GPIOs:** GPIO 23 (Relay 1), GPIO 22 (Relay 2), GPIO 21 (Relay 3), GPIO 19 (Relay 4)
- **Manual Wall Switch Inputs (Debounced):** GPIO 34, 35, 32, 33 (Active LOW with internal pull-up)
- **Power Sensor:** PZEM-004T v3.0 on HardwareSerial2 (RX2: GPIO 16, TX2: GPIO 17)
- **Status LED:** GPIO 2 (Built-in Blue LED)
- **Config / Factory Reset Button:** GPIO 0 (BOOT button)

### Flashing Steps
1. Open `HomeControlSketch/HomeControlSketch.ino` in Arduino IDE or PlatformIO.
2. Ensure the required libraries are installed:
   - `Firebase ESP32 Client` (by Mobizt)
   - `PZEM004Tv30` (by Mandar Kale)
   - `ElegantOTA` & `ESPAsyncWebServer`
   - `ArduinoJson` (v6 or v7)
3. Select board: **DOIT ESP32 DEVKIT V1**.
4. Set Flash Frequency: **80MHz**, Upload Speed: **921600**.
5. Connect ESP32 via Micro-USB and click **Upload**.

### 3-Mode Failover Operation
1. **Mode 1 (Cloud):** ESP32 connects to local 2.4GHz WiFi and streams state changes with Firebase RTDB in <120ms.
2. **Mode 2 (Local LAN):** If internet is down, access `http://apnaghar.local` over mDNS on the home WiFi network.
3. **Mode 3 (Offline AP):** If home WiFi is disconnected, ESP32 broadcasts fallback AP `SmartHome_Control` (IP: `192.168.4.1`) for direct offline appliance control.

---

## 📊 5. Presentation & Documentation

- **PPTX Deck:** `ApnaGhar_v2.0_Presentation.pptx` (15 slides widescreen 16:9, rich aubergine & marigold palette, architecture diagrams, QR codes to live website and APK download).
- **3D Enclosure:** `hardware/enclosure/enclosure.scad` (Flame-retardant UL94-V0 ABS snap-fit casing with DIN rail mounting).
- **PCB CAD:** `hardware/pcb/` (KiCad 7 schematics, 2-layer PCB layout with 2.5mm creepage isolation between AC mains and DC low-voltage traces).

---

## 🎓 8 Commands Viva Reference
| Command | Purpose |
|---|---|
| `npx serve web` | Runs web dashboard locally without cloud deployment |
| `vercel --prod` | Deploys static/web frontend live to globally distributed CDN |
| `firebase deploy --only database` | Locks database with row-level security and input validation |
| `firebase deploy --only functions` | Deploys FCM notification handlers to Google Cloud Functions |
| `flutter build apk --release` | Packages and signs release APK for Android devices |
| `flutter build appbundle --release` | Generates `.aab` file optimized for Google Play Store |
| `openscad hardware/enclosure/enclosure.scad` | Renders parametric 3D printable model for custom PCB box |
| `python generate_pptx.py` | Programmatically generates the 15-slide presentation deck |
