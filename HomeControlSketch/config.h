/*
 * Configuration File
 * Edit this file with your settings before uploading to ESP32
 * 
 * ✅ NEW: No JWT token needed!
 * Just set your DEVICE_ID below. The firmware auto-fetches
 * the auth token on boot once the device is claimed online.
 * 
 * Step 1: Set DEVICE_ID to your pre-registered ID (given by admin)
 * Step 2: Upload firmware to ESP32 (ONE TIME only)
 * Step 3: User registers online at the dashboard → device works automatically!
 */

#ifndef CONFIG_H
#define CONFIG_H

// ============= ★ YOUR DEVICE ID ★ =============
// Set this to your pre-registered Device ID.
// The user will claim this ID from the web dashboard.
// No password or JWT needed here — it's fetched automatically!
#define DEVICE_ID  "MICK345"      // ← Mick's Device ID

// ============= Access Point Configuration =============
// Setup portal AP (used during initial WiFi setup only)
const char* AP_SSID = "SmartHome_Setup";
const char* AP_PASSWORD = "12345678";  // Change this!

// ============= Always-On Hotspot (AP+STA Dual Mode) =============
// After WiFi connects, ESP32 ALSO creates this hotspot
// so ANY device can connect directly — no matter what network!
// Connect to this WiFi → open 192.168.4.1 in browser
#define ENABLE_ALWAYS_ON_AP true
const char* HOTSPOT_SSID = "SmartHome_Control";
const char* HOTSPOT_PASSWORD = "12345678";  // Change this!

// ============= Device Configuration =============
const char* DEVICE_NAME = "SmartHome";
const int WEB_SERVER_PORT = 80;

// ============= GPIO Pin Configuration =============
// Customize these pins based on your wiring
const int RELAY_PIN_1 = 23;  // Switch 1
const int RELAY_PIN_2 = 22;  // Switch 2
const int RELAY_PIN_3 = 21;  // Switch 3
const int RELAY_PIN_4 = 19;  // Switch 4

// ============= Relay Configuration =============
// Most relay modules are ACTIVE_LOW (relay ON when pin is LOW)
// If your relays work opposite, change to false
const bool ACTIVE_LOW = true;

// Define ON/OFF states based on relay type
#define RELAY_ON  (ACTIVE_LOW ? LOW : HIGH)
#define RELAY_OFF (ACTIVE_LOW ? HIGH : LOW)

// ============= Network Configuration =============
// WiFi connection timeout (milliseconds)
const unsigned long WIFI_TIMEOUT = 20000;  // 20 seconds

// Enable/disable features
#define ENABLE_SERIAL_DEBUG true
#define ENABLE_STATE_PERSISTENCE true  // Remember states after reboot
#define ENABLE_CORS true  // Enable for mobile app integration
#define ENABLE_CAPTIVE_PORTAL true  // WiFi setup wizard
#define ENABLE_MDNS true  // Access via http://smarthome.local

// ============= mDNS Configuration =============
// Access your device from any browser on any device: http://smarthome.local
// Change the hostname below to customize the URL
const char* MDNS_HOSTNAME = "smarthome";  // → http://smarthome.local

// ============= Switch Names (for local web interface) =============
const char* SWITCH_1_NAME = "Living Room";
const char* SWITCH_2_NAME = "Bedroom";
const char* SWITCH_3_NAME = "Kitchen";
const char* SWITCH_4_NAME = "Fan";

#endif
