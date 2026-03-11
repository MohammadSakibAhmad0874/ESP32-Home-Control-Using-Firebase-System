# 🏠 ApnaGhar — Smart Home Control System

> **Apna Ghar, Apna Control — Smart Home, Your Way**

A custom ESP32-based platform for controlling home switches via WiFi — **zero-code setup**, **real-time WebSocket control**, and **cloud access from anywhere in the world**.

---

## ✨ Features

- 📱 **WiFi Setup Wizard** — Configure WiFi from your phone, no code needed
- 📡 **Always-On Hotspot** — ESP32 broadcasts `SmartHome_Control` WiFi for direct access
- ☁️ **Cloud Dashboard** — Control from **anywhere** via Railway-hosted backend
- 🔐 **Login / Device Claim Flow** — Unique Device ID + password authentication
- 👑 **Admin Panel** — Monitor and control ALL devices from one place
- ⚡ **Real-time WebSocket** — Instant switch state updates, no polling
- 📊 **Power Usage Tracker** — kWh estimator with per-switch wattage and cost (₹)
- ⏰ **Automation Schedules** — Time-based ON/OFF rules with day-of-week selection
- 🔄 **AP+STA Dual Mode** — Home WiFi + own hotspot at the same time
- 💾 **State Persistence** — Remembers all switch states after power loss
- 🟢 **Smart Online/Offline Status** — IP address hidden when device is offline (shows `—`)
- 🔒 **Secure** — JWT auth, HTTPS on all endpoints

## 🛠 Hardware Requirements

- ESP32 Development Board
- 4-Channel Relay Module (5V)
- Jumper Wires
- 5V Power Supply (2A recommended)
- Electrical wiring and safety equipment

## 🚀 Quick Start

1. **Hardware Setup** — See [Hardware Setup Guide](docs/hardware_setup.md)
2. **Upload Firmware** — Flash `firmware/HomeControlSketch.ino` via Arduino IDE
3. **Connect to Setup WiFi** — Connect your phone to `SmartHome_Setup` (password: `12345678`)
4. **Setup Wizard Opens** — Pick your home WiFi and enter the password
5. **Done!** — ESP32 joins your WiFi and keeps its own hotspot running

### 📡 Access from Any Phone / Laptop / Tablet (Local)

| Step | Action |
|------|--------|
| 1️⃣ | Connect to WiFi: **`SmartHome_Control`** (password: `12345678`) |
| 2️⃣ | Open browser → **`http://192.168.4.1`** |
| 3️⃣ | Done! Control switches 🎉 |

---

## ☁️ Deployment Architecture

| Service | Role | URL |
|---------|------|-----|
| **Railway** | Python/FastAPI backend + WebSocket server | `https://esp32-home-control-using-firebase-system-production.up.railway.app` |
| **Vercel** | Static frontend hosting | `https://apna-ghar-sooty.vercel.app` |

### 🚂 Railway (Backend)

The backend runs on Railway and handles:
- REST API (`/api/auth`, `/api/devices`, `/api/admin`)
- WebSocket connections for real-time device control
- SQLite database for device/user/schedule storage

To redeploy: push to the `main` branch and Railway auto-deploys.

```bash
git add .
git commit -m "your message"
git push origin main
```

### ▲ Vercel (Frontend)

The `web/` folder is deployed to Vercel as a static site.

To redeploy: push to `main` — Vercel auto-deploys from the connected GitHub repo.

### Step: Register Your Device

1. Open the Vercel URL on any phone/laptop
2. Click **Claim Your Device** tab
3. Enter your Device ID → set name, email, password
4. Dashboard opens! ✅

### Step: Upload ESP32 Firmware

1. Open `firmware/HomeControlSketch.ino` in Arduino IDE
2. Set your WiFi credentials in the Captive Portal (no code edit needed)
3. Click **Upload** → Serial Monitor confirms connection

---

## 📖 Documentation

- [Hardware Setup](docs/hardware_setup.md) — Wiring and safety guidelines
- [WiFi Setup Guide](docs/wifi_setup.md) — Configure WiFi through the wizard

## 🎯 Project Structure

```
HomeControl/
├── web/                   # 🌐 Frontend (Vercel-hosted)
│   ├── index.html         # Login / Claim Device page
│   ├── dashboard.html     # Switch control + schedules + power
│   ├── admin.html         # Admin panel (all devices)
│   ├── style.css          # Design system
│   └── app.js             # Shared API/auth helpers
├── backend/               # ⚙️ Python FastAPI backend (Railway)
│   ├── main.py            # Entry point — API routes + WebSocket
│   └── web/               # Served static fallback copy
├── firmware/              # 🔧 ESP32 Arduino firmware
│   ├── HomeControlSketch.ino
│   └── firebaseSync.h
├── cloud/                 # 🗂️ Legacy cloud version
└── docs/                  # Documentation
```

## 🔄 Changelog

### Latest
- 🟢 **Offline IP fix** — IP field now shows `—` when device is offline (was showing stale cached IP)
- ⏰ **Schedules** — Automation with day-of-week selection
- 📊 **Power Usage** — kWh tracker per switch with cost estimates

## ⚠️ Safety Warning

This project controls mains electricity. Always:
- Work with power disconnected
- Use proper isolation
- Follow local electrical codes
- Consider professional installation verification

## 📝 License

Open source — use and modify as you wish!

---

**Built with ❤️ for complete control of your smart home — ApnaGhar**
