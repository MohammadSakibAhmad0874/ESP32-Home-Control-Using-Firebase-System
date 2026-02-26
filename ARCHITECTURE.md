# 🏠 SmartHome (ApnaGhar) — Complete System Architecture

> **Project:** ApnaGhar Smart Home Control System  
> **Firebase Project:** `apnaghar-3f865`  
> **Live URL:** https://apnaghar-3f865.web.app  
> **Last Updated:** Feb 2026

---

## 📋 Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture Diagram](#2-architecture-diagram)
3. [Component Breakdown](#3-component-breakdown)
4. [Firebase Database Structure](#4-firebase-database-structure)
5. [How It Works — Data Flow](#5-how-it-works--data-flow)
6. [User Flows](#6-user-flows)
7. [New User Registration Guide](#7-new-user-registration-guide)
8. [How a New User Gets the Product](#8-how-a-new-user-gets-the-product)
9. [Admin Panel Guide](#9-admin-panel-guide)
10. [Local vs Cloud Control](#10-local-vs-cloud-control)
11. [Security Model](#11-security-model)
12. [Device (ESP32) Configuration](#12-device-esp32-configuration)
13. [Known Issues & Fixes](#13-known-issues--fixes)

---

## 1. System Overview

SmartHome is an **IoT home automation system** that lets users control electrical switches (lights, fans, appliances) from:

- 🌍 **Anywhere in the world** via a cloud web app
- 📶 **Local network** via the ESP32's built-in web server
- 📡 **Direct hotspot** by connecting to the ESP32's own WiFi (no internet needed)

### Technology Stack

| Layer | Technology |
|---|---|
| Hardware | ESP32 microcontroller + 4-channel relay module |
| Firmware | Arduino C++ (ESP32 Arduino SDK) |
| Cloud Database | Firebase Realtime Database |
| Authentication | Firebase Authentication (Email/Password) |
| Web Frontend | HTML + CSS + JavaScript (Vanilla) |
| Hosting | Firebase Hosting |
| Local Server | ESP32 built-in HTTP server (port 80) |

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACES                         │
├───────────────────────┬─────────────────────────────────────┤
│  🌍 CLOUD WEB APP     │  📶 LOCAL WEB UI  │ 📡 AP HOTSPOT  │
│  apnaghar-3f865       │  http://smart      │  SmartHome_    │
│  .web.app             │  home.local        │  Control WiFi  │
│  (anywhere in world)  │  (same network)    │  → 192.168.4.1 │
└───────────┬───────────┴────────┬───────────┴───────┬────────┘
            │ HTTPS              │ HTTP               │ HTTP
            ▼                   ▼                   ▼
┌───────────────────┐   ┌───────────────────────────────────┐
│  FIREBASE CLOUD   │   │         ESP32 DEVICE              │
│                   │   │                                   │
│  ┌─────────────┐  │   │  ┌────────────────────────────┐   │
│  │  Auth       │  │   │  │  WiFi Manager              │   │
│  │  (login/reg)│  │   │  │  - Station Mode (STA)      │   │
│  └─────────────┘  │   │  │  - AP Mode (hotspot)       │   │
│                   │   │  │  - Captive Portal Setup     │   │
│  ┌─────────────┐  │◄──┼──│  └────────────────────────┘   │
│  │  Realtime   │  │   │  │                                │
│  │  Database   │──┼──►│  │  ┌────────────────────────┐   │
│  │             │  │   │  │  │  Firebase Sync Module  │   │
│  │  /devices   │  │   │  │  │  - GET relay states    │   │
│  │  /users     │  │   │  │  │  - PUT online status   │   │
│  │  /admins    │  │   │  │  │  - Heartbeat (30s)     │   │
│  └─────────────┘  │   │  │  └────────────────────────┘   │
│                   │   │  │                                │
│  ┌─────────────┐  │   │  │  ┌────────────────────────┐   │
│  │  Hosting    │  │   │  │  │  Relay Control         │   │
│  │  index.html │  │   │  │  │  - 4x GPIO pins        │   │
│  │  dashboard  │  │   │  │  │  - Active-LOW relays   │   │
│  │  admin.html │  │   │  │  │  - State persistence   │   │
│  └─────────────┘  │   │  │  └────────────────────────┘   │
└───────────────────┘   └───────────────────────────────────┘
                                        │
                                        │ GPIO pins (23,22,21,19)
                                        ▼
                        ┌───────────────────────────────┐
                        │      RELAY MODULE (4-ch)      │
                        ├────────┬────────┬─────────────┤
                        │ Relay1 │ Relay2 │ Relay3 │ R4 │
                        │ Living │ Bedroom│ Kitchen│ Fan│
                        │ Room   │        │        │    │
                        └────────┴────────┴────────┴────┘
                                        │
                              230V AC appliances
                        (lights, fans, air coolers, etc.)
```

---

## 3. Component Breakdown

### 3.1 Frontend — Cloud Web App (`/cloud` folder)

| File | Purpose |
|---|---|
| `index.html` | Login + New Device Registration page |
| `dashboard.html` | User dashboard — shows device status + relay toggles |
| `admin.html` | Admin panel — monitors ALL devices & users |
| `app.js` | Shared JS utilities (auth helpers, toggle relay, logout) |
| `firebase-config.js` | Firebase project configuration & SDK init |
| `style.css` | Full dark-mode UI styling system |

### 3.2 Firmware — ESP32 (`/firmware` folder)

| File | Purpose |
|---|---|
| `HomeControlSketch.ino` | Main sketch — `setup()` + `loop()` entry point |
| `config.h` | All user-configurable settings (pins, names, features) |
| `wifiManager.h` | WiFi connection, captive portal, AP+STA dual mode |
| `relayControl.h` | GPIO relay control with state persistence (NVS flash) |
| `firebaseSync.h` | HTTP REST client for Firebase Realtime DB sync |

### 3.3 Cloud Backend — Firebase

| Service | Usage |
|---|---|
| **Firebase Auth** | Email/password user accounts |
| **Realtime Database** | Device state, relay status, online/offline, lastSeen |
| **Firebase Hosting** | Serves the web app globally via CDN |

---

## 4. Firebase Database Structure

```json
{
  "admins": {
    "<uid>": true
  },

  "users": {
    "<uid>": {
      "name": "Ghosty",
      "email": "user@email.com",
      "deviceId": "SH-001"
    }
  },

  "devices": {
    "SH-001": {
      "owner": "<firebase-uid>",
      "ownerName": "Ghosty",
      "email": "user@email.com",
      "deviceId": "SH-001",
      "numSwitches": 4,
      "online": true,
      "lastSeen": 1772000000,
      "ip": "192.168.1.105",
      "createdAt": 1772000000,
      "relays": {
        "relay1": { "state": true,  "name": "Living Room" },
        "relay2": { "state": false, "name": "Bedroom" },
        "relay3": { "state": false, "name": "Kitchen" },
        "relay4": { "state": true,  "name": "Fan" }
      }
    }
  }
}
```

**Key relationships:**
- Each `user` has ONE `deviceId`
- Each `device` has ONE `owner` (uid)
- `admins` node is a flat list of uids → `true`

---

## 5. How It Works — Data Flow

### Controlling a Switch from the Web App

```
User clicks toggle on dashboard
        │
        ▼
app.js: toggleRelay()
        │
        ▼  WRITE
Firebase Realtime DB
devices/SH-001/relays/relay1/state = true
        │
        ▼  (ESP32 polls every 2 seconds)
ESP32: syncFromCloud()
        │   firebaseGet("devices/SH-001/relays")
        │   Parses JSON response
        │   Detects state changed: relay1 false→true
        ▼
GPIO pin 23 → LOW (RELAY_ON)
        │
        ▼
Physical relay closes → Light turns ON ✅
```

### ESP32 Heartbeat (every 30 seconds)

```
ESP32: sendHeartbeat()
        │
        ▼  PATCH
Firebase: devices/SH-001/online = true
                          lastSeen = <unix timestamp>
        │
        ▼
Dashboard reads online=true → shows 🟢 ESP32 Online
```

### Local Toggle (physical button or local web page)

```
User presses physical button / uses http://smarthome.local
        │
        ▼
ESP32: setRelay() → toggles GPIO
        │
        ▼
notifyCloudStateChange() → PUT to Firebase
        │
        ▼
Firebase updated → Dashboard reflects new state in real-time
```

---

## 6. User Flows

### 6.1 Existing User — Login

```
Open https://apnaghar-3f865.web.app
        │
        ▼
Enter Device ID (e.g., SH-001) + Password
        │
        ▼
index.html looks up: devices/SH-001/email → user@email.com
        │
        ▼
Firebase Auth: signInWithEmailAndPassword()
        │
        ▼
Device ID stored in localStorage
        │
        ▼
Redirect → dashboard.html
        │
        ▼
Real-time listener on devices/SH-001 activates
        │
        ▼
Shows current online status + all relay toggle switches ✅
```

### 6.2 Controlling a Device

```
Dashboard loaded
        │
        ├── Shows: 🟢 ESP32 Online / 🔴 Offline
        ├── Shows: Last seen X min ago
        └── Shows: 4 switches with ON/OFF state
                │
                ▼ (User clicks switch)
        Firebase write: relay state flips
                │
                ▼ (ESP32 polls in ≤2 seconds)
        Physical relay triggered
```

---

## 7. New User Registration Guide

### Step 1 — Open the Web App

Go to: **https://apnaghar-3f865.web.app**

### Step 2 — Click "Register Device" tab

Fill in the form:

| Field | Example | Notes |
|---|---|---|
| Your Name | Ghosty | Display name |
| New Device ID | SH-002 | Must be UNIQUE (e.g. SH-001, SH-002...) |
| Email | user@email.com | Used for login |
| Password | mypassword | Min 6 characters |
| Number of Switches | 4 | How many relays your ESP32 has |

### Step 3 — Click "Register New Device"

The system will:
1. ✅ Check if `SH-002` already exists (if yes → error)
2. ✅ Create Firebase Auth account (email + password)
3. ✅ Create device entry in database with 4 relays (all OFF)
4. ✅ Map UID → device in `/users`
5. ✅ Redirect to dashboard

### Step 4 — Configure the ESP32 Firmware

Open `firmware/firebaseSync.h` and change:

```cpp
#define FIREBASE_HOST  "apnaghar-3f865-default-rtdb.firebaseio.com"
#define FIREBASE_AUTH  "YOUR_DATABASE_SECRET"   // From Firebase Console
#define DEVICE_ID      "SH-002"                 // Must match what you registered!
```

Open `firmware/config.h` and set switch names:

```cpp
const char* SWITCH_1_NAME = "Living Room";
const char* SWITCH_2_NAME = "Bedroom";
const char* SWITCH_3_NAME = "Kitchen";
const char* SWITCH_4_NAME = "Fan";
```

### Step 5 — Flash Firmware to ESP32

1. Open `firmware/HomeControlSketch.ino` in Arduino IDE
2. Select board: **ESP32 Dev Module**
3. Click **Upload**
4. Open Serial Monitor (115200 baud) to see status logs

### Step 6 — Connect ESP32 to WiFi

1. ESP32 boots and creates hotspot: **SmartHome_Setup**
2. Connect your phone/laptop to that hotspot
3. A captive portal opens automatically (or go to `192.168.4.1`)
4. Select your home WiFi and enter the password
5. ESP32 connects and syncs with Firebase ☁️

---

## 8. How a New User Gets the Product

### Hardware Required (User must buy)

| Item | Purpose | Approx. Cost |
|---|---|---|
| ESP32 Dev Board | Main microcontroller | ~$5-10 |
| 4-Channel Relay Module | Controls 230V AC appliances | ~$3-5 |
| Jumper Wires | Wiring connections | ~$2 |
| 5V Power Supply | Powers ESP32 | ~$3 |
| Electrical box (optional) | Safe enclosure | ~$5 |

### Wiring (GPIO Pins)

```
ESP32 GPIO 23 → Relay Module IN1 (Switch 1 - Living Room)
ESP32 GPIO 22 → Relay Module IN2 (Switch 2 - Bedroom)
ESP32 GPIO 21 → Relay Module IN3 (Switch 3 - Kitchen)
ESP32 GPIO 19 → Relay Module IN4 (Switch 4 - Fan)
ESP32 GND     → Relay Module GND
ESP32 5V/VIN  → Relay Module VCC
```

### Setup Journey

```
1. BUY hardware (ESP32 + relay module)
         │
         ▼
2. WIRE hardware (6 jumper wires — see above)
         │
         ▼
3. REGISTER on web app (https://apnaghar-3f865.web.app)
   → Choose your unique Device ID (e.g., SH-003)
         │
         ▼
4. CONFIGURE firmware
   → Edit firebaseSync.h: set DEVICE_ID = "SH-003"
   → Edit config.h: set switch names
         │
         ▼
5. FLASH firmware to ESP32 via Arduino IDE
         │
         ▼
6. SETUP WiFi via captive portal (first time only)
         │
         ▼
7. DONE — Control from anywhere! 🎉
```

---

## 9. Admin Panel Guide

The admin panel is at: **https://apnaghar-3f865.web.app/admin.html**

Only accessible to users listed in `/admins` in Firebase.

### First Time Admin Setup

1. Go to `admin.html`
2. Click **"👑 Make Me Admin"** (only appears when no admin exists)
3. Your UID is written to `/admins/<uid> = true`

### What Admins Can See

- **Total Devices** — count of all registered ESP32s
- **Online / Offline** counts in real-time  
- **All device cards** showing:
  - Device ID and owner name
  - Online/Offline status with last seen time
  - All relay states (can toggle them from admin panel!)

---

## 10. Local vs Cloud Control

| Feature | Cloud (Firebase) | Local Network | Direct Hotspot |
|---|---|---|---|
| **Works without internet** | ❌ | ✅ | ✅ |
| **Works away from home** | ✅ | ❌ | ❌ |
| **Real-time updates** | ✅ | ✅ | ✅ |
| **Access URL** | apnaghar-3f865.web.app | smarthome.local or ESP32's IP | 192.168.4.1 |
| **Auth required** | ✅ | ❌ | ❌ |
| **Sync delay** | ~2 seconds | Instant | Instant |

---

## 11. Security Model

| What | How |
|---|---|
| User accounts | Firebase Authentication (email+password) |
| Device access | Users can only see their own device (by `deviceId` stored in profile) |
| Admin access | Checked via `/admins/<uid>` node in DB |
| Firebase DB rules | Should restrict reads/writes by authenticated UID |
| Local web server | No auth (anyone on same network can control) |
| Hotspot | Password protected: `12345678` (change in `config.h`!) |
| API calls from ESP32 | Database Secret in `FIREBASE_AUTH` (keep private!) |

> ⚠️ **Important:** Change the hotspot passwords in `config.h` before deploying!  
> The default `12345678` is a security risk.

---

## 12. Device (ESP32) Configuration

### config.h — All Settings

```cpp
// Hotspot name when no WiFi configured
const char* AP_SSID     = "SmartHome_Setup";
const char* AP_PASSWORD = "12345678";          // CHANGE THIS

// Always-on control hotspot (after WiFi connects)
const char* HOTSPOT_SSID     = "SmartHome_Control";
const char* HOTSPOT_PASSWORD = "12345678";     // CHANGE THIS

// GPIO relay pins
const int RELAY_PIN_1 = 23;
const int RELAY_PIN_2 = 22;
const int RELAY_PIN_3 = 21;
const int RELAY_PIN_4 = 19;

// Switch names shown in local web UI
const char* SWITCH_1_NAME = "Living Room";
const char* SWITCH_2_NAME = "Bedroom";
const char* SWITCH_3_NAME = "Kitchen";
const char* SWITCH_4_NAME = "Fan";
```

### firebaseSync.h — Cloud Settings

```cpp
#define FIREBASE_HOST  "apnaghar-3f865-default-rtdb.firebaseio.com"
#define FIREBASE_AUTH  "YOUR_DATABASE_SECRET"  // Keep secret!
#define DEVICE_ID      "SH-001"               // Must match registered ID
```

### Sync Timings

| Event | Interval |
|---|---|
| Poll Firebase for relay commands | Every **2 seconds** |
| Send heartbeat (online + lastSeen) | Every **30 seconds** |
| WiFi connection timeout | 20 seconds |

---

## 13. Known Issues & Fixes

### ❌ `lastSeen` shows "20509 days ago"

**Root Cause:** `firebaseSync.h` uses `millis()` (milliseconds since ESP32 boot) instead of a real Unix timestamp. `millis()` after a few hours might be e.g. `3,600,000` — not a valid date.

**Fix in `firebaseSync.h`** — replace `millis()` with an NTP-fetched Unix time (requires `<time.h>`):

```cpp
// Add to top of firebaseSync.h:
#include <time.h>

// In initFirebaseSync() and sendHeartbeat(), replace millis() with:
time_t now;
time(&now);   // Gets Unix timestamp in seconds
// Then use: String(now)  instead of String(millis())
```

**Temporary frontend fix** *(already applied in dashboard.html)*: auto-detect if timestamp is in seconds range and convert before display.

---

## Quick Reference

| Action | How |
|---|---|
| Open web dashboard | https://apnaghar-3f865.web.app |
| Register new device | Open web app → "Register Device" tab |
| Control locally | Connect to `SmartHome_Control` WiFi → open `192.168.4.1` |
| Control on local network | Open `http://smarthome.local` in browser |
| Admin panel | https://apnaghar-3f865.web.app/admin.html |
| Add new relay/switch | Increase `numSwitches` on registration, wire new GPIO |
| Update firmware | Edit `config.h`/`firebaseSync.h` → re-upload via Arduino IDE |
| Deploy web changes | `firebase deploy --only hosting` in project folder |
