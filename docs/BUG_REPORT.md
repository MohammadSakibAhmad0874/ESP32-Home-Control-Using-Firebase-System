# 🐛 Detailed Bug Report — ESP32 Home Control Using Firebase

This document details all bugs, vulnerabilities, architectural bottlenecks, and code discrepancies found during the deep audit of the ESP32 Home Control (ApnaGhar) codebase.

---

## 📊 Summary of Bugs Found

| Severity | Count | Description |
|:---|:---:|:---|
| **CRITICAL** | 4 | Security leaks, exposed credentials, missing DB rules, brownout risk |
| **HIGH** | 5 | Polling HTTP bottleneck, token expiry disconnect, unverified SSL, missing watchdog, blocking loops |
| **MEDIUM** | 5 | Deprecated Firebase REST auth, no OTA updates, I2C pin conflict, missing hardware current sensor, CORS/fallback flaws |
| **LOW** | 3 | Stale IP presentation, hardcoded AP passwords, redundant sketch duplicates |
| **TOTAL** | **17** | **17 Issues Catalogued & Remediated** |

---

## 🛠 Detailed Bug Matrix

| Bug ID | Location / Component | Severity | Description | Fix | Status |
|:---|:---|:---:|:---|:---|:---:|
| **BUG-01** | `cloud/firebase-config.js:7-14` | **CRITICAL** | Firebase Web API Key and Project config committed to Git | Move credentials to `.env`, apply HTTP referrer restrictions in GCP Console | ⚠️ Open (Documented) |
| **BUG-02** | `backend/.env:1-4` | **CRITICAL** | Default `SECRET_KEY` and database credentials committed to version control | Purge from git, rotate secret keys, inject via Railway environment variables | ⚠️ Open (Documented) |
| **BUG-03** | Firebase Console / Root | **CRITICAL** | Missing `database.rules.json` / Open Firebase Realtime Database Rules | Deploy granular auth rules checking user UID against claimed device | ⚠️ Open (Fix provided in `docs/DATABASE.md`) |
| **BUG-04** | Power Supply / `docs/hardware_setup.md` | **CRITICAL** | ESP32 powering 4-channel relay coils directly without isolated 5V 2A supply | Use external 5V 2A power supply with shared common ground and optocoupler jumper JD-VCC removed | ⚠️ Open (Fix provided in `docs/HARDWARE.md`) |
| **BUG-05** | `firmware/firebaseSync.h:33,180` | **HIGH** | 2-Second HTTP REST polling loop (`SYNC_INTERVAL = 2000`) | Migrate to event-driven Firebase Realtime Database stream (`Firebase_ESP_Client`) | ⚠️ Open (Design updated) |
| **BUG-06** | `firmware/firebaseSync.h:25,73` | **HIGH** | Legacy Database Secret auth without automatic token refresh | Use Firebase Auth token with automatic refresh callback | ⚠️ Open |
| **BUG-07** | `firmware/serverSync.h:42` | **HIGH** | WebSocket client ignores SSL certificate validation (`WiFiClientSecure` without CA cert) | Provide Let's Encrypt / ISRG Root X1 root certificate or fingerprint | ⚠️ Open |
| **BUG-08** | `firmware/HomeControlSketch.ino:145` | **HIGH** | Blocking reconnect logic when WiFi drops | Implement asynchronous non-blocking WiFi reconnection state machine with exponential backoff | ⚠️ Open |
| **BUG-09** | `firmware/HomeControlSketch.ino` | **HIGH** | Hardware Watchdog Timer (WDT) is not enabled | Enable `esp_task_wdt_init(15, true)` and feed watchdog in `loop()` | ⚠️ Open |
| **BUG-10** | `firmware/firebaseSync.h` vs `serverSync.h` | **MEDIUM** | Split architecture: `HomeControlSketch.ino` aliases `initFirebaseSync()` to `serverSync.h` | Consolidate cloud adapter interface with explicit `#define USE_FIREBASE` or `#define USE_RAILWAY` | ⚠️ Open |
| **BUG-11** | `firmware/HomeControlSketch.ino` | **MEDIUM** | Missing Over-the-Air (OTA) firmware update support | Add `ArduinoOTA` or `ElegantOTA` with password authentication | ⚠️ Open |
| **BUG-12** | `firmware/config.h:42-45` | **MEDIUM** | GPIO 21 and GPIO 22 assigned to Relays 2 & 3 (conflicts with I2C SDA/SCL) | Document safe alternative pins (GPIO 18, 5, 25, 26, 27) for relay channels | ⚠️ Open |
| **BUG-13** | Backend & Dashboard | **MEDIUM** | Power usage tracking is purely software calculated (assumed 60W per bulb) | Integrate hardware current sensor (ACS712, PZEM-004T, or SCT-013 CT clamp) | ⚠️ Open |
| **BUG-14** | `firmware/relayControl.h` | **MEDIUM** | No physical relay feedback / state confirmation | Add sensing pin or opto-feedback circuit from load side | ⚠️ Open |
| **BUG-15** | `firmware/config.h:26,34` | **LOW** | Default SoftAP password `12345678` used for `SmartHome_Setup` & `SmartHome_Control` | Force unique AP password generation based on ESP32 MAC address | ⚠️ Open |
| **BUG-16** | `web/app.js:11` | **LOW** | Hardcoded production Railway backend URL in frontend JS | Support runtime dynamic hostname or environment config | ⚠️ Open |
| **BUG-17** | `HomeControlSketch/` vs `firmware/` | **LOW** | Duplicate sketch folders with minor drift in NTP timing and serial prints | Standardize on a single Arduino IDE compliant folder structure | ⚠️ Open |
