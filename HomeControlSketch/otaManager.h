/*
 * Over-the-Air (OTA) Firmware Update Manager
 * Allows updating firmware wirelessly via ArduinoOTA and ElegantOTA web portal.
 */

#ifndef OTA_MANAGER_H
#define OTA_MANAGER_H

#include <ArduinoOTA.h>
#include <WebServer.h>
#include <ElegantOTA.h>

extern WebServer server;

/*
 * Initialize ArduinoOTA and ElegantOTA
 */
inline void initOTA() {
    // ── Arduino IDE OTA setup ──
    ArduinoOTA.setHostname(DEVICE_ID);
    ArduinoOTA.setPassword("ApnaGhar@2026");

    ArduinoOTA.onStart([]() {
        String type;
        if (ArduinoOTA.getCommand() == U_FLASH) {
            type = "sketch";
        } else { // U_SPIFFS
            type = "filesystem";
        }
        #if ENABLE_SERIAL_DEBUG
        Serial.println("⚡ OTA Start: Updating " + type);
        #endif
    });

    ArduinoOTA.onEnd([]() {
        #if ENABLE_SERIAL_DEBUG
        Serial.println("\n✓ OTA Update Finished! Rebooting...");
        #endif
        delay(250);
        ESP.restart();
    });

    ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
        #if ENABLE_SERIAL_DEBUG
        Serial.printf("OTA Progress: %u%%\r", (progress / (total / 100)));
        #endif
    });

    ArduinoOTA.onError([](ota_error_t error) {
        #if ENABLE_SERIAL_DEBUG
        Serial.printf("⚠ OTA Error[%u]: ", error);
        if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
        else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
        else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
        else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
        else if (error == OTA_END_ERROR) Serial.println("End Failed");
        #endif
    });

    ArduinoOTA.begin();

    // ── ElegantOTA Web Portal setup ──
    // Access at: http://<device-ip>/update or http://smarthome.local/update
    ElegantOTA.begin(&server);
    ElegantOTA.setAuth("admin", "ApnaGhar@2026");

    #if ENABLE_SERIAL_DEBUG
    Serial.println("✓ Wireless OTA Updates Active:");
    Serial.println("  1. Arduino IDE Port (Network discovery)");
    Serial.println("  2. Web Browser: http://" + String(MDNS_HOSTNAME) + ".local/update (User: admin)");
    #endif
}

/*
 * Run OTA handlers. Call this inside loop().
 */
inline void handleOTA() {
    ArduinoOTA.handle();
    ElegantOTA.loop();
}

#endif // OTA_MANAGER_H
