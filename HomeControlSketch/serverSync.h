/*
 * HomeControl — Self-Hosted Server Sync Module
 *
 * Auto-Token Edition: No more hardcoded JWT!
 * The ESP32 fetches its own auth token from the server on every boot.
 * It just needs the DEVICE_ID from config.h → no re-upload needed after
 * the user claims the device online.
 *
 * Flow:
 *   1. ESP32 boots + connects to WiFi
 *   2. Calls GET /api/esp/connect/{DEVICE_ID} → server returns JWT
 *   3. Uses JWT to open WebSocket on /ws/esp/{DEVICE_ID}?token={JWT}
 *   4. If device not yet claimed: retries every 30s until user registers online
 *
 * Library to install in Arduino IDE:
 *   Tools → Manage Libraries → search "WebSockets" by Markus Sattler → Install
 *   Tools → Manage Libraries → search "ArduinoJson" → Install
 *   Tools → Manage Libraries → search "HTTPClient" (built-in for ESP32)
 *
 * Message Protocol (JSON):
 *   Server → ESP32: {"type":"relay_cmd","relay1":true,"relay2":false,...}
 *   ESP32 → Server: {"type":"heartbeat","ip":"192.168.1.10"}
 *   ESP32 → Server: {"type":"state_update","states":{"relay1":true,...}}
 */

#ifndef SERVER_SYNC_H
#define SERVER_SYNC_H

#include <WebSocketsClient.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <time.h>

// =====================================================================
// SERVER CONFIGURATION
// =====================================================================

// Railway backend hostname (no https://, no trailing slash)
#define SERVER_HOST     "esp32-home-control-using-firebase-system-production.up.railway.app"
#define SERVER_PORT     443           // 443 for HTTPS/WSS (Railway)
#define SERVER_SSL      true          // Railway uses SSL

// How often to retry token fetch if device is not yet claimed
#define TOKEN_RETRY_INTERVAL_MS  30000UL

// Heartbeat interval after connection established
#define HEARTBEAT_INTERVAL_MS  30000UL

// DEVICE_ID comes from config.h — do NOT define it here
// =====================================================================

WebSocketsClient wsClient;

bool serverSyncEnabled = false;
String deviceToken = "";            // JWT fetched automatically on boot

unsigned long lastHeartbeatTime = 0;
unsigned long lastTokenRetryTime = 0;
bool tokenFetched = false;

// Forward declarations
void pushStatesToServer();
void sendHeartbeatWS();
void connectWebSocket();

// ── WebSocket Event Handler ──────────────────────────────────────────────────

void webSocketEvent(WStype_t type, uint8_t* payload, size_t length) {
    switch (type) {

    case WStype_CONNECTED:
        serverSyncEnabled = true;
        #if ENABLE_SERIAL_DEBUG
        Serial.println("☁ WS Connected to server!");
        #endif
        // Immediately send our current state
        pushStatesToServer();
        break;

    case WStype_DISCONNECTED:
        serverSyncEnabled = false;
        #if ENABLE_SERIAL_DEBUG
        Serial.println("☁ WS Disconnected. Will reconnect...");
        #endif
        break;

    case WStype_TEXT: {
        // Parse incoming JSON command from the server
        String msg = String((char*)payload);

        StaticJsonDocument<512> doc;
        if (deserializeJson(doc, msg) != DeserializationError::Ok) break;

        String msgType = doc["type"] | "";

        if (msgType == "relay_cmd") {
            // Server says: toggle specific relay(s)
            bool stateChanged = false;
            for (int i = 0; i < 4; i++) {
                String key = "relay" + String(i + 1);
                if (doc.containsKey(key)) {
                    bool newState = doc[key].as<bool>();
                    if (newState != relayStates[i]) {
                        setRelay(i, newState);
                        stateChanged = true;
                        #if ENABLE_SERIAL_DEBUG
                        Serial.printf("☁ Command: relay%d → %s\n", i + 1, newState ? "ON" : "OFF");
                        #endif
                    }
                }
            }
            // Confirm back to server
            if (stateChanged) pushStatesToServer();

        } else if (msgType == "ping") {
            // Server ping — respond with heartbeat
            sendHeartbeatWS();
        }
        break;
    }

    case WStype_ERROR:
        #if ENABLE_SERIAL_DEBUG
        Serial.println("☁ WS Error");
        #endif
        break;

    default:
        break;
    }
}

