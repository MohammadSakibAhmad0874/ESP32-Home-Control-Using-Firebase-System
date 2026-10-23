/*
 * Configuration File — ESP32 Home Control (ApnaGhar)
 * Edit this file with your settings before uploading to ESP32
 */

#ifndef CONFIG_H
#define CONFIG_H

// ============= ★ YOUR DEVICE ID ★ =============
// Set this to your pre-registered Device ID.
// The user will claim this ID from the web dashboard.
#define DEVICE_ID  "SAKIB7860"    // ← Change this to your assigned Device ID

// ============= Firebase Realtime Stream Configuration =============
#define USE_FIREBASE_STREAM     true
#define FIREBASE_API_KEY        "AIzaSyDFXGOMsOqLRa60sOdUlGT925taGmR1KDc" // Replace with restricted key in prod
#define FIREBASE_DATABASE_URL   "https://apnaghar-3f865-default-rtdb.firebaseio.com"
#define FIREBASE_USER_EMAIL     "device@apnaghar.com"
#define FIREBASE_USER_PASSWORD  "DevicePass123"

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

// ============= Physical Wall Switch Feedback Pins =============
// Safe GPIOs with internal pull-ups for manual mechanical switches
#define ENABLE_MANUAL_SWITCHES true
const int MANUAL_SWITCH_PIN_1 = 25;
const int MANUAL_SWITCH_PIN_2 = 26;
const int MANUAL_SWITCH_PIN_3 = 27;
const int MANUAL_SWITCH_PIN_4 = 32;

// ============= Hardware Energy Sensing Configuration =============
#define ENABLE_POWER_MONITORING true
#define USE_PZEM               true   // true = PZEM-004T v3.0 UART; false = ACS712 Analog
#define PZEM_RX_PIN            16     // Connects to PZEM TX
#define PZEM_TX_PIN            17     // Connects to PZEM RX
#define ACS712_ANALOG_PIN      34     // Safe ADC1 input pin for ACS712

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
#define ENABLE_SERIAL_DEBUG     true
#define ENABLE_STATE_PERSISTENCE true  // Remember states after reboot
#define ENABLE_CORS             true  // Enable for mobile app integration
#define ENABLE_CAPTIVE_PORTAL   true  // WiFi setup wizard
#define ENABLE_MDNS             true  // Access via http://smarthome.local
#define ENABLE_OTA              true  // Over-the-air updates
#define ENABLE_WATCHDOG         true  // Hardware Task Watchdog (15s)

// ============= mDNS Configuration =============
// Access your device from any browser on any device: http://smarthome.local
const char* MDNS_HOSTNAME = "smarthome";  // → http://smarthome.local

// ============= Switch Names (for local web interface) =============
const char* SWITCH_1_NAME = "Living Room";
const char* SWITCH_2_NAME = "Bedroom";
const char* SWITCH_3_NAME = "Kitchen";
const char* SWITCH_4_NAME = "Fan";

#endif // CONFIG_H
