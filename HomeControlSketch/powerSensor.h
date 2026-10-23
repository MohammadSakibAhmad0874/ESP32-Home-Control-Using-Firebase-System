/*
 * Hardware Energy & Power Sensing Module — ESP32 Home Control
 * Supports PZEM-004T v3.0 via Hardware Serial2 (UART) and ACS712 Hall-Effect Analog sensor.
 */

#ifndef POWER_SENSOR_H
#define POWER_SENSOR_H

#include <Arduino.h>
#include "config.h"

#if USE_PZEM
#include <PZEM004Tv30.h>
// PZEM-004T connected to ESP32 Serial2: RX on GPIO 16, TX on GPIO 17
static PZEM004Tv30 pzem(&Serial2, PZEM_RX_PIN, PZEM_TX_PIN);
#endif

// Power measurement data struct
struct PowerData {
    float voltage;    // Volts (V)
    float current;    // Amperes (A)
    float power;      // Watts (W)
    float energy;     // Kilowatt-hours (kWh)
    float frequency;  // Hertz (Hz)
    float pf;         // Power Factor (0.00 - 1.00)
    bool valid;
};

static unsigned long lastPowerReadTime = 0;
static const unsigned long POWER_READ_INTERVAL = 10000; // Read every 10 seconds

/*
 * Initialize Hardware Serial for PZEM-004T or ADC pin for ACS712
 */
inline void initPowerSensor() {
#if ENABLE_POWER_MONITORING
    #if USE_PZEM
    // Initialize Hardware Serial 2 (Baud 9600, 8N1, RX=16, TX=17)
    Serial2.begin(9600, SERIAL_8N1, PZEM_RX_PIN, PZEM_TX_PIN);
    #if ENABLE_SERIAL_DEBUG
    Serial.println("✓ PZEM-004T v3.0 Power Sensor initialized on Serial2 (RX 16, TX 17)");
    #endif
    #else
    pinMode(ACS712_ANALOG_PIN, INPUT);
    analogReadResolution(12); // 12-bit ADC (0 - 4095)
    #if ENABLE_SERIAL_DEBUG
    Serial.println("✓ ACS712 Current Sensor initialized on Analog GPIO " + String(ACS712_ANALOG_PIN));
    #endif
    #endif
#endif
}

/*
 * Read power telemetry from the active sensor
 */
inline PowerData readPowerData() {
    PowerData d = {0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 1.0f, false};

#if ENABLE_POWER_MONITORING
    #if USE_PZEM
    float v = pzem.voltage();
    float i = pzem.current();
    float p = pzem.power();
    float e = pzem.energy();
    float f = pzem.frequency();
    float pf = pzem.pf();

    if (!isnan(v)) {
        d.voltage = v;
        d.current = isnan(i) ? 0.0f : i;
        d.power = isnan(p) ? 0.0f : p;
        d.energy = isnan(e) ? 0.0f : e;
        d.frequency = isnan(f) ? 50.0f : f;
        d.pf = isnan(pf) ? 1.0f : pf;
        d.valid = true;
    }
    #else
    // Fallback: ACS712 20A Sensor (Sensitivity: 100mV/A, zero at 2.5V or 1.65V with divider)
    long sum = 0;
    for (int sample = 0; sample < 100; sample++) {
        sum += analogRead(ACS712_ANALOG_PIN);
        delayMicroseconds(100);
    }
    float rawVoltage = (sum / 100.0f / 4095.0f) * 3.3f;
    float currentAmps = abs(rawVoltage - 1.65f) / 0.100f; // 20A version calibrated
    d.voltage = 230.0f; // Assumed nominal mains voltage
    d.current = currentAmps;
    d.power = d.voltage * d.current;
    d.frequency = 50.0f;
    d.valid = true;
    #endif
#endif

    return d;
}

#endif // POWER_SENSOR_H
