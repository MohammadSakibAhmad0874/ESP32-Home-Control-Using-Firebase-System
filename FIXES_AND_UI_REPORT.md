# ApnaGhar v2.1 — Security Hardening, Pipeline Flow & 3D Glassmorphism UI Report

**Release Version:** v2.1.0  
**Build Date:** October 2026  
**Live Production URL:** [https://web-iota-ruddy-37.vercel.app](https://web-iota-ruddy-37.vercel.app)  
**Fixed Android APK:** [`ApnaGhar-v2.2-3D-Glass.apk`](file:///c:/Users/Ghosty/Desktop/ESP32-Home-Control-Using-Firebase-System-main/ApnaGhar-v2.2-3D-Glass.apk) (57.3 MB)

---

## 1. Executive Summary & Problems Resolved

| Bug ID | Severity | Root Cause | Engineering Resolution |
| :--- | :--- | :--- | :--- |
| **BUG-1: "Dangerous / Deceptive Site" Warning** | **CRITICAL** | Browser flagged Vercel URL due to: open unauthenticated admin page, missing HTTPS security headers (`HSTS`, `CSP`, `X-Frame-Options`), lack of privacy policy & terms, missing `favicon.ico`, `manifest.json`, and `robots.txt`. | Added full enterprise security headers in [`vercel.json`](file:///c:/Users/Ghosty/Desktop/ESP32-Home-Control-Using-Firebase-System-main/web/vercel.json), created public `favicon.ico`, `manifest.json`, `robots.txt` (disallowing `/admin`), and live legal routes [`/privacy`](file:///c:/Users/Ghosty/Desktop/ESP32-Home-Control-Using-Firebase-System-main/web/src/pages/PrivacyPage.jsx) and [`/terms`](file:///c:/Users/Ghosty/Desktop/ESP32-Home-Control-Using-Firebase-System-main/web/src/pages/TermsPage.jsx). |
| **BUG-2: Direct Admin Access Hole** | **CRITICAL** | Navigating to `/admin` or `/dashboard` directly allowed any anonymous user to view, edit, or delete hardware nodes and toggle switches without an account. | Implemented role-based route guards: [`ProtectedRoute`](file:///c:/Users/Ghosty/Desktop/ESP32-Home-Control-Using-Firebase-System-main/web/src/components/ProtectedRoute.jsx) and [`AdminRoute`](file:///c:/Users/Ghosty/Desktop/ESP32-Home-Control-Using-Firebase-System-main/web/src/components/AdminRoute.jsx). Public landing page (`/`) is now completely separated from authenticated dashboards. |
| **BUG-3: Missing Device Claim & Admin Approval Flow** | **HIGH** | Users could arbitrarily control any device without verification or authorization from the device owner. | Established a secure request queue: New users register (`role=user`) -> submit Device ID (e.g. `SAKIB7860`) -> verified against Firebase -> creates request in `/deviceRequests` -> Admin reviews and approves in Admin Panel -> user gains relay control. |
| **BUG-4: Admin Data Invisible Bug** | **HIGH** | Previous admin page called `.val()` without null checks, causing blank tables and JavaScript exceptions on empty nodes. | Refactored Firebase RTDB queries with `Object.entries(snapshot.val() || {})`, loading skeletons, and empty states across 3 tabs (Pending Requests, All Devices, Registered Users). |
| **BUG-5: Outdated Basic UI vs Reference Design** | **MEDIUM** | Previous dashboard had flat dark boxes without high-contrast neon accents or 3D depth. | Completely redesigned web and mobile UI using **3D Glassmorphism** (`rgba(26,31,46,0.65)`, 20px blur, glowing neon cyan `#00D9FF` and magenta `#FF2E93` pill switches, floating 3D device mockup, and animated Recharts energy consumption graph). |

---

## 2. End-to-End System Pipeline Flow

```mermaid
graph TD
  A[User clicks Vercel link] --> B[Landing Page Public - 3D Glass UI - No auth fetch]
  B --> C{Has account?}
  C -- No --> D[Signup - Glass form with motion]
  D --> E[Create /users/{uid} role=user]
  E --> F[User Dashboard - Glass stats + My Devices empty state]
  C -- Yes --> G[Login - Glass form]
  G --> H{Check /users/{uid}/role}
  H -- user --> F
  H -- admin --> I[Admin Dashboard - 3 tabs with glass tables]
  F --> J[Add Device ID - Glass modal]
  J --> K{Device exists in /devices?}
  K -- No --> L[Error: Device not found]
  K -- Yes --> M[Create /deviceRequests/{id}_{uid} status=pending]
  M --> N[Show Pending with spinner]
  I --> O[Admin sees pending in Tab 1]
  O --> P{Approve?}
  P -- Yes --> Q[Write /users/{uid}/devices/{id}=true + owner]
  P -- No --> R[Reject]
  Q --> S[User can control 4 relays with 3D toggles + energy chart]
```

---

## 3. UI/UX 3D Glassmorphism Comparison

### Reference Design vs Implementation

| UI Element | Reference Specification | Implementation Details |
| :--- | :--- | :--- |
| **Theme & Canvas** | Deep dark canvas `#0B0E14` with hexagonal grid and radial neon glows. | Custom CSS grid background with dual radial glow layers (cyan `#00D9FF` and magenta `#FF2E93`). |
| **Card Styling** | Glassmorphic containers with 20px backdrop blur, `border: 1px solid rgba(255,255,255,0.1)`, inner highlight. | `.glass-panel` and `.glass-card` classes with multi-layer drop shadows and inset highlights. |
| **Overview Badges** | Overview row with Lights (6 On), Devices (14 Active), Security (Armed), Climate (72°F / 22°C). | 4 glass cards on User Dashboard matching exact layout, icons, and neon accents. |
| **3D Floating Mockup** | Floating mobile and tablet devices with dynamic perspective and soft shadows. | Embedded [`/hero-3d-mockup.png`](file:///c:/Users/Ghosty/Desktop/ESP32-Home-Control-Using-Firebase-System-main/web/public/hero-3d-mockup.png) animated with CSS 3D keyframe transforms. |
| **Switch Toggles** | Glowing pill toggles with smooth spring motion and neon glow when active. | Framer Motion layout toggles with spring physics (`stiffness: 500, damping: 30`) and cyan/magenta box-shadow glows. |
| **Energy Consumption** | Daily Consumption bar chart (18.4 kWh) with gradient bars from Mon to Sun. | Responsive Recharts Bar Chart with purple-to-cyan gradient fills and interactive tooltips. |

---

## 4. How to Verify & Test the Live Pipeline

### As Administrator:
1. Open [https://web-iota-ruddy-37.vercel.app/login](https://web-iota-ruddy-37.vercel.app/login).
2. Login with your Admin credentials (e.g. `admin@apnaghar.com` / `Admin@123`).
3. You will be automatically routed to **`/admin`** with 3 dedicated management tabs:
   - **Tab 1 (Pending Requests):** View incoming device claim requests with one-click **[Approve]** and **[Reject]**.
   - **Tab 2 (Hardware Devices):** View all ESP32 nodes, live telemetry pings, and pre-register new hardware.
   - **Tab 3 (Registered Users):** Inspect all accounts and promote team members to Administrator.

### As a Normal User:
1. Open [https://web-iota-ruddy-37.vercel.app](https://web-iota-ruddy-37.vercel.app) (Public Landing Page).
2. Click **Create Free Account** and register a new user.
3. You are redirected to **`/dashboard`** showing an empty state with **"+ Link New Device ID"**.
4. Enter `SAKIB7860`. The request is verified against Firebase and submitted to the queue.
5. In another tab or as admin, approve the request.
6. The user dashboard instantly updates in real-time, unlocking full 4-relay control with 3D glowing toggles!

---

## 5. Security Headers Telemetry Verification

```http
HTTP/2 200 OK
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self' https: data: blob:; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://*.firebaseio.com https://*.googleapis.com; connect-src 'self' https://*.firebaseio.com https://*.googleapis.com wss://*.firebaseio.com https://esp32-home-control-using-firebase-system-production.up.railway.app;
```
