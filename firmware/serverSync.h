/*
 * HomeControl — Self-Hosted Server Sync Module
 *
 * Replaces firebaseSync.h with WebSocket-based real-time communication.
 * Uses the arduinoWebSockets library (by Markus Sattler).
 *
 * Library to install in Arduino IDE:
 *   Tools → Manage Libraries → search "WebSockets" by Markus Sattler → Install
 *
 * This gives INSTANT relay control (no 2-second polling!).
 * The ESP32 maintains a persistent WebSocket connection to the server.
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
#include <time.h>

// =====================================================================
// SERVER CONFIGURATION
// Change these to match your Ngrok URL or self-hosted server.
// =====================================================================

// Your Ngrok hostname (no https://, no trailing slash)
// Current URL from your running Ngrok tunnel:
#define SERVER_HOST     "cespitosely-exiguous-homer.ngrok-free.dev"
#define SERVER_PORT     443           // 443 for HTTPS/WSS (Ngrok), 80 for HTTP/WS (LAN)
#define SERVER_SSL      true          // Set false if using plain HTTP (LAN test)

// Your Device ID — must match what you registered on the web dashboard
#define DEVICE_ID       "SH-001"

// JWT Token — get this from /api/auth/login using curl or Postman,
// then paste the token string here.
// Tip: Use a long expiry (7 days) and re-generate monthly.
#define DEVICE_JWT      "PASTE-YOUR-JWT-TOKEN-HERE"

// Heartbeat interval
#define HEARTBEAT_INTERVAL_MS  30000UL

// =====================================================================

WebSocketsClient wsClient;

bool serverSyncEnabled = false;
unsigned long lastHeartbeatTime = 0;
unsigned long lastReconnectAttempt = 0;

// Forward declarations
String buildStateUpdateJSON();
void pushStatesToServer();

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
            // Server ping — respond with pong via heartbeat
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

// ── Initialization ────────────────────────────────────────────────────────────

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

void initServerSync() {
    if (String(SERVER_HOST) == "YOUR-NGROK-HOST.ngrok-free.app") {
        #if ENABLE_SERIAL_DEBUG
        Serial.println("⚠ Server not configured — cloud sync disabled.");
        Serial.println("  Edit firmware/serverSync.h with your server URL and JWT.");
        #endif
        serverSyncEnabled = false;
        return;
    }

    if (String(DEVICE_JWT) == "PASTE-YOUR-JWT-TOKEN-HERE") {
        #if ENABLE_SERIAL_DEBUG
        Serial.println("⚠ JWT Token not set — cloud sync disabled.");
        Serial.println("  1. Register on dashboard");
        Serial.println("  2. Login via curl: curl -X POST http://{HOST}/api/auth/login \\");
        Serial.println("     -H 'Content-Type: application/json' \\");
        Serial.println("     -d '{\"device_id\":\"SH-001\",\"password\":\"yourpassword\"}'");
        Serial.println("  3. Copy 'token' value into DEVICE_JWT in serverSync.h");
        #endif
        serverSyncEnabled = false;
        return;
    }

    #if ENABLE_SERIAL_DEBUG
    Serial.println("\n☁ HomeControl Server Sync starting...");
    Serial.printf("  Device ID: %s\n", DEVICE_ID);
    Serial.printf("  Server:    %s:%d\n", SERVER_HOST, SERVER_PORT);
    #endif

    // Build WebSocket path: /ws/esp/{device_id}?token={jwt}
    String wsPath = "/ws/esp/" + String(DEVICE_ID) + "?token=" + String(DEVICE_JWT);

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
 * Handles WebSocket keep-alive and heartbeats.
 */
void cloudSyncLoop() {
    wsClient.loop();    // Must be called every loop() iteration
    sendHeartbeatWS();
}

/*
 * Alias so main sketch doesn't need changing
 */
void initFirebaseSync() {
    initServerSync();
}

#endif // SERVER_SYNC_H
