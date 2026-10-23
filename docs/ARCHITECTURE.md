# 🏛️ Complete Production System Architecture (v2.0) — ApnaGhar

This document outlines the final, fully implemented production architecture of the ApnaGhar ESP32 Home Control ecosystem, integrating all 13 core subsystems.

---

## 1. End-to-End Production Topology Diagram

```mermaid
graph TD
    subgraph CLIENT_INTERFACES [User Interaction Layer]
        PhoneApp["📱 Flutter App (Play Store AAB)"]
        WebDash["💻 Vercel Web Dashboard (React/Tailwind)"]
        VoiceAlexa["🗣️ Amazon Alexa (Echo / Voice)"]
        VoiceGoogle["🗣️ Google Assistant (Nest / Voice)"]
        WallSwitches["🔘 Physical Wall Switches (GPIO 25,26,27,32)"]
    end

    subgraph CLOUD_BACKEND [Cloud & Voice Fulfillment Layer]
        FCM["📲 Firebase Cloud Messaging (Push Alerts)"]
        RTDB[("🔥 Firebase Realtime Database (database.rules.json)")]
        AlexaLambda["☁️ AWS Lambda (SmartHome v3)"]
        GoogleFunction["☁️ Google Actions Fulfillment Function"]
        RailwayBackend["⚙️ Railway FastAPI Backend (JWT / Postgres)"]
    end

    subgraph EDGE_CONTROLLER [Edge Hardware: Custom 2-Layer PCB]
        ESP32["⚡ ESP32-WROOM-32E (Dual-Core 240MHz)"]
        WDT["⏱️ Hardware Task Watchdog (15s WDT)"]
        OTA["📡 Over-the-Air Manager (ElegantOTA & ArduinoOTA)"]
        PZEM["⚡ PZEM-004T v3.0 (UART RX16 / TX17)"]
        Opto["🛡️ 4x EL817 Optocouplers (5kV Isolation)"]
        Relays["🔌 4x 10A Songle Relays"]
        Snubbers["🛡️ 4x RC Snubbers (100nF X2 + 100 Ohm 2W)"]
        MOV["⚡ 14D431K Varistor + 2A Fuse"]
        PowerModule["🔋 HLK-PM01 (240V AC to 5V DC Isolated)"]
    end

    subgraph AC_LOADS [Household Electrical Loads]
        Bulb1["💡 Living Room Light"]
        Bulb2["💡 Bedroom Lamp"]
        Bulb3["💡 Kitchen Light"]
        Fan["🌀 Ceiling Fan (Inductive Load)"]
    end

    %% Voice Connections
    VoiceAlexa --> AlexaLambda --> RTDB
    VoiceGoogle --> GoogleFunction --> RTDB

    %% Client App Connections
    PhoneApp <== HTTPS / Realtime Stream ==> RTDB
    WebDash <== WebSocket / HTTPS ==> RTDB
    FCM -. Push Notifications .-> PhoneApp

    %% Hardware Connections
    RTDB <== Event-Driven Stream (Firebase_ESP_Client) ==> ESP32
    RTDB -. State Trigger .-> FCM
    WallSwitches --> ESP32

    ESP32 --- WDT
    ESP32 --- OTA
    PZEM <-->|UART 9600| ESP32

    ESP32 --> Opto --> Relays
    Relays --- Snubbers
    PowerModule --> ESP32

    MOV --- PowerModule
    Relays ==> Bulb1 & Bulb2 & Bulb3 & Fan
```

---

## 2. Subsystem Integration Summary

| Subsystem # | Component | Protocol / Interface | Latency / Metric | Safety / Isolation |
|:---:|:---|:---|:---:|:---|
| **1** | **Firebase SDK Streaming** | WebSockets / HTTP Stream | $< 120\text{ ms}$ | Token auto-refresh every 3600s |
| **2** | **Firebase Security Rules** | JSON Auth Scope | N/A | Owner-locked UID validation |
| **3** | **Hardware Current Sensing** | UART Serial2 (PZEM-004T) | 10s intervals | Split-core optical isolation |
| **4** | **OTA Wireless Updates** | HTTP Port 80 / ElegantOTA | $\sim 25\text{ s}$ upload | MD5 checksum + password auth |
| **5** | **Hardware Watchdog (WDT)** | FreeRTOS Task Watchdog | 15.0s timeout | Panic auto-reset on hang |
| **6** | **Custom 2-Layer PCB** | 2oz Copper FR4 (100x80mm) | Rated 10A | 8.0mm creepage slot under optos |
| **7** | **Flame-Retardant Enclosure** | UL94 V-0 ABS (120x90x40mm) | V-0 Rated | Internal AC/DC physical divider |
| **8** | **Voice Control Ecosystem** | Alexa Skill v3 & Google Smart Home | $< 800\text{ ms}$ | OAuth2 Token Account Linking |
| **9** | **Mobile App (Flutter)** | Provider + StreamBuilder | Realtime | Signed APK/AAB release key |
| **10** | **Push Notifications (FCM)** | Firebase Cloud Messaging | $< 2.0\text{ s}$ | High-priority Android notification channel |
| **11** | **Physical Switch Feedback** | GPIO 25,26,27,32 (`INPUT_PULLUP`)| 50ms debounce | Isolated from mains AC |
| **12** | **Inductive Snubber Circuit**| 100nF 275V X2 + 100$\Omega$ 2W | Clamps spikes $< 340\text{V}$ | Eliminates contact welding arc |
