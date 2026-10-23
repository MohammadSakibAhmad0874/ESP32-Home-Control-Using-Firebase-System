/*
 * Physical Wall Switch Feedback & Debounce Module — ESP32 Home Control
 * Connects standard residential wall switches to ESP32 inputs.
 * Toggling the physical switch toggles the relay, updates local RAM/NVS,
 * and notifies the Firebase Realtime Database and connected clients.
 */

#ifndef MANUAL_SWITCH_H
#define MANUAL_SWITCH_H

#include <Arduino.h>
#include "config.h"
#include "relayControl.h"

// Forward declaration from firebaseStream.h
void publishRelayToFirebase(int relayIndex, bool state);

static const int MANUAL_SWITCH_PINS[4] = {
    MANUAL_SWITCH_PIN_1,
    MANUAL_SWITCH_PIN_2,
    MANUAL_SWITCH_PIN_3,
    MANUAL_SWITCH_PIN_4
};

static bool lastManualState[4] = {HIGH, HIGH, HIGH, HIGH};
static unsigned long lastDebounceTime[4] = {0, 0, 0, 0};
static const unsigned long DEBOUNCE_DELAY_MS = 50; // 50ms debouncing window

/*
 * Initialize manual switch input pins with internal pullups
 */
inline void initManualSwitches() {
#if ENABLE_MANUAL_SWITCHES
    for (int i = 0; i < 4; i++) {
        pinMode(MANUAL_SWITCH_PINS[i], INPUT_PULLUP);
        lastManualState[i] = digitalRead(MANUAL_SWITCH_PINS[i]);
    }
    #if ENABLE_SERIAL_DEBUG
    Serial.printf("✓ Physical Wall Switches initialized on GPIOs: %d, %d, %d, %d (INPUT_PULLUP)\n",
                  MANUAL_SWITCH_PINS[0], MANUAL_SWITCH_PINS[1], MANUAL_SWITCH_PINS[2], MANUAL_SWITCH_PINS[3]);
    #endif
#endif
}

/*
 * Poll physical wall switches for user toggle events (non-blocking)
 */
inline void checkManualSwitches() {
#if ENABLE_MANUAL_SWITCHES
    for (int i = 0; i < 4; i++) {
        bool reading = digitalRead(MANUAL_SWITCH_PINS[i]);

        if (reading != lastManualState[i]) {
            if ((millis() - lastDebounceTime[i]) > DEBOUNCE_DELAY_MS) {
                lastDebounceTime[i] = millis();
                lastManualState[i] = reading;

                // Toggle the corresponding relay channel
                toggleRelay(i);
                bool newState = getRelayState(i);

                #if ENABLE_SERIAL_DEBUG
                Serial.printf("🔘 Physical Wall Switch %d flipped! Relay %d is now %s\n",
                              i + 1, i + 1, newState ? "ON" : "OFF");
                #endif

                // Push synchronized state to Firebase RTDB
                publishRelayToFirebase(i, newState);
            }
        }
    }
#endif
}

#endif // MANUAL_SWITCH_H
