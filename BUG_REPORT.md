# 🐛 Bug Report — ESP32 Home Control Using Firebase

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

| Bug ID | Location / Component | Severity | Description | Impact | Recommended Fix | Status |
|:---|:---|:---:|:---|:---|:---|:---:|
| **BUG-01** | `cloud/firebase-config.js:7-14` | **CRITICAL** | Firebase Web API Key and Project config committed to Git | Anyone with read access can target the Firebase project | Move credentials to `.env`, use restricted API keys with HTTP referrer checks | ⚠️ Open (Documented) |
| **BUG-02** | `backend/.env:1-4` | **CRITICAL** | Default `SECRET_KEY` and database credentials committed to version control | JWT tokens can be forged; database can be accessed if exposed | Remove `.env` from git, rotate keys, enforce `.gitignore` | ⚠️ Open (Documented) |
| **BUG-03** | Firebase Console / Root | **CRITICAL** | Missing `database.rules.json` / Open Firebase Realtime Database Rules | Anyone with database URL can read and flip relays | Implement granular auth rules checking user UID against claimed device | ⚠️ Open (Fix provided in `docs/DATABASE.md`) |
| **BUG-04** | Power Supply / `docs/hardware_setup.md` | **CRITICAL** | ESP32 powering 4-channel relay coils directly without isolated 5V 2A supply | Coils draw 320mA+ causing ESP32 3.3V brownout and reboot loops | Use external 5V 2A power supply with shared common ground and optocoupler jumper JD-VCC removed | ⚠️ Open (Fix provided in `docs/HARDWARE.md`) |
| **BUG-05** | `firmware/firebaseSync.h:33,180` | **HIGH** | 2-Second HTTP REST polling loop (`SYNC_INTERVAL = 2000`) | ESP32 sends constant GET requests; creates latency, high SSL overhead, drains Firebase quota | Migrate to WebSocket stream or event-driven Firebase Realtime Database stream (`Firebase_ESP_Client`) | ⚠️ Open (Design updated) |
| **BUG-06** | `firmware/firebaseSync.h:25,73` | **HIGH** | Legacy Database Secret auth without automatic token refresh | Firebase ID tokens expire after 1 hour (3600s); legacy DB secrets are deprecated by Google | Use Firebase Auth token with automatic refresh callback | ⚠️ Open |
| **BUG-07** | `firmware/serverSync.h:42` | **HIGH** | WebSocket client ignores SSL certificate validation (`WiFiClientSecure` without CA cert) | Vulnerable to Man-in-the-Middle (MitM) attacks on untrusted WiFi | Provide Let's Encrypt / ISRG Root X1 root certificate or fingerprint | ⚠️ Open |
| **BUG-08** | `firmware/HomeControlSketch.ino:145` | **HIGH** | Blocking reconnect logic when WiFi drops | If home router reboots or WiFi drops, loop hangs on network reconnect and blocks local web server | Implement asynchronous non-blocking WiFi reconnection state machine with exponential backoff | ⚠️ Open |
| **BUG-09** | `firmware/HomeControlSketch.ino` | **HIGH** | Hardware Watchdog Timer (WDT) is not enabled | If firmware locks up during DNS lookup, SSL handshake, or WiFi hang, device stays unresponsive forever | Enable `esp_task_wdt_init(15, true)` and feed watchdog in `loop()` | ⚠️ Open |
| **BUG-10** | `firmware/firebaseSync.h` vs `serverSync.h` | **MEDIUM** | Split architecture: `HomeControlSketch.ino` aliases `initFirebaseSync()` to `serverSync.h` | Confusion between Firebase RTDB and custom Railway WebSocket backend | Consolidate cloud adapter interface with explicit `#define USE_FIREBASE` or `#define USE_RAILWAY` | ⚠️ Open |
| **BUG-11** | `firmware/HomeControlSketch.ino` | **MEDIUM** | Missing Over-the-Air (OTA) firmware update support | Device sealed inside wall switchboards requires physical disassembly and USB cable for updates | Add `ArduinoOTA` or `ElegantOTA` with password authentication | ⚠️ Open |
| **BUG-12** | `firmware/config.h:42-45` | **MEDIUM** | GPIO 21 and GPIO 22 assigned to Relays 2 & 3 | GPIO 21/22 are default I2C pins (SDA/SCL); prevents attaching I2C sensors (OLED, BME280, RTC) without pin remapping | Document safe alternative pins (GPIO 18, 5, 25, 26, 27) for relay channels | ⚠️ Open |
| **BUG-13** | Backend & Dashboard | **MEDIUM** | Power usage tracking is purely software calculated (assumed 60W per bulb) | Inaccurate kWh & cost metrics if actual loads are 15W LED, 75W fan, or 1500W geyser | Integrate hardware current sensor (ACS712, PZEM-004T, or SCT-013 CT clamp) | ⚠️ Open |
| **BUG-14** | `firmware/relayControl.h` | **MEDIUM** | No physical relay feedback / state confirmation | If relay fails to switch mechanically, app still reflects commanded state | Add sensing pin or opto-feedback circuit from load side | ⚠️ Open |
| **BUG-15** | `firmware/config.h:26,34` | **LOW** | Default SoftAP password `12345678` used for `SmartHome_Setup` & `SmartHome_Control` | Anyone within WiFi range can connect to ESP32 setup portal and hijack network settings | Force unique AP password generation or require admin button press for setup mode | ⚠️ Open |
| **BUG-16** | `web/app.js:11` | **LOW** | Hardcoded production Railway backend URL in frontend JS | Switching between staging, local development, and production requires editing source files | Support runtime dynamic hostname or environment config | ⚠️ Open |
| **BUG-17** | `HomeControlSketch/` vs `firmware/` | **LOW** | Duplicate sketch folders with minor drift in NTP timing and serial prints | Developers editing `firmware/` might upload outdated `HomeControlSketch/` | Standardize on a single Arduino IDE compliant folder structure | ⚠️ Open |

