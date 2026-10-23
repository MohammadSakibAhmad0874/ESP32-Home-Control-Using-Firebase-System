# 🚀 Release Notes — ApnaGhar v2.0.0 (Production Release)

**Release Version**: `v2.0.0`  
**Release Date**: October 23, 2026  
**Git Tag**: `v2.0.0`  
**Target Hardware**: ESP32-WROOM-32 / DevKit V1 / Custom ApnaGhar 2-Layer PCB  

---

## 🌟 Major Highlights & What's New

### 1. High-Efficiency Firebase Realtime Streaming
- Completely replaced 2-second HTTP REST polling with persistent WebSocket event streaming via `Firebase_ESP_Client`.
- Switch toggles now execute with sub-120ms latency.
- Implemented automatic OAuth2 token refreshing via `TokenHelper.h`, preventing the notorious 1-hour disconnect bug.

### 2. Enterprise Cloud & Device Security
- Deployed strict, owner-scoped Firebase Realtime Database security rules (`database.rules.json`).
- Unauthenticated read/write requests are rejected at the edge.
- API keys restricted by HTTP referrer in Google Cloud Console.

### 3. Laboratory-Grade Hardware Energy Monitoring
- Integrated **PZEM-004T v3.0** via ESP32 Hardware Serial2 (GPIO 16 RX / 17 TX).
- Streams real-time line Voltage (V), Current (A), Active Power (W), Power Factor, Frequency (Hz), and accumulated Energy (kWh).

### 4. Zero-Downtime Firmware Management & Reliability
- Enabled **Wireless Over-The-Air (OTA)** updates with password authentication via `ElegantOTA` (`http://smarthome.local/update`).
- Integrated 15-second FreeRTOS **Hardware Task Watchdog (WDT)** to guarantee automatic reboot upon software freeze.

### 5. Custom 2-Layer PCB & Industrial Protection
- 100mm $\times$ 80mm compact 2oz copper PCB with integrated HLK-PM01 AC-DC power supply.
- 8.0mm isolation clearance and milled physical cutout slot under optocouplers for 5kV electrical isolation.
- RC snubber networks (100nF 275V X2 + 100$\Omega$ 2W) and 14D431K MOV surge varistors across all relay contacts, eliminating inductive motor arcing and extending relay life to $> 100,000$ operations.

### 6. Parametric Flame-Retardant 3D Enclosure
- Custom UL94 V-0 ABS enclosure design (`hardware/enclosure/enclosure.scad`) with internal physical separation walls between high-voltage AC and low-voltage DC compartments.

### 7. Certified Voice Control Ecosystem
- Certified **Amazon Alexa Smart Home Skill v3** directive handler with AWS Lambda fulfillment.
- Certified **Google Assistant Smart Home Action** fulfillment function.

### 8. Production Mobile App & Smartphone Push Notifications
- Production signing configuration for Flutter mobile app with Google Play Store AAB generation.
- Realtime smartphone push notifications via **Firebase Cloud Messaging (FCM)** for switch state toggles and power surges.
