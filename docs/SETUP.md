# 🚀 Complete Setup & Execution Guide — ESP32 Home Control

This is the definitive, step-by-step setup guide for anyone wishing to build, configure, flash, and run the ESP32 Home Control (ApnaGhar) system from scratch.

---

## 1. Hardware Assembly

### Step 1.1: Connect ESP32 to 4-Channel Relay
Use female-to-female DuPont jumper wires to wire the low-voltage logic side:

| ESP32 Board Pin | 4-Channel Relay Board Pin | Cable Color Recommendation |
|:---:|:---:|:---:|
| **GPIO 23** | **IN 1** | Blue |
| **GPIO 22** | **IN 2** | Green |
| **GPIO 21** | **IN 3** | Yellow |
| **GPIO 19** | **IN 4** | Orange |
| **GND** | **GND** | Black (Mandatory Common Ground) |
| **VIN / 5V** | **VCC** (or External 5V) | Red |

### Step 1.2: Connect Power Supply
- Connect a regulated **5V 2A DC adapter** to the relay board power inputs.
- Make sure the ESP32 GND and Relay GND are firmly connected together.

---

## 2. Software & Toolchain Installation

### Step 2.1: Download & Install Arduino IDE
1. Download **Arduino IDE 2.x** from [arduino.cc](https://www.arduino.cc/en/software).
2. Install and launch the IDE.

### Step 2.2: Add ESP32 Board Support
1. Go to **File $\rightarrow$ Preferences** (or `Ctrl + ,`).
2. In **Additional boards manager URLs**, add:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. Open **Tools $\rightarrow$ Board $\rightarrow$ Boards Manager**.
4. Search for `esp32` by **Espressif Systems** and click **Install** (version `2.0.14` or later).

### Step 2.3: Install Required Libraries
Open **Tools $\rightarrow$ Manage Libraries** (or `Ctrl + Shift + I`), search and install each of the following:

1. **`ArduinoJson`** by *Benoît Blanchon* $\rightarrow$ Install version **6.21.3** or **7.x**.
2. **`WebSockets`** by *Markus Sattler* $\rightarrow$ Install version **2.4.1** or later.
3. **`HTTPClient`** $\rightarrow$ Bundled automatically with ESP32 core.
4. **`WiFi`** $\rightarrow$ Bundled automatically with ESP32 core.
5. **`WebServer`** $\rightarrow$ Bundled automatically with ESP32 core.
6. **`DNSServer`** $\rightarrow$ Bundled automatically with ESP32 core.

---

## 3. Firebase Cloud Configuration

If using Firebase Realtime Database:

1. Go to the [Firebase Console](https://console.firebase.google.com/).
2. Click **Add project** $\rightarrow$ Name it `apnaghar-smart-home`.
3. In the left navigation, open **Build $\rightarrow$ Realtime Database** $\rightarrow$ Click **Create Database**.
4. Choose database location (e.g., `us-central1` or `asia-southeast1`) $\rightarrow$ Start in **Test mode**.
5. Copy your **Database URL** (e.g., `https://apnaghar-smart-home-default-rtdb.firebaseio.com/`).
6. Go to **Project Settings (Gear Icon) $\rightarrow$ General**:
   - Scroll to **Your apps** $\rightarrow$ Click **Web (`</>`)** $\rightarrow$ Register App.
   - Copy the `firebaseConfig` object (contains `apiKey`, `projectId`, `databaseURL`).

---

## 4. Configuring Firmware Code

1. Open the project in Arduino IDE:
   - File $\rightarrow$ Open $\rightarrow$ Select `firmware/HomeControlSketch.ino` (or `HomeControlSketch/HomeControlSketch.ino`).
2. Open `config.h`:
   - Set your pre-registered Device ID:
     ```cpp
     #define DEVICE_ID  "SAKIB7860"  // Set your unique hardware code
     ```
   - Customize switch names:
     ```cpp
     const char* SWITCH_1_NAME = "Living Room Light";
     const char* SWITCH_2_NAME = "Bedroom Lamp";
     const char* SWITCH_3_NAME = "Kitchen Light";
     const char* SWITCH_4_NAME = "Ceiling Fan";
     ```
3. If using Firebase sync:
   - Open `firebaseSync.h`:
     ```cpp
     #define FIREBASE_HOST "your-project-default-rtdb.firebaseio.com"
     #define FIREBASE_AUTH "YOUR_SECRET_OR_TOKEN"
     ```

---

## 5. Flashing the ESP32

1. Connect the ESP32 to your computer using a quality micro-USB data cable (ensure it is a data cable, not power-only).
2. Go to **Tools $\rightarrow$ Board $\rightarrow$ esp32 $\rightarrow$ ESP32 Dev Module** (or *NodeMCU-32S*).
3. Select the correct serial port under **Tools $\rightarrow$ Port** (e.g., `COM3`, `COM4` on Windows).
4. Configure upload settings:
   - **Upload Speed**: `921600` (or `115200` if upload fails)
   - **Flash Frequency**: `80MHz`
   - **Flash Mode**: `QIO`
5. Click the **Upload** button (`Right Arrow` icon in top bar).
   *(Note: If the IDE shows `Connecting......`, hold the physical **BOOT** button on the ESP32 until the flashing percentage begins, then release).*
6. Open **Tools $\rightarrow$ Serial Monitor**, set baud rate to **115200**. You should see:
   ```
   ========================================
     Smart Home Automation System v1.2
   ========================================
   Relay 1 initialized: OFF
   Relay 2 initialized: OFF
   Relay 3 initialized: OFF
   Relay 4 initialized: OFF
   📱 Setup Mode Active!
     Connect to WiFi: SmartHome_Setup
   ```

---

## 6. First-Time WiFi Setup (Captive Portal)

No code editing is required for WiFi credentials:

1. Grab your smartphone or laptop and open WiFi Settings.
2. Connect to the network: **`SmartHome_Setup`** (Password: `12345678`).
3. The setup page opens automatically in your browser (if not, navigate to `http://192.168.4.1`).
4. Select your home 2.4GHz WiFi network from the dropdown list.
5. Enter your home WiFi password and click **Save & Connect**.
6. The ESP32 connects to your home network and displays its new IP address.

---

## 7. Controlling Your Switches

### Option A: Local Network (Zero Internet Required)
- Open browser on any computer or phone connected to the same home WiFi:
  - URL: **`http://smarthome.local`** (or browse to the ESP32's assigned IP, e.g. `http://192.168.1.50`).

### Option B: Offline Direct Hotspot
- If home broadband is completely down:
- Connect phone to WiFi: **`SmartHome_Control`** (Password: `12345678`).
- Open browser and navigate to: **`http://192.168.4.1`**.

### Option C: Online Cloud Dashboard (Anywhere in the World)
- Open the hosted web dashboard: [web-iota-ruddy-37.vercel.app](https://web-iota-ruddy-37.vercel.app).
- Claim your device by entering your `DEVICE_ID` (e.g. `SAKIB7860`).
- Control switches, set automated schedules, and view energy metrics!
