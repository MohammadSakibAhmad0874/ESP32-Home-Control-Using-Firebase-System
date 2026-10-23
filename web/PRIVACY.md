# Privacy Policy — ApnaGhar v2.1

**Last Updated: October 2026**

At **ApnaGhar** ("we", "our", or "us"), we prioritize the privacy and security of your smart home environment. This Privacy Policy details how we collect, store, and protect your data when using the ApnaGhar web portal, mobile application, and connected IoT hardware.

---

### 1. Information We Collect
- **Account Credentials:** When you register, we collect your name, email address, and authentication credentials securely managed through Firebase Authentication.
- **Hardware Telemetry:** To manage your appliances, we store your hardware Device ID, local IP addresses, relay states (`ON`/`OFF`), power/energy readings (via PZEM-004T), and device heartbeat timestamps.
- **Access Requests:** When linking a new device, device authorization requests are transmitted to the project administrator for verification.

### 2. How Your Data Is Used
- To authenticate you into your private dashboard.
- To transmit real-time switch toggle commands to your ESP32 controller over encrypted HTTPS/WSS channels.
- To calculate and display energy usage statistics and real-time operational status.
- We **never** sell, rent, or monetize your personal or telemetry data to third parties.

### 3. Data Storage & Security
- All communications utilize TLS 1.3 encryption (HTTPS and WSS).
- Firebase Realtime Database Security Rules strictly enforce that only authenticated users with verified ownership can view or control assigned hardware devices.
- Administrative controls are isolated behind role-based access control (RBAC).

### 4. Your Rights
You can request account deletion, unclaim hardware devices, or inspect your telemetry logs at any time by contacting your network administrator.

### 5. Contact
For privacy inquiries or technical support, contact `admin@apnaghar.com` or visit our GitHub repository: [ApnaGhar Repository](https://github.com/MohammadSakibAhmad0874/ESP32-Home-Control-Using-Firebase-System).
