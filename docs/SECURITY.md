# 🔒 Security Audit & Vulnerability Assessment — ESP32 Home Control

This document catalogs all security vulnerabilities identified across firmware, cloud infrastructure, backend microservices, and client frontends, along with step-by-step remediation plans.

---

## 1. Vulnerability Summary Matrix

| Vulnerability ID | Finding Description | Affected Component | Severity | CVSS Score | Remediation Status |
|:---:|:---|:---|:---:|:---:|:---:|
| **SEC-01** | Firebase Web API Key & App IDs Committed to Public Git | `cloud/firebase-config.js:7-14` | **CRITICAL** | 9.1 | Immediate Key Rotation Required |
| **SEC-02** | Default Backend JWT Secret & DB Password in `.env` | `backend/.env:1-4` | **CRITICAL** | 9.8 | Purge from Git + Rotate Secret |
| **SEC-03** | Insecure / Wildcard Firebase Realtime Database Rules | Firebase RTDB Cloud Console | **CRITICAL** | 9.4 | Deploy Granular Security Rules |
| **SEC-04** | Deprecated Database Secret & Missing Token Refresh | `firmware/firebaseSync.h:25` | **HIGH** | 7.5 | Implement OAuth2 Refresh Logic |
| **SEC-05** | Unvalidated SSL / TLS Certificates on ESP32 | `firmware/serverSync.h:42` | **HIGH** | 7.4 | Embed Root CA Certificate |
| **SEC-06** | Static / Insecure SoftAP Default Password (`12345678`) | `firmware/config.h:26,34` | **HIGH** | 7.1 | Generate Dynamic AP Passwords |
| **SEC-07** | Lack of Hardware Watchdog Protection (Denial of Service) | `firmware/HomeControlSketch.ino`| **MEDIUM** | 6.2 | Enable Task WDT (FreeRTOS) |
| **SEC-08** | Insecure HTTP REST Polling over Clear/Simple Endpoints | `firmware/firebaseSync.h:73` | **MEDIUM** | 5.8 | Upgrade to Secure WebSocket/MQTT |

---

## 2. In-Depth Vulnerability Analysis & Exploitation Scenarios

### SEC-01: Exposed Firebase API Key & Project Config
- **File**: `cloud/firebase-config.js`
- **Exposed Value**: `apiKey: "AIzaSyDFXGOMsOqLRa60sOdUlGT925taGmR1KDc"`
- **Risk**: While Firebase API keys are technically client identifiers, leaving them unrestricted coupled with open database rules permits malicious actors to consume project quotas, trigger denial of service, or extract all stored user IDs.
- **Fix**:
  1. Open Google Cloud Console $\rightarrow$ **APIs & Services $\rightarrow$ Credentials**.
  2. Locate the key and apply **Application Restrictions** (Restrict to HTTP referrers matching your Vercel domain `*.vercel.app`).
  3. Apply **API Restrictions** (Limit specifically to *Firebase Realtime Database API* and *Identity Toolkit API*).

---

### SEC-02: Hardcoded Production Secrets in Git Repository
- **File**: `backend/.env`
- **Exposed Value**:
  ```ini
  SECRET_KEY=change-me-to-a-very-long-random-string-min-32-characters-please
  DATABASE_URL=postgresql+asyncpg://homecontrol:homecontrol123@db:5432/homecontrol
  ```
- **Risk**: Any attacker reading the repository can forge arbitrary JWT tokens signed with this key, claiming `role: admin`, and gaining unauthorized access to every registered user and physical smart switch.
- **Fix**:
  1. Remove `.env` from Git tracking:
     ```bash
     git rm --cached backend/.env
     echo "backend/.env" >> .gitignore
     ```
  2. Generate a cryptographically secure 256-bit secret:
     ```bash
     python -c "import secrets; print(secrets.token_hex(32))"
     ```
  3. Set the generated secret inside Railway's Environment Variables dashboard, never in code.

---

### SEC-03: Open Firebase Realtime Database Rules
- **Vulnerability**: If database rules remain set to:
  ```json
  {
    "rules": {
      ".read": true,
      ".write": true
    }
  }
  ```
