/*
 * Firebase Realtime Database Event Streaming Module
 * Replaces high-latency 2-second HTTP polling with event-driven WebSocket
 * streaming and automated OAuth2 token refresh using Firebase_ESP_Client.
 */

#ifndef FIREBASE_STREAM_H
#define FIREBASE_STREAM_H

#include <Firebase_ESP_Client.h>
#include <addons/TokenHelper.h>
#include <addons/RTDBHelper.h>
#include "config.h"
#include "relayControl.h"

// Firebase data objects
static FirebaseData fbdo;
static FirebaseData stream;
static FirebaseAuth auth;
static FirebaseConfig config;

static bool firebaseStreamReady = false;
static unsigned long lastFirebasePing = 0;

/*
 * Stream event callback: triggers instantly whenever a relay state changes in Firebase
 */
inline void streamCallback(FirebaseStream data) {
#if ENABLE_SERIAL_DEBUG
    Serial.printf("⚡ Firebase Stream event: Path=%s, Type=%s\n",
                  data.dataPath().c_str(), data.dataType().c_str());
#endif

    String path = data.dataPath();

    // Check if the stream event updated a specific relay
    if (path.indexOf("relay1") > -1) {
        bool state = data.boolData();
        setRelay(0, state);
    } else if (path.indexOf("relay2") > -1) {
        bool state = data.boolData();
        setRelay(1, state);
    } else if (path.indexOf("relay3") > -1) {
        bool state = data.boolData();
        setRelay(2, state);
    } else if (path.indexOf("relay4") > -1) {
        bool state = data.boolData();
        setRelay(3, state);
    } else if (path == "/" || path == "") {
        // Entire relays node was written as JSON
        if (data.dataType() == "json") {
            FirebaseJson &json = data.jsonObject();
            FirebaseJsonData result;

            if (json.get(result, "relay1/state")) setRelay(0, result.boolValue);
            if (json.get(result, "relay2/state")) setRelay(1, result.boolValue);
            if (json.get(result, "relay3/state")) setRelay(2, result.boolValue);
            if (json.get(result, "relay4/state")) setRelay(3, result.boolValue);
        }
    }
}

/*
 * Stream timeout callback: handles connection dropouts and automatic recovery
 */
inline void streamTimeoutCallback(bool timeout) {
    if (timeout) {
#if ENABLE_SERIAL_DEBUG
        Serial.println("⚠ Firebase stream timed out. Auto-resuming connection...");
#endif
    }
    if (!stream.httpConnected()) {
#if ENABLE_SERIAL_DEBUG
        Serial.printf("⚠ Firebase stream error code: %d, reason: %s\n",
                      stream.httpCode(), stream.errorReason().c_str());
#endif
    }
}

/*
 * Initialize Firebase streaming connection and authentication with auto-refresh
 */
inline void initFirebaseStream() {
#if ENABLE_SERIAL_DEBUG
    Serial.println("\n🔥 Initializing Firebase Realtime Stream...");
#endif

    config.api_key = FIREBASE_API_KEY;
    config.database_url = FIREBASE_DATABASE_URL;
    auth.user.email = FIREBASE_USER_EMAIL;
    auth.user.password = FIREBASE_USER_PASSWORD;

    // Automatic token refresh callback (prevents 1-hour disconnect bug)
    config.token_status_callback = tokenStatusCallback;
    config.max_token_generation_retry = 5;

    Firebase.begin(&config, &auth);
    Firebase.reconnectWiFi(true);
    fbdo.setResponseSize(4096);

    String streamPath = "/devices/" + String(DEVICE_ID) + "/relays";
    if (!Firebase.RTDB.beginStream(&stream, streamPath.c_str())) {
#if ENABLE_SERIAL_DEBUG
        Serial.printf("❌ Firebase stream begin failed: %s\n", stream.errorReason().c_str());
#endif
        firebaseStreamReady = false;
        return;
    }

    Firebase.RTDB.setStreamCallback(&stream, streamCallback, streamTimeoutCallback);
    firebaseStreamReady = true;

#if ENABLE_SERIAL_DEBUG
    Serial.println("✓ Firebase Realtime Streaming ACTIVE on " + streamPath);
#endif

    // Update online telemetry
    String devPath = "/devices/" + String(DEVICE_ID);
    Firebase.RTDB.setBoolAsync(&fbdo, (devPath + "/online").c_str(), true);
    Firebase.RTDB.setStringAsync(&fbdo, (devPath + "/ip").c_str(), WiFi.localIP().toString().c_str());
}

/*
 * Publish single relay state back to Firebase asynchronously
 */
inline void publishRelayToFirebase(int relayIndex, bool state) {
    if (!Firebase.ready()) return;
    String path = "/devices/" + String(DEVICE_ID) + "/relays/relay" + String(relayIndex + 1) + "/state";
    Firebase.RTDB.setBoolAsync(&fbdo, path.c_str(), state);
}

/*
 * Keepalive and token auto-refresh verification loop
 */
inline void handleFirebaseStreamLoop() {
    if (Firebase.ready()) {
        // Automatic token expiry check (refreshes before 3600s expiration)
        if (Firebase.isTokenExpired()) {
            Firebase.refreshToken(&config);
#if ENABLE_SERIAL_DEBUG
            Serial.println("🔄 Firebase Auth token refreshed automatically.");
#endif
        }

        // Heartbeat every 30 seconds
        if (millis() - lastFirebasePing > 30000) {
            lastFirebasePing = millis();
            String path = "/devices/" + String(DEVICE_ID) + "/lastSeen";
            Firebase.RTDB.setIntAsync(&fbdo, path.c_str(), (int)(millis() / 1000));
        }
    }
}

#endif // FIREBASE_STREAM_H