// ── Auto Token Fetch ──────────────────────────────────────────────────────────

/*
 * Calls GET https://SERVER_HOST/api/esp/connect/{DEVICE_ID}
 * If the device has been claimed online, returns a JWT token.
 * If not yet claimed, returns false so we can retry later.
 */
bool fetchDeviceToken() {
    #if ENABLE_SERIAL_DEBUG
    Serial.println("\n☁ Fetching device token from server...");
    Serial.printf("  Device ID: %s\n", DEVICE_ID);
    #endif

    WiFiClientSecure client;
    client.setInsecure();  // Skip SSL certificate verification (self-signed OK)

    HTTPClient http;
    String url = "https://" + String(SERVER_HOST) + "/api/esp/connect/" + String(DEVICE_ID);
    http.begin(client, url);
    http.setTimeout(10000);  // 10 second timeout

    int httpCode = http.GET();

    if (httpCode == 200) {
        String payload = http.getString();
        http.end();

        StaticJsonDocument<512> doc;
        if (deserializeJson(doc, payload) == DeserializationError::Ok) {
            const char* token = doc["token"];
            if (token && strlen(token) > 0) {
                deviceToken = String(token);
                tokenFetched = true;
                #if ENABLE_SERIAL_DEBUG
                Serial.println("☁ Token received successfully!");
                Serial.printf("  Owner: %s\n", (const char*)doc["name"] | "—");
                #endif
                return true;
            }
        }
        #if ENABLE_SERIAL_DEBUG
        Serial.println("⚠ Token parse failed.");
        #endif
    } else if (httpCode == 503) {
        // Device exists but hasn't been claimed yet
        #if ENABLE_SERIAL_DEBUG
        Serial.println("⏳ Device not yet claimed online.");
        Serial.println("   → Have the user visit the dashboard and claim this Device ID.");
        Serial.printf("   → Retrying in %d seconds...\n", TOKEN_RETRY_INTERVAL_MS / 1000);
        #endif
    } else if (httpCode == 404) {
        #if ENABLE_SERIAL_DEBUG
        Serial.printf("❌ Device ID '%s' not found on server.\n", DEVICE_ID);
        Serial.println("   → Check your DEVICE_ID in config.h.");
        #endif
    } else {
        #if ENABLE_SERIAL_DEBUG
        Serial.printf("⚠ Token fetch failed. HTTP %d\n", httpCode);
        #endif
    }

    http.end();
    return false;
}

// ── WebSocket Connection ──────────────────────────────────────────────────────

void connectWebSocket() {
    if (deviceToken.length() == 0) return;

    #if ENABLE_SERIAL_DEBUG
    Serial.println("☁ Connecting WebSocket to server...");
    Serial.printf("  %s:%d\n", SERVER_HOST, SERVER_PORT);
    #endif

    // Build WebSocket path: /ws/esp/{device_id}?token={jwt}
    String wsPath = "/ws/esp/" + String(DEVICE_ID) + "?token=" + deviceToken;

    wsClient.onEvent(webSocketEvent);

    if (SERVER_SSL) {
        wsClient.beginSSL(SERVER_HOST, SERVER_PORT, wsPath.c_str());
    } else {
        wsClient.begin(SERVER_HOST, SERVER_PORT, wsPath.c_str());
    }

    wsClient.setReconnectInterval(5000);   // Reconnect every 5s if disconnected
    wsClient.enableHeartbeat(15000, 3000, 2); // Ping every 15s, timeout 3s, 2 failures

    #if ENABLE_SERIAL_DEBUG
    Serial.println("☁ WebSocket client initialized!");
    #endif
}