- **Exploit Scenario**:
  An attacker executes a single terminal command:
  ```bash
  curl -X PUT -d '{"state": true}' \
    "https://apnaghar-3f865-default-rtdb.firebaseio.com/devices/SH-001/relays/relay1.json"
  ```
  Result: The user's physical appliance switches on or off without any authentication, presenting a serious fire or safety hazard!
- **Fix**:
  Deploy the secured `database.rules.json` documented in [docs/DATABASE.md](file:///C:/Users/Ghosty/Desktop/ESP32-Home-Control-Using-Firebase-System-main/docs/DATABASE.md).

---

### SEC-04: Legacy Database Secret & Token Expiry Vulnerability
- **Code**:
  ```cpp
  #define FIREBASE_AUTH "YOUR_DATABASE_SECRET_HERE"
  String url = "https://" + String(FIREBASE_HOST) + "/" + path + ".json?auth=" + String(FIREBASE_AUTH);
  ```
- **Risk**: Google has marked legacy database secrets as deprecated. When switching to Firebase Auth ID tokens, tokens automatically expire every 3,600 seconds (1 hour). Without token refresh handling, the ESP32 disconnects permanently after 60 minutes until power cycled.
- **Fix**:
  Use the official `Firebase_ESP_Client` library which implements automated background token refresh:
  ```cpp
  #include <Firebase_ESP_Client.h>
  #include <addons/TokenHelper.h>

  FirebaseData fbdo;
  FirebaseAuth auth;
  FirebaseConfig config;

  void setup() {
    config.api_key = FIREBASE_API_KEY;
    config.database_url = FIREBASE_URL;
    auth.user.email = DEVICE_EMAIL;
    auth.user.password = DEVICE_PASSWORD;
    Firebase.begin(&config, &auth);
    Firebase.reconnectWiFi(true);
  }
  ```

---

### SEC-05: Unvalidated SSL/TLS Certificate on ESP32
- **Code in `serverSync.h`**:
  Uses `WiFiClientSecure` without installing CA Root Certificates (`client.setInsecure()`).
- **Risk**: The ESP32 accepts any SSL certificate, allowing attackers on the same local network or a rogue AP to intercept commands via Man-in-the-Middle (MitM) attacks.
- **Fix**:
  Provide the ISRG Root X1 (Let's Encrypt) Certificate Authority root PEM string to the client:
  ```cpp
  const char* rootCACertificate = \
  "-----BEGIN CERTIFICATE-----\n" \
  "MIIFazCCA1OgAwIBAgIRAIIQz7DSQONZRGPgu2OCiwAwDQYJKoZIhvcNAQELBQAw\n" \
  "... [ISRG Root X1 Certificate] ...\n" \
  "-----END CERTIFICATE-----\n";

  client.setCACert(rootCACertificate);
  ```

---

### SEC-06: Predictable Default AP Passwords
- **Code**: `AP_PASSWORD = "12345678"` and `HOTSPOT_PASSWORD = "12345678"`.
- **Risk**: Anyone in physical proximity of the home can connect to `SmartHome_Setup` or `SmartHome_Control`, override WiFi credentials, or toggle household switches.
- **Fix**:
  Derive a unique password based on the ESP32 chip MAC address:
  ```cpp
  String getUniqueAPPassword() {
    uint8_t mac[6];
    WiFi.macAddress(mac);
    char buf[16];
    snprintf(buf, sizeof(buf), "Ghar@%02X%02X", mac[4], mac[5]);
    return String(buf); // e.g. "Ghar@3F8A"
  }
  ```

---

## 3. Security Checklist for Production Deployment

- [ ] All API keys restricted in Google Cloud Console by HTTP referrer.
- [ ] Database secrets removed in favor of Firebase Auth User credentials.
- [ ] Production rules deployed to Firebase RTDB via `firebase deploy --only database`.
- [ ] Backend `.env` removed from Git index and stored in Railway environment secrets.
- [ ] Microcontroller firmware embeds root CA certificate for TLS verification.
- [ ] SoftAP password dynamically generated or printed on a physical device label.
- [ ] Firmware updates protected via password-protected OTA (`ArduinoOTA.setPassword()`).
