# 🌐 ApnaGhar Production Web Dashboard

This web interface serves as the primary browser dashboard for managing your ESP32 Home Control units. It connects in real-time to Firebase Realtime Database and the Railway FastAPI backend.

---

## 🚀 Features

- 🔐 **Dual Auth Flow**: Secure login via Firebase Authentication and Device Claiming using unique hardware IDs (`DEVICE_ID`).
- ⚡ **Realtime Event Streaming**: Listens to `/devices/{deviceId}/relays` via Firebase SDK v10 `onValue()` and WebSocket connection — zero polling delay.
- 🔌 **4-Channel Toggle Matrix**: Fast, responsive toggles for all 4 home appliances with optimistic UI feedback.
- 📊 **Live Power & Energy Telemetry**: Displays real-time line Voltage (V), Current (A), Active Power (W), and cumulative Energy (kWh) streamed from the onboard PZEM-004T sensor.
- ⏰ **Smart Automation Scheduler**: Day-of-week and time-of-day trigger configurations.
- 👑 **Super-Admin Panel**: Comprehensive telemetry, IP addresses, and state inspection for all registered family switches.

---

## 🛠 Local Development & Testing

1. Serve statically via Python, Node.js, or any static HTTP server:
   ```bash
   # Using Python 3 built-in server:
   cd web
   python -m http.server 3000
   ```
2. Or using `npx serve`:
   ```bash
   npx serve web
   ```
3. Open `http://localhost:3000` in your web browser.

---

## ☁️ Deployment to Vercel

The dashboard is configured for zero-configuration continuous deployment on Vercel:

1. Install Vercel CLI (optional):
   ```bash
   npm install -g vercel
   ```
2. Deploy directly from repository root:
   ```bash
   vercel --prod
   ```
3. Configuration defined in [`vercel.json`](vercel.json):
   - Clean URLs enabled (e.g. `/dashboard` $\to$ `/dashboard.html`)
   - HTTPS Strict-Transport-Security & X-Frame-Options headers applied
