# HomeControl — Self-Hosted Deployment Guide

## What You've Built

Your own Firebase-replacement that runs on Docker. No monthly cost, no vendor lock-in.

```
📱 Phone → Ngrok URL → Nginx → FastAPI + PostgreSQL
                                      ↕ WebSocket
                                   ESP32 Device
```

---

## Part 1 — First-Time Setup (Do Once)

### Step 1: Install Prerequisites

| Software | Download | Notes |
|---|---|---|
| **Docker Desktop** | https://www.docker.com/products/docker-desktop | Enable WSL2 when asked |
| **Ngrok** | https://ngrok.com/download | Create a free account |

### Step 2: Get Your Free Ngrok Static Domain

1. Go to https://dashboard.ngrok.com/domains
2. Click **"New Domain"** → Ngrok gives you a free static hostname like `abc-123.ngrok-free.app`
3. Copy your **Auth Token** from https://dashboard.ngrok.com/get-started/your-authtoken

### Step 3: Configure Ngrok

Open `ngrok.yml` and fill in:
```yaml
authtoken: "YOUR_ACTUAL_AUTHTOKEN"
tunnels:
  homecontrol:
    hostname: "abc-123.ngrok-free.app"   # ← Your free static domain
```

### Step 4: Configure the Backend Secret

Open `backend/.env` and set a strong secret key:
```
SECRET_KEY=your-very-long-random-string-here-make-it-at-least-32-chars
```

### Step 5: Start the Server

**Double-click `start_server.bat`** or run in PowerShell:
```powershell
cd C:\Users\Ghosty\Desktop\HomeControlbase\HomeControl
docker compose up -d --build
ngrok start --all --config ngrok.yml
```

### Step 6: Open the Dashboard

- **Local (your PC):** http://localhost/cloud/index.html
- **Anywhere in world:** https://abc-123.ngrok-free.app/cloud/index.html

### Step 7: Register Your First Device + Make Admin

1. Open the dashboard → **Register Device** tab
2. Fill in your details (e.g., Device ID: `SH-001`)
3. After registering, go to `http://localhost/cloud/admin.html`
4. Click **"👑 Make Me Admin"** (only works when no admin exists yet)

---

## Part 2 — Configure ESP32 Firmware

### Step 1: Get Your JWT Token

After registering, get your token via curl (or use Postman):
```bash
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"device_id":"SH-001","password":"yourpassword"}'
```
Copy the `"token"` value from the response.

### Step 2: Install Arduino Library

Open Arduino IDE → **Tools → Manage Libraries**
Search for **"WebSockets"** by **Markus Sattler** → Install

### Step 3: Edit `firmware/serverSync.h`

```cpp
#define SERVER_HOST  "abc-123.ngrok-free.app"  // Your Ngrok domain
#define SERVER_PORT  443
#define SERVER_SSL   true
#define DEVICE_ID    "SH-001"
#define DEVICE_JWT   "eyJhbGci..."               // Paste your token here
```

### Step 4: Flash and Test

1. Open `firmware/HomeControlSketch.ino` in Arduino IDE
2. Select board: **ESP32 Dev Module**
3. Click **Upload**
4. Open Serial Monitor (115200 baud) — you should see:
   ```
   ☁ HomeControl Server Sync starting...
   ⏰ Syncing NTP time... OK
   ☁ WS Connected to server!
   ```

---

## Part 3 — Always-On for Free (Optional)

If you want the server running even when your laptop is OFF:

### Option A: Render.com (Recommended — Truly Free)

1. Push your code to GitHub
2. Go to https://render.com → **New Web Service**
3. Connect your GitHub repo
4. Settings:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add free PostgreSQL via Render → copy the `DATABASE_URL`
6. Add environment variables (same as `.env`)
7. Your URL will be like `homecontrol.onrender.com`
8. Update `SERVER_HOST` in ESP32 firmware

> **Note:** Render free tier sleeps after 15 min inactivity. Use a free uptime monitor like [UptimeRobot](https://uptimerobot.com) to ping it every 5 minutes to keep it awake.

### Option B: Oracle Cloud Free Tier

Oracle gives a **permanently free** VM (2 vCPUs, 1 GB RAM). Run Docker there.
See: https://www.oracle.com/cloud/free/

---

## Quick Reference

| Task | Command/URL |
|---|---|
| Start server | Double-click `start_server.bat` |
| Stop server | Double-click `stop_server.bat` |
| View logs | `docker compose logs -f` |
| Dashboard | `http://localhost/cloud/index.html` |
| Admin panel | `http://localhost/cloud/admin.html` |
| API docs | `http://localhost/api/docs` (Swagger UI) |
| API health | `http://localhost/api/health` |
| View DB | `docker exec -it homecontrol-db psql -U homecontrol homecontrol` |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Docker not starting | Start Docker Desktop first |
| Port 80 in use | Change `80:80` to `8080:80` in `docker-compose.yml` |
| ESP32 won't connect | Check `SERVER_HOST` and `DEVICE_JWT` in `serverSync.h` |
| JWT expired | Re-login, copy new token, re-flash ESP32 |
| DB data lost | DB is in a Docker named volume — safe across restarts |