// ── NTP Time Sync ─────────────────────────────────────────────────────────────

void initNTP() {
    configTime(0, 0, "pool.ntp.org", "time.nip.io");
    #if ENABLE_SERIAL_DEBUG
    Serial.print("⏰ Syncing NTP time");
    #endif
    time_t now = 0;
    int retries = 0;
    while (now < 1000000000UL && retries++ < 20) {
        delay(300);
        time(&now);
        #if ENABLE_SERIAL_DEBUG
        Serial.print(".");
        #endif
    }
    #if ENABLE_SERIAL_DEBUG
    Serial.println(now > 1000000000UL ? " OK" : " FAILED (no internet?)");
    #endif
}

// ── Initialization ────────────────────────────────────────────────────────────

void initServerSync() {
    if (String(SERVER_HOST) == "YOUR-SERVER-HOST.up.railway.app") {
        #if ENABLE_SERIAL_DEBUG
        Serial.println("⚠ Server not configured — cloud sync disabled.");
        Serial.println("  Edit firmware/serverSync.h with your Railway URL.");
        #endif
        serverSyncEnabled = false;
        return;
    }

    // Try to fetch the JWT token
    if (fetchDeviceToken()) {
        // Token acquired — connect WebSocket immediately
        connectWebSocket();
    } else {
        // Token not available yet — will retry in cloudSyncLoop()
        lastTokenRetryTime = millis();
    }
}

// ── State sync helpers ────────────────────────────────────────────────────────

void sendHeartbeatWS() {
    if (!serverSyncEnabled) return;
    if (millis() - lastHeartbeatTime < HEARTBEAT_INTERVAL_MS) return;
    lastHeartbeatTime = millis();

    String json = "{\"type\":\"heartbeat\",\"ip\":\"" + WiFi.localIP().toString() + "\"}";
    wsClient.sendTXT(json);

    #if ENABLE_SERIAL_DEBUG
    Serial.println("☁ WS Heartbeat sent");
    #endif
}

void pushStatesToServer() {
    if (!serverSyncEnabled) return;

    String json = "{\"type\":\"state_update\",\"states\":{";
    for (int i = 0; i < 4; i++) {
        json += "\"relay" + String(i + 1) + "\":" + (relayStates[i] ? "true" : "false");
        if (i < 3) json += ",";
    }
    json += "}}";

    wsClient.sendTXT(json);
}

/*
 * Call this when a relay is toggled locally (physical button or local web page)
 * Notifies the server so the dashboard updates in real-time.
 */
void notifyCloudStateChange(int relayIndex, bool newState) {
    if (!serverSyncEnabled) return;

    String json = "{\"type\":\"state_update\",\"states\":{\"relay" +
                  String(relayIndex + 1) + "\":" + (newState ? "true" : "false") + "}}";
    wsClient.sendTXT(json);
}

/*
 * Main loop — call this in loop()
 * Handles WebSocket keep-alive, heartbeats, and token retries.
 */
void cloudSyncLoop() {
    // If we have a token, run the WebSocket loop normally
    if (tokenFetched) {
        wsClient.loop();    // Must be called every loop() iteration
        sendHeartbeatWS();
        return;
    }

    // No token yet — retry fetching at TOKEN_RETRY_INTERVAL_MS
    if (millis() - lastTokenRetryTime >= TOKEN_RETRY_INTERVAL_MS) {
        lastTokenRetryTime = millis();
        #if ENABLE_SERIAL_DEBUG
        Serial.println("☁ Retrying token fetch...");
        #endif
        if (fetchDeviceToken()) {
            // Token acquired! Start WebSocket connection now
            connectWebSocket();
        }
    }
}

/*
 * Alias so main sketch doesn't need changing
 */
void initFirebaseSync() {
    initServerSync();
}

#endif // SERVER_SYNC_H