---

## 🔍 Bug Category Deep Dive

### Category A: Firebase Architecture Bugs
1. **HTTP REST Polling instead of Stream Listener**:
   In `firebaseSync.h`, the ESP32 performs HTTP GET requests every 2,000ms:
   ```cpp
   String response = firebaseGet("devices/" + String(DEVICE_ID) + "/relays");
   ```
   *Why this is a bug*: Each HTTP GET establishes an SSL/TLS TCP handshake consuming ~30KB RAM and 400-800ms of CPU time.
   *Resolution*: Use WebSocket streaming or the event-driven `Firebase_ESP_Client` stream callback.

2. **Deprecated Database Secret Authentication**:
   Google deprecated database secrets in Firebase RTDB. Production apps must use Firebase Authentication (Email/Password or Anonymous) with token refresh handled via Firebase REST API or SDK.

3. **Database Path Discrepancy**:
   `firebaseSync.h` writes to `devices/{DEVICE_ID}/relays/relay1/state`, while legacy systems frequently expected `/home/relay1`. The cloud dashboard and firmware must maintain strict schema consistency.

---

### Category B: ESP32 Hardware & Operating System Bugs
1. **Power Supply & Brownout Detection**:
   Relay modules have an electromagnet coil requiring 70-80mA at 5V per activated channel. When 4 relays trigger simultaneously:
   $$I_{total} = 4 \times 80\text{mA} + I_{ESP32} (\sim 160\text{mA peak WiFi}) \approx 480\text{mA}$$
   Powering from ESP32 development board pins causes a voltage drop on the internal LDO regulator, triggering the ESP32 Hardware Brownout Detector (`Brownout detector was triggered`).
   *Resolution*: Jumper JD-VCC isolation with dedicated 5V 2A DC adapter.

2. **Strapping Pins & Flash Memory Pins**:
   - Pins used in `config.h`: GPIO 23, 22, 21, 19.
   - Status: **SAFE**. These pins avoid ESP32 flash memory pins (GPIO 6-11) and strapping pins (GPIO 0, 2, 12, 15).
   - However, GPIO 21 and 22 conflict with default hardware I2C bus.

3. **Missing Hardware Watchdog**:
   If network stack or DNS freezes, `loop()` halts. Adding `esp_task_wdt` ensures the watchdog triggers a reset after a 15-second hang.

---

### Category C: App & Cloud Bugs
1. **Exposed Credentials**:
   Firebase project configuration (`apiKey`, `projectId`, `appId`) and Railway PostgreSQL credentials should be stored in secure environment variable stores, not committed directly to GitHub.
2. **Offline Device State Lag**:
   Fixed in commit `b553488` for the web app, but still requires robust heartbeat timeouts on the Firebase RTDB side using `.info/connected` and `onDisconnect()`.
